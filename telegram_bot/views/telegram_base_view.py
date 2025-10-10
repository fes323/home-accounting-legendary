"""
Базовые views для Telegram WebApp
"""
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

from ..utils import get_telegram_error_response

logger = logging.getLogger(__name__)


class TelegramWebAppBaseView(View):
    """
    Базовый класс для всех Telegram WebApp views

    Обеспечивает единообразную обработку аутентификации и ошибок
    без необходимости передачи параметров аутентификации в каждом запросе.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Обработка запроса с проверкой аутентификации

        Args:
            request: HTTP запрос
            *args: Дополнительные аргументы
            **kwargs: Дополнительные именованные аргументы

        Returns:
            HTTP ответ
        """
        try:
            # Проверяем аутентификацию
            if not request.user.is_authenticated:
                return self._handle_unauthenticated(request)

            # Проверяем, что пользователь имеет telegram_id
            if not hasattr(request.user, 'telegram_id') or not request.user.telegram_id:
                logger.warning(
                    f"User {request.user.username} has no telegram_id")
                return self._handle_invalid_user(request)

            # Вызываем родительский метод
            return super().dispatch(request, *args, **kwargs)

        except Exception as e:
            logger.error(
                f"Error in TelegramWebAppBaseView.dispatch: {e}", exc_info=True)
            return self._handle_server_error(request, str(e))

    def _handle_unauthenticated(self, request):
        """
        Обработка неаутентифицированных запросов

        Args:
            request: HTTP запрос

        Returns:
            HTTP ответ
        """
        # Проверяем, что это запрос из Telegram
        if self._is_telegram_request(request):
            # Перенаправляем на страницу авторизации
            return redirect('telegram_bot:auto_auth')
        else:
            # Возвращаем ошибку для не-Telegram запросов
            error_response = get_telegram_error_response('unauthorized')
            return JsonResponse(error_response, status=error_response['code'])

    def _handle_invalid_user(self, request):
        """
        Обработка запросов от пользователей без telegram_id

        Args:
            request: HTTP запрос

        Returns:
            HTTP ответ
        """
        logger.warning(f"Invalid user: {request.user.username}")
        error_response = get_telegram_error_response('user_not_found')
        return JsonResponse(error_response, status=error_response['code'])

    def _handle_server_error(self, request, error_message):
        """
        Обработка серверных ошибок

        Args:
            request: HTTP запрос
            error_message: Сообщение об ошибке

        Returns:
            HTTP ответ
        """
        error_response = get_telegram_error_response(
            'server_error', error_message)
        return JsonResponse(error_response, status=error_response['code'])

    def _is_telegram_request(self, request):
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

    def get_context_data(self, **kwargs):
        """
        Получение контекста для шаблона

        Args:
            **kwargs: Дополнительные параметры контекста

        Returns:
            dict: Контекст для шаблона
        """
        context = {
            'user': self.request.user,
            'is_telegram_user': hasattr(self.request.user, 'telegram_id'),
        }
        context.update(kwargs)
        return context


@method_decorator(login_required, name='dispatch')
class TelegramWebAppAuthenticatedView(TelegramWebAppBaseView):
    """
    Базовый класс для аутентифицированных Telegram WebApp views

    Автоматически проверяет аутентификацию пользователя.
    """
    pass


class TelegramWebAppPublicView(TelegramWebAppBaseView):
    """
    Базовый класс для публичных Telegram WebApp views

    Не требует аутентификации, но проверяет, что запрос из Telegram.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Обработка запроса без проверки аутентификации

        Args:
            request: HTTP запрос
            *args: Дополнительные аргументы
            **kwargs: Дополнительные именованные аргументы

        Returns:
            HTTP ответ
        """
        try:
            # Проверяем, что это запрос из Telegram
            if not self._is_telegram_request(request):
                error_response = get_telegram_error_response('unauthorized')
                return JsonResponse(error_response, status=error_response['code'])

            # Вызываем родительский метод
            return super().dispatch(request, *args, **kwargs)

        except Exception as e:
            logger.error(
                f"Error in TelegramWebAppPublicView.dispatch: {e}", exc_info=True)
            return self._handle_server_error(request, str(e))
