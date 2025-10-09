"""
Модуль обработчиков Telegram бота для учета финансов.

Этот модуль содержит все обработчики команд и callback-запросов,
организованные по функциональным группам.
"""

from .main_router import register_handlers

__all__ = ['register_handlers']
