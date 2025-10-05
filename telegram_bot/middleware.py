import asyncio
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()


class DatabaseMiddleware(BaseMiddleware):
    """Middleware для работы с Django ORM в async контексте"""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Убеждаемся, что соединение с БД активно
        if connection.connection is None:
            connection.connect()

        try:
            return await handler(event, data)
        finally:
            # Закрываем соединение после обработки
            if connection.connection is not None:
                connection.close()


class AuthMiddleware(BaseMiddleware):
    """Middleware для аутентификации пользователей Telegram"""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем пользователя из события
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user

        if user:
            # Создаем или получаем пользователя Django
            django_user, created = await self.get_or_create_user(user)
            data['django_user'] = django_user
            data['is_new_user'] = created

        return await handler(event, data)

    async def get_or_create_user(self, telegram_user):
        """Получение или создание пользователя Django"""
        try:
            # Пытаемся найти пользователя по telegram_id
            django_user = await asyncio.to_thread(
                User.objects.get,
                username=f"tg_{telegram_user.id}"
            )
            return django_user, False
        except User.DoesNotExist:
            # Создаем нового пользователя
            django_user = await asyncio.to_thread(
                User.objects.create_user,
                username=f"tg_{telegram_user.id}",
                first_name=telegram_user.first_name or "",
                last_name=telegram_user.last_name or "",
                email=f"{telegram_user.id}@telegram.local"
            )
            return django_user, True
