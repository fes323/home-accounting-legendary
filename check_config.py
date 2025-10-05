#!/usr/bin/env python
"""
Скрипт для проверки конфигурации проекта
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def check_env_file():
    """Проверка наличия и корректности .env файла"""
    print("🔍 Проверка файла .env...")

    env_path = Path('.env')
    if not env_path.exists():
        print("❌ Файл .env не найден!")
        print("   Скопируйте env.example как .env и заполните значениями")
        return False

    print("✅ Файл .env найден")

    # Загружаем переменные
    load_dotenv(env_path)

    return True


def check_required_variables():
    """Проверка обязательных переменных"""
    print("\n🔍 Проверка обязательных переменных...")

    required_vars = [
        'SECRET_KEY',
        'TELEGRAM_BOT_TOKEN',
        'BOT_USERNAME',
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD',
        'DB_HOST',
        'DB_PORT',
    ]

    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            print(
                f"✅ {var}: {'*' * len(value) if 'PASSWORD' in var or 'SECRET' in var else value}")

    if missing_vars:
        print(f"\n❌ Отсутствуют переменные: {', '.join(missing_vars)}")
        return False

    print("\n✅ Все обязательные переменные установлены")
    return True


def check_django_settings():
    """Проверка настроек Django"""
    print("\n🔍 Проверка настроек Django...")

    settings_module = os.getenv('DJANGO_SETTINGS_MODULE', 'core.settings.dev')
    print(f"📋 Настройки Django: {settings_module}")

    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    print(f"🐛 Режим отладки: {debug}")

    allowed_hosts = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1')
    print(f"🌐 Разрешенные хосты: {allowed_hosts}")

    return True


def check_database_config():
    """Проверка конфигурации базы данных"""
    print("\n🔍 Проверка конфигурации базы данных...")

    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')

    print(f"🗄️ База данных: {db_name}")
    print(f"👤 Пользователь: {db_user}")
    print(f"🌐 Хост: {db_host}:{db_port}")

    return True


def check_telegram_config():
    """Проверка конфигурации Telegram бота"""
    print("\n🔍 Проверка конфигурации Telegram бота...")

    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    bot_username = os.getenv('BOT_USERNAME')
    webhook_url = os.getenv('TELEGRAM_WEBHOOK_URL')

    if bot_token:
        print(f"🤖 Токен бота: {bot_token[:10]}...")
    else:
        print("❌ Токен бота не установлен")
        return False

    if bot_username:
        print(f"👤 Имя пользователя бота: @{bot_username}")
    else:
        print("❌ Имя пользователя бота не установлено")
        return False

    if webhook_url:
        print(f"🔗 Webhook URL: {webhook_url}")
    else:
        print("⚠️ Webhook URL не установлен (будет использоваться polling)")

    return True


def check_security_settings():
    """Проверка настроек безопасности"""
    print("\n🔍 Проверка настроек безопасности...")

    debug = os.getenv('DEBUG', 'True').lower() == 'true'

    if debug:
        print("⚠️ Режим отладки включен - настройки безопасности отключены")
        return True

    ssl_redirect = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
    csrf_secure = os.getenv('CSRF_COOKIE_SECURE', 'False').lower() == 'true'
    session_secure = os.getenv(
        'SESSION_COOKIE_SECURE', 'False').lower() == 'true'

    print(f"🔒 SSL редирект: {ssl_redirect}")
    print(f"🍪 CSRF cookie secure: {csrf_secure}")
    print(f"🍪 Session cookie secure: {session_secure}")

    if not ssl_redirect:
        print("⚠️ SSL редирект отключен")

    return True


def main():
    """Основная функция проверки"""
    print("🔧 Проверка конфигурации Home Accounting Legendary")
    print("=" * 60)

    checks = [
        check_env_file,
        check_required_variables,
        check_django_settings,
        check_database_config,
        check_telegram_config,
        check_security_settings,
    ]

    all_passed = True
    for check in checks:
        try:
            if not check():
                all_passed = False
        except Exception as e:
            print(f"❌ Ошибка при проверке: {e}")
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ Все проверки пройдены успешно!")
        print("🚀 Проект готов к запуску")
    else:
        print("❌ Обнаружены проблемы в конфигурации")
        print("📖 См. CONFIGURATION_GUIDE.md для помощи")
        sys.exit(1)


if __name__ == "__main__":
    main()
