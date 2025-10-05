#!/usr/bin/env python
"""
Скрипт для быстрого решения проблемы конфликта Telegram бота
"""
import os
import subprocess
import sys
import time


def main():
    print("🔧 Утилита для решения конфликта Telegram бота")
    print("=" * 50)

    # Проверяем, находимся ли мы в правильной директории
    if not os.path.exists('manage.py'):
        print("❌ Ошибка: manage.py не найден. Запустите скрипт из корневой директории проекта.")
        return

    print("1. Остановка всех экземпляров бота...")
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'stop_bot', '--force'
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("✅ Все экземпляры бота остановлены")
        else:
            print(f"⚠️ Предупреждение: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⚠️ Таймаут при остановке бота")
    except Exception as e:
        print(f"⚠️ Ошибка при остановке: {e}")

    print("\n2. Ожидание завершения процессов...")
    time.sleep(2)

    print("3. Запуск бота...")
    try:
        subprocess.run([
            sys.executable, 'manage.py', 'run_bot'
        ])
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")


if __name__ == "__main__":
    main()
