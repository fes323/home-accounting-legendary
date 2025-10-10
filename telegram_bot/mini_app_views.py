import json
import logging
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from accounting.models.transaction import Transaction
from accounting.models.transactionCategory import TransactionCategoryTree
from accounting.models.wallet import Wallet
from users.models.user import User

logger = logging.getLogger(__name__)


class TelegramMiniAppView(View):
    """Базовый класс для Telegram Mini App views"""

    def get_context_data(self, **kwargs):
        """Добавляем параметр аутентификации в контекст"""
        # Для Django View базового класса нет get_context_data, поэтому создаем пустой контекст
        context = {}
        context['auth_param'] = self.request.GET.get('_auth', '')
        context.update(kwargs)
        return context

    def dispatch(self, request, *args, **kwargs):
        from django.conf import settings

        # В режиме отладки разрешаем доступ без Telegram данных
        if settings.TELEGRAM_MINIAPP_DEBUG_MODE and not self._is_telegram_request(request):
            # Создаем тестового пользователя для разработки
            from users.models.user import User
            test_user, created = User.objects.get_or_create(
                telegram_id=123456789,  # Тестовый ID
                defaults={
                    'username': 'test_user',
                    'first_name': 'Test',
                    'last_name': 'User'
                }
            )
            request.user = test_user
            return super().dispatch(request, *args, **kwargs)

        # Проверяем, что запрос приходит из Telegram
        if not self._is_telegram_request(request):
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        # Получаем пользователя из Telegram данных
        user = self._get_telegram_user(request)
        if not user:
            return JsonResponse({'error': 'User not found'}, status=401)

        request.user = user
        return super().dispatch(request, *args, **kwargs)

    def _is_telegram_request(self, request):
        """Проверяем, что запрос приходит из Telegram"""
        # Проверяем данные Telegram WebApp в поле _auth (согласно документации Aiogram)
        init_data = request.GET.get('_auth') or request.POST.get('_auth')
        if init_data:
            return True

        # Также проверяем старый формат для совместимости
        init_data = request.GET.get(
            'tgWebAppData') or request.POST.get('tgWebAppData')
        if init_data:
            return True

        # Проверяем User-Agent Telegram WebApp
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'TelegramBot' in user_agent or 'Telegram' in user_agent:
            return True

        # Проверяем заголовки, которые отправляет Telegram
        if 'X-Telegram-Bot-Api-Secret-Token' in request.META:
            return True

        # Проверяем Referer от Telegram
        referer = request.META.get('HTTP_REFERER', '')
        if 'web.telegram.org' in referer or 'webk.telegram.org' in referer or 'webz.telegram.org' in referer:
            return True

        return False

    def _get_telegram_user(self, request):
        """Получаем пользователя из Telegram данных"""
        try:
            # Получаем данные из Telegram WebApp (сначала проверяем _auth, потом старый формат)
            init_data = request.GET.get('_auth') or request.POST.get('_auth')
            if not init_data:
                init_data = request.GET.get(
                    'tgWebAppData') or request.POST.get('tgWebAppData')

            if not init_data:
                logger.warning("No Telegram WebApp data found in request")
                return None

            # Используем aiogram 3 для безопасной проверки данных WebApp
            from django.conf import settings
            bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')

            if bot_token:
                try:
                    from aiogram.utils.web_app import \
                        safe_parse_webapp_init_data
                    webapp_data = safe_parse_webapp_init_data(
                        bot_token, init_data)
                    # WebAppInitData - это объект с атрибутами, не словарь
                    user_obj = webapp_data.user
                    user_data = {
                        'id': user_obj.id,
                        'first_name': user_obj.first_name,
                        'last_name': user_obj.last_name,
                        'username': user_obj.username,
                    }
                except (ValueError, ImportError) as e:
                    logger.warning(
                        f"Failed to parse WebApp data with aiogram: {e}")
                    # Fallback на старую логику
                    from .telegram_auth import get_telegram_user_from_webapp
                    user_data = get_telegram_user_from_webapp(
                        init_data, verify_signature=True)
            else:
                # Если нет токена, используем старую логику без проверки подписи
                from .telegram_auth import get_telegram_user_from_webapp
                user_data = get_telegram_user_from_webapp(
                    init_data, verify_signature=False)

            if not user_data:
                logger.warning(
                    "Failed to parse or verify Telegram WebApp data")
                return None

            telegram_id = user_data.get('id')
            if not telegram_id:
                logger.warning("No telegram_id found in user data")
                return None

            # Ищем или создаем пользователя
            user = User.objects.filter(telegram_id=telegram_id).first()
            if not user:
                # Создаем нового пользователя
                username = user_data.get('username') or f"tg_{telegram_id}"
                user = User.objects.create(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', ''),
                )
                logger.info(
                    f"Created new user: {user.username} (telegram_id: {telegram_id})")

            return user

        except Exception as e:
            logger.error(f"Error getting telegram user: {e}", exc_info=True)
            return None


class MiniAppDiagnosticView(View):
    """Диагностическая страница для проверки конфигурации Mini App"""

    def get(self, request):
        from django.conf import settings

        # Парсим Telegram данные для диагностики
        telegram_data_parsed = {}
        signature_valid = False
        # Проверяем оба формата данных
        init_data = request.GET.get('_auth') or request.POST.get('_auth')
        if not init_data:
            init_data = request.GET.get(
                'tgWebAppData') or request.POST.get('tgWebAppData')

        if init_data:
            try:
                from .telegram_auth import (get_telegram_user_from_webapp,
                                            verify_telegram_webapp_data)
                telegram_data_parsed = get_telegram_user_from_webapp(
                    init_data, verify_signature=False)
                signature_valid = verify_telegram_webapp_data(
                    init_data, settings.TELEGRAM_BOT_TOKEN)
            except Exception as e:
                telegram_data_parsed = {'error': str(e)}

        # Детальная диагностика Telegram запроса
        telegram_detection_details = {
            'has_auth_data': bool(request.GET.get('_auth') or request.POST.get('_auth')),
            'has_tgWebAppData': bool(request.GET.get('tgWebAppData') or request.POST.get('tgWebAppData')),
            'has_any_telegram_data': bool(init_data),
            'user_agent_contains_telegram': 'Telegram' in request.META.get('HTTP_USER_AGENT', ''),
            'has_telegram_secret_token': 'X-Telegram-Bot-Api-Secret-Token' in request.META,
            'referer_from_telegram': any(domain in request.META.get('HTTP_REFERER', '')
                                         for domain in ['web.telegram.org', 'webk.telegram.org', 'webz.telegram.org']),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'referer': request.META.get('HTTP_REFERER', ''),
            'all_headers': {k: v for k, v in request.META.items() if k.startswith('HTTP_')}
        }

        # Собираем информацию о конфигурации
        config_info = {
            'DEBUG': settings.DEBUG,
            'TELEGRAM_MINIAPP_URL': settings.TELEGRAM_MINIAPP_URL,
            'TELEGRAM_MINIAPP_DEBUG_MODE': settings.TELEGRAM_MINIAPP_DEBUG_MODE,
            'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
            'TELEGRAM_BOT_TOKEN': settings.TELEGRAM_BOT_TOKEN[:10] + '...' if settings.TELEGRAM_BOT_TOKEN else 'Not set',
            'request_host': request.get_host(),
            'request_method': request.method,
            'is_telegram_request': self._is_telegram_request(request),
            'telegram_detection_details': telegram_detection_details,
            'telegram_data_raw': init_data[:100] + '...' if init_data and len(init_data) > 100 else init_data,
            'telegram_data_parsed': telegram_data_parsed,
            'signature_valid': signature_valid,
            'all_get_params': dict(request.GET),
            'all_post_params': dict(request.POST),
        }

        # Если это запрос из браузера, показываем диагностическую информацию
        if not self._is_telegram_request(request):
            return render(request, 'telegram_bot/diagnostic.html', {
                'config_info': config_info
            })

        # Если это запрос из Telegram, перенаправляем на главную
        return redirect('telegram_bot:mini_app_dashboard')

    def _is_telegram_request(self, request):
        """Проверяем, что запрос приходит из Telegram"""
        init_data = request.GET.get(
            'tgWebAppData') or request.POST.get('tgWebAppData')
        return bool(init_data)


class MiniAppDashboardView(TelegramMiniAppView):
    """Главная страница mini-app"""

    def get(self, request):
        # Получаем статистику
        user_transactions = Transaction.objects.filter(user=request.user)

        # Статистика за последние 30 дней
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        recent_transactions = user_transactions.filter(
            date__gte=thirty_days_ago)

        total_income = recent_transactions.filter(t_type='IN').aggregate(
            total=Sum('amount')
        )['total'] or 0

        total_expense = recent_transactions.filter(t_type='EX').aggregate(
            total=Sum('amount')
        )['total'] or 0

        balance = total_income - total_expense

        # Последние транзакции
        recent_transactions_list = user_transactions.order_by(
            '-created_at')[:5]

        # Кошельки
        wallets = Wallet.objects.filter(user=request.user)

        context = self.get_context_data(
            total_income=total_income,
            total_expense=total_expense,
            balance=balance,
            recent_transactions=recent_transactions_list,
            wallets=wallets,
            transaction_count=recent_transactions.count(),
            user=request.user
        )

        return render(request, 'telegram_bot/dashboard.html', context)


class TransactionListView(TelegramMiniAppView):
    """Список транзакций"""

    def get(self, request):
        transactions = Transaction.objects.filter(
            user=request.user).order_by('-created_at')

        # Фильтрация
        t_type = request.GET.get('type')
        wallet_id = request.GET.get('wallet')
        category_id = request.GET.get('category')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')

        if t_type:
            transactions = transactions.filter(t_type=t_type)
        if wallet_id:
            transactions = transactions.filter(wallet_id=wallet_id)
        if category_id:
            transactions = transactions.filter(category_id=category_id)
        if date_from:
            transactions = transactions.filter(date__gte=date_from)
        if date_to:
            transactions = transactions.filter(date__lte=date_to)

        # Пагинация
        paginator = Paginator(transactions, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Данные для фильтров
        wallets = Wallet.objects.filter(user=request.user)
        categories = TransactionCategoryTree.objects.filter(user=request.user)

        context = self.get_context_data(
            page_obj=page_obj,
            wallets=wallets,
            categories=categories,
            filters={
                'type': t_type,
                'wallet': wallet_id,
                'category': category_id,
                'date_from': date_from,
                'date_to': date_to,
            }
        )

        return render(request, 'telegram_bot/transactions/list.html', context)


class TransactionCreateView(TelegramMiniAppView):
    """Создание транзакции"""

    def get(self, request):
        wallets = Wallet.objects.filter(user=request.user)
        categories = TransactionCategoryTree.objects.filter(user=request.user)

        context = self.get_context_data(
            wallets=wallets,
            categories=categories,
            transaction_types=Transaction.CHOICES
        )

        return render(request, 'telegram_bot/transactions/create.html', context)

    def post(self, request):
        try:
            with transaction.atomic():
                wallet = get_object_or_404(
                    Wallet, uuid=request.POST.get('wallet'), user=request.user)
                category = None
                if request.POST.get('category'):
                    category = get_object_or_404(
                        TransactionCategoryTree, uuid=request.POST.get('category'), user=request.user)

                transaction_obj = Transaction.objects.create(
                    t_type=request.POST.get('t_type'),
                    wallet=wallet,
                    user=request.user,
                    category=category,
                    amount=request.POST.get('amount'),
                    tax=request.POST.get('tax', 0),
                    description=request.POST.get('description', ''),
                    date=request.POST.get('date', datetime.now().date())
                )

                # Обновляем баланс кошелька
                if transaction_obj.t_type == 'IN':
                    wallet.balance += transaction_obj.amount
                else:
                    wallet.balance -= transaction_obj.amount
                wallet.save()

                messages.success(request, 'Транзакция успешно создана!')
                return redirect('telegram_bot:transactions')

        except Exception as e:
            logger.error(f"Error creating transaction: {e}")
            messages.error(
                request, f'Ошибка при создании транзакции: {str(e)}')
            return redirect('telegram_bot:transaction_create')


class TransactionEditView(TelegramMiniAppView):
    """Редактирование транзакции"""

    def get(self, request, transaction_id):
        transaction_obj = get_object_or_404(
            Transaction, uuid=transaction_id, user=request.user)
        wallets = Wallet.objects.filter(user=request.user)
        categories = TransactionCategoryTree.objects.filter(user=request.user)

        context = self.get_context_data(
            transaction=transaction_obj,
            wallets=wallets,
            categories=categories,
            transaction_types=Transaction.CHOICES
        )

        return render(request, 'telegram_bot/transactions/edit.html', context)

    def post(self, request, transaction_id):
        try:
            with transaction.atomic():
                transaction_obj = get_object_or_404(
                    Transaction, uuid=transaction_id, user=request.user)

                # Сохраняем старые значения для пересчета баланса
                old_amount = transaction_obj.amount
                old_type = transaction_obj.t_type
                old_wallet = transaction_obj.wallet

                wallet = get_object_or_404(
                    Wallet, uuid=request.POST.get('wallet'), user=request.user)
                category = None
                if request.POST.get('category'):
                    category = get_object_or_404(
                        TransactionCategoryTree, uuid=request.POST.get('category'), user=request.user)

                # Обновляем транзакцию
                transaction_obj.t_type = request.POST.get('t_type')
                transaction_obj.wallet = wallet
                transaction_obj.category = category
                transaction_obj.amount = float(request.POST.get('amount'))
                transaction_obj.tax = float(request.POST.get('tax', 0))
                transaction_obj.description = request.POST.get(
                    'description', '')
                transaction_obj.date = request.POST.get(
                    'date', datetime.now().date())
                transaction_obj.save()

                # Пересчитываем балансы кошельков
                # Убираем старую транзакцию
                if old_type == 'IN':
                    old_wallet.balance -= old_amount
                else:
                    old_wallet.balance += old_amount
                old_wallet.save()

                # Добавляем новую транзакцию
                if transaction_obj.t_type == 'IN':
                    wallet.balance += transaction_obj.amount
                else:
                    wallet.balance -= transaction_obj.amount
                wallet.save()

                messages.success(request, 'Транзакция успешно обновлена!')
                return redirect('telegram_bot:transactions')

        except Exception as e:
            logger.error(f"Error updating transaction: {e}")
            messages.error(
                request, f'Ошибка при обновлении транзакции: {str(e)}')
            return redirect('telegram_bot:transaction_edit', transaction_id=transaction_id)


class TransactionDeleteView(TelegramMiniAppView):
    """Удаление транзакции"""

    def post(self, request, transaction_id):
        try:
            with transaction.atomic():
                transaction_obj = get_object_or_404(
                    Transaction, uuid=transaction_id, user=request.user)
                wallet = transaction_obj.wallet

                # Возвращаем баланс кошелька
                if transaction_obj.t_type == 'IN':
                    wallet.balance -= transaction_obj.amount
                else:
                    wallet.balance += transaction_obj.amount
                wallet.save()

                transaction_obj.delete()

                messages.success(request, 'Транзакция успешно удалена!')
                return redirect('telegram_bot:transactions')

        except Exception as e:
            logger.error(f"Error deleting transaction: {e}")
            messages.error(
                request, f'Ошибка при удалении транзакции: {str(e)}')
            return redirect('telegram_bot:transactions')


class WalletListView(TelegramMiniAppView):
    """Список кошельков"""

    def get(self, request):
        wallets = Wallet.objects.filter(user=request.user).order_by('title')

        context = self.get_context_data(
            wallets=wallets
        )

        return render(request, 'telegram_bot/wallets/list.html', context)


class WalletCreateView(TelegramMiniAppView):
    """Создание кошелька"""

    def get(self, request):
        from accounting.models.currencyCBR import CurrencyCBR
        currencies = CurrencyCBR.objects.all()

        context = self.get_context_data(
            currencies=currencies
        )

        return render(request, 'telegram_bot/wallets/create.html', context)

    def post(self, request):
        try:
            from accounting.models.currencyCBR import CurrencyCBR

            currency = get_object_or_404(
                CurrencyCBR, id=request.POST.get('currency'))

            wallet = Wallet.objects.create(
                user=request.user,
                title=request.POST.get('title'),
                currency=currency,
                balance=float(request.POST.get('balance', 0)),
                is_family_access=request.POST.get('is_family_access') == 'on',
                description=request.POST.get('description', '')
            )

            messages.success(request, 'Кошелек успешно создан!')
            return redirect('telegram_bot:wallets')

        except Exception as e:
            logger.error(f"Error creating wallet: {e}")
            messages.error(request, f'Ошибка при создании кошелька: {str(e)}')
            return redirect('telegram_bot:wallet_create')


class WalletEditView(TelegramMiniAppView):
    """Редактирование кошелька"""

    def get(self, request, wallet_id):
        wallet = get_object_or_404(Wallet, uuid=wallet_id, user=request.user)
        from accounting.models.currencyCBR import CurrencyCBR
        currencies = CurrencyCBR.objects.all()

        context = self.get_context_data(
            wallet=wallet,
            currencies=currencies
        )

        return render(request, 'telegram_bot/wallets/edit.html', context)

    def post(self, request, wallet_id):
        try:
            from accounting.models.currencyCBR import CurrencyCBR

            wallet = get_object_or_404(
                Wallet, uuid=wallet_id, user=request.user)
            currency = get_object_or_404(
                CurrencyCBR, id=request.POST.get('currency'))

            wallet.title = request.POST.get('title')
            wallet.currency = currency
            wallet.balance = float(request.POST.get('balance', 0))
            wallet.is_family_access = request.POST.get(
                'is_family_access') == 'on'
            wallet.description = request.POST.get('description', '')
            wallet.save()

            messages.success(request, 'Кошелек успешно обновлен!')
            return redirect('telegram_bot:wallets')

        except Exception as e:
            logger.error(f"Error updating wallet: {e}")
            messages.error(
                request, f'Ошибка при обновлении кошелька: {str(e)}')
            return redirect('telegram_bot:wallet_edit', wallet_id=wallet_id)


class WalletDeleteView(TelegramMiniAppView):
    """Удаление кошелька"""

    def post(self, request, wallet_id):
        try:
            wallet = get_object_or_404(
                Wallet, uuid=wallet_id, user=request.user)

            # Проверяем, есть ли транзакции в этом кошельке
            transaction_count = Transaction.objects.filter(
                wallet=wallet, user=request.user).count()
            if transaction_count > 0:
                messages.error(
                    request, f'Нельзя удалить кошелек с {transaction_count} транзакциями')
                return redirect('telegram_bot:wallets')

            wallet.delete()

            messages.success(request, 'Кошелек успешно удален!')
            return redirect('telegram_bot:wallets')

        except Exception as e:
            logger.error(f"Error deleting wallet: {e}")
            messages.error(request, f'Ошибка при удалении кошелька: {str(e)}')
            return redirect('telegram_bot:wallets')


class CategoryListView(TelegramMiniAppView):
    """Список категорий"""

    def get(self, request):
        categories = TransactionCategoryTree.objects.filter(
            user=request.user).order_by('title')

        context = self.get_context_data(
            categories=categories
        )

        return render(request, 'telegram_bot/categories/list.html', context)


class CategoryCreateView(TelegramMiniAppView):
    """Создание категории"""

    def get(self, request):
        categories = TransactionCategoryTree.objects.filter(user=request.user)

        context = self.get_context_data(
            categories=categories
        )

        return render(request, 'telegram_bot/categories/create.html', context)

    def post(self, request):
        try:
            parent = None
            if request.POST.get('parent'):
                parent = get_object_or_404(
                    TransactionCategoryTree, uuid=request.POST.get('parent'), user=request.user)

            category = TransactionCategoryTree.objects.create(
                user=request.user,
                title=request.POST.get('title'),
                parent=parent,
                description=request.POST.get('description', '')
            )

            messages.success(request, 'Категория успешно создана!')
            return redirect('telegram_bot:categories')

        except Exception as e:
            logger.error(f"Error creating category: {e}")
            messages.error(request, f'Ошибка при создании категории: {str(e)}')
            return redirect('telegram_bot:category_create')


class CategoryEditView(TelegramMiniAppView):
    """Редактирование категории"""

    def get(self, request, category_id):
        category = get_object_or_404(
            TransactionCategoryTree, uuid=category_id, user=request.user)
        categories = TransactionCategoryTree.objects.filter(
            user=request.user).exclude(uuid=category_id)

        context = self.get_context_data(
            category=category,
            categories=categories
        )

        return render(request, 'telegram_bot/categories/edit.html', context)

    def post(self, request, category_id):
        try:
            category = get_object_or_404(
                TransactionCategoryTree, uuid=category_id, user=request.user)

            parent = None
            if request.POST.get('parent'):
                parent = get_object_or_404(
                    TransactionCategoryTree, uuid=request.POST.get('parent'), user=request.user)

            category.title = request.POST.get('title')
            category.parent = parent
            category.description = request.POST.get('description', '')
            category.save()

            messages.success(request, 'Категория успешно обновлена!')
            return redirect('telegram_bot:categories')

        except Exception as e:
            logger.error(f"Error updating category: {e}")
            messages.error(
                request, f'Ошибка при обновлении категории: {str(e)}')
            return redirect('telegram_bot:category_edit', category_id=category_id)


class CategoryDeleteView(TelegramMiniAppView):
    """Удаление категории"""

    def post(self, request, category_id):
        try:
            category = get_object_or_404(
                TransactionCategoryTree, uuid=category_id, user=request.user)

            # Проверяем, есть ли транзакции в этой категории
            transaction_count = Transaction.objects.filter(
                category=category, user=request.user).count()
            if transaction_count > 0:
                messages.error(
                    request, f'Нельзя удалить категорию с {transaction_count} транзакциями')
                return redirect('telegram_bot:categories')

            # Проверяем, есть ли дочерние категории
            children_count = category.get_children().count()
            if children_count > 0:
                messages.error(
                    request, f'Нельзя удалить категорию с {children_count} подкатегориями')
                return redirect('telegram_bot:categories')

            category.delete()

            messages.success(request, 'Категория успешно удалена!')
            return redirect('telegram_bot:categories')

        except Exception as e:
            logger.error(f"Error deleting category: {e}")
            messages.error(request, f'Ошибка при удалении категории: {str(e)}')
            return redirect('telegram_bot:categories')
