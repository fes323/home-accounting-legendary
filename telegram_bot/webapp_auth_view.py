"""
View для обработки авторизации через Telegram WebApp API
"""
import logging

from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from users.models.user import User

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebAppAuthView(View):
    """
    View для обработки авторизации через Telegram WebApp API
    Согласно документации Aiogram, данные передаются в поле _auth
    """

    def post(self, request):
        """POST запрос - обрабатываем авторизацию через Telegram WebApp"""

        try:
            # Получаем данные из поля _auth (согласно документации Aiogram)
            init_data = request.POST.get('_auth')
            if not init_data:
                logger.warning("No _auth data found in request")
                return JsonResponse({'error': 'No auth data provided'}, status=400)

            # Парсим и валидируем данные Telegram WebApp
            from .telegram_auth import get_telegram_user_from_webapp
            user_data = get_telegram_user_from_webapp(
                init_data, verify_signature=True)

            if not user_data:
                logger.warning(
                    "Failed to parse or verify Telegram WebApp data")
                return JsonResponse({'error': 'Invalid auth data'}, status=401)

            telegram_id = user_data.get('id')
            if not telegram_id:
                logger.warning("No telegram_id found in user data")
                return JsonResponse({'error': 'No user ID in auth data'}, status=400)

            # Ищем или создаем пользователя
            user = User.objects.filter(telegram_id=telegram_id).first()
            if not user:
                # Создаем нового пользователя
                username = user_data.get('username') or f"tg_{telegram_id}"
                user = User.objects.create(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', ''),
                )
                logger.info(
                    f"Created new user: {user.username} (telegram_id: {telegram_id})")

            # Возвращаем успешный ответ
            return JsonResponse({
                'ok': True,
                'user': {
                    'id': str(user.uuid),
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'telegram_id': user.telegram_id,
                }
            })

        except Exception as e:
            logger.error(f"Error in Telegram WebApp auth: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)

    def get(self, request):
        """GET запрос - показываем информацию о WebApp API"""

        return JsonResponse({
            'ok': True,
            'message': 'Telegram WebApp Auth API',
            'usage': {
                'method': 'POST',
                'field': '_auth',
                'description': 'Send Telegram WebApp init data in _auth field'
            },
            'example': {
                'curl': 'curl -X POST -d "_auth=YOUR_TELEGRAM_INIT_DATA" https://wallet.my-bucket.ru/telegram/webapp-auth/'
            }
        })


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebAppTestView(View):
    """
    Тестовая страница для проверки WebApp API
    """

    def get(self, request):
        """GET запрос - показываем тестовую страницу"""

        # Проверяем, есть ли данные в URL
        init_data = request.GET.get('_auth') or request.GET.get('tgWebAppData')

        context = {
            'init_data': init_data,
            'has_auth_data': bool(init_data),
            'settings': {
                'TELEGRAM_MINIAPP_DEBUG_MODE': settings.TELEGRAM_MINIAPP_DEBUG_MODE,
                'TELEGRAM_BOT_TOKEN': settings.TELEGRAM_BOT_TOKEN[:10] + '...' if settings.TELEGRAM_BOT_TOKEN else 'Not set',
            }
        }

        return JsonResponse({
            'ok': True,
            'test_page': True,
            'data': context
        })

    def post(self, request):
        """POST запрос - тестируем авторизацию"""

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
                'ok': True,
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
