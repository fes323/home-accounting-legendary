# 🔧 Исправление авторизации через Telegram на продакшене

## 🎯 Проблема
Авторизация через Telegram WebApp не работает на продакшене. Остается тестовый пользователь.

## 🔍 Выявленные проблемы

### 1. Отсутствуют настройки Telegram Mini App в production.env.template
**Проблема:** В файле `production.env.template` отсутствовали настройки `TELEGRAM_MINIAPP_URL` и `TELEGRAM_MINIAPP_DEBUG_MODE`.

**Решение:** Добавлены недостающие настройки в шаблон.

### 2. Блокировка iframe настройками безопасности
**Проблема:** `X_FRAME_OPTIONS = 'DENY'` блокирует встраивание Telegram WebApp в iframe.

**Решение:** Изменено на `X_FRAME_OPTIONS = 'SAMEORIGIN'` и создан специальный middleware.

### 3. CSRF защита блокирует Telegram запросы
**Проблема:** Django CSRF middleware блокирует запросы от Telegram WebApp.

**Решение:** Создан кастомный middleware для обработки Telegram запросов.

## ✅ Внесенные исправления

### 1. Обновлен `production.env.template`
```env
# URL Telegram Mini App (полный URL с протоколом)
TELEGRAM_MINIAPP_URL=https://wallet.my-bucket.ru/telegram/mini-app/

# Разрешить доступ к Mini App без Telegram данных (для отладки)
TELEGRAM_MINIAPP_DEBUG_MODE=False
```

### 2. Создан `telegram_bot/middleware_telegram.py`
- `TelegramWebAppMiddleware` - отключает CSRF для Telegram запросов
- `TelegramWebAppSecurityMiddleware` - настраивает заголовки безопасности для Telegram WebApp

### 3. Обновлены настройки Django
- Изменен `X_FRAME_OPTIONS` на `SAMEORIGIN`
- Добавлены кастомные middleware в `MIDDLEWARE`

### 4. Создан скрипт `update_production_auth.py`
Автоматизирует обновление настроек на сервере.

## 🚀 Инструкция по исправлению на сервере

### Шаг 1: Обновите код на сервере
```bash
# Перейдите в директорию проекта
cd /var/www/wallet.my-bucket.ru/home-accounting-legendary

# Получите последние изменения
git pull origin main

# Активируйте виртуальное окружение
source venv/bin/activate
```

### Шаг 2: Обновите настройки
```bash
# Запустите скрипт обновления
python update_production_auth.py
```

Или вручную:
```bash
# Создайте резервную копию
cp .env .env.backup

# Обновите .env из шаблона
cp production.env.template .env

# Проверьте, что все настройки присутствуют
grep -E "TELEGRAM_MINIAPP_URL|TELEGRAM_MINIAPP_DEBUG_MODE" .env
```

### Шаг 3: Перезапустите сервисы
```bash
# Перезапустите Django приложение
sudo systemctl restart wallet-app

# Перезапустите Telegram бота
sudo systemctl restart wallet-bot

# Проверьте статус сервисов
sudo systemctl status wallet-app
sudo systemctl status wallet-bot
```

### Шаг 4: Проверьте логи
```bash
# Просмотр логов Django в реальном времени
sudo journalctl -u wallet-app -f

# Просмотр логов бота
sudo journalctl -u wallet-bot -f
```

### Шаг 5: Протестируйте исправления
1. **Откройте диагностическую страницу:**
   ```
   https://wallet.my-bucket.ru/telegram/mini-app/diagnostic/
   ```

2. **Проверьте Mini App из Telegram бота:**
   - Откройте бота в Telegram
   - Нажмите кнопку "📱 Веб-приложение"
   - Проверьте, что авторизация работает

## 🔧 Отладка проблем

### Если авторизация все еще не работает:

#### 1. Включите режим отладки
```bash
# Отредактируйте .env файл
nano .env

# Измените на:
TELEGRAM_MINIAPP_DEBUG_MODE=True

# Перезапустите сервис
sudo systemctl restart wallet-app
```

#### 2. Проверьте настройки бота в BotFather
- Убедитесь, что Mini App URL правильно настроен
- URL должен быть: `https://wallet.my-bucket.ru/telegram/mini-app/`

#### 3. Проверьте сетевые настройки
```bash
# Проверьте доступность домена
curl -I https://wallet.my-bucket.ru/telegram/mini-app/diagnostic/

# Проверьте SSL сертификат
openssl s_client -connect wallet.my-bucket.ru:443 -servername wallet.my-bucket.ru
```

#### 4. Проверьте логи на ошибки
```bash
# Ищите ошибки авторизации
sudo journalctl -u wallet-app | grep -i "telegram\|auth\|error"

# Ищите ошибки CSRF
sudo journalctl -u wallet-app | grep -i "csrf\|forbidden"
```

## 🎯 Ожидаемый результат

После исправлений:

1. ✅ **Telegram WebApp открывается без ошибок** - нет блокировки iframe
2. ✅ **Авторизация работает корректно** - пользователи создаются автоматически
3. ✅ **Нет ошибок CSRF** - middleware правильно обрабатывает Telegram запросы
4. ✅ **Диагностическая страница показывает корректные данные** - все настройки присутствуют
5. ✅ **Логи не содержат ошибок авторизации** - все работает стабильно

## 📞 Поддержка

Если проблема не решена после всех шагов:

1. **Проверьте диагностическую страницу** - она покажет все параметры
2. **Проверьте логи Django** - ищите сообщения об ошибках
3. **Убедитесь, что домен доступен** - проверьте DNS и SSL
4. **Проверьте настройки бота** - URL Mini App должен быть правильным

## 🔄 Откат изменений

Если что-то пошло не так:

```bash
# Восстановите резервную копию .env
cp .env.backup .env

# Перезапустите сервисы
sudo systemctl restart wallet-app
sudo systemctl restart wallet-bot
```
