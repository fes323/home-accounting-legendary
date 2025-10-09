# 🔄 Инструкция по обновлению сервера

## Проблема
На сервере отсутствуют настройки Mini App в `core/settings/production.py`, что вызывает ошибку:
```
'Settings' object has no attribute 'TELEGRAM_MINIAPP_DEBUG_MODE'
```

## Решение

### 1. Обновите файл настроек на сервере

Добавьте в файл `/var/www/wallet.my-bucket.ru/home-accounting-legendary/core/settings/production.py`:

```python
# После строки 137 (BOT_DESCRIPTION = "Личный помощник для учета финансов")
# Mini App settings
TELEGRAM_MINIAPP_URL = os.getenv('TELEGRAM_MINIAPP_URL', '')
TELEGRAM_MINIAPP_DEBUG_MODE = os.getenv('TELEGRAM_MINIAPP_DEBUG_MODE', 'False').lower() == 'true'
```

### 2. Исправьте настройки шаблонов

В том же файле найдите строку:
```python
'DIRS': [],
```

И замените на:
```python
'DIRS': [BASE_DIR / 'templates'],
```

### 3. Перезапустите сервисы

```bash
# Перезапуск Django приложения
sudo systemctl restart wallet-app

# Проверка статуса
sudo systemctl status wallet-app
```

### 4. Проверьте работу

1. Откройте корневой URL: `https://wallet.my-bucket.ru/`
2. Откройте Mini App: `https://wallet.my-bucket.ru/telegram/mini-app/`
3. Проверьте диагностику: `https://wallet.my-bucket.ru/telegram/mini-app/diagnostic/`

## Альтернативный способ (через git)

Если у вас настроен git на сервере:

```bash
# Перейдите в директорию проекта
cd /var/www/wallet.my-bucket.ru/home-accounting-legendary/

# Получите последние изменения
git pull origin main

# Перезапустите сервисы
sudo systemctl restart wallet-app
sudo systemctl restart wallet-bot
```

## Проверка конфигурации

### Проверьте переменные окружения
```bash
# Проверьте .env файл
cat /var/www/wallet.my-bucket.ru/.env | grep TELEGRAM_MINIAPP
```

Должно быть:
```env
TELEGRAM_MINIAPP_URL=https://wallet.my-bucket.ru/telegram/mini-app/
TELEGRAM_MINIAPP_DEBUG_MODE=False
```

### Проверьте логи
```bash
# Логи Django
sudo journalctl -u wallet-app -f

# Логи nginx
sudo tail -f /var/log/nginx/wallet.my-bucket.ru.error.log
```

## Если проблема не решается

1. Убедитесь, что файл `.env` содержит все необходимые переменные
2. Проверьте, что Django использует правильный файл настроек (`production.py`)
3. Убедитесь, что все файлы шаблонов скопированы на сервер
4. Проверьте права доступа к файлам

## Команды для диагностики

```bash
# Проверка конфигурации Django
cd /var/www/wallet.my-bucket.ru/home-accounting-legendary/
python manage.py check --settings=core.settings.production

# Проверка переменных окружения
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('TELEGRAM_MINIAPP_URL:', os.getenv('TELEGRAM_MINIAPP_URL'))
print('TELEGRAM_MINIAPP_DEBUG_MODE:', os.getenv('TELEGRAM_MINIAPP_DEBUG_MODE'))
"

# Проверка доступности
curl -I https://wallet.my-bucket.ru/
curl -I https://wallet.my-bucket.ru/telegram/mini-app/
```

После выполнения этих шагов Mini App должен работать корректно.
