"""
Команда для диагностики проблем аутентификации Telegram WebApp
"""
import json

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Диагностирует проблемы с аутентификацией Telegram WebApp'

    def handle(self, *args, **options):
        self.stdout.write(
            'Диагностика проблем аутентификации Telegram WebApp...\n')

        # Проверяем конфигурацию
        self.stdout.write('=== КОНФИГУРАЦИЯ ===')

        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        miniapp_url = getattr(settings, 'TELEGRAM_MINIAPP_URL', '')
        debug_mode = getattr(settings, 'TELEGRAM_MINIAPP_DEBUG_MODE', False)
        allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])

        self.stdout.write(
            f'TELEGRAM_BOT_TOKEN: {"✓ Настроен" if bot_token else "✗ Не настроен"}')
        self.stdout.write(
            f'TELEGRAM_MINIAPP_URL: {"✓ Настроен" if miniapp_url else "✗ Не настроен"}')
        self.stdout.write(
            f'DEBUG_MODE: {"✓ Включен" if debug_mode else "✗ Выключен"}')
        self.stdout.write(f'ALLOWED_HOSTS: {allowed_hosts}')

        # Проверяем middleware
        self.stdout.write('\n=== MIDDLEWARE ===')
        middleware_list = getattr(settings, 'MIDDLEWARE', [])
        telegram_middleware = [
            m for m in middleware_list if 'telegram' in m.lower()]

        if telegram_middleware:
            self.stdout.write('Telegram middleware:')
            for middleware in telegram_middleware:
                self.stdout.write(f'  ✓ {middleware}')
        else:
            self.stdout.write('✗ Telegram middleware не найден')

        # Проверяем URL patterns
        self.stdout.write('\n=== URL PATTERNS ===')
        try:
            from django.urls import get_resolver
            resolver = get_resolver()
            telegram_urls = []

            def collect_urls(url_patterns, prefix=''):
                for pattern in url_patterns:
                    if hasattr(pattern, 'url_patterns'):
                        collect_urls(pattern.url_patterns,
                                     prefix + str(pattern.pattern))
                    else:
                        url_name = getattr(pattern, 'name', None)
                        if url_name and 'telegram' in url_name:
                            telegram_urls.append(
                                f'{prefix}{pattern.pattern} -> {url_name}')

            collect_urls(resolver.url_patterns)

            if telegram_urls:
                self.stdout.write('Telegram URLs:')
                for url in telegram_urls[:10]:  # Показываем первые 10
                    self.stdout.write(f'  ✓ {url}')
                if len(telegram_urls) > 10:
                    self.stdout.write(
                        f'  ... и еще {len(telegram_urls) - 10} URL')
            else:
                self.stdout.write('✗ Telegram URLs не найдены')

        except Exception as e:
            self.stdout.write(f'✗ Ошибка при проверке URL: {e}')

        # Рекомендации
        self.stdout.write('\n=== РЕКОМЕНДАЦИИ ===')

        issues = []
        if not bot_token:
            issues.append('Установите TELEGRAM_BOT_TOKEN в настройках')
        if not miniapp_url:
            issues.append('Установите TELEGRAM_MINIAPP_URL в настройках')
        if debug_mode:
            issues.append('Отключите DEBUG_MODE в продакшене')
        if '*' in allowed_hosts:
            issues.append('Замените "*" в ALLOWED_HOSTS на конкретные домены')

        if issues:
            self.stdout.write('Обнаружены проблемы:')
            for issue in issues:
                self.stdout.write(f'  ⚠ {issue}')
        else:
            self.stdout.write('✓ Конфигурация выглядит корректно')

        # Информация о типичных проблемах
        self.stdout.write('\n=== ТИПИЧНЫЕ ПРОБЛЕМЫ ===')
        self.stdout.write(
            '1. "No hash found" - данные аутентификации повреждены или отсутствуют')
        self.stdout.write(
            '2. "No user data found" - в данных нет информации о пользователе')
        self.stdout.write(
            '3. "Unauthorized" - запрос не проходит проверку аутентификации')
        self.stdout.write(
            '4. Частые запросы без данных - возможно, JavaScript не передает параметры')

        self.stdout.write('\n=== ДИАГНОСТИКА ЗАВЕРШЕНА ===')
