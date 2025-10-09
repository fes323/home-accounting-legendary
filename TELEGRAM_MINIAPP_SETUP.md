# Настройка Telegram Mini App

Инструкция по настройке и развертыванию Telegram Mini App для финансового учета.

## Структура проекта

```
backend/
├── accounting/          # Django app для учета
├── users/              # Django app для пользователей
├── telegram_bot/       # Telegram Bot и Mini App
│   ├── mini_app_views.py # Django views для Mini App
│   └── templates/      # HTML шаблоны
│       └── telegram_bot/
│           ├── base.html        # Базовый шаблон
│           ├── dashboard.html   # Главная страница
│           ├── transactions/    # Шаблоны транзакций
│           ├── wallets/         # Шаблоны кошельков
│           └── categories/      # Шаблоны категорий
└── core/               # Основные настройки Django
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

### 2. Mini App (Django Templates)

Mini App теперь встроен в Django и использует HTML шаблоны с Bootstrap для responsive дизайна.

1. Убедитесь, что Django сервер запущен:
```bash
python manage.py runserver
```

2. Mini App доступен по адресу:
```
http://localhost:8000/telegram/mini-app/
```

3. Для работы в Telegram WebApp добавьте параметры:
```
http://localhost:8000/telegram/mini-app/?tgWebAppData=...
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

### 3. Настройка URL в переменных окружения

Добавьте в файл `.env`:
```env
TELEGRAM_MINIAPP_URL=https://your-domain.com/telegram/mini-app/
```

URL автоматически будет использоваться в коде через настройки Django.

## Mini App Endpoints

### Основные страницы
- `GET /telegram/mini-app/` - Главная страница (дашборд)
- `GET /telegram/mini-app/transactions/` - Список транзакций
- `GET /telegram/mini-app/transactions/create/` - Создание транзакции
- `GET /telegram/mini-app/transactions/{id}/edit/` - Редактирование транзакции
- `POST /telegram/mini-app/transactions/{id}/delete/` - Удаление транзакции

### Кошельки
- `GET /telegram/mini-app/wallets/` - Список кошельков
- `GET /telegram/mini-app/wallets/create/` - Создание кошелька
- `GET /telegram/mini-app/wallets/{id}/edit/` - Редактирование кошелька
- `POST /telegram/mini-app/wallets/{id}/delete/` - Удаление кошелька

### Категории
- `GET /telegram/mini-app/categories/` - Список категорий
- `GET /telegram/mini-app/categories/create/` - Создание категории
- `GET /telegram/mini-app/categories/{id}/edit/` - Редактирование категории
- `POST /telegram/mini-app/categories/{id}/delete/` - Удаление категории

## API Endpoints (для внешних приложений)

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

1. Настройте Django для продакшена:
```bash
python manage.py collectstatic
python manage.py migrate
```

2. Настройте веб-сервер (nginx/apache) для обслуживания Django приложения

3. Убедитесь, что все статические файлы доступны

### 2. Настройка домена

1. Получите SSL сертификат для вашего домена
2. Настройте веб-сервер для обслуживания Django приложения
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

### 1. Главная страница (Дашборд)
- Статистика доходов и расходов за месяц
- Последние транзакции
- Быстрые действия (добавить доход/расход)
- Обзор кошельков
- Адаптивный дизайн для мобильных устройств

### 2. Управление транзакциями
- Просмотр истории всех транзакций
- Фильтрация по типу, кошельку, категории, дате
- Добавление новых транзакций
- Редактирование существующих
- Удаление транзакций
- Пагинация для больших списков

### 3. Управление кошельками
- Просмотр всех кошельков
- Создание новых кошельков
- Редактирование кошельков
- Удаление кошельков (с проверкой транзакций)
- Статистика по кошелькам

### 4. Управление категориями
- Просмотр всех категорий
- Создание новых категорий
- Редактирование категорий
- Удаление категорий (с проверкой транзакций и подкатегорий)
- Иерархическая структура категорий

### 5. Авторизация и безопасность
- Автоматическая авторизация через Telegram
- Проверка подписи Telegram WebApp
- Изоляция данных по пользователям
- Responsive дизайн для всех устройств

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

### 2. Отладка Mini App
Откройте Developer Tools в браузере для проверки JavaScript

### 3. Проверка Mini App
```bash
# Проверка доступности главной страницы
curl -X GET http://localhost:8000/telegram/mini-app/

# Проверка API (для внешних приложений)
curl -X GET http://localhost:8000/api/transactions/ \
  -H "Authorization: Bearer your-token"
```

### 4. Проверка шаблонов
```bash
python manage.py check --deploy
```

## Поддержка

При возникновении проблем:
1. Проверьте логи Django
2. Убедитесь в правильности настроек
3. Проверьте доступность Mini App
4. Проверьте настройки Telegram Bot
5. Убедитесь, что все шаблоны загружаются корректно
6. Проверьте работу JavaScript в браузере
