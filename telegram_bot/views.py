import json
import logging

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from telegram_bot.bot import create_webhook_app

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(View):
    """Webhook для получения обновлений от Telegram"""

    def post(self, request):
        try:
            # Получаем данные от Telegram
            update_data = json.loads(request.body.decode('utf-8'))

            # Логируем обновление
            logger.info(f"Received update: {update_data}")

            # Здесь будет обработка через aiogram
            # Пока просто возвращаем OK
            return JsonResponse({'status': 'ok'})

        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    def get(self, request):
        """Проверка webhook"""
        return JsonResponse({'status': 'webhook is working'})


@csrf_exempt
@require_http_methods(["POST"])
def telegram_webhook(request):
    """Простой webhook endpoint"""
    try:
        update_data = json.loads(request.body.decode('utf-8'))
        logger.info(f"Received update: {update_data}")

        # Здесь будет интеграция с aiogram
        return JsonResponse({'status': 'ok'})

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return JsonResponse({'error': str(e)}, status=500)
