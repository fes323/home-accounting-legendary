"""
Views для аутентификации Telegram WebApp
"""
import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ..backends.telegram_auth import TelegramWebAppAuthBackend

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebAppAuthView(View):
    """
    View для обработки аутентификации через Telegram WebApp

    Принимает данные от Telegram WebApp, аутентифицирует пользователя
    и сохраняет его в сессии Django.
    """

    def get(self, request):
        """
        GET запрос - показываем страницу авторизации
        """
        return render(request, 'telegram_bot/telegram_auth.html', {
            'title': 'Авторизация через Telegram',
            'error_message': None
        })

    def post(self, request):
        """
        POST запрос - обрабатываем данные аутентификации
        """
        try:
            # Получаем данные из запроса
            telegram_data = request.POST.get('_auth')
            if not telegram_data:
                return JsonResponse({
                    'success': False,
                    'error': 'No authentication data provided'
                }, status=400)

            # Аутентифицируем пользователя
            auth_backend = TelegramWebAppAuthBackend()
            user = auth_backend.authenticate(
                request, telegram_data=telegram_data)

            if user:
                # Входим в систему
                login(request, user)

                # Возвращаем успешный ответ
                return JsonResponse({
                    'success': True,
                    'user': {
                        'id': str(user.uuid),
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'telegram_id': getattr(user, 'telegram_id', None)
                    },
                    'redirect_url': reverse('telegram_bot:mini_app_dashboard')
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Authentication failed'
                }, status=401)

        except Exception as e:
            logger.error(f"Error in Telegram WebApp authentication: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


class TelegramWebAppLogoutView(View):
    """
    View для выхода из системы
    """

    def post(self, request):
        """
        POST запрос - выход из системы
        """
        try:
            # Очищаем сессию
            if request.session:
                request.session.flush()

            # Выходим из системы
            from django.contrib.auth import logout
            logout(request)

            messages.success(request, 'Вы успешно вышли из системы')

            # Перенаправляем на страницу авторизации
            return redirect('telegram_bot:auto_auth')

        except Exception as e:
            logger.error(f"Error during logout: {e}")
            messages.error(request, 'Ошибка при выходе из системы')
            return redirect('telegram_bot:mini_app_dashboard')


class TelegramWebAppStatusView(View):
    """
    View для проверки статуса аутентификации
    """

    def get(self, request):
        """
        GET запрос - возвращает статус аутентификации
        """
        if request.user.is_authenticated:
            return JsonResponse({
                'authenticated': True,
                'user': {
                    'id': str(request.user.uuid),
                    'username': request.user.username,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'telegram_id': getattr(request.user, 'telegram_id', None)
                }
            })
        else:
            return JsonResponse({
                'authenticated': False,
                'user': None
            })


class TelegramWebAppRedirectView(View):
    """
    View для обработки перенаправлений после аутентификации
    """

    def get(self, request):
        """
        GET запрос - обрабатывает перенаправление
        """
        # Проверяем, есть ли данные аутентификации в запросе
        telegram_data = request.GET.get('_auth')

        if telegram_data:
            # Аутентифицируем пользователя
            auth_backend = TelegramWebAppAuthBackend()
            user = auth_backend.authenticate(
                request, telegram_data=telegram_data)

            if user:
                # Входим в систему
                login(request, user)
                messages.success(request, 'Авторизация успешна!')

                # Перенаправляем на главную страницу
                return redirect('telegram_bot:mini_app_dashboard')
            else:
                messages.error(request, 'Ошибка авторизации')
                return redirect('telegram_bot:auto_auth')
        else:
            # Нет данных аутентификации, перенаправляем на страницу авторизации
            return redirect('telegram_bot:auto_auth')
