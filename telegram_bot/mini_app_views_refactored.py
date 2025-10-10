"""
Рефакторенные views для Telegram Mini App
Используют новую систему аутентификации через сессии Django
"""
import logging
from datetime import datetime, timedelta

from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounting.models.transaction import Transaction
from accounting.models.transactionCategory import TransactionCategoryTree
from accounting.models.wallet import Wallet

from .utils import safe_float_conversion
from .views.telegram_base_view import TelegramWebAppAuthenticatedView

logger = logging.getLogger(__name__)


class MiniAppDashboardView(TelegramWebAppAuthenticatedView):
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
        )

        return render(request, 'telegram_bot/dashboard.html', context)


class TransactionListView(TelegramWebAppAuthenticatedView):
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


class TransactionCreateView(TelegramWebAppAuthenticatedView):
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
                    return redirect('telegram_bot:transaction_create')

                is_valid, amount, error_msg = safe_float_conversion(
                    amount_str, 0.0, 'сумма')
                if not is_valid:
                    logger.error(f"Invalid amount value: '{amount_str}'")
                    messages.error(request, error_msg)
                    return redirect('telegram_bot:transaction_create')

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
                return redirect('telegram_bot:transactions')

        except Exception as e:
            logger.error(f"Error creating transaction: {e}")
            messages.error(
                request, f'Ошибка при создании транзакции: {str(e)}')
            return redirect('telegram_bot:transaction_create')


class TransactionEditView(TelegramWebAppAuthenticatedView):
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
                    return redirect('telegram_bot:transaction_edit', transaction_id=transaction_id)

                is_valid, amount, error_msg = safe_float_conversion(
                    amount_str, 0.0, 'сумма')
                if not is_valid:
                    logger.error(f"Invalid amount value: '{amount_str}'")
                    messages.error(request, error_msg)
                    return redirect('telegram_bot:transaction_edit', transaction_id=transaction_id)
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
                return redirect('telegram_bot:transactions')

        except Exception as e:
            logger.error(f"Error updating transaction: {e}")
            messages.error(
                request, f'Ошибка при обновлении транзакции: {str(e)}')
            return redirect('telegram_bot:transaction_edit', transaction_id=transaction_id)


class TransactionDeleteView(TelegramWebAppAuthenticatedView):
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


class WalletListView(TelegramWebAppAuthenticatedView):
    """Список кошельков"""

    def get(self, request):
        wallets = Wallet.objects.filter(user=request.user).order_by('title')

        context = self.get_context_data(
            wallets=wallets
        )

        return render(request, 'telegram_bot/wallets/list.html', context)


class WalletCreateView(TelegramWebAppAuthenticatedView):
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
                return redirect('telegram_bot:wallet_create')

            wallet = Wallet.objects.create(
                user=request.user,
                title=request.POST.get('title'),
                currency=currency,
                balance=balance,
                is_family_access=request.POST.get('is_family_access') == 'on',
                description=request.POST.get('description', '')
            )

            messages.success(request, 'Кошелек успешно создан!')
            return redirect('telegram_bot:wallets')

        except Exception as e:
            logger.error(f"Error creating wallet: {e}")
            messages.error(request, f'Ошибка при создании кошелька: {str(e)}')
            return redirect('telegram_bot:wallet_create')


class WalletEditView(TelegramWebAppAuthenticatedView):
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
                return redirect('telegram_bot:wallet_edit', wallet_id=wallet_id)
            wallet.balance = balance

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


class WalletDeleteView(TelegramWebAppAuthenticatedView):
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


class CategoryListView(TelegramWebAppAuthenticatedView):
    """Список категорий"""

    def get(self, request):
        categories = TransactionCategoryTree.objects.filter(
            user=request.user).order_by('title')

        context = self.get_context_data(
            categories=categories
        )

        return render(request, 'telegram_bot/categories/list.html', context)


class CategoryCreateView(TelegramWebAppAuthenticatedView):
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


class CategoryEditView(TelegramWebAppAuthenticatedView):
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


class CategoryDeleteView(TelegramWebAppAuthenticatedView):
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
