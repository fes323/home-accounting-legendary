# Устранение неполадок Mini-App в Dev билде

## Проблема: Ошибка при переходе в mini-app с браузера

### Описание проблемы
При попытке открыть mini-app в браузере на dev билде возникает ошибка аутентификации или доступа.

### Причины и решения

#### 1. Неправильная настройка дебаг режима

**Проблема**: `TELEGRAM_MINIAPP_DEBUG_MODE=False` в .env файле

**Решение**: Установить `TELEGRAM_MINIAPP_DEBUG_MODE=True` в .env файле для dev билда

```env
# В .env файле для dev билда
TELEGRAM_MINIAPP_DEBUG_MODE=True
```

#### 2. Конфликт в настройках аутентификации

**Проблема**: Дублирование `AUTHENTICATION_BACKENDS` в `base.py`

**Решение**: Исправлено в коде - убрано дублирование и добавлен правильный порядок backends

#### 3. Middleware блокирует доступ

**Проблема**: `TelegramWebAppAuthMiddleware` блокирует не-Telegram запросы

**Решение**: Добавлена поддержка дебаг режима в middleware

### Проверка конфигурации

#### 1. Проверить настройки в dev.py
```python
# Должно быть включено для dev билда
TELEGRAM_MINIAPP_DEBUG_MODE = True
```

#### 2. Проверить .env файл
```env
TELEGRAM_MINIAPP_DEBUG_MODE=True
DEBUG=True
DJANGO_SETTINGS_MODULE=core.settings.dev
```

#### 3. Проверить middleware
Middleware должен автоматически создавать тестового пользователя в дебаг режиме.

### Тестирование

#### 1. Диагностическая страница
Откройте в браузере: `http://localhost:8000/telegram/mini-app/diagnostic/`

Эта страница покажет:
- Текущие настройки конфигурации
- Статус дебаг режима
- Информацию о запросе
- Рекомендации по исправлению

#### 2. Главная страница mini-app
Откройте в браузере: `http://localhost:8000/telegram/mini-app/`

В дебаг режиме должна автоматически создаться сессия с тестовым пользователем.

### Логирование

Проверьте логи в `logs/dev.log` на наличие сообщений:
```
DEBUG mode: authenticated test user test_user
```

### Частые ошибки

#### 1. "Unauthorized" ошибка
- Проверьте `TELEGRAM_MINIAPP_DEBUG_MODE=True`
- Убедитесь, что используете dev настройки

#### 2. "User not found" ошибка
- Проверьте, что middleware правильно обрабатывает дебаг режим
- Убедитесь, что тестовый пользователь создается

#### 3. Редирект на страницу авторизации
- Проверьте настройки middleware
- Убедитесь, что путь не исключен из обработки

#### 4. "'WSGIRequest' object has no attribute 'user'" ошибка
- **Причина**: Middleware выполняется до `AuthenticationMiddleware`
- **Решение**: Убедитесь, что `TelegramWebAppAuthMiddleware` идет после `AuthenticationMiddleware` в `MIDDLEWARE` настройках
- **Проверка**: В `core/settings/base.py` порядок должен быть:
  ```python
  MIDDLEWARE = [
      'django.middleware.security.SecurityMiddleware',
      'django.contrib.sessions.middleware.SessionMiddleware',
      'django.middleware.common.CommonMiddleware',
      'telegram_bot.middleware_telegram.TelegramWebAppMiddleware',
      'django.contrib.auth.middleware.AuthenticationMiddleware',  # ДОЛЖЕН БЫТЬ ДО
      'telegram_bot.middleware_telegram_auth.TelegramWebAppAuthMiddleware',  # НАШЕГО MIDDLEWARE
      'django.contrib.messages.middleware.MessageMiddleware',
      'telegram_bot.middleware_telegram.TelegramWebAppSecurityMiddleware',
  ]
  ```

### Восстановление после ошибок

1. Остановите сервер
2. Проверьте настройки в .env
3. Перезапустите сервер
4. Очистите кеш браузера
5. Попробуйте снова

### Контакты

При возникновении проблем проверьте:
1. Логи в `logs/dev.log`
2. Диагностическую страницу
3. Настройки в `core/settings/dev.py`
4. Переменные окружения в .env
