from telegram_bot.bot import run_polling
import os
import sys

import django
from django.core.management.base import BaseCommand

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')
django.setup()


class Command(BaseCommand):
    help = 'Запуск Telegram бота в режиме polling (для разработки)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--webhook',
            action='store_true',
            help='Запустить в режиме webhook вместо polling',
        )

    def handle(self, *args, **options):
        if options['webhook']:
            self.stdout.write(
                self.style.WARNING('Режим webhook пока не реализован')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Запуск бота в режиме polling...')
            )
            try:
                run_polling()
            except KeyboardInterrupt:
                self.stdout.write(
                    self.style.WARNING('Бот остановлен пользователем')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка запуска бота: {e}')
                )
