"""
Утилиты для авторизации через Telegram WebApp
"""
import hashlib
import hmac
import json
import urllib.parse
from typing import Dict, Optional

from django.conf import settings


def verify_telegram_webapp_data(init_data: str, bot_token: str) -> bool:
    """
    Проверяет подпись данных Telegram WebApp

    Args:
        init_data: Строка с данными от Telegram WebApp
        bot_token: Токен бота для проверки подписи

    Returns:
        bool: True если подпись корректна
    """
    try:
        # Парсим данные
        parsed_data = urllib.parse.parse_qs(init_data)

        # Извлекаем hash
        if 'hash' not in parsed_data:
            return False

        received_hash = parsed_data['hash'][0]

        # Создаем строку для проверки
        data_check_string = []
        for key in sorted(parsed_data.keys()):
            if key != 'hash':
                data_check_string.append(f"{key}={parsed_data[key][0]}")

        data_check_string = '\n'.join(data_check_string)

        # Создаем секретный ключ
        secret_key = hmac.new(
            "WebAppData".encode('utf-8'),
            bot_token.encode('utf-8'),
            hashlib.sha256
        ).digest()

        # Вычисляем hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(calculated_hash, received_hash)

    except Exception:
        return False


def parse_telegram_webapp_data(init_data: str) -> Optional[Dict]:
    """
    Парсит данные Telegram WebApp и возвращает информацию о пользователе

    Args:
        init_data: Строка с данными от Telegram WebApp

    Returns:
        Dict с данными пользователя или None при ошибке
    """
    try:
        parsed_data = urllib.parse.parse_qs(init_data)

        if 'user' not in parsed_data:
            return None

        user_data = json.loads(parsed_data['user'][0])
        return user_data

    except Exception:
        return None


def get_telegram_user_from_webapp(init_data: str, verify_signature: bool = True) -> Optional[Dict]:
    """
    Получает данные пользователя из Telegram WebApp с проверкой подписи

    Args:
        init_data: Строка с данными от Telegram WebApp
        verify_signature: Проверять ли подпись (по умолчанию True)

    Returns:
        Dict с данными пользователя или None при ошибке
    """
    if verify_signature:
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        if not bot_token:
            # Если нет токена, пропускаем проверку подписи
            pass
        elif not verify_telegram_webapp_data(init_data, bot_token):
            return None

    return parse_telegram_webapp_data(init_data)
