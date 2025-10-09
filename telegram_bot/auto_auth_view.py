"""
View для автоматической авторизации через Telegram WebApp
"""
import logging

from django.shortcuts import render
from django.views import View

logger = logging.getLogger(__name__)


class AutoAuthView(View):
    """
    View для автоматической авторизации через Telegram WebApp
    Эта страница получает initData из Telegram WebApp и перенаправляет на основное приложение
    """

    def get(self, request):
        """GET запрос - показываем страницу автоматической авторизации"""

        # Проверяем, есть ли данные Telegram WebApp в URL (для отладки)
        init_data = request.GET.get('_auth') or request.GET.get('tgWebAppData')

        context = {
            'init_data': init_data,
            'has_auth_data': bool(init_data),
        }

        return render(request, 'telegram_bot/auto_auth.html', context)
