"""
Тестовая страница для проверки авторизации через Telegram
"""
import logging

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from users.models.user import User

logger = logging.getLogger(__name__)


class TestAuthView(View):
    """
    Тестовая страница для проверки авторизации через Telegram
    """

    def get(self, request):
        """GET запрос - показываем тестовую страницу"""

        # Собираем информацию о запросе
        request_info = {
            'method': request.method,
            'host': request.get_host(),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'referer': request.META.get('HTTP_REFERER', ''),
            'all_headers': {k: v for k, v in request.META.items() if k.startswith('HTTP_')},
            'get_params': dict(request.GET),
            'post_params': dict(request.POST),
        }

        # Проверяем, есть ли данные Telegram WebApp
        init_data = request.GET.get(
            'tgWebAppData') or request.POST.get('tgWebAppData')
        telegram_data = None

        if init_data:
            try:
                from .telegram_auth import get_telegram_user_from_webapp
                telegram_data = get_telegram_user_from_webapp(
                    init_data, verify_signature=False)
            except Exception as e:
                telegram_data = {'error': str(e)}

        # Пытаемся получить пользователя
        user = None
        if telegram_data and 'id' in telegram_data:
            try:
                user = User.objects.filter(
                    telegram_id=telegram_data['id']).first()
                if not user:
                    # Создаем тестового пользователя
                    user = User.objects.create(
                        telegram_id=telegram_data['id'],
                        username=telegram_data.get(
                            'username') or f"tg_{telegram_data['id']}",
                        first_name=telegram_data.get('first_name', ''),
                        last_name=telegram_data.get('last_name', ''),
                    )
                    logger.info(f"Created test user: {user.username}")
            except Exception as e:
                logger.error(f"Error creating user: {e}")

        context = {
            'request_info': request_info,
            'telegram_data': telegram_data,
            'user': user,
            'init_data': init_data,
            'settings': {
                'TELEGRAM_MINIAPP_DEBUG_MODE': settings.TELEGRAM_MINIAPP_DEBUG_MODE,
                'TELEGRAM_BOT_TOKEN': settings.TELEGRAM_BOT_TOKEN[:10] + '...' if settings.TELEGRAM_BOT_TOKEN else 'Not set',
            }
        }

        return render(request, 'telegram_bot/test_auth.html', context)

    def post(self, request):
        """POST запрос - обрабатываем авторизацию"""

        # Получаем данные из формы
        telegram_id = request.POST.get('telegram_id')
        username = request.POST.get('username', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        if not telegram_id:
            return JsonResponse({'error': 'Telegram ID is required'}, status=400)

        try:
            # Ищем или создаем пользователя
            user = User.objects.filter(telegram_id=telegram_id).first()
            if not user:
                user = User.objects.create(
                    telegram_id=telegram_id,
                    username=username or f"tg_{telegram_id}",
                    first_name=first_name,
                    last_name=last_name,
                )
                logger.info(f"Created user via test form: {user.username}")

            return JsonResponse({
                'success': True,
                'user': {
                    'id': str(user.uuid),
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'telegram_id': user.telegram_id,
                }
            })

        except Exception as e:
            logger.error(f"Error in test auth: {e}")
            return JsonResponse({'error': str(e)}, status=500)
