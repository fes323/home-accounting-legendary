# Настройка Telegram Mini App

Инструкция по настройке и развертыванию Telegram Mini App для финансового учета.

## Структура проекта

```
backend/
├── accounting/          # Django app для учета
├── users/              # Django app для пользователей
├── telegram_bot/       # Telegram Bot
└── core/               # Основные настройки Django

frontend/               # React Mini App
├── src/
│   ├── components/     # React компоненты
│   ├── pages/          # Страницы приложения
│   ├── services/       # API сервисы
│   └── contexts/       # React контексты
└── public/
```

## Установка и настройка

### 1. Backend (Django)

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Выполните миграции:
```bash
python manage.py migrate
```

3. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

4. Запустите сервер разработки:
```bash
python manage.py runserver
```

### 2. Frontend (React)

1. Перейдите в папку frontend:
```bash
cd frontend
```

2. Установите зависимости:
```bash
npm install
```

3. Скопируйте файл конфигурации:
```bash
cp env.example .env
```

4. Настройте переменные окружения в `.env`:
```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_TELEGRAM_BOT_USERNAME=your_bot_username
```

5. Запустите приложение:
```bash
npm start
```

## Настройка Telegram Bot

### 1. Создание бота

1. Найдите @BotFather в Telegram
2. Создайте нового бота командой `/newbot`
3. Получите токен бота
4. Добавьте токен в настройки Django

### 2. Настройка WebApp

1. Установите WebApp URL в боте:
```
/setmenubutton
```

2. Укажите URL вашего приложения (например, `https://your-domain.com`)

### 3. Обновление URL в коде

В файле `telegram_bot/handlers/webapp_handlers.py` замените:
```python
web_app_url = "https://your-domain.com"  # Замените на ваш URL
```

## API Endpoints

### Аутентификация
- `POST /api/user/auth/telegram/` - Авторизация через Telegram

### Транзакции
- `GET /api/transactions/` - Список транзакций
- `POST /api/transactions/` - Создание транзакции
- `PUT /api/transactions/{id}/` - Обновление транзакции
- `DELETE /api/transactions/{id}/` - Удаление транзакции

### Категории
- `GET /api/categories/` - Список категорий
- `POST /api/categories/` - Создание категории
- `PUT /api/categories/{id}/` - Обновление категории
- `DELETE /api/categories/{id}/` - Удаление категории

### Кошельки
- `GET /api/wallets/` - Список кошельков

## Развертывание

### 1. Подготовка к продакшену

1. Соберите React приложение:
```bash
cd frontend
npm run build
```

2. Настройте веб-сервер (nginx/apache) для обслуживания статических файлов

3. Настройте Django для продакшена:
```bash
python manage.py collectstatic
```

### 2. Настройка домена

1. Получите SSL сертификат для вашего домена
2. Настройте веб-сервер для обслуживания React приложения
3. Обновите URL в Telegram Bot

### 3. Настройка переменных окружения

Создайте файл `.env` с настройками:
```
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
TELEGRAM_BOT_TOKEN=your-bot-token
ALLOWED_HOSTS=your-domain.com
```

## Функционал Mini App

### 1. Просмотр транзакций
- История всех транзакций
- Фильтрация по типу (доход/расход)
- Фильтрация по дате
- Статистика по доходам и расходам

### 2. Управление транзакциями
- Добавление новых транзакций
- Редактирование существующих
- Удаление транзакций
- Выбор категории и кошелька

### 3. Управление категориями
- Дерево категорий
- Создание новых категорий
- Редактирование категорий
- Удаление категорий
- Подкатегории

### 4. Авторизация
- Автоматическая авторизация через Telegram
- Безопасная передача данных
- Сохранение сессии

## Безопасность

1. **Проверка подписи Telegram**: Реализуйте проверку подписи в `users/serializers.py`
2. **CORS**: Настройте CORS для вашего домена
3. **HTTPS**: Используйте только HTTPS в продакшене
4. **Валидация данных**: Все данные проверяются на сервере

## Отладка

### 1. Логи Django
```bash
tail -f logs/dev.log
```

### 2. Логи React
Откройте Developer Tools в браузере

### 3. Проверка API
```bash
curl -X GET http://localhost:8000/api/transactions/ \
  -H "Authorization: Bearer your-token"
```

## Поддержка

При возникновении проблем:
1. Проверьте логи
2. Убедитесь в правильности настроек
3. Проверьте доступность API
4. Проверьте настройки Telegram Bot
