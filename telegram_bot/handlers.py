import asyncio

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message

from telegram_bot.keyboards import (categories_keyboard, main_menu_keyboard,
                                    transaction_type_keyboard,
                                    wallets_keyboard)
from telegram_bot.utils import format_balance, format_transaction

# Создание роутера
router = Router()

# Состояния для FSM


class TransactionStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_description = State()
    waiting_for_category = State()
    waiting_for_wallet = State()


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
        lambda: list(Wallet.objects.filter(user=django_user))
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

    await message.answer(
        "💰 <b>Добавление дохода</b>\n\n"
        "Введите сумму дохода:",
        reply_markup=transaction_type_keyboard()
    )


@router.message(Command("expense"))
async def cmd_expense(message: Message, state: FSMContext):
    """Добавить расход"""
    await state.set_state(TransactionStates.waiting_for_amount)
    await state.update_data(transaction_type="EX")

    await message.answer(
        "💸 <b>Добавление расхода</b>\n\n"
        "Введите сумму расхода:",
        reply_markup=transaction_type_keyboard()
    )


@router.message(Command("wallets"))
async def cmd_wallets(message: Message, django_user):
    """Управление кошельками"""
    from accounting.models.wallet import Wallet

    wallets = await asyncio.to_thread(
        lambda: list(Wallet.objects.filter(user=django_user))
    )

    text = "💳 <b>Управление кошельками</b>\n\n"

    if wallets:
        text += "Ваши кошельки:\n"
        for wallet in wallets:
            text += f"• {wallet.title} - {format_balance(wallet.balance)} {wallet.currency.char_code}\n"
    else:
        text += "У вас пока нет кошельков."

    await message.answer(
        text,
        reply_markup=wallets_keyboard()
    )


@router.message(Command("categories"))
async def cmd_categories(message: Message, django_user):
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

    await message.answer(
        text,
        reply_markup=categories_keyboard()
    )


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
    try:
        amount = float(message.text.replace(',', '.'))
        if amount <= 0:
            await message.answer("❌ Сумма должна быть положительной!")
            return

        await state.update_data(amount=amount)
        await state.set_state(TransactionStates.waiting_for_description)

        await message.answer(
            "📝 Введите описание транзакции:",
            reply_markup=transaction_type_keyboard()
        )

    except ValueError:
        await message.answer("❌ Неверный формат суммы! Введите число.")


@router.message(TransactionStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext, django_user):
    """Обработка описания транзакции"""
    await state.update_data(description=message.text)
    await state.set_state(TransactionStates.waiting_for_wallet)

    from accounting.models.wallet import Wallet

    wallets = await asyncio.to_thread(
        lambda: list(Wallet.objects.filter(user=django_user))
    )

    if not wallets:
        await message.answer(
            "❌ У вас нет кошельков! Сначала создайте кошелек командой /wallets"
        )
        await state.clear()
        return

    text = "💳 Выберите кошелек для транзакции:"
    await message.answer(text, reply_markup=wallets_keyboard())


def register_handlers(dp):
    """Регистрация всех обработчиков"""
    dp.include_router(router)
