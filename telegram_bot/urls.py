from django.urls import path

from telegram_bot.auto_auth_view import AutoAuthView
from telegram_bot.mini_app_views import MiniAppDiagnosticView
from telegram_bot.mini_app_views_refactored import (CategoryCreateView,
                                                    CategoryDeleteView,
                                                    CategoryEditView,
                                                    CategoryListView,
                                                    MiniAppDashboardView,
                                                    TransactionCreateView,
                                                    TransactionDeleteView,
                                                    TransactionEditView,
                                                    TransactionListView,
                                                    WalletCreateView,
                                                    WalletDeleteView,
                                                    WalletEditView,
                                                    WalletListView)
from telegram_bot.mobile_debug_view import MobileDebugView
from telegram_bot.test_auth_view import TestAuthView
from telegram_bot.views.telegram_auth_view import (TelegramWebAppAuthView,
                                                   TelegramWebAppLogoutView,
                                                   TelegramWebAppRedirectView,
                                                   TelegramWebAppStatusView)
from telegram_bot.webapp_integration_view import WebAppIntegrationView
from telegram_bot.webhook_views import TelegramWebhookView, telegram_webhook

app_name = 'telegram_bot'

urlpatterns = [
    # Webhook endpoints
    path('webhook/', TelegramWebhookView.as_view(), name='webhook'),
    path('webhook/simple/', telegram_webhook, name='simple_webhook'),

    # WebApp API endpoints
    path('webapp-auth/', TelegramWebAppAuthView.as_view(), name='webapp_auth'),
    path('webapp-logout/', TelegramWebAppLogoutView.as_view(), name='webapp_logout'),
    path('webapp-status/', TelegramWebAppStatusView.as_view(), name='webapp_status'),
    path('webapp-redirect/', TelegramWebAppRedirectView.as_view(),
         name='webapp_redirect'),
    path('webapp-integration/', WebAppIntegrationView.as_view(),
         name='webapp_integration'),
    path('auto-auth/', AutoAuthView.as_view(), name='auto_auth'),
    path('mobile-debug/', MobileDebugView.as_view(), name='mobile_debug'),

    # Mini App endpoints
    path('mini-app/', MiniAppDashboardView.as_view(), name='mini_app_dashboard'),
    path('mini-app/diagnostic/', MiniAppDiagnosticView.as_view(),
         name='mini_app_diagnostic'),
    path('mini-app/test-auth/', TestAuthView.as_view(), name='test_auth'),

    # Transaction endpoints
    path('mini-app/transactions/',
         TransactionListView.as_view(), name='transactions'),
    path('mini-app/transactions/create/',
         TransactionCreateView.as_view(), name='transaction_create'),
    path('mini-app/transactions/<uuid:transaction_id>/edit/',
         TransactionEditView.as_view(), name='transaction_edit'),
    path('mini-app/transactions/<uuid:transaction_id>/delete/',
         TransactionDeleteView.as_view(), name='transaction_delete'),

    # Wallet endpoints
    path('mini-app/wallets/', WalletListView.as_view(), name='wallets'),
    path('mini-app/wallets/create/',
         WalletCreateView.as_view(), name='wallet_create'),
    path('mini-app/wallets/<uuid:wallet_id>/edit/',
         WalletEditView.as_view(), name='wallet_edit'),
    path('mini-app/wallets/<uuid:wallet_id>/delete/',
         WalletDeleteView.as_view(), name='wallet_delete'),

    # Category endpoints
    path('mini-app/categories/', CategoryListView.as_view(), name='categories'),
    path('mini-app/categories/create/',
         CategoryCreateView.as_view(), name='category_create'),
    path('mini-app/categories/<uuid:category_id>/edit/',
         CategoryEditView.as_view(), name='category_edit'),
    path('mini-app/categories/<uuid:category_id>/delete/',
         CategoryDeleteView.as_view(), name='category_delete'),
]
