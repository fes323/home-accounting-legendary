# Telegram Mini App - Финансовый учет

Минималистичное React приложение для управления финансами через Telegram Bot.

## Функционал

- 📊 Просмотр и редактирование транзакций с историей
- 📁 Управление категориями в виде дерева
- 🔐 Авторизация через Telegram
- 📱 Адаптивный дизайн для мобильных устройств

## Установка

1. Установите зависимости:
```bash
npm install
```

2. Скопируйте файл конфигурации:
```bash
cp env.example .env
```

3. Настройте переменные окружения в `.env`:
```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_TELEGRAM_BOT_USERNAME=your_bot_username
```

## Запуск

```bash
npm start
```

Приложение будет доступно по адресу `http://localhost:3000`

## Сборка для продакшена

```bash
npm run build
```

## Интеграция с Telegram Bot

Для интеграции с Telegram Bot добавьте кнопку в бота:

```python
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text="📱 Открыть приложение",
        web_app=WebAppInfo(url="https://your-domain.com")
    )]
])
```

## API Endpoints

- `GET /api/transactions/` - Список транзакций
- `POST /api/transactions/` - Создание транзакции
- `PUT /api/transactions/{id}/` - Обновление транзакции
- `DELETE /api/transactions/{id}/` - Удаление транзакции
- `GET /api/categories/` - Список категорий
- `POST /api/categories/` - Создание категории
- `PUT /api/categories/{id}/` - Обновление категории
- `DELETE /api/categories/{id}/` - Удаление категории
- `GET /api/wallets/` - Список кошельков
- `POST /api/user/auth/telegram/` - Авторизация через Telegram

## Технологии

- React 18
- React Router
- React Hook Form
- Axios
- Telegram WebApp SDK
- Lucide React (иконки)
- date-fns (работа с датами)
