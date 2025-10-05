import os
from pathlib import Path

from dotenv import load_dotenv

# Определяем путь к корню проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем переменные окружения из .env файла
load_dotenv(BASE_DIR / '.env')

# ===========================================
# TELEGRAM BOT CONFIGURATION
# ===========================================

# Основные настройки бота
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL', '')
TELEGRAM_WEBHOOK_SECRET = os.getenv('TELEGRAM_WEBHOOK_SECRET', '')

# Bot settings
BOT_USERNAME = os.getenv('BOT_USERNAME', '')
BOT_DESCRIPTION = "Личный помощник для учета финансов"

# Webhook settings
WEBHOOK_PATH = '/telegram/webhook/'
WEBHOOK_URL = f"{TELEGRAM_WEBHOOK_URL}{WEBHOOK_PATH}" if TELEGRAM_WEBHOOK_URL else ''

# Bot commands
BOT_COMMANDS = [
    {
        "command": "start",
        "description": "Начать работу с ботом"
    },
    {
        "command": "balance",
        "description": "Показать баланс кошельков"
    },
    {
        "command": "income",
        "description": "Добавить доход"
    },
    {
        "command": "expense",
        "description": "Добавить расход"
    },
    {
        "command": "wallets",
        "description": "Управление кошельками"
    },
    {
        "command": "categories",
        "description": "Управление категориями"
    },
    {
        "command": "help",
        "description": "Помощь по командам"
    }
]

# ===========================================
# VALIDATION
# ===========================================


def validate_config():
    """Проверка корректности конфигурации"""
    errors = []

    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN не установлен")

    if not BOT_USERNAME:
        errors.append("BOT_USERNAME не установлен")

    if errors:
        raise ValueError(f"Ошибки конфигурации: {', '.join(errors)}")

    return True


# Автоматическая проверка при импорте
try:
    validate_config()
except ValueError as e:
    print(f"Предупреждение: {e}")
