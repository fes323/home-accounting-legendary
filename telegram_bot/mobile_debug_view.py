"""
View для диагностики мобильных проблем с Telegram WebApp
"""
import logging

from django.shortcuts import render
from django.views import View

logger = logging.getLogger(__name__)


class MobileDebugView(View):
    """
    View для диагностики мобильных проблем с Telegram WebApp
    """

    def get(self, request):
        """GET запрос - показываем страницу диагностики"""

        # Проверяем, есть ли данные Telegram WebApp в URL (для отладки)
        init_data = request.GET.get('_auth') or request.GET.get('tgWebAppData')

        context = {
            'init_data': init_data,
            'has_auth_data': bool(init_data),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'is_mobile': self._is_mobile_request(request),
        }

        return render(request, 'telegram_bot/mobile_debug.html', context)

    def _is_mobile_request(self, request):
        """Проверяем, является ли запрос с мобильного устройства"""
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        mobile_indicators = ['mobile', 'android', 'iphone', 'ipad', 'ipod']
        return any(indicator in user_agent for indicator in mobile_indicators)
