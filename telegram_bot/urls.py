from django.urls import path

from telegram_bot.views import TelegramWebhookView, telegram_webhook

app_name = 'telegram_bot'

urlpatterns = [
    path('webhook/', TelegramWebhookView.as_view(), name='webhook'),
    path('webhook/simple/', telegram_webhook, name='simple_webhook'),
]
