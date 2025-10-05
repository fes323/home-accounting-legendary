#!/usr/bin/env python
"""
Простой скрипт для тестирования Telegram бота
Использование: python test_bot.py
"""

from telegram_bot.bot import run_polling
import os
import sys

import django

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')
django.setup()


if __name__ == '__main__':
    print("🤖 Запуск Telegram бота...")
    print("Для остановки нажмите Ctrl+C")

    try:
        run_polling()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
