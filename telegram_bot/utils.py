from decimal import Decimal
from typing import List, Optional

from accounting.models.transaction import Transaction
from accounting.models.transactionCategory import TransactionCategoryTree
from accounting.models.wallet import Wallet


def format_balance(amount: Decimal) -> str:
    """Форматирование суммы для отображения"""
    if amount is None:
        return "0.00"

    # Форматируем с разделителями тысяч
    formatted = f"{amount:,.2f}"
    return formatted.replace(',', ' ').replace('.', ',')


def format_transaction(transaction: Transaction) -> str:
    """Форматирование транзакции для отображения"""
    emoji = "💰" if transaction.t_type == "IN" else "💸"
    type_text = "Доход" if transaction.t_type == "IN" else "Расход"

    text = f"{emoji} <b>{type_text}</b>\n"
    text += f"Сумма: {format_balance(transaction.amount)} {transaction.wallet.currency.char_code}\n"

    if transaction.description:
        text += f"Описание: {transaction.description}\n"

    if transaction.category:
        text += f"Категория: {transaction.category.title}\n"

    if transaction.tax > 0:
        text += f"Налог: {format_balance(transaction.tax)} {transaction.wallet.currency.char_code}\n"

    text += f"Дата: {transaction.date.strftime('%d.%m.%Y')}\n"
    text += f"Кошелек: {transaction.wallet.title}"

    return text


def format_wallet_info(wallet: Wallet) -> str:
    """Форматирование информации о кошельке"""
    text = f"💳 <b>{wallet.title}</b>\n"
    text += f"Баланс: {format_balance(wallet.balance)} {wallet.currency.char_code}\n"

    if wallet.description:
        text += f"Описание: {wallet.description}\n"

    text += f"Семейный доступ: {'Да' if wallet.is_family_access else 'Нет'}\n"
    text += f"Создан: {wallet.created_at.strftime('%d.%m.%Y')}"

    return text


def format_category_tree(categories: List[TransactionCategoryTree]) -> str:
    """Форматирование дерева категорий"""
    if not categories:
        return "📂 Категории не найдены"

    text = "📂 <b>Категории:</b>\n\n"

    for category in categories:
        indent = "  " * category.level
        text += f"{indent}• {category.title}\n"

        if category.description:
            text += f"{indent}  <i>{category.description}</i>\n"

    return text


def format_statistics(user, period_days: int = 30) -> str:
    """Форматирование статистики пользователя"""
    from datetime import timedelta

    from django.db import models
    from django.utils import timezone

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=period_days)

    # Получаем транзакции за период
    transactions = Transaction.objects.filter(
        user=user,
        date__range=[start_date, end_date]
    )

    income = sum(t.amount for t in transactions.filter(t_type="IN"))
    expense = sum(t.amount for t in transactions.filter(t_type="EX"))

    text = f"📊 <b>Статистика за {period_days} дней</b>\n\n"
    text += f"💰 Доходы: {format_balance(income)}\n"
    text += f"💸 Расходы: {format_balance(expense)}\n"
    text += f"📈 Баланс: {format_balance(income - expense)}\n\n"

    # Топ категорий расходов
    expense_categories = transactions.filter(t_type="EX").values('category__title').annotate(
        total=models.Sum('amount')
    ).order_by('-total')[:5]

    if expense_categories:
        text += "🏆 <b>Топ категорий расходов:</b>\n"
        for cat in expense_categories:
            if cat['category__title']:
                text += f"• {cat['category__title']}: {format_balance(cat['total'])}\n"

    return text


def validate_amount(text: str) -> Optional[Decimal]:
    """Валидация введенной суммы"""
    try:
        # Заменяем запятую на точку и убираем пробелы
        cleaned = text.replace(',', '.').replace(' ', '')
        amount = Decimal(cleaned)

        if amount <= 0:
            return None

        return amount
    except (ValueError, TypeError):
        return None


def validate_description(text: str) -> str:
    """Валидация описания"""
    if not text or len(text.strip()) == 0:
        return "Без описания"

    # Ограничиваем длину
    return text.strip()[:255]


def get_currency_emoji(char_code: str) -> str:
    """Получение эмодзи для валюты"""
    currency_emojis = {
        'RUB': '🇷🇺',
        'USD': '🇺🇸',
        'EUR': '🇪🇺',
        'CNY': '🇨🇳',
        'GBP': '🇬🇧',
        'JPY': '🇯🇵',
        'KZT': '🇰🇿',
        'UAH': '🇺🇦',
        'BYN': '🇧🇾',
    }

    return currency_emojis.get(char_code, '💱')
