# 🔧 Устранение неполадок Telegram Mini App

## Проблема: Ошибка 400 при открытии Mini App

### Симптомы
- При открытии Mini App из Telegram бота или браузера получаете ошибку 400
- Mini App не загружается
- В логах Django видны ошибки авторизации

### Причины
1. **Отсутствие Telegram данных** - Mini App требует данные от Telegram WebApp
2. **Неправильная конфигурация** - неверные настройки в `.env`
3. **Проблемы с доменом** - домен не в списке ALLOWED_HOSTS

## Решение

### 1. Включите режим отладки для тестирования

Добавьте в файл `.env`:
```env
TELEGRAM_MINIAPP_DEBUG_MODE=True
```

Это позволит тестировать Mini App из браузера без данных Telegram.

### 2. Проверьте конфигурацию

Убедитесь, что в `.env` правильно настроены:
```env
TELEGRAM_MINIAPP_URL=https://wallet.my-bucket.ru/telegram/mini-app/
TELEGRAM_MINIAPP_DEBUG_MODE=True
ALLOWED_HOSTS=wallet.my-bucket.ru,localhost,127.0.0.1
```

### 3. Используйте диагностическую страницу

Откройте в браузере:
```
https://wallet.my-bucket.ru/telegram/mini-app/diagnostic/
```

Эта страница покажет:
- Текущую конфигурацию
- Информацию о запросе
- Статус Telegram данных
- Рекомендации по исправлению

### 4. Проверьте логи Django

```bash
# Просмотр логов в реальном времени
tail -f logs/dev.log

# Или через journalctl
sudo journalctl -u wallet-app -f
```

### 5. Перезапустите сервисы

```bash
# Перезапуск Django приложения
sudo systemctl restart wallet-app

# Перезапуск Telegram бота
sudo systemctl restart wallet-bot

# Проверка статуса
sudo systemctl status wallet-app
sudo systemctl status wallet-bot
```

## Настройка для разных сред

### Разработка
```env
DEBUG=True
TELEGRAM_MINIAPP_DEBUG_MODE=True
TELEGRAM_MINIAPP_URL=http://localhost:8000/telegram/mini-app/
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Продакшен
```env
DEBUG=False
TELEGRAM_MINIAPP_DEBUG_MODE=False
TELEGRAM_MINIAPP_URL=https://wallet.my-bucket.ru/telegram/mini-app/
ALLOWED_HOSTS=wallet.my-bucket.ru
```

## Проверка работы Mini App

### 1. Из браузера (режим отладки)
```
https://wallet.my-bucket.ru/telegram/mini-app/diagnostic/
```

### 2. Из Telegram бота
1. Найдите бота в Telegram
2. Отправьте команду `/app`
3. Нажмите кнопку "📱 Открыть приложение"

### 3. Прямая ссылка (только с Telegram данными)
```
https://wallet.my-bucket.ru/telegram/mini-app/?tgWebAppData=...
```

## Частые ошибки

### Ошибка 400 "Unauthorized"
**Причина:** Mini App не получает данные от Telegram
**Решение:** Включите `TELEGRAM_MINIAPP_DEBUG_MODE=True` для тестирования

### Ошибка 500 "User not found"
**Причина:** Пользователь не найден в базе данных
**Решение:** Убедитесь, что пользователь зарегистрирован через бота

### Mini App не открывается из Telegram
**Причина:** Неправильный URL в настройках бота
**Решение:** Проверьте `TELEGRAM_MINIAPP_URL` в `.env`

### Ошибка "DisallowedHost"
**Причина:** Домен не в списке ALLOWED_HOSTS
**Решение:** Добавьте домен в `ALLOWED_HOSTS`

## Диагностические команды

### Проверка конфигурации Django
```bash
python manage.py check --deploy
```

### Проверка переменных окружения
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('TELEGRAM_MINIAPP_URL:', os.getenv('TELEGRAM_MINIAPP_URL'))"
```

### Проверка доступности Mini App
```bash
curl -I https://wallet.my-bucket.ru/telegram/mini-app/diagnostic/
```

### Проверка nginx
```bash
sudo nginx -t
sudo systemctl status nginx
```

## Логи для отладки

### Django логи
```bash
tail -f logs/dev.log | grep -i "mini\|telegram\|error"
```

### Nginx логи
```bash
sudo tail -f /var/log/nginx/wallet.my-bucket.ru.error.log
sudo tail -f /var/log/nginx/wallet.my-bucket.ru.access.log
```

### Systemd логи
```bash
sudo journalctl -u wallet-app -f
sudo journalctl -u wallet-bot -f
```

## Безопасность

⚠️ **Важно:** Режим отладки (`TELEGRAM_MINIAPP_DEBUG_MODE=True`) должен быть отключен в продакшене!

### Проверка безопасности
```bash
# Убедитесь, что режим отладки выключен
grep "TELEGRAM_MINIAPP_DEBUG_MODE" .env
# Должно быть: TELEGRAM_MINIAPP_DEBUG_MODE=False
```

## Поддержка

Если проблема не решается:
1. Проверьте диагностическую страницу
2. Изучите логи Django и nginx
3. Убедитесь в правильности конфигурации
4. Проверьте работу Telegram бота
5. Создайте Issue с подробным описанием проблемы
