"""
Middleware для обработки Telegram WebApp запросов
"""
import logging

from django.core.exceptions import SuspiciousOperation
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
        # Проверяем наличие данных Telegram WebApp (сначала _auth, потом старый формат)
        init_data = request.GET.get('_auth') or request.POST.get('_auth')
        if not init_data:
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

        # Проверяем Referer от Telegram
        referer = request.META.get('HTTP_REFERER', '')
        if 'web.telegram.org' in referer or 'webk.telegram.org' in referer or 'webz.telegram.org' in referer:
            return True

        return False


class TelegramWebAppSecurityMiddleware:
    """
    Middleware для дополнительной безопасности Telegram WebApp
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
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
        except SuspiciousOperation as e:
            logger.warning(f"Suspicious operation detected: {e}")
            return JsonResponse({
                'error': 'Bad Request',
                'message': 'Invalid request detected'
            }, status=400)
        except Exception as e:
            logger.error(
                f"Error in TelegramWebAppSecurityMiddleware: {e}", exc_info=True)
            return JsonResponse({
                'error': 'Internal Server Error',
                'message': 'An error occurred while processing the request'
            }, status=500)

    def _is_telegram_webapp_request(self, request):
        """
        Проверяем, является ли запрос от Telegram WebApp
        """
        # Проверяем наличие данных Telegram WebApp (сначала _auth, потом старый формат)
        init_data = request.GET.get('_auth') or request.POST.get('_auth')
        if not init_data:
            init_data = request.GET.get(
                'tgWebAppData') or request.POST.get('tgWebAppData')

        if init_data:
            return True

        # Проверяем User-Agent Telegram WebApp
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'TelegramBot' in user_agent or 'Telegram' in user_agent:
            return True

        # Проверяем Referer от Telegram
        referer = request.META.get('HTTP_REFERER', '')
        if 'web.telegram.org' in referer or 'webk.telegram.org' in referer or 'webz.telegram.org' in referer:
            return True

        return False
