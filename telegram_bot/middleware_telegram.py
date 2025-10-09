"""
Middleware для обработки Telegram WebApp запросов
"""
import logging

from django.http import JsonResponse
from django.middleware.csrf import CsrfViewMiddleware

logger = logging.getLogger(__name__)


class TelegramWebAppMiddleware(CsrfViewMiddleware):
    """
    Middleware для обработки Telegram WebApp запросов
    Отключает CSRF проверку для Telegram WebApp запросов
    """

    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Проверяем, является ли это запросом от Telegram WebApp
        if self._is_telegram_webapp_request(request):
            # Для Telegram WebApp запросов пропускаем CSRF проверку
            return None

        # Для всех остальных запросов применяем стандартную CSRF проверку
        return super().process_view(request, callback, callback_args, callback_kwargs)

    def _is_telegram_webapp_request(self, request):
        """
        Проверяем, является ли запрос от Telegram WebApp
        """
        # Проверяем наличие данных Telegram WebApp
        init_data = request.GET.get(
            'tgWebAppData') or request.POST.get('tgWebAppData')
        if init_data:
            return True

        # Проверяем User-Agent Telegram WebApp
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'TelegramBot' in user_agent or 'Telegram' in user_agent:
            return True

        # Проверяем заголовки, которые отправляет Telegram
        if 'X-Telegram-Bot-Api-Secret-Token' in request.META:
            return True

        return False


class TelegramWebAppSecurityMiddleware:
    """
    Middleware для дополнительной безопасности Telegram WebApp
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Добавляем заголовки безопасности для Telegram WebApp
        if self._is_telegram_webapp_request(request):
            # Разрешаем встраивание в iframe для Telegram
            request.META['HTTP_X_FRAME_OPTIONS'] = 'ALLOWALL'

        response = self.get_response(request)

        # Устанавливаем заголовки для Telegram WebApp
        if self._is_telegram_webapp_request(request):
            response['X-Frame-Options'] = 'ALLOWALL'
            response['Content-Security-Policy'] = "frame-ancestors 'self' https://web.telegram.org https://webk.telegram.org https://webz.telegram.org;"

        return response

    def _is_telegram_webapp_request(self, request):
        """
        Проверяем, является ли запрос от Telegram WebApp
        """
        # Проверяем наличие данных Telegram WebApp
        init_data = request.GET.get(
            'tgWebAppData') or request.POST.get('tgWebAppData')
        if init_data:
            return True

        # Проверяем User-Agent Telegram WebApp
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'TelegramBot' in user_agent or 'Telegram' in user_agent:
            return True

        return False
