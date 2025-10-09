"""
Обработчики настроек и помощи.
"""

from aiogram import F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from telegram_bot.keyboards import main_menu_keyboard
from telegram_bot.utils import format_balance

from .base import BaseHandler


class SettingsHandler(BaseHandler):
    """Обработчик настроек и помощи."""

    def _register_handlers(self):
        """Регистрация обработчиков настроек."""
        # Команды
        self.router.message.register(self.cmd_start, CommandStart())
        self.router.message.register(self.cmd_help, Command("help"))

        # Кнопки главного меню
        self.router.message.register(self.btn_help, F.text == "❓ Помощь")

    async def cmd_start(self, message: Message, django_user, is_new_user: bool):
        """Обработчик команды /start."""
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

    async def cmd_help(self, message: Message):
        """Помощь по командам."""
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

    async def btn_help(self, message: Message):
        """Обработчик кнопки помощь."""
        await self.cmd_help(message)
