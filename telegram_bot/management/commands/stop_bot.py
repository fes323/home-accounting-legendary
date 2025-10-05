import os
import sys
import time

import django
import psutil
from django.core.management.base import BaseCommand

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')
django.setup()


class Command(BaseCommand):
    help = 'Остановка всех экземпляров Telegram бота'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Принудительно завершить процессы (kill)',
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

    def handle(self, *args, **options):
        processes = self.find_bot_processes()

        if not processes:
            self.stdout.write(
                self.style.SUCCESS('Активные экземпляры бота не найдены')
            )
            return

        self.stdout.write(
            self.style.WARNING(
                f'Найдено {len(processes)} активных экземпляров бота:')
        )

        for proc in processes:
            try:
                self.stdout.write(
                    f'  PID: {proc.pid}, CMD: {" ".join(proc.info["cmdline"])}')
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if not options['force']:
            self.stdout.write(
                self.style.WARNING(
                    '\nДля остановки процессов используйте --force'
                )
            )
            return

        # Останавливаем процессы
        for proc in processes:
            try:
                proc.terminate()
                self.stdout.write(f'Остановлен процесс {proc.pid}')
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Ждем завершения процессов
        time.sleep(2)

        # Проверяем, какие процессы еще работают
        remaining_processes = []
        for proc in processes:
            try:
                if proc.is_running():
                    remaining_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Принудительно завершаем оставшиеся процессы
        if remaining_processes:
            self.stdout.write(
                self.style.WARNING(
                    f'Принудительно завершаем {len(remaining_processes)} процессов...'
                )
            )
            for proc in remaining_processes:
                try:
                    proc.kill()
                    self.stdout.write(
                        f'Принудительно завершен процесс {proc.pid}')
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        self.stdout.write(
            self.style.SUCCESS('Все экземпляры бота остановлены')
        )
