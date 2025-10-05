#!/usr/bin/env python
"""
Скрипт для диагностики процессов бота
"""
import sys

import psutil


def find_bot_processes():
    """Найти все процессы Python, которые могут быть экземплярами бота"""
    bot_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status']):
        try:
            if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                cmdline = proc.info['cmdline']
                if cmdline and any('run_bot' in arg for arg in cmdline):
                    bot_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return bot_processes


def main():
    print("🔍 Диагностика процессов бота")
    print("=" * 50)

    processes = find_bot_processes()

    if not processes:
        print("✅ Активные экземпляры бота не найдены")
        return

    print(f"Найдено {len(processes)} активных экземпляров бота:")
    print()

    for i, proc in enumerate(processes, 1):
        try:
            print(f"{i}. PID: {proc.pid}")
            print(f"   Статус: {proc.status()}")
            print(f"   Команда: {' '.join(proc.info['cmdline'])}")
            print(f"   Работает: {proc.is_running()}")
            print()
        except Exception as e:
            print(f"{i}. PID: {proc.pid} - Ошибка получения информации: {e}")
            print()

    # Предложение остановить процессы
    if processes:
        print("Для остановки всех процессов используйте:")
        print("python manage.py stop_bot --force")
        print()
        print("Или для запуска с автоматической остановкой:")
        print("python manage.py run_bot --kill-existing")


if __name__ == "__main__":
    main()
