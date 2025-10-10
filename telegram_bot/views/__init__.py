"""
Views для Telegram WebApp
"""
from .telegram_auth_view import (TelegramWebAppAuthView,
                                 TelegramWebAppLogoutView,
                                 TelegramWebAppRedirectView,
                                 TelegramWebAppStatusView)
from .telegram_base_view import (TelegramWebAppAuthenticatedView,
                                 TelegramWebAppBaseView)

__all__ = [
    'TelegramWebAppAuthView',
    'TelegramWebAppLogoutView',
    'TelegramWebAppRedirectView',
    'TelegramWebAppStatusView',
    'TelegramWebAppAuthenticatedView',
    'TelegramWebAppBaseView'
]
