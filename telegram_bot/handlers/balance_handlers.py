"""
Обработчики баланса и статистики.
"""

import asyncio

from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message

from telegram_bot.utils import format_balance

from .base import BaseHandler


class BalanceHandler(BaseHandler):
    """Обработчик баланса."""

    def _register_handlers(self):
        """Регистрация обработчиков баланса."""
        # Команды
        self.router.message.register(self.cmd_balance, Command("balance"))

        # Кнопки главного меню
        self.router.message.register(self.btn_balance, F.text == "💰 Баланс")

    async def cmd_balance(self, message: Message, django_user):
        """Показать баланс кошельков."""
        from accounting.models.wallet import Wallet
        from telegram_bot.utils import get_currency_emoji

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

        # Группируем кошельки по валютам
        wallets_by_currency = {}
        for wallet in wallets:
            currency_code = wallet.currency.char_code
            if currency_code not in wallets_by_currency:
                wallets_by_currency[currency_code] = {
                    'currency': wallet.currency,
                    'wallets': [],
                    'total_balance': 0
                }
            wallets_by_currency[currency_code]['wallets'].append(wallet)
            wallets_by_currency[currency_code]['total_balance'] += wallet.balance

        text = f"💰 <b>Ваши кошельки:</b>\n\n"

        # Выводим кошельки по валютам
        for currency_code, currency_data in wallets_by_currency.items():
            currency_emoji = get_currency_emoji(currency_code)
            text += f"{currency_emoji} <b>{currency_data['currency'].name} ({currency_code})</b>\n"

            for wallet in currency_data['wallets']:
                text += f"  💳 {wallet.title}\n"
                text += f"     Баланс: {format_balance(wallet.balance)} {currency_code}\n"
                if wallet.description:
                    text += f"     Описание: {wallet.description}\n"
                text += "\n"

            text += f"  📊 <b>Итого: {format_balance(currency_data['total_balance'])} {currency_code}</b>\n\n"

        await message.answer(text)

    async def btn_balance(self, message: Message, django_user):
        """Обработчик кнопки баланс."""
        await self.cmd_balance(message, django_user)
