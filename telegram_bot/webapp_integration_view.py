"""
View для тестирования интеграции с Telegram WebApp
"""
import logging

from django.shortcuts import render
from django.views import View

logger = logging.getLogger(__name__)


class WebAppIntegrationView(View):
    """
    View для тестирования интеграции с Telegram WebApp
    """

    def get(self, request):
        """GET запрос - показываем страницу интеграции"""

        # Проверяем, есть ли данные Telegram WebApp
        init_data = request.GET.get('_auth') or request.GET.get('tgWebAppData')

        context = {
            'init_data': init_data,
            'has_auth_data': bool(init_data),
            'request_method': request.method,
            'all_get_params': dict(request.GET),
            'all_post_params': dict(request.POST),
        }

        return render(request, 'telegram_bot/webapp_integration.html', context)
