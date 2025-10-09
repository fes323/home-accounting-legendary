from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup, WebAppInfo)
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
    builder.add(KeyboardButton(text="📱 Веб-приложение"))
    builder.add(KeyboardButton(text="⚙️ Настройки"))
    builder.add(KeyboardButton(text="❓ Помощь"))

    builder.adjust(1, 2, 2, 2, 1, 1)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие..."
    )


def web_app_keyboard(web_app_url):
    """Клавиатура с кнопкой для открытия WebApp"""
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(
        text="📱 Открыть приложение",
        web_app=WebAppInfo(url=web_app_url)
    ))

    return builder.as_markup()


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


def skip_keyboard():
    """Клавиатура с кнопкой пропустить"""
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(
        text="⏭️ Пропустить",
        callback_data="skip_field"
    ))
    builder.add(InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel_transaction"
    ))

    builder.adjust(1)

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


def category_selection_keyboard(categories, for_parent=False):
    """Клавиатура для выбора категории"""
    builder = InlineKeyboardBuilder()

    for category in categories:
        indent = "  " * category.level
        callback_data = f"select_category_parent_{category.uuid}" if for_parent else f"select_category_{category.uuid}"
        builder.add(InlineKeyboardButton(
            text=f"{indent}{category.title}",
            callback_data=callback_data
        ))

    if not for_parent:
        builder.add(InlineKeyboardButton(
            text="➕ Создать новую категорию",
            callback_data="create_new_category"
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


def category_parent_selection_keyboard(categories):
    """Клавиатура для выбора родительской категории"""
    builder = InlineKeyboardBuilder()

    for category in categories:
        indent = "  " * category.level
        builder.add(InlineKeyboardButton(
            text=f"{indent}{category.title}",
            callback_data=f"select_category_parent_{category.uuid}"
        ))

    builder.add(InlineKeyboardButton(
        text="⏭️ Создать корневую категорию",
        callback_data="create_root_category"
    ))
    builder.add(InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel_category"
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


def paginated_categories_keyboard(categories, page=0, items_per_page=10):
    """Клавиатура для категорий с пагинацией"""
    builder = InlineKeyboardBuilder()

    # Вычисляем индексы для текущей страницы
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    page_categories = categories[start_idx:end_idx]

    # Добавляем кнопки категорий
    for category in page_categories:
        indent = "  " * category.level
        builder.add(InlineKeyboardButton(
            text=f"{indent}{category.title}",
            callback_data=f"select_category_parent_{category.uuid}"
        ))

    # Добавляем кнопки навигации если нужно
    total_pages = (len(categories) + items_per_page - 1) // items_per_page
    if total_pages > 1:
        nav_row = []

        # Кнопка "Назад"
        if page > 0:
            nav_row.append(InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"categories_page_{page - 1}"
            ))

        # Кнопка "Далее"
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton(
                text="Далее ➡️",
                callback_data=f"categories_page_{page + 1}"
            ))

        if nav_row:
            builder.row(*nav_row)

    # Добавляем стандартные кнопки
    builder.add(InlineKeyboardButton(
        text="⏭️ Создать корневую категорию",
        callback_data="create_root_category"
    ))
    builder.add(InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel_category"
    ))

    builder.adjust(1)

    return builder.as_markup()


def paginated_category_selection_keyboard(categories, page=0, items_per_page=10, for_parent=False):
    """Клавиатура для выбора категории с пагинацией"""
    builder = InlineKeyboardBuilder()

    # Вычисляем индексы для текущей страницы
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    page_categories = categories[start_idx:end_idx]

    # Добавляем кнопки категорий
    for category in page_categories:
        indent = "  " * category.level
        callback_data = f"select_category_parent_{category.uuid}" if for_parent else f"select_category_{category.uuid}"
        builder.add(InlineKeyboardButton(
            text=f"{indent}{category.title}",
            callback_data=callback_data
        ))

    # Добавляем кнопки навигации если нужно
    total_pages = (len(categories) + items_per_page - 1) // items_per_page
    if total_pages > 1:
        nav_row = []

        # Кнопка "Назад"
        if page > 0:
            nav_row.append(InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"category_select_page_{page - 1}"
            ))

        # Кнопка "Далее"
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton(
                text="Далее ➡️",
                callback_data=f"category_select_page_{page + 1}"
            ))

        if nav_row:
            builder.row(*nav_row)

    # Добавляем дополнительные кнопки
    if not for_parent:
        builder.add(InlineKeyboardButton(
            text="➕ Создать новую категорию",
            callback_data="create_new_category"
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
