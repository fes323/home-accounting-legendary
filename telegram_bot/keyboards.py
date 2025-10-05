from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def main_menu_keyboard():
    """Главное меню бота"""
    builder = ReplyKeyboardBuilder()

    builder.add(KeyboardButton(text="💰 Баланс"))
    builder.add(KeyboardButton(text="➕ Доход"))
    builder.add(KeyboardButton(text="➖ Расход"))
    builder.add(KeyboardButton(text="💳 Кошельки"))
    builder.add(KeyboardButton(text="📂 Категории"))
    builder.add(KeyboardButton(text="📊 Статистика"))
    builder.add(KeyboardButton(text="⚙️ Настройки"))
    builder.add(KeyboardButton(text="❓ Помощь"))

    builder.adjust(2, 2, 2, 2)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие..."
    )


def wallets_keyboard():
    """Клавиатура для управления кошельками"""
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(
        text="➕ Создать кошелек",
        callback_data="create_wallet"
    ))
    builder.add(InlineKeyboardButton(
        text="📝 Редактировать",
        callback_data="edit_wallets"
    ))
    builder.add(InlineKeyboardButton(
        text="🗑️ Удалить",
        callback_data="delete_wallets"
    ))

    builder.adjust(1)

    return builder.as_markup()


def categories_keyboard():
    """Клавиатура для управления категориями"""
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(
        text="➕ Создать категорию",
        callback_data="create_category"
    ))
    builder.add(InlineKeyboardButton(
        text="📝 Редактировать",
        callback_data="edit_categories"
    ))
    builder.add(InlineKeyboardButton(
        text="🗑️ Удалить",
        callback_data="delete_categories"
    ))

    builder.adjust(1)

    return builder.as_markup()


def transaction_type_keyboard():
    """Клавиатура для отмены транзакции"""
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel_transaction"
    ))

    return builder.as_markup()


def wallet_selection_keyboard(wallets):
    """Клавиатура для выбора кошелька"""
    builder = InlineKeyboardBuilder()

    for wallet in wallets:
        builder.add(InlineKeyboardButton(
            text=f"{wallet.title} ({wallet.balance} {wallet.currency.char_code})",
            callback_data=f"select_wallet_{wallet.uuid}"
        ))

    builder.add(InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel_transaction"
    ))

    builder.adjust(1)

    return builder.as_markup()


def category_selection_keyboard(categories):
    """Клавиатура для выбора категории"""
    builder = InlineKeyboardBuilder()

    for category in categories:
        indent = "  " * category.level
        builder.add(InlineKeyboardButton(
            text=f"{indent}{category.title}",
            callback_data=f"select_category_{category.uuid}"
        ))

    builder.add(InlineKeyboardButton(
        text="❌ Без категории",
        callback_data="no_category"
    ))
    builder.add(InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel_transaction"
    ))

    builder.adjust(1)

    return builder.as_markup()


def currency_selection_keyboard():
    """Клавиатура для выбора валюты"""
    builder = InlineKeyboardBuilder()

    # Основные валюты
    currencies = [
        ("RUB", "🇷🇺 Рубль"),
        ("USD", "🇺🇸 Доллар"),
        ("EUR", "🇪🇺 Евро"),
        ("CNY", "🇨🇳 Юань"),
    ]

    for code, name in currencies:
        builder.add(InlineKeyboardButton(
            text=name,
            callback_data=f"select_currency_{code}"
        ))

    builder.add(InlineKeyboardButton(
        text="➕ Другие валюты",
        callback_data="other_currencies"
    ))

    builder.adjust(2)

    return builder.as_markup()


def confirmation_keyboard(action):
    """Клавиатура подтверждения действия"""
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(
        text="✅ Да",
        callback_data=f"confirm_{action}"
    ))
    builder.add(InlineKeyboardButton(
        text="❌ Нет",
        callback_data=f"cancel_{action}"
    ))

    builder.adjust(2)

    return builder.as_markup()


def back_keyboard():
    """Клавиатура с кнопкой назад"""
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="back"
    ))

    return builder.as_markup()
