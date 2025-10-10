"""
Middleware для автоматического перенаправления на авторизацию
"""
import logging

from django.shortcuts import redirect
from django.urls import reverse

logger = logging.getLogger(__name__)


class TelegramAuthRedirectMiddleware:
    """
    Middleware для автоматического перенаправления на авторизацию
    когда пользователь заходит из Telegram без данных аутентификации
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Проверяем только запросы к Telegram mini-app
        if request.path.startswith('/telegram/mini-app/'):
            # Проверяем, что это запрос из Telegram
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            referer = request.META.get('HTTP_REFERER', '')
            is_telegram_browser = (
                'TelegramBot' in user_agent or 'Telegram' in user_agent or
                'web.telegram.org' in referer or 'webk.telegram.org' in referer or 'webz.telegram.org' in referer
            )

            # Проверяем наличие данных аутентификации
            has_auth_data = bool(
                request.GET.get('_auth') or
                request.POST.get('_auth') or
                request.GET.get('tgWebAppData') or
                request.POST.get('tgWebAppData') or
                '&_auth=' in request.path
            )

            # Если это Telegram браузер, но нет данных аутентификации
            if is_telegram_browser and not has_auth_data:
                # Исключаем страницы авторизации и диагностики
                excluded_paths = [
                    '/telegram/mini-app/diagnostic/',
                    '/telegram/auto-auth/',
                    '/telegram/webapp-auth/',
                    '/telegram/webapp-test/',
                    '/telegram/webapp-integration/',
                    '/telegram/mobile-debug/',
                    '/telegram/mini-app/test-auth/',
                ]

                if not any(request.path.startswith(path) for path in excluded_paths):
                    logger.info(
                        f"Redirecting Telegram user to auth page: {request.path}")
                    return redirect('telegram_bot:auto_auth')

        response = self.get_response(request)
        return response
