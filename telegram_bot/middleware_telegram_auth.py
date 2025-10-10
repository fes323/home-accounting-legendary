"""
Middleware для обработки аутентификации Telegram WebApp
"""
import logging

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.urls import reverse

logger = logging.getLogger(__name__)


class TelegramWebAppAuthMiddleware:
    """
    Middleware для автоматической аутентификации пользователей Telegram WebApp

    Обрабатывает входящие запросы и автоматически аутентифицирует пользователей
    на основе данных Telegram WebApp, сохраняя их в сессии Django.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Пути, которые требуют аутентификации
        self.protected_paths = [
            '/telegram/mini-app/',
        ]
        # Пути, которые исключаются из проверки
        self.excluded_paths = [
            '/telegram/mini-app/diagnostic/',
            '/telegram/auto-auth/',
            '/telegram/webapp-auth/',
            '/telegram/webapp-test/',
            '/telegram/webapp-integration/',
            '/telegram/mobile-debug/',
            '/telegram/mini-app/test-auth/',
        ]

    def __call__(self, request):
        # Обрабатываем только запросы к Telegram mini-app
        if self._should_process_request(request):
            self._process_telegram_auth(request)

        response = self.get_response(request)
        return response

    def _should_process_request(self, request) -> bool:
        """
        Определяет, нужно ли обрабатывать запрос

        Args:
            request: HTTP запрос

        Returns:
            bool: True если запрос нужно обработать
        """
        path = request.path

        # Проверяем, что это путь к Telegram mini-app
        if not any(path.startswith(protected_path) for protected_path in self.protected_paths):
            return False

        # Исключаем определенные пути
        if any(path.startswith(excluded_path) for excluded_path in self.excluded_paths):
            return False

        return True

    def _process_telegram_auth(self, request):
        """
        Обрабатывает аутентификацию Telegram WebApp

        Args:
            request: HTTP запрос
        """
        # Если пользователь уже аутентифицирован, пропускаем
        if request.user.is_authenticated:
            return

        # Проверяем, что это запрос из Telegram
        if not self._is_telegram_request(request):
            return

        # Извлекаем данные аутентификации
        telegram_data = self._extract_telegram_data(request)

        if telegram_data:
            # Аутентифицируем пользователя
            user = authenticate(request, telegram_data=telegram_data)

            if user:
                # Входим в систему
                login(request, user)
                logger.info(
                    f"User {user.username} authenticated via Telegram WebApp")
            else:
                # Аутентификация не удалась, перенаправляем на страницу авторизации
                self._redirect_to_auth(request)
        else:
            # Нет данных аутентификации, перенаправляем на страницу авторизации
            self._redirect_to_auth(request)

    def _is_telegram_request(self, request) -> bool:
        """
        Определяет, является ли запрос запросом из Telegram

        Args:
            request: HTTP запрос

        Returns:
            bool: True если запрос из Telegram
        """
        # Проверяем User-Agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'TelegramBot' in user_agent or 'Telegram' in user_agent:
            return True

        # Проверяем Referer
        referer = request.META.get('HTTP_REFERER', '')
        if any(domain in referer for domain in [
            'web.telegram.org',
            'webk.telegram.org',
            'webz.telegram.org'
        ]):
            return True

        # Проверяем заголовки Telegram
        if 'X-Telegram-Bot-Api-Secret-Token' in request.META:
            return True

        return False

    def _extract_telegram_data(self, request) -> str:
        """
        Извлекает данные Telegram WebApp из запроса

        Args:
            request: HTTP запрос

        Returns:
            str: Данные аутентификации или None
        """
        # Проверяем параметр _auth
        telegram_data = request.GET.get('_auth') or request.POST.get('_auth')
        if telegram_data:
            return telegram_data

        # Проверяем старый формат
        telegram_data = request.GET.get(
            'tgWebAppData') or request.POST.get('tgWebAppData')
        if telegram_data:
            return telegram_data

        # Проверяем данные в пути URL
        if '&_auth=' in request.path:
            path_parts = request.path.split('&_auth=')
            if len(path_parts) > 1:
                # Восстанавливаем правильный путь
                request.path = path_parts[0]
                request.path_info = path_parts[0]
                return '&_auth='.join(path_parts[1:])

        return None

    def _redirect_to_auth(self, request):
        """
        Перенаправляет на страницу авторизации

        Args:
            request: HTTP запрос
        """
        # Проверяем, что это не AJAX запрос
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return

        # Перенаправляем на страницу авторизации
        auth_url = reverse('telegram_bot:auto_auth')
        logger.info(f"Redirecting to auth page: {request.path}")

        # Используем redirect для перенаправления
        # В middleware мы не можем напрямую возвращать HttpResponse,
        # поэтому устанавливаем флаг для последующей обработки
        request._telegram_auth_redirect = auth_url
