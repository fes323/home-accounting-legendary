import os
import signal
import sys
import time

import django
import psutil
from django.core.management.base import BaseCommand

from telegram_bot.bot import run_polling

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
        parser.add_argument(
            '--kill-existing',
            action='store_true',
            help='Остановить все существующие экземпляры бота перед запуском',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Принудительно запустить бота, игнорируя конфликты',
        )

    def find_bot_processes(self):
        """Найти все процессы Python, которые могут быть экземплярами бота"""
        bot_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                    cmdline = proc.info['cmdline']
                    if cmdline and any('run_bot' in arg for arg in cmdline):
                        bot_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return bot_processes

    def kill_processes_aggressive(self, processes):
        """Агрессивная остановка процессов"""
        for proc in processes:
            try:
                # Сначала пытаемся terminate
                proc.terminate()
                self.stdout.write(
                    f'Отправлен сигнал завершения процессу {proc.pid}')

                # Ждем немного
                time.sleep(0.5)

                # Если процесс все еще работает, убиваем принудительно
                if proc.is_running():
                    proc.kill()
                    self.stdout.write(
                        f'Принудительно завершен процесс {proc.pid}')

            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                self.stdout.write(
                    f'Не удалось завершить процесс {proc.pid}: {e}')
                continue

    def kill_bot_processes(self):
        """Остановить все найденные процессы бота"""
        processes = self.find_bot_processes()
        if not processes:
            self.stdout.write(
                self.style.SUCCESS('Активные экземпляры бота не найдены')
            )
            return True

        self.stdout.write(
            self.style.WARNING(
                f'Найдено {len(processes)} активных экземпляров бота')
        )

        # Используем агрессивную остановку
        self.kill_processes_aggressive(processes)

        # Ждем завершения процессов
        time.sleep(2)

        # Финальная проверка
        final_check = self.find_bot_processes()
        if final_check:
            self.stdout.write(
                self.style.ERROR(
                    f'Предупреждение: {len(final_check)} процессов все еще активны!'
                )
            )
            # Показываем информацию о процессах, которые не удалось остановить
            for proc in final_check:
                try:
                    self.stdout.write(
                        f'  PID: {proc.pid}, CMD: {" ".join(proc.info["cmdline"])}')
                except:
                    self.stdout.write(f'  PID: {proc.pid}')
            return False
        else:
            self.stdout.write(
                self.style.SUCCESS('Все экземпляры бота остановлены')
            )
            return True

    def handle(self, *args, **options):
        # Сначала останавливаем существующие процессы если запрошено
        if options['kill_existing']:
            self.stdout.write(
                self.style.SUCCESS(
                    'Остановка существующих экземпляров бота...')
            )
            success = self.kill_bot_processes()
            if not success:
                self.stdout.write(
                    self.style.ERROR(
                        'Не удалось остановить все процессы. Попробуйте запустить '
                        'команду stop_bot --force отдельно.'
                    )
                )
                return

        # Проверяем наличие активных процессов бота (только если не использовали --kill-existing)
        if not options['kill_existing']:
            existing_processes = self.find_bot_processes()
            if existing_processes and not options['force']:
                self.stdout.write(
                    self.style.ERROR(
                        f'Найдено {len(existing_processes)} активных экземпляров бота!'
                    )
                )
                self.stdout.write(
                    self.style.WARNING(
                        'Используйте --kill-existing для остановки существующих экземпляров '
                        'или --force для принудительного запуска'
                    )
                )
                return

        if options['webhook']:
            self.stdout.write(
                self.style.WARNING('Режим webhook пока не реализован')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Запуск бота в режиме polling...')
            )

            # Настройка обработчика сигналов для корректного завершения
            def signal_handler(signum, frame):
                self.stdout.write(
                    self.style.WARNING(
                        '\nПолучен сигнал завершения. Остановка бота...')
                )
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            try:
                run_polling()
            except KeyboardInterrupt:
                self.stdout.write(
                    self.style.WARNING('Бот остановлен пользователем')
                )
            except Exception as e:
                error_msg = str(e)
                if 'Conflict' in error_msg and 'getUpdates' in error_msg:
                    self.stdout.write(
                        self.style.ERROR(
                            'Конфликт: уже запущен другой экземпляр бота!\n'
                            'Используйте --kill-existing для остановки существующих экземпляров'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Ошибка запуска бота: {e}')
                    )
