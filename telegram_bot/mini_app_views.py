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
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from accounting.models.transaction import Transaction
from accounting.models.transactionCategory import TransactionCategoryTree
from accounting.models.wallet import Wallet
from users.models.user import User

from .utils import (diagnose_telegram_request, get_telegram_error_response,
                    log_telegram_request, safe_float_conversion)

logger = logging.getLogger(__name__)


class TelegramMiniAppView(View):
    """Базовый класс для Telegram Mini App views"""

    def get_context_data(self, **kwargs):
        """Добавляем параметр аутентификации в контекст"""
        # Для Django View базового класса нет get_context_data, поэтому создаем пустой контекст
        context = {}
        # Получаем _auth из GET или POST параметров
        context['auth_param'] = self.get_auth_param()
        context.update(kwargs)
        return context

    def get_auth_param(self):
        """Получаем параметр аутентификации из запроса"""
        return self.request.GET.get('_auth', '') or self.request.POST.get('_auth', '')

    def dispatch(self, request, *args, **kwargs):
        from django.conf import settings

        try:
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
                log_telegram_request(request, 'WARNING')
                error_response = get_telegram_error_response('unauthorized')
                return JsonResponse(error_response, status=error_response['code'])

            # Получаем пользователя из Telegram данных
            user = self._get_telegram_user(request)
            if not user:
                log_telegram_request(request, 'WARNING')
                error_response = get_telegram_error_response('user_not_found')
                return JsonResponse(error_response, status=error_response['code'])

            request.user = user
            return super().dispatch(request, *args, **kwargs)

        except Exception as e:
            log_telegram_request(request, 'ERROR')
            logger.error(
                f"Error in TelegramMiniAppView.dispatch: {e}", exc_info=True)
            error_response = get_telegram_error_response(
                'server_error', str(e))
            return JsonResponse(error_response, status=error_response['code'])

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

            # Проверяем, не попали ли данные аутентификации в путь URL
            if not init_data and request.path:
                # Ищем параметры аутентификации в пути URL (исправляем ошибки маршрутизации)
                path_parts = request.path.split('&_auth=')
                if len(path_parts) > 1:
                    # Восстанавливаем правильный путь и извлекаем данные аутентификации
                    correct_path = path_parts[0]
                    auth_data = '&_auth='.join(path_parts[1:])
                    logger.warning(
                        f"Found auth data in URL path, correcting: {request.path} -> {correct_path}")
                    # Обновляем путь в запросе для корректной обработки
                    request.path = correct_path
                    request.path_info = correct_path
                    init_data = auth_data

            if not init_data:
                logger.warning("No Telegram WebApp data found in request")
                return None

            # Логируем полученные данные для отладки (без полного содержимого)
            logger.info(f"Received Telegram WebApp data: {init_data[:50]}...")

            # Используем aiogram 3 для безопасной проверки данных WebApp
            from django.conf import settings
            bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')

            user_data = None

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
                    logger.info(
                        f"Successfully parsed WebApp data with aiogram for user: {user_obj.id}")
                except (ValueError, ImportError, AttributeError) as e:
                    logger.warning(
                        f"Failed to parse WebApp data with aiogram: {e}")
                    # Fallback на старую логику
                    try:
                        from .telegram_auth import \
                            get_telegram_user_from_webapp
                        user_data = get_telegram_user_from_webapp(
                            init_data, verify_signature=True)
                        if user_data:
                            logger.info(
                                f"Successfully parsed WebApp data with fallback method for user: {user_data.get('id')}")
                    except Exception as fallback_error:
                        logger.error(
                            f"Fallback parsing also failed: {fallback_error}")
                        user_data = None
            else:
                logger.warning(
                    "No Telegram bot token configured, using unverified parsing")
                # Если нет токена, используем старую логику без проверки подписи
                try:
                    from .telegram_auth import get_telegram_user_from_webapp
                    user_data = get_telegram_user_from_webapp(
                        init_data, verify_signature=False)
                    if user_data:
                        logger.info(
                            f"Successfully parsed WebApp data without verification for user: {user_data.get('id')}")
                except Exception as unverified_error:
                    logger.error(
                        f"Unverified parsing failed: {unverified_error}")
                    user_data = None

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
            else:
                logger.info(
                    f"Found existing user: {user.username} (telegram_id: {telegram_id})")

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

        # Используем новую утилиту для диагностики
        diagnosis = diagnose_telegram_request(request)

        # Собираем информацию о конфигурации
        config_info = {
            'DEBUG': settings.DEBUG,
            'TELEGRAM_MINIAPP_URL': settings.TELEGRAM_MINIAPP_URL,
            'TELEGRAM_MINIAPP_DEBUG_MODE': settings.TELEGRAM_MINIAPP_DEBUG_MODE,
            'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
            'TELEGRAM_BOT_TOKEN': settings.TELEGRAM_BOT_TOKEN[:10] + '...' if settings.TELEGRAM_BOT_TOKEN else 'Not set',
            'request_host': request.get_host(),
            'request_method': request.method,
            'is_telegram_request': diagnosis['is_telegram_request'],
            'telegram_detection_details': diagnosis['detection_methods'],
            'telegram_data_raw': init_data[:100] + '...' if init_data and len(init_data) > 100 else init_data,
            'telegram_data_parsed': diagnosis['parsed_data'],
            'signature_valid': signature_valid,
            'all_get_params': dict(request.GET),
            'all_post_params': dict(request.POST),
            'diagnosis_errors': diagnosis['errors'],
            'recommendations': diagnosis['recommendations'],
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
            transactions = transactions.filter(wallet__uuid=wallet_id)
        if category_id:
            transactions = transactions.filter(category__uuid=category_id)
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

                # Безопасная конвертация суммы
                amount_str = request.POST.get('amount')
                if not amount_str or not amount_str.strip():
                    messages.error(request, 'Сумма не может быть пустой')
                    redirect_url = reverse('telegram_bot:transaction_create')
                    auth_param = self.get_auth_param()
                    if auth_param:
                        redirect_url += f'?_auth={auth_param}'
                    return redirect(redirect_url)

                is_valid, amount, error_msg = safe_float_conversion(
                    amount_str, 0.0, 'сумма')
                if not is_valid:
                    logger.error(f"Invalid amount value: '{amount_str}'")
                    messages.error(request, error_msg)
                    redirect_url = reverse('telegram_bot:transaction_create')
                    auth_param = self.get_auth_param()
                    if auth_param:
                        redirect_url += f'?_auth={auth_param}'
                    return redirect(redirect_url)

                # Безопасная конвертация налога
                tax_str = request.POST.get('tax', '0')
                _, tax, _ = safe_float_conversion(tax_str, 0.0, 'налог')

                transaction_obj = Transaction.objects.create(
                    t_type=request.POST.get('t_type'),
                    wallet=wallet,
                    user=request.user,
                    category=category,
                    amount=amount,
                    tax=tax,
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
                # Добавляем auth_param к редиректу
                redirect_url = reverse('telegram_bot:transactions')
                auth_param = self.get_auth_param()
                if auth_param:
                    redirect_url += f'?_auth={auth_param}'
                return redirect(redirect_url)

        except Exception as e:
            logger.error(f"Error creating transaction: {e}")
            messages.error(
                request, f'Ошибка при создании транзакции: {str(e)}')
            # Добавляем auth_param к редиректу при ошибке
            redirect_url = reverse('telegram_bot:transaction_create')
            auth_param = self.get_auth_param()
            if auth_param:
                redirect_url += f'?_auth={auth_param}'
            return redirect(redirect_url)


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

                # Безопасная конвертация суммы
                amount_str = request.POST.get('amount')
                if not amount_str or not amount_str.strip():
                    messages.error(request, 'Сумма не может быть пустой')
                    redirect_url = reverse('telegram_bot:transaction_edit', kwargs={
                                           'transaction_id': transaction_id})
                    auth_param = self.get_auth_param()
                    if auth_param:
                        redirect_url += f'?_auth={auth_param}'
                    return redirect(redirect_url)

                is_valid, amount, error_msg = safe_float_conversion(
                    amount_str, 0.0, 'сумма')
                if not is_valid:
                    logger.error(f"Invalid amount value: '{amount_str}'")
                    messages.error(request, error_msg)
                    redirect_url = reverse('telegram_bot:transaction_edit', kwargs={
                                           'transaction_id': transaction_id})
                    auth_param = self.get_auth_param()
                    if auth_param:
                        redirect_url += f'?_auth={auth_param}'
                    return redirect(redirect_url)
                transaction_obj.amount = amount

                # Безопасная конвертация налога
                tax_str = request.POST.get('tax', '0')
                _, tax, _ = safe_float_conversion(tax_str, 0.0, 'налог')
                transaction_obj.tax = tax

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
                # Добавляем auth_param к редиректу
                redirect_url = reverse('telegram_bot:transactions')
                auth_param = self.get_auth_param()
                if auth_param:
                    redirect_url += f'?_auth={auth_param}'
                return redirect(redirect_url)

        except Exception as e:
            logger.error(f"Error updating transaction: {e}")
            messages.error(
                request, f'Ошибка при обновлении транзакции: {str(e)}')
            # Добавляем auth_param к редиректу при ошибке
            redirect_url = reverse('telegram_bot:transaction_edit', kwargs={
                                   'transaction_id': transaction_id})
            auth_param = self.get_auth_param()
            if auth_param:
                redirect_url += f'?_auth={auth_param}'
            return redirect(redirect_url)


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
                # Добавляем auth_param к редиректу
                redirect_url = reverse('telegram_bot:transactions')
                auth_param = self.get_auth_param()
                if auth_param:
                    redirect_url += f'?_auth={auth_param}'
                return redirect(redirect_url)

        except Exception as e:
            logger.error(f"Error deleting transaction: {e}")
            messages.error(
                request, f'Ошибка при удалении транзакции: {str(e)}')
            # Добавляем auth_param к редиректу при ошибке
            redirect_url = reverse('telegram_bot:transactions')
            auth_param = self.get_auth_param()
            if auth_param:
                redirect_url += f'?_auth={auth_param}'
            return redirect(redirect_url)


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
                CurrencyCBR, uuid=request.POST.get('currency'))

            # Безопасная конвертация баланса
            balance_str = request.POST.get('balance', '0')
            is_valid, balance, error_msg = safe_float_conversion(
                balance_str, 0.0, 'баланс')
            if not is_valid:
                logger.error(f"Invalid balance value: '{balance_str}'")
                messages.error(request, error_msg)
                redirect_url = reverse('telegram_bot:wallet_create')
                auth_param = self.get_auth_param()
                if auth_param:
                    redirect_url += f'?_auth={auth_param}'
                return redirect(redirect_url)

            wallet = Wallet.objects.create(
                user=request.user,
                title=request.POST.get('title'),
                currency=currency,
                balance=balance,
                is_family_access=request.POST.get('is_family_access') == 'on',
                description=request.POST.get('description', '')
            )

            messages.success(request, 'Кошелек успешно создан!')
            # Добавляем auth_param к редиректу
            redirect_url = reverse('telegram_bot:wallets')
            auth_param = self.get_auth_param()
            if auth_param:
                redirect_url += f'?_auth={auth_param}'
            return redirect(redirect_url)

        except Exception as e:
            logger.error(f"Error creating wallet: {e}")
            messages.error(request, f'Ошибка при создании кошелька: {str(e)}')
            # Добавляем auth_param к редиректу при ошибке
            redirect_url = reverse('telegram_bot:wallet_create')
            auth_param = self.get_auth_param()
            if auth_param:
                redirect_url += f'?_auth={auth_param}'
            return redirect(redirect_url)


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
                CurrencyCBR, uuid=request.POST.get('currency'))

            wallet.title = request.POST.get('title')
            wallet.currency = currency

            # Безопасная конвертация баланса
            balance_str = request.POST.get('balance', '0')
            is_valid, balance, error_msg = safe_float_conversion(
                balance_str, 0.0, 'баланс')
            if not is_valid:
                logger.error(f"Invalid balance value: '{balance_str}'")
                messages.error(request, error_msg)
                redirect_url = reverse('telegram_bot:wallet_edit', kwargs={
                                       'wallet_id': wallet_id})
                auth_param = self.get_auth_param()
                if auth_param:
                    redirect_url += f'?_auth={auth_param}'
                return redirect(redirect_url)
            wallet.balance = balance

            wallet.is_family_access = request.POST.get(
                'is_family_access') == 'on'
            wallet.description = request.POST.get('description', '')
            wallet.save()

            messages.success(request, 'Кошелек успешно обновлен!')
            # Добавляем auth_param к редиректу
            redirect_url = reverse('telegram_bot:wallets')
            auth_param = self.get_auth_param()
            if auth_param:
                redirect_url += f'?_auth={auth_param}'
            return redirect(redirect_url)

        except Exception as e:
            logger.error(f"Error updating wallet: {e}")
            messages.error(
                request, f'Ошибка при обновлении кошелька: {str(e)}')
            # Добавляем auth_param к редиректу при ошибке
            redirect_url = reverse('telegram_bot:wallet_edit', kwargs={
                                   'wallet_id': wallet_id})
            auth_param = self.get_auth_param()
            if auth_param:
                redirect_url += f'?_auth={auth_param}'
            return redirect(redirect_url)


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
                # Добавляем auth_param к редиректу
                redirect_url = reverse('telegram_bot:wallets')
                auth_param = self.get_auth_param()
                if auth_param:
                    redirect_url += f'?_auth={auth_param}'
                return redirect(redirect_url)

            wallet.delete()

            messages.success(request, 'Кошелек успешно удален!')
            # Добавляем auth_param к редиректу
            redirect_url = reverse('telegram_bot:wallets')
            auth_param = self.get_auth_param()
            if auth_param:
                redirect_url += f'?_auth={auth_param}'
            return redirect(redirect_url)

        except Exception as e:
            logger.error(f"Error deleting wallet: {e}")
            messages.error(request, f'Ошибка при удалении кошелька: {str(e)}')
            # Добавляем auth_param к редиректу при ошибке
            redirect_url = reverse('telegram_bot:wallets')
            auth_param = self.get_auth_param()
            if auth_param:
                redirect_url += f'?_auth={auth_param}'
            return redirect(redirect_url)


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
            # Добавляем auth_param к редиректу
            redirect_url = reverse('telegram_bot:categories')
            auth_param = self.get_auth_param()
            if auth_param:
                redirect_url += f'?_auth={auth_param}'
            return redirect(redirect_url)

        except Exception as e:
            logger.error(f"Error creating category: {e}")
            messages.error(request, f'Ошибка при создании категории: {str(e)}')
            # Добавляем auth_param к редиректу при ошибке
            redirect_url = reverse('telegram_bot:category_create')
            auth_param = self.get_auth_param()
            if auth_param:
                redirect_url += f'?_auth={auth_param}'
            return redirect(redirect_url)


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
            # Добавляем auth_param к редиректу
            redirect_url = reverse('telegram_bot:categories')
            auth_param = self.get_auth_param()
            if auth_param:
                redirect_url += f'?_auth={auth_param}'
            return redirect(redirect_url)

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
                # Добавляем auth_param к редиректу
                redirect_url = reverse('telegram_bot:categories')
                auth_param = self.get_auth_param()
                if auth_param:
                    redirect_url += f'?_auth={auth_param}'
                return redirect(redirect_url)

            # Проверяем, есть ли дочерние категории
            children_count = category.get_children().count()
            if children_count > 0:
                messages.error(
                    request, f'Нельзя удалить категорию с {children_count} подкатегориями')
                # Добавляем auth_param к редиректу
                redirect_url = reverse('telegram_bot:categories')
                auth_param = self.get_auth_param()
                if auth_param:
                    redirect_url += f'?_auth={auth_param}'
                return redirect(redirect_url)

            category.delete()

            messages.success(request, 'Категория успешно удалена!')
            # Добавляем auth_param к редиректу
            redirect_url = reverse('telegram_bot:categories')
            auth_param = self.get_auth_param()
            if auth_param:
                redirect_url += f'?_auth={auth_param}'
            return redirect(redirect_url)

        except Exception as e:
            logger.error(f"Error deleting category: {e}")
            messages.error(request, f'Ошибка при удалении категории: {str(e)}')
            # Добавляем auth_param к редиректу при ошибке
            redirect_url = reverse('telegram_bot:categories')
            auth_param = self.get_auth_param()
            if auth_param:
                redirect_url += f'?_auth={auth_param}'
            return redirect(redirect_url)
