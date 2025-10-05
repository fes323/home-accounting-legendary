#!/usr/bin/env python
"""
Тестовый скрипт для проверки логики команды run_bot
"""
import os
import sys

import psutil


def find_bot_processes():
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


def test_logic():
    print("🔍 Тестирование логики команды run_bot")
    print("=" * 50)

    # Симулируем разные сценарии
    scenarios = [
        {"kill_existing": False, "force": False, "name": "Обычный запуск"},
        {"kill_existing": True, "force": False, "name": "С --kill-existing"},
        {"kill_existing": False, "force": True, "name": "С --force"},
    ]

    processes = find_bot_processes()
    print(f"Найдено активных процессов бота: {len(processes)}")

    for scenario in scenarios:
        print(f"\n📋 Сценарий: {scenario['name']}")
        print(f"   kill_existing: {scenario['kill_existing']}")
        print(f"   force: {scenario['force']}")

        # Логика из исправленной команды
        if scenario['kill_existing']:
            print("   ✅ Остановка существующих экземпляров...")
            # Здесь была бы остановка процессов
        elif not scenario['kill_existing']:
            if processes and not scenario['force']:
                print("   ❌ Найдены активные процессы, запуск заблокирован")
            else:
                print("   ✅ Запуск разрешен")
        else:
            print("   ✅ Запуск разрешен")


if __name__ == "__main__":
    test_logic()
