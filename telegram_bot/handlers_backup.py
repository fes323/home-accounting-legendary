import asyncio
import logging
from decimal import Decimal

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message

from telegram_bot.keyboards import (categories_keyboard,
                                    category_parent_selection_keyboard,
                                    category_selection_keyboard,
                                    confirmation_keyboard,
                                    currency_selection_keyboard,
                                    main_menu_keyboard, skip_keyboard,
                                    transaction_type_keyboard,
                                    wallet_selection_keyboard,
                                    wallets_keyboard)
from telegram_bot.utils import (format_balance, format_transaction,
                                validate_amount)

# Создание роутера
router = Router()


async def cleanup_previous_inline_keyboards(message: Message, state: FSMContext):
    """Удаление inline кнопок из предыдущих сообщений"""
    data = await state.get_data()
    messages_with_keyboards = data.get('messages_with_keyboards', [])

    for msg_id in messages_with_keyboards:
        try:
            await message.bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=msg_id,
                reply_markup=None
            )
        except Exception as e:
            logging.warning(
                f"Не удалось удалить кнопки из сообщения {msg_id}: {e}")

    # Очищаем список сообщений с кнопками
    await state.update_data(messages_with_keyboards=[])


async def save_message_with_keyboard(message: Message, state: FSMContext):
    """Сохранение ID сообщения с inline кнопками для последующего удаления кнопок"""
    data = await state.get_data()
    messages_with_keyboards = data.get('messages_with_keyboards', [])
    messages_with_keyboards.append(message.message_id)
    await state.update_data(messages_with_keyboards=messages_with_keyboards)

# Состояния для FSM


class TransactionStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_description = State()
    waiting_for_category = State()
    waiting_for_wallet = State()


class WalletStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_currency = State()


class CategoryStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_parent = State()


@router.message(CommandStart())
async def cmd_start(message: Message, django_user, is_new_user: bool):
    """Обработчик команды /start"""
    if is_new_user:
        text = f"👋 Добро пожаловать в ваш личный помощник по учету финансов!\n\n"
        text += f"Я помогу вам:\n"
        text += f"• 📊 Отслеживать доходы и расходы\n"
        text += f"• 💰 Управлять кошельками\n"
        text += f"• 📈 Анализировать траты по категориям\n"
        text += f"• 👨‍👩‍👧‍👦 Вести семейный бюджет\n\n"
        text += f"Для начала создайте кошелек командой /wallets"
    else:
        text = f"👋 С возвращением, {django_user.first_name}!\n\n"
        text += f"Ваш общий баланс: {format_balance(django_user.total_balance)}"

    await message.answer(
        text,
        reply_markup=main_menu_keyboard()
    )


@router.message(Command("balance"))
async def cmd_balance(message: Message, django_user):
    """Показать баланс кошельков"""
    from accounting.models.wallet import Wallet

    wallets = await asyncio.to_thread(
        lambda: list(Wallet.objects.filter(
            user=django_user).select_related('currency'))
    )

    if not wallets:
        await message.answer(
            "💳 У вас пока нет кошельков.\n"
            "Создайте первый кошелек командой /wallets"
        )
        return

    text = f"💰 <b>Ваши кошельки:</b>\n\n"
    total_balance = 0

    for wallet in wallets:
        text += f"💳 {wallet.title}\n"
        text += f"   Баланс: {format_balance(wallet.balance)} {wallet.currency.char_code}\n"
        if wallet.description:
            text += f"   Описание: {wallet.description}\n"
        text += "\n"
        total_balance += wallet.balance

    text += f"📊 <b>Общий баланс: {format_balance(total_balance)}</b>"

    await message.answer(text)


@router.message(Command("income"))
async def cmd_income(message: Message, state: FSMContext):
    """Добавить доход"""
    await state.set_state(TransactionStates.waiting_for_amount)
    await state.update_data(transaction_type="IN")

    sent_message = await message.answer(
        "💰 <b>Добавление дохода</b>\n\n"
        "Введите сумму дохода:",
        reply_markup=transaction_type_keyboard()
    )
    await save_message_with_keyboard(sent_message, state)


@router.message(Command("expense"))
async def cmd_expense(message: Message, state: FSMContext):
    """Добавить расход"""
    await state.set_state(TransactionStates.waiting_for_amount)
    await state.update_data(transaction_type="EX")

    sent_message = await message.answer(
        "💸 <b>Добавление расхода</b>\n\n"
        "Введите сумму расхода:",
        reply_markup=transaction_type_keyboard()
    )
    await save_message_with_keyboard(sent_message, state)


@router.message(Command("wallets"))
async def cmd_wallets(message: Message, django_user, state: FSMContext):
    """Управление кошельками"""
    from accounting.models.wallet import Wallet

    wallets = await asyncio.to_thread(
        lambda: list(Wallet.objects.filter(
            user=django_user).select_related('currency'))
    )

    text = "💳 <b>Управление кошельками</b>\n\n"

    if wallets:
        text += "Ваши кошельки:\n"
        for wallet in wallets:
            text += f"• {wallet.title} - {format_balance(wallet.balance)} {wallet.currency.char_code}\n"
    else:
        text += "У вас пока нет кошельков."

    sent_message = await message.answer(
        text,
        reply_markup=wallets_keyboard()
    )
    await save_message_with_keyboard(sent_message, state)


@router.message(Command("categories"))
async def cmd_categories(message: Message, django_user, state: FSMContext):
    """Управление категориями"""
    from accounting.models.transactionCategory import TransactionCategoryTree

    categories = await asyncio.to_thread(
        lambda: list(TransactionCategoryTree.objects.filter(user=django_user))
    )

    text = "📂 <b>Управление категориями</b>\n\n"

    if categories:
        text += "Ваши категории:\n"
        for category in categories:
            indent = "  " * category.level
            text += f"{indent}• {category.title}\n"
    else:
        text += "У вас пока нет категорий."

    sent_message = await message.answer(
        text,
        reply_markup=categories_keyboard()
    )
    await save_message_with_keyboard(sent_message, state)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Помощь по командам"""
    text = "🤖 <b>Доступные команды:</b>\n\n"
    text += "/start - Начать работу с ботом\n"
    text += "/balance - Показать баланс кошельков\n"
    text += "/income - Добавить доход\n"
    text += "/expense - Добавить расход\n"
    text += "/wallets - Управление кошельками\n"
    text += "/categories - Управление категориями\n"
    text += "/help - Показать эту справку\n\n"
    text += "💡 <i>Используйте кнопки меню для быстрого доступа к функциям</i>"

    await message.answer(text)


# Обработчик состояний FSM
@router.message(TransactionStates.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext, django_user):
    """Обработка введенной суммы"""
    amount = validate_amount(message.text)

    if amount is None:
        await message.answer("❌ Неверный формат суммы! Введите положительное число.")
        return

    await state.update_data(amount=amount)
    await state.set_state(TransactionStates.waiting_for_description)

    sent_message = await message.answer(
        "📝 Введите описание транзакции:",
        reply_markup=transaction_type_keyboard()
    )
    await save_message_with_keyboard(sent_message, state)


@router.message(TransactionStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext, django_user):
    """Обработка описания транзакции"""
    await state.update_data(description=message.text)
    await state.set_state(TransactionStates.waiting_for_wallet)

    from accounting.models.wallet import Wallet

    wallets = await asyncio.to_thread(
        lambda: list(Wallet.objects.filter(
            user=django_user).select_related('currency'))
    )

    if not wallets:
        await message.answer(
            "❌ У вас нет кошельков! Сначала создайте кошелек командой /wallets"
        )
        await state.clear()
        return

    text = "💳 Выберите кошелек для транзакции:"
    sent_message = await message.answer(text, reply_markup=wallet_selection_keyboard(wallets))
    await save_message_with_keyboard(sent_message, state)


# Обработчики кнопок главного меню
@router.message(F.text == "💰 Баланс")
async def btn_balance(message: Message, django_user):
    """Обработчик кнопки баланс"""
    await cmd_balance(message, django_user)


@router.message(F.text == "➕ Доход")
async def btn_income(message: Message, state: FSMContext):
    """Обработчик кнопки доход"""
    await cmd_income(message, state)


@router.message(F.text == "➖ Расход")
async def btn_expense(message: Message, state: FSMContext):
    """Обработчик кнопки расход"""
    await cmd_expense(message, state)


@router.message(F.text == "💳 Кошельки")
async def btn_wallets(message: Message, django_user, state: FSMContext):
    """Обработчик кнопки кошельки"""
    await cmd_wallets(message, django_user, state)


@router.message(F.text == "📂 Категории")
async def btn_categories(message: Message, django_user, state: FSMContext):
    """Обработчик кнопки категории"""
    await cmd_categories(message, django_user, state)


@router.message(F.text == "❓ Помощь")
async def btn_help(message: Message):
    """Обработчик кнопки помощь"""
    await cmd_help(message)

# Обработчики callback-запросов для кошельков


@router.callback_query(F.data == "create_wallet")
async def callback_create_wallet(callback: CallbackQuery, state: FSMContext):
    """Создание нового кошелька"""
    await cleanup_previous_inline_keyboards(callback.message, state)
    await state.set_state(WalletStates.waiting_for_title)
    await callback.message.edit_text(
        "💳 <b>Создание кошелька</b>\n\n"
        "Введите название кошелька:",
        reply_markup=None
    )
    await callback.answer()


@router.message(WalletStates.waiting_for_title)
async def process_wallet_title(message: Message, state: FSMContext):
    """Обработка названия кошелька"""
    await state.update_data(title=message.text)
    await state.set_state(WalletStates.waiting_for_description)

    sent_message = await message.answer(
        "📝 Введите описание кошелька:",
        reply_markup=skip_keyboard()
    )
    await save_message_with_keyboard(sent_message, state)


@router.message(WalletStates.waiting_for_description)
async def process_wallet_description(message: Message, state: FSMContext, django_user):
    """Обработка описания кошелька"""
    description = message.text if message.text != "-" else ""
    await state.update_data(description=description)
    await state.set_state(WalletStates.waiting_for_currency)

    sent_message = await message.answer(
        "💱 Выберите валюту кошелька:",
        reply_markup=currency_selection_keyboard()
    )
    await save_message_with_keyboard(sent_message, state)


@router.callback_query(F.data == "skip_field")
async def callback_skip_field(callback: CallbackQuery, state: FSMContext):
    """Обработка кнопки пропустить"""
    current_state = await state.get_state()

    if current_state == WalletStates.waiting_for_description:
        await state.update_data(description="")
        await state.set_state(WalletStates.waiting_for_currency)
        await cleanup_previous_inline_keyboards(callback.message, state)
        await callback.message.edit_text(
            "💱 Выберите валюту кошелька:",
            reply_markup=currency_selection_keyboard()
        )
    elif current_state == CategoryStates.waiting_for_description:
        await state.update_data(description="")
        # Переходим к выбору родительской категории
        from accounting.models.transactionCategory import \
            TransactionCategoryTree
        from users.models.user import User

        # Получаем пользователя Django
        django_user = await asyncio.to_thread(
            User.objects.get, telegram_id=callback.from_user.id
        )

        categories = await asyncio.to_thread(
            lambda: list(
                TransactionCategoryTree.objects.filter(user=django_user))
        )

        if categories:
            await state.set_state(CategoryStates.waiting_for_parent)
            await cleanup_previous_inline_keyboards(callback.message, state)
            await callback.message.edit_text(
                "📂 Выберите родительскую категорию:",
                reply_markup=category_parent_selection_keyboard(categories)
            )
        else:
            # Создаем корневую категорию
            try:
                await create_category(state, django_user, None)
                await cleanup_previous_inline_keyboards(callback.message, state)
                await callback.message.edit_text("✅ Категория создана!", reply_markup=None)
                await state.clear()
            except Exception as e:
                logging.error(
                    f"Error creating root category in skip_field: {str(e)}")
                await cleanup_previous_inline_keyboards(callback.message, state)

                if "already exists" in str(e) or "unique constraint" in str(e).lower():
                    error_msg = "❌ Категория с таким названием уже существует"
                else:
                    error_msg = f"❌ Ошибка при создании категории: {str(e)}"

                await callback.message.edit_text(error_msg, reply_markup=None)

    await callback.answer()


@router.callback_query(F.data.startswith("select_currency_"))
async def callback_select_currency(callback: CallbackQuery, state: FSMContext, django_user):
    """Выбор валюты для кошелька"""
    currency_code = callback.data.split("_")[-1]

    from accounting.models.currencyCBR import CurrencyCBR
    from accounting.models.wallet import Wallet

    try:
        currency = await asyncio.to_thread(
            CurrencyCBR.objects.get, char_code=currency_code
        )

        data = await state.get_data()

        # Создаем кошелек
        wallet = await asyncio.to_thread(
            lambda: Wallet.objects.create(
                user=django_user,
                title=data['title'],
                description=data['description'],
                currency=currency
            )
        )

        # Получаем кошелек с загруженной валютой для отображения
        wallet = await asyncio.to_thread(
            Wallet.objects.select_related('currency').get, uuid=wallet.uuid
        )

        await cleanup_previous_inline_keyboards(callback.message, state)
        await callback.message.edit_text(
            f"✅ <b>Кошелек создан!</b>\n\n"
            f"💳 {wallet.title}\n"
            f"💰 Баланс: {format_balance(wallet.balance)} {wallet.currency.char_code}\n"
            f"📝 Описание: {wallet.description or 'Нет описания'}",
            reply_markup=None
        )

        await state.clear()
        await callback.answer("Кошелек успешно создан!")

    except Exception as e:
        await cleanup_previous_inline_keyboards(callback.message, state)
        await callback.message.edit_text(
            f"❌ Ошибка при создании кошелька: {str(e)}",
            reply_markup=None
        )
        await callback.answer("Произошла ошибка")

# Обработчики callback-запросов для транзакций


@router.callback_query(F.data.startswith("select_wallet_"))
async def callback_select_wallet(callback: CallbackQuery, state: FSMContext, django_user):
    """Выбор кошелька для транзакции"""
    wallet_uuid = callback.data.split("_")[-1]

    from accounting.models.wallet import Wallet

    try:
        wallet = await asyncio.to_thread(
            Wallet.objects.select_related(
                'currency').get, uuid=wallet_uuid, user=django_user
        )

        data = await state.get_data()
        data['wallet_uuid'] = wallet_uuid
        await state.update_data(wallet_uuid=wallet_uuid)

        # Получаем категории пользователя
        from accounting.models.transactionCategory import \
            TransactionCategoryTree
        categories = await asyncio.to_thread(
            lambda: list(
                TransactionCategoryTree.objects.filter(user=django_user))
        )

        if categories:
            await cleanup_previous_inline_keyboards(callback.message, state)
            await state.set_state(TransactionStates.waiting_for_category)
            await callback.message.edit_text(
                f"📂 Выберите категорию для транзакции:",
                reply_markup=category_selection_keyboard(categories)
            )
        else:
            # Создаем транзакцию без категории
            transaction, updated_wallet = await create_transaction(state, django_user, wallet, None)

            # Получаем обновленные данные состояния
            updated_data = await state.get_data()
            await cleanup_previous_inline_keyboards(callback.message, state)
            await callback.message.edit_text(
                f"✅ <b>Транзакция добавлена!</b>\n\n"
                f"💰 Сумма: {format_balance(updated_data['amount'])} {updated_wallet.currency.char_code}\n"
                f"📝 Описание: {updated_data['description']}\n"
                f"💳 Кошелек: {updated_wallet.title}",
                reply_markup=None
            )
            await state.clear()

        await callback.answer()

    except Exception as e:
        await cleanup_previous_inline_keyboards(callback.message, state)
        await callback.message.edit_text(
            f"❌ Ошибка при выборе кошелька: {str(e)}",
            reply_markup=None
        )
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data.startswith("select_category_"))
async def callback_select_category(callback: CallbackQuery, state: FSMContext, django_user):
    """Выбор категории для транзакции"""
    category_uuid = callback.data.split("_")[-1]

    from accounting.models.transactionCategory import TransactionCategoryTree
    from accounting.models.wallet import Wallet

    try:
        category = await asyncio.to_thread(
            TransactionCategoryTree.objects.get, uuid=category_uuid, user=django_user
        )

        data = await state.get_data()

        if 'wallet_uuid' not in data:
            await callback.message.edit_text(
                "❌ Ошибка: информация о кошельке потеряна. Начните транзакцию заново.",
                reply_markup=None
            )
            await state.clear()
            await callback.answer("Произошла ошибка")
            return

        wallet = await asyncio.to_thread(
            Wallet.objects.select_related(
                'currency').get, uuid=data['wallet_uuid'], user=django_user
        )

        transaction, updated_wallet = await create_transaction(state, django_user, wallet, category)

        await cleanup_previous_inline_keyboards(callback.message, state)
        await callback.message.edit_text(
            f"✅ <b>Транзакция добавлена!</b>\n\n"
            f"💰 Сумма: {format_balance(data['amount'])} {updated_wallet.currency.char_code}\n"
            f"📝 Описание: {data['description']}\n"
            f"📂 Категория: {category.title}\n"
            f"💳 Кошелек: {updated_wallet.title}",
            reply_markup=None
        )

        await state.clear()
        await callback.answer("Транзакция успешно добавлена!")

    except Exception as e:
        await cleanup_previous_inline_keyboards(callback.message, state)
        await callback.message.edit_text(
            f"❌ Ошибка при выборе категории: {str(e)}",
            reply_markup=None
        )
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "no_category")
async def callback_no_category(callback: CallbackQuery, state: FSMContext, django_user):
    """Создание транзакции без категории"""
    from accounting.models.wallet import Wallet

    try:
        data = await state.get_data()

        if 'wallet_uuid' not in data:
            await callback.message.edit_text(
                "❌ Ошибка: информация о кошельке потеряна. Начните транзакцию заново.",
                reply_markup=None
            )
            await state.clear()
            await callback.answer("Произошла ошибка")
            return

        wallet = await asyncio.to_thread(
            Wallet.objects.select_related(
                'currency').get, uuid=data['wallet_uuid'], user=django_user
        )

        transaction, updated_wallet = await create_transaction(state, django_user, wallet, None)

        await cleanup_previous_inline_keyboards(callback.message, state)
        await callback.message.edit_text(
            f"✅ <b>Транзакция добавлена!</b>\n\n"
            f"💰 Сумма: {format_balance(data['amount'])} {updated_wallet.currency.char_code}\n"
            f"📝 Описание: {data['description']}\n"
            f"💳 Кошелек: {updated_wallet.title}",
            reply_markup=None
        )

        await state.clear()
        await callback.answer("Транзакция успешно добавлена!")

    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка при создании транзакции: {str(e)}",
            reply_markup=None
        )
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "cancel_transaction")
async def callback_cancel_transaction(callback: CallbackQuery, state: FSMContext):
    """Отмена транзакции"""
    await cleanup_previous_inline_keyboards(callback.message, state)
    await state.clear()
    await callback.message.edit_text("❌ Транзакция отменена", reply_markup=None)
    await callback.answer("Транзакция отменена")


@router.callback_query(F.data == "cancel_category")
async def callback_cancel_category(callback: CallbackQuery, state: FSMContext):
    """Отмена создания категории"""
    await cleanup_previous_inline_keyboards(callback.message, state)
    await state.clear()
    await callback.message.edit_text("❌ Создание категории отменено", reply_markup=None)
    await callback.answer("Создание категории отменено")

# Обработчики callback-запросов для категорий


@router.callback_query(F.data == "create_category")
async def callback_create_category(callback: CallbackQuery, state: FSMContext):
    """Создание новой категории"""
    logging.info("Starting category creation process")
    await cleanup_previous_inline_keyboards(callback.message, state)
    await state.set_state(CategoryStates.waiting_for_title)
    await callback.message.edit_text(
        "📂 <b>Создание категории</b>\n\n"
        "Введите название категории:",
        reply_markup=None
    )
    await callback.answer()


@router.message(CategoryStates.waiting_for_title)
async def process_category_title(message: Message, state: FSMContext):
    """Обработка названия категории"""
    logging.info(f"Processing category title: {message.text}")
    await state.update_data(title=message.text)
    await state.set_state(CategoryStates.waiting_for_description)

    sent_message = await message.answer(
        "📝 Введите описание категории:",
        reply_markup=skip_keyboard()
    )
    await save_message_with_keyboard(sent_message, state)


@router.message(CategoryStates.waiting_for_description)
async def process_category_description(message: Message, state: FSMContext, django_user):
    """Обработка описания категории"""
    description = message.text if message.text != "-" else ""
    logging.info(f"Processing category description: {description}")
    await state.update_data(description=description)

    # Получаем существующие категории для выбора родительской
    from accounting.models.transactionCategory import TransactionCategoryTree
    categories = await asyncio.to_thread(
        lambda: list(TransactionCategoryTree.objects.filter(user=django_user))
    )

    logging.info(
        f"Found {len(categories)} existing categories for user {django_user}")

    if categories:
        await state.set_state(CategoryStates.waiting_for_parent)
        sent_message = await message.answer(
            "📂 Выберите родительскую категорию:",
            reply_markup=category_parent_selection_keyboard(categories)
        )
        await save_message_with_keyboard(sent_message, state)
    else:
        # Создаем корневую категорию
        logging.info("No existing categories, creating root category")
        await create_category(state, django_user, None)
        await message.answer("✅ Категория создана!")
        await state.clear()


@router.callback_query(F.data == "create_root_category")
async def callback_create_root_category(callback: CallbackQuery, state: FSMContext, django_user):
    """Создание корневой категории"""
    try:
        await create_category(state, django_user, None)
        await cleanup_previous_inline_keyboards(callback.message, state)
        await callback.message.edit_text("✅ Категория создана!", reply_markup=None)
        await state.clear()
        await callback.answer("Категория успешно создана!")
    except Exception as e:
        logging.error(f"Error in callback_create_root_category: {str(e)}")
        await cleanup_previous_inline_keyboards(callback.message, state)

        # Более информативное сообщение об ошибке
        if "already exists" in str(e) or "unique constraint" in str(e).lower():
            error_msg = "❌ Категория с таким названием уже существует"
        else:
            error_msg = f"❌ Ошибка при создании категории: {str(e)}"

        await callback.message.edit_text(error_msg, reply_markup=None)
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data.startswith("select_category_parent_"))
async def callback_select_parent_category(callback: CallbackQuery, state: FSMContext, django_user):
    """Выбор родительской категории"""
    category_uuid = callback.data.split("_")[-1]

    logging.info(f"Selecting parent category with UUID: {category_uuid}")

    from accounting.models.transactionCategory import TransactionCategoryTree

    try:
        parent_category = await asyncio.to_thread(
            TransactionCategoryTree.objects.get, uuid=category_uuid, user=django_user
        )

        logging.info(f"Found parent category: {parent_category}")

        await create_category(state, django_user, parent_category)

        await cleanup_previous_inline_keyboards(callback.message, state)
        await callback.message.edit_text("✅ Категория создана!", reply_markup=None)
        await state.clear()
        await callback.answer("Категория успешно создана!")

    except Exception as e:
        logging.error(f"Error in callback_select_parent_category: {str(e)}")
        await cleanup_previous_inline_keyboards(callback.message, state)

        # Более информативное сообщение об ошибке
        if "already exists" in str(e) or "unique constraint" in str(e).lower():
            error_msg = "❌ Категория с таким названием уже существует в данной родительской категории"
        elif "not found" in str(e).lower():
            error_msg = "❌ Родительская категория не найдена"
        else:
            error_msg = f"❌ Ошибка при создании категории: {str(e)}"

        await callback.message.edit_text(error_msg, reply_markup=None)
        await callback.answer("Произошла ошибка")

# Вспомогательные функции


async def create_transaction(state: FSMContext, django_user, wallet, category):
    """Создание транзакции"""
    import logging

    from accounting.models.transaction import Transaction
    from accounting.models.wallet import Wallet

    data = await state.get_data()

    # Логируем данные для отладки
    logging.info(f"Creating transaction: user={django_user.username}, wallet={wallet.title}, "
                 f"type={data['transaction_type']}, amount={data['amount']}, "
                 f"description={data['description']}")

    transaction = await asyncio.to_thread(
        lambda: Transaction.objects.create(
            user=django_user,
            wallet=wallet,
            category=category,
            t_type=data['transaction_type'],
            amount=Decimal(str(data['amount'])),
            description=data['description']
        )
    )

    # Принудительно обновляем баланс кошелька
    await asyncio.to_thread(
        lambda: wallet.refresh_from_db()
    )

    # Пересчитываем баланс на основе всех транзакций
    from django.db.models import Sum
    total_income = await asyncio.to_thread(
        lambda: Transaction.objects.filter(wallet=wallet, t_type='IN').aggregate(
            total=Sum('amount'))['total'] or Decimal('0')
    )
    total_expense = await asyncio.to_thread(
        lambda: Transaction.objects.filter(wallet=wallet, t_type='EX').aggregate(
            total=Sum('amount'))['total'] or Decimal('0')
    )

    new_balance = total_income - total_expense
    await asyncio.to_thread(
        lambda: Wallet.objects.filter(
            uuid=wallet.uuid).update(balance=new_balance)
    )

    # Обновляем объект кошелька из базы данных
    wallet = await asyncio.to_thread(
        Wallet.objects.select_related('currency').get, uuid=wallet.uuid
    )

    # Логируем результат
    logging.info(
        f"Transaction created: {transaction.uuid}, wallet balance after: {wallet.balance}")

    return transaction, wallet


async def create_category(state: FSMContext, django_user, parent_category):
    """Создание категории"""
    from accounting.models.transactionCategory import TransactionCategoryTree

    data = await state.get_data()

    # Логируем данные для отладки
    logging.info(f"Creating category with data: {data}")
    logging.info(f"Parent category: {parent_category}")
    logging.info(f"Django user: {django_user}")

    try:
        # Проверяем уникальность названия категории для пользователя
        existing_category = await asyncio.to_thread(
            lambda: TransactionCategoryTree.objects.filter(
                user=django_user,
                title=data['title'],
                parent=parent_category
            ).first()
        )

        if existing_category:
            logging.warning(
                f"Category with title '{data['title']}' already exists for user {django_user}")
            raise ValueError(
                f"Категория с названием '{data['title']}' уже существует")

        category = await asyncio.to_thread(
            lambda: TransactionCategoryTree.objects.create(
                user=django_user,
                parent=parent_category,
                title=data['title'],
                description=data['description']
            )
        )
        logging.info(f"Category created successfully: {category}")
        return category
    except Exception as e:
        logging.error(f"Error creating category: {str(e)}")
        raise


def register_handlers(dp):
    """Регистрация всех обработчиков"""
    dp.include_router(router)
