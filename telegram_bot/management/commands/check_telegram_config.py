"""
Команда для проверки конфигурации Telegram WebApp
"""
from django.core.management.base import BaseCommand

from telegram_bot.utils import validate_telegram_config


class Command(BaseCommand):
    help = 'Проверяет конфигурацию Telegram WebApp'

    def handle(self, *args, **options):
        self.stdout.write('Проверка конфигурации Telegram WebApp...\n')

        validation = validate_telegram_config()

        # Выводим результаты проверки
        if validation['valid']:
            self.stdout.write(
                self.style.SUCCESS('✓ Конфигурация корректна')
            )
        else:
            self.stdout.write(
                self.style.ERROR('✗ Обнаружены проблемы в конфигурации')
            )

        # Показываем конфигурацию
        self.stdout.write('\nКонфигурация:')
        config = validation['config']
        for key, value in config.items():
            status = '✓' if value else '✗'
            self.stdout.write(f'  {status} {key}: {value}')

        # Показываем проблемы
        if validation['issues']:
            self.stdout.write('\nПроблемы:')
            for issue in validation['issues']:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ {issue}')
                )

        # Показываем предупреждения
        if validation['warnings']:
            self.stdout.write('\nПредупреждения:')
            for warning in validation['warnings']:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ {warning}')
                )

        # Рекомендации
        if not validation['valid']:
            self.stdout.write('\nРекомендации:')
            self.stdout.write(
                '  1. Установите TELEGRAM_BOT_TOKEN в настройках')
            self.stdout.write(
                '  2. Установите TELEGRAM_MINIAPP_URL в настройках')
            self.stdout.write('  3. Проверьте ALLOWED_HOSTS')
            self.stdout.write('  4. Убедитесь, что DEBUG=False в продакшене')
