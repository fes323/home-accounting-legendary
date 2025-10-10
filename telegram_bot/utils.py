"""
Утилиты для работы с Telegram WebApp
"""
import json
import logging
from typing import Any, Dict, Optional

from django.conf import settings
from django.http import HttpRequest

logger = logging.getLogger(__name__)


def diagnose_telegram_request(request: HttpRequest) -> Dict[str, Any]:
    """
    Диагностика Telegram WebApp запроса

    Args:
        request: HTTP запрос

    Returns:
        Dict с диагностической информацией
    """
    diagnosis = {
        'is_telegram_request': False,
        'detection_methods': {},
        'raw_data': {},
        'parsed_data': {},
        'errors': [],
        'recommendations': []
    }

    # Проверяем различные способы определения Telegram запроса
    detection_methods = {
        'has_auth_param': bool(request.GET.get('_auth') or request.POST.get('_auth')),
        'has_tgWebAppData': bool(request.GET.get('tgWebAppData') or request.POST.get('tgWebAppData')),
        'user_agent_telegram': 'Telegram' in request.META.get('HTTP_USER_AGENT', ''),
        'has_telegram_secret_token': 'X-Telegram-Bot-Api-Secret-Token' in request.META,
        'referer_telegram': any(domain in request.META.get('HTTP_REFERER', '')
                                for domain in ['web.telegram.org', 'webk.telegram.org', 'webz.telegram.org']),
    }

    diagnosis['detection_methods'] = detection_methods
    diagnosis['is_telegram_request'] = any(detection_methods.values())

    # Собираем сырые данные
    raw_data = {
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'referer': request.META.get('HTTP_REFERER', ''),
        'host': request.get_host(),
        'method': request.method,
        'path': request.path,
        'auth_param': request.GET.get('_auth') or request.POST.get('_auth'),
        'tgWebAppData': request.GET.get('tgWebAppData') or request.POST.get('tgWebAppData'),
    }
    diagnosis['raw_data'] = raw_data

    # Пытаемся распарсить данные
    init_data = raw_data['auth_param'] or raw_data['tgWebAppData']
    if init_data:
        try:
            from .telegram_auth import parse_telegram_webapp_data
            parsed_data = parse_telegram_webapp_data(init_data)
            if parsed_data:
                diagnosis['parsed_data'] = {
                    'user_id': parsed_data.get('id'),
                    'username': parsed_data.get('username'),
                    'first_name': parsed_data.get('first_name'),
                    'last_name': parsed_data.get('last_name'),
                }
        except Exception as e:
            diagnosis['errors'].append(f"Failed to parse Telegram data: {e}")

    # Проверяем конфигурацию
    config_issues = []
    if not getattr(settings, 'TELEGRAM_BOT_TOKEN', ''):
        config_issues.append("TELEGRAM_BOT_TOKEN not configured")
    if not getattr(settings, 'TELEGRAM_MINIAPP_URL', ''):
        config_issues.append("TELEGRAM_MINIAPP_URL not configured")

    if config_issues:
        diagnosis['errors'].extend(config_issues)

    # Рекомендации
    recommendations = []
    if not diagnosis['is_telegram_request']:
        recommendations.append(
            "Request doesn't appear to be from Telegram WebApp")
    if not init_data:
        recommendations.append("No Telegram WebApp data found in request")
    if config_issues:
        recommendations.append("Check Telegram bot configuration")

    diagnosis['recommendations'] = recommendations

    return diagnosis


def log_telegram_request(request: HttpRequest, level: str = 'INFO') -> None:
    """
    Логирует информацию о Telegram WebApp запросе

    Args:
        request: HTTP запрос
        level: Уровень логирования
    """
    diagnosis = diagnose_telegram_request(request)

    log_data = {
        'path': request.path,
        'method': request.method,
        'host': request.get_host(),
        'is_telegram_request': diagnosis['is_telegram_request'],
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'has_auth_data': bool(diagnosis['raw_data']['auth_param']),
        'has_tgWebAppData': bool(diagnosis['raw_data']['tgWebAppData']),
        'user_id': diagnosis['parsed_data'].get('user_id'),
        'errors': diagnosis['errors'],
    }

    if level.upper() == 'ERROR':
        logger.error(f"Telegram request error: {json.dumps(log_data)}")
    elif level.upper() == 'WARNING':
        logger.warning(f"Telegram request warning: {json.dumps(log_data)}")
    else:
        logger.info(f"Telegram request: {json.dumps(log_data)}")


def validate_telegram_config() -> Dict[str, Any]:
    """
    Проверяет конфигурацию Telegram бота

    Returns:
        Dict с результатами проверки
    """
    validation = {
        'valid': True,
        'issues': [],
        'warnings': [],
        'config': {}
    }

    # Проверяем основные настройки
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    miniapp_url = getattr(settings, 'TELEGRAM_MINIAPP_URL', '')
    debug_mode = getattr(settings, 'TELEGRAM_MINIAPP_DEBUG_MODE', False)

    validation['config'] = {
        'bot_token_configured': bool(bot_token),
        'miniapp_url_configured': bool(miniapp_url),
        'debug_mode': debug_mode,
        'allowed_hosts': getattr(settings, 'ALLOWED_HOSTS', []),
    }

    # Проверяем проблемы
    if not bot_token:
        validation['issues'].append("TELEGRAM_BOT_TOKEN not configured")
        validation['valid'] = False

    if not miniapp_url:
        validation['issues'].append("TELEGRAM_MINIAPP_URL not configured")
        validation['valid'] = False

    # Проверяем предупреждения
    if debug_mode:
        validation['warnings'].append(
            "Debug mode is enabled - this should be disabled in production")

    if '*' in getattr(settings, 'ALLOWED_HOSTS', []):
        validation['warnings'].append(
            "ALLOWED_HOSTS contains '*' - this is insecure")

    return validation


def get_telegram_error_response(error_type: str, message: str = None) -> Dict[str, Any]:
    """
    Возвращает стандартизированный ответ об ошибке для Telegram WebApp

    Args:
        error_type: Тип ошибки
        message: Дополнительное сообщение

    Returns:
        Dict с информацией об ошибке
    """
    error_responses = {
        'unauthorized': {
            'error': 'Unauthorized',
            'message': message or 'Access denied. Please open this app from Telegram.',
            'code': 401
        },
        'invalid_data': {
            'error': 'Invalid Data',
            'message': message or 'Invalid Telegram WebApp data received.',
            'code': 400
        },
        'user_not_found': {
            'error': 'User Not Found',
            'message': message or 'User authentication failed.',
            'code': 401
        },
        'server_error': {
            'error': 'Server Error',
            'message': message or 'An internal server error occurred.',
            'code': 500
        },
        'not_found': {
            'error': 'Not Found',
            'message': message or 'The requested resource was not found.',
            'code': 404
        }
    }

    return error_responses.get(error_type, error_responses['server_error'])
