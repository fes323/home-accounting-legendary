"""
Обработчики кошельков.
"""

import asyncio
import logging

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.keyboards import (currency_selection_keyboard, skip_keyboard,
                                    wallets_keyboard)
from telegram_bot.utils import format_balance

from .base import BaseHandler, ErrorHandler, ResponseFormatter, StateManager
from .states import WalletStates


class WalletHandler(BaseHandler):
    """Обработчик кошельков."""

    def _register_handlers(self):
        """Регистрация обработчиков кошельков."""
        # Команды
        self.router.message.register(self.cmd_wallets, Command("wallets"))

        # Кнопки главного меню
        self.router.message.register(self.btn_wallets, F.text == "💳 Кошельки")

        # FSM состояния
        self.router.message.register(
            self.process_wallet_title, WalletStates.waiting_for_title)
        self.router.message.register(
            self.process_wallet_description, WalletStates.waiting_for_description)

        # Callback обработчики
        self.router.callback_query.register(
            self.callback_create_wallet, F.data == "create_wallet")
        self.router.callback_query.register(
            self.callback_select_currency, F.data.startswith("select_currency_"))
        self.router.callback_query.register(
            self.callback_skip_field, F.data == "skip_field")

    async def cmd_wallets(self, message: Message, django_user, state: FSMContext):
        """Управление кошельками."""
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
        await StateManager.save_message_with_keyboard(sent_message, state)

    async def btn_wallets(self, message: Message, django_user, state: FSMContext):
        """Обработчик кнопки кошельки."""
        await self.cmd_wallets(message, django_user, state)

    async def callback_create_wallet(self, callback: CallbackQuery, state: FSMContext):
        """Создание нового кошелька."""
        await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
        await state.set_state(WalletStates.waiting_for_title)
        await callback.message.edit_text(
            "💳 <b>Создание кошелька</b>\n\n"
            "Введите название кошелька:",
            reply_markup=None
        )
        await callback.answer()

    async def process_wallet_title(self, message: Message, state: FSMContext):
        """Обработка названия кошелька."""
        await state.update_data(title=message.text)
        await state.set_state(WalletStates.waiting_for_description)

        sent_message = await message.answer(
            "📝 Введите описание кошелька:",
            reply_markup=skip_keyboard()
        )
        await StateManager.save_message_with_keyboard(sent_message, state)

    async def process_wallet_description(self, message: Message, state: FSMContext, django_user):
        """Обработка описания кошелька."""
        description = message.text if message.text != "-" else ""
        await state.update_data(description=description)
        await state.set_state(WalletStates.waiting_for_currency)

        sent_message = await message.answer(
            "💱 Выберите валюту кошелька:",
            reply_markup=currency_selection_keyboard()
        )
        await StateManager.save_message_with_keyboard(sent_message, state)

    async def callback_select_currency(self, callback: CallbackQuery, state: FSMContext, django_user):
        """Выбор валюты для кошелька."""
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

            await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
            await callback.message.edit_text(
                ResponseFormatter.format_success_message(
                    "Кошелек создан!",
                    [
                        f"💳 {wallet.title}",
                        f"💰 Баланс: {format_balance(wallet.balance)} {wallet.currency.char_code}",
                        f"📝 Описание: {wallet.description or 'Нет описания'}"
                    ]
                ),
                reply_markup=None
            )

            await state.clear()
            await callback.answer("Кошелек успешно создан!")

        except Exception as e:
            await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
            await callback.message.edit_text(
                ErrorHandler.handle_database_error(e, "создание кошелька"),
                reply_markup=None
            )
            await callback.answer("Произошла ошибка")

    async def callback_skip_field(self, callback: CallbackQuery, state: FSMContext):
        """Обработка кнопки пропустить."""
        current_state = await state.get_state()

        if current_state == WalletStates.waiting_for_description:
            await state.update_data(description="")
            await state.set_state(WalletStates.waiting_for_currency)
            await StateManager.cleanup_previous_inline_keyboards(callback.message, state)
            await callback.message.edit_text(
                "💱 Выберите валюту кошелька:",
                reply_markup=currency_selection_keyboard()
            )

        await callback.answer()
