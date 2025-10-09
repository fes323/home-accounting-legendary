"""
Обработчики для Telegram WebApp.
"""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from django.conf import settings

from ..keyboards import web_app_keyboard


class WebAppHandler:
    """Обработчик для Telegram WebApp."""

    def __init__(self):
        self.router = Router()
        self._register_handlers()

    def _register_handlers(self):
        """Регистрация обработчиков."""

        @self.router.message(Command("app"))
        async def open_web_app(message: Message):
            """Открытие WebApp."""
            web_app_url = settings.TELEGRAM_MINIAPP_URL

            await message.answer(
                "📱 <b>Откройте веб-приложение</b>\n\n"
                "Для удобного управления финансами используйте веб-приложение с расширенным функционалом.",
                reply_markup=web_app_keyboard(web_app_url)
            )

        @self.router.message(F.text == "📱 Веб-приложение")
        async def web_app_button(message: Message):
            """Обработка кнопки веб-приложения."""
            web_app_url = settings.TELEGRAM_MINIAPP_URL

            await message.answer(
                "📱 <b>Откройте веб-приложение</b>\n\n"
                "Для удобного управления финансами используйте веб-приложение с расширенным функционалом.",
                reply_markup=web_app_keyboard(web_app_url)
            )

    def get_router(self):
        """Получение роутера."""
        return self.router
