import asyncio
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.db import close_old_connections, connection

User = get_user_model()


class DatabaseMiddleware(BaseMiddleware):
    """Middleware для работы с Django ORM в async контексте"""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Закрываем старые соединения перед обработкой
        await sync_to_async(close_old_connections)()

        try:
            return await handler(event, data)
        finally:
            # Закрываем соединения после обработки
            await sync_to_async(close_old_connections)()


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
                telegram_id=telegram_user.id
            )
            return django_user, False
        except User.DoesNotExist:
            # Создаем нового пользователя
            django_user = await asyncio.to_thread(
                User.objects.create_user,
                telegram_id=telegram_user.id,
                username=telegram_user.username or telegram_user.id,
                first_name=telegram_user.first_name or "",
                last_name=telegram_user.last_name or "",
                email=f"{telegram_user.id}@telegram.local"
            )
            return django_user, True
