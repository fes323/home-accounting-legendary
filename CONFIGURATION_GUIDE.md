# Конфигурация проекта Home Accounting Legendary

## Обзор

Проект использует единую систему конфигурации на основе переменных окружения через файлы `.env`. Все настройки централизованы и легко настраиваются для разных окружений.

## Структура файлов

### Основные файлы конфигурации

- **`env.example`** - Пример конфигурации для Git (безопасен для коммита)
- **`production.env.template`** - Шаблон для продакшена (скопировать как `.env`)
- **`.env`** - Основной файл конфигурации (НЕ коммитить в Git!)

### Файлы настроек Django

- **`core/settings/base.py`** - Базовые настройки (общие для всех окружений)
- **`core/settings/dev.py`** - Настройки для разработки
- **`core/settings/production.py`** - Настройки для продакшена
- **`telegram_bot/config.py`** - Конфигурация Telegram бота

## Переменные окружения

### Django Settings
```bash
DJANGO_SETTINGS_MODULE=core.settings.dev  # или production
SECRET_KEY=your-secret-key-here
DEBUG=True  # или False для продакшена
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Configuration
```bash
DB_NAME=HAL_development
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=127.0.0.1
DB_PORT=5432
```

### Telegram Bot Configuration
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_WEBHOOK_URL=https://yourdomain.com
TELEGRAM_WEBHOOK_SECRET=your-webhook-secret-token
BOT_USERNAME=your_bot_username
```

### Security Settings (Production)
```bash
SECURE_SSL_REDIRECT=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
```

### Logging Configuration
```bash
LOG_FILE_PATH=/var/log/django/wallet_app.log
LOG_LEVEL=INFO
```

### Static Files Configuration
```bash
STATIC_ROOT=/var/www/wallet/static/
MEDIA_ROOT=/var/www/wallet/media/
```

### Redis Configuration (Optional)
```bash
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

### Email Configuration (Optional)
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### Celery Configuration (Optional)
```bash
CELERY_BROKER_URL=redis://127.0.0.1:6379/1
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/1
```

## Настройка для разработки

1. Скопируйте `env.example` как `.env`:
   ```bash
   cp env.example .env
   ```

2. Отредактируйте `.env` файл с вашими настройками:
   ```bash
   # Установите токен бота
   TELEGRAM_BOT_TOKEN=your_actual_bot_token
   
   # Настройте базу данных
   DB_PASSWORD=your_db_password
   
   # И так далее...
   ```

3. Убедитесь, что Django использует правильные настройки:
   ```bash
   export DJANGO_SETTINGS_MODULE=core.settings.dev
   ```

## Настройка для продакшена

1. Скопируйте `production.env.template` как `.env`:
   ```bash
   cp production.env.template .env
   ```

2. Отредактируйте `.env` файл с продакшен настройками:
   ```bash
   # Установите продакшен значения
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   
   # Настройте базу данных
   DB_NAME=HAL_production
   DB_PASSWORD=your-production-db-password
   
   # И так далее...
   ```

3. Убедитесь, что Django использует продакшен настройки:
   ```bash
   export DJANGO_SETTINGS_MODULE=core.settings.production
   ```

## Безопасность

### Важные правила:

1. **НИКОГДА не коммитьте файл `.env` в Git!**
2. Используйте `env.example` для примеров конфигурации
3. Генерируйте уникальные секретные ключи для каждого окружения
4. Используйте сильные пароли для базы данных
5. Ограничьте доступ к файлу `.env` на сервере (chmod 600)

### Добавление в .gitignore:
```
.env
*.env
!.env.example
```

## Проверка конфигурации

Telegram бот автоматически проверяет корректность конфигурации при запуске. Если есть ошибки, они будут выведены в консоль.

## Миграция со старой системы

Если у вас была старая система конфигурации:

1. Скопируйте значения из `main.ini` и `production.env` в новый `.env`
2. Удалите старые файлы конфигурации
3. Обновите все импорты в коде

## Troubleshooting

### Проблема: Переменные окружения не загружаются
**Решение:** Убедитесь, что файл `.env` находится в корне проекта и содержит правильные переменные.

### Проблема: Бот не запускается
**Решение:** Проверьте, что `TELEGRAM_BOT_TOKEN` и `BOT_USERNAME` установлены в `.env`.

### Проблема: База данных не подключается
**Решение:** Проверьте настройки `DB_*` в `.env` файле.

### Проблема: Статические файлы не загружаются
**Решение:** Проверьте настройки `STATIC_ROOT` и `MEDIA_ROOT` в `.env`.
