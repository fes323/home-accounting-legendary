"""
Базовые классы и утилиты для обработчиков.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message


class BaseHandler(ABC):
    """Базовый класс для всех обработчиков."""

    def __init__(self):
        self.router = Router()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._register_handlers()

    @abstractmethod
    def _register_handlers(self):
        """Регистрация обработчиков в роутере."""
        pass

    def get_router(self) -> Router:
        """Получение роутера с зарегистрированными обработчиками."""
        return self.router


class StateManager:
    """Менеджер состояний FSM."""

    @staticmethod
    async def cleanup_previous_inline_keyboards(message: Message, state: FSMContext):
        """Удаление inline кнопок из предыдущих сообщений."""
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

    @staticmethod
    async def save_message_with_keyboard(message: Message, state: FSMContext):
        """Сохранение ID сообщения с inline кнопками для последующего удаления кнопок."""
        data = await state.get_data()
        messages_with_keyboards = data.get('messages_with_keyboards', [])
        messages_with_keyboards.append(message.message_id)
        await state.update_data(messages_with_keyboards=messages_with_keyboards)


class ErrorHandler:
    """Обработчик ошибок."""

    @staticmethod
    def handle_database_error(error: Exception, context: str = "") -> str:
        """Обработка ошибок базы данных."""
        error_msg = str(error).lower()

        if "already exists" in error_msg or "unique constraint" in error_msg:
            return "❌ Запись с такими данными уже существует"
        elif "not found" in error_msg:
            return "❌ Запись не найдена"
        elif "permission denied" in error_msg:
            return "❌ Недостаточно прав для выполнения операции"
        else:
            return f"❌ Ошибка базы данных: {str(error)}"

    @staticmethod
    def handle_validation_error(error: Exception, context: str = "") -> str:
        """Обработка ошибок валидации."""
        return f"❌ Ошибка валидации: {str(error)}"

    @staticmethod
    def handle_general_error(error: Exception, context: str = "") -> str:
        """Обработка общих ошибок."""
        return f"❌ Произошла ошибка: {str(error)}"


class ResponseFormatter:
    """Форматировщик ответов."""

    @staticmethod
    def format_success_message(title: str, details: List[str] = None) -> str:
        """Форматирование сообщения об успехе."""
        message = f"✅ <b>{title}</b>\n\n"

        if details:
            for detail in details:
                message += f"{detail}\n"

        return message.strip()

    @staticmethod
    def format_error_message(title: str, details: List[str] = None) -> str:
        """Форматирование сообщения об ошибке."""
        message = f"❌ <b>{title}</b>\n\n"

        if details:
            for detail in details:
                message += f"{detail}\n"

        return message.strip()

    @staticmethod
    def format_info_message(title: str, details: List[str] = None) -> str:
        """Форматирование информационного сообщения."""
        message = f"ℹ️ <b>{title}</b>\n\n"

        if details:
            for detail in details:
                message += f"{detail}\n"

        return message.strip()
