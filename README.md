# 🏠 Home Accounting Legendary

**Легендарная система домашнего учета с Telegram ботом и Django Mini App**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.1.2-green.svg)](https://djangoproject.com)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://telegram.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)](https://postgresql.org)

## 📋 Описание проекта

Home Accounting Legendary — это современная система управления личными финансами, построенная на Django с интеграцией Telegram бота и Django Mini App. Проект позволяет пользователям вести учет доходов и расходов через удобный интерфейс мессенджера и веб-приложение, управлять несколькими кошельками и получать детальную аналитику своих финансов.

## ✨ Основные возможности

### 💰 Финансовый учет
- 📊 Учет доходов и расходов
- 💳 Управление несколькими кошельками
- 📂 Иерархические категории транзакций
- 💱 Поддержка разных валют
- 📈 Статистика и аналитика

### 👨‍👩‍👧‍👦 Семейный функционал
- 🔐 Семейный доступ к кошелькам
- 👥 Совместное управление финансами
- 📱 Индивидуальные настройки для каждого пользователя

### 🤖 Telegram интеграция
- 📱 Удобный интерфейс в Telegram
- ⚡ Быстрые команды для операций
- 🔔 Уведомления о транзакциях
- 📊 Мгновенная статистика
- 🌐 Django Mini App для расширенного функционала

### 🌐 Веб-приложение (Django Mini App)
- 📱 Responsive интерфейс для Telegram WebApp
- 📊 Просмотр и редактирование транзакций с историей
- 📁 Управление категориями в виде дерева
- 🔐 Авторизация через Telegram
- 📈 Детальная статистика доходов и расходов
- 💳 Управление кошельками
- 📱 Адаптивный дизайн для мобильных устройств

## 🚀 Быстрый старт

### Предварительные требования
- Python 3.11+
- PostgreSQL 12+
- Telegram Bot Token (от @BotFather)

### Установка

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/yourusername/HomeAccountingLegendary.git
   cd HomeAccountingLegendary/backend
   ```

2. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте переменные окружения:**
   ```bash
   cp env.example .env
   # Отредактируйте .env файл с вашими настройками
   ```

4. **Настройте базу данных:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Запустите Django сервер:**
   ```bash
   python manage.py runserver
   ```

6. **Запустите Telegram бота:**
   ```bash
   python manage.py run_bot
   ```

## 📚 Документация

### Основные руководства
- 📖 **[Быстрый старт](README/QUICK_START.md)** - Пошаговая настройка проекта
- ⚙️ **[Руководство по конфигурации](README/CONFIGURATION_GUIDE.md)** - Подробная настройка системы
- 🤖 **[Настройка Telegram бота](README/TELEGRAM_BOT_SETUP.md)** - Создание и настройка бота
- 🌐 **[Настройка Telegram Mini App](TELEGRAM_MINIAPP_SETUP.md)** - Развертывание Django Mini App

### Дополнительные материалы
- 🔧 **[Настройка переменных окружения](README/DOTENV_SETUP.md)** - Работа с .env файлами
- 🚨 **[Решение конфликтов бота](README/BOT_CONFLICT_SOLUTION.md)** - Устранение проблем
- 🔄 **[Исправление бота](README/RUN_BOT_FIX.md)** - Диагностика и исправление
- 🔧 **[Устранение неполадок Mini App](README/MINIAPP_TROUBLESHOOTING.md)** - Решение проблем с Mini App

## 🏗️ Архитектура проекта

```
backend/
├── accounting/          # Модуль учета финансов
│   ├── models/         # Модели данных
│   ├── views/          # API представления
│   ├── serializers.py  # Сериализаторы DRF
│   └── management/     # Команды управления
├── telegram_bot/       # Telegram бот и Mini App
│   ├── bot.py          # Основной файл бота
│   ├── handlers/       # Обработчики команд
│   ├── keyboards.py    # Клавиатуры интерфейса
│   ├── middleware.py   # Middleware
│   ├── mini_app_views.py # Django views для Mini App
│   └── templates/      # HTML шаблоны для Mini App
│       └── telegram_bot/
│           ├── base.html        # Базовый шаблон
│           ├── dashboard.html   # Главная страница
│           ├── transactions/    # Шаблоны транзакций
│           ├── wallets/         # Шаблоны кошельков
│           └── categories/      # Шаблоны категорий
├── users/              # Модуль пользователей
│   ├── models/         # Модели пользователей
│   ├── views/          # API пользователей
│   └── serializers.py  # Сериализаторы
├── core/               # Основные настройки Django
│   └── settings/       # Конфигурация для разных сред
└── README/             # Документация проекта
```

## 🛠️ Технологический стек

### Backend
- **Django 5.1.2** - Веб-фреймворк
- **Django REST Framework** - API
- **PostgreSQL** - База данных
- **Django MPTT** - Иерархические структуры

### Frontend (Django Mini App)
- **Django Templates** - HTML шаблоны
- **Bootstrap 5.3** - CSS фреймворк для responsive дизайна
- **Bootstrap Icons** - Иконки
- **Telegram WebApp SDK** - Интеграция с Telegram
- **JavaScript** - Интерактивность

### Telegram Bot
- **aiogram 3.4.1** - Современная библиотека для ботов
- **aiohttp** - Асинхронные HTTP запросы
- **cryptg** - Быстрое шифрование

### Дополнительные библиотеки
- **pandas** - Обработка данных
- **numpy** - Численные вычисления
- **python-dotenv** - Управление переменными окружения
- **psutil** - Системная информация

## 🔧 Команды управления

### Django команды
```bash
# Запуск сервера разработки
python manage.py runserver

# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Сбор статических файлов
python manage.py collectstatic
```

### Команды бота
```bash
# Запуск бота (polling)
python manage.py run_bot

# Запуск бота (webhook)
python manage.py run_bot --webhook

# Остановка бота
python manage.py stop_bot
```

### Команды Mini App
```bash
# Запуск Django сервера для Mini App
python manage.py runserver

# Сборка статических файлов
python manage.py collectstatic

# Проверка шаблонов
python manage.py check --deploy
```

## 📱 Telegram команды

- `/start` - Начать работу с ботом
- `/balance` - Показать баланс кошельков
- `/income` - Добавить доход
- `/expense` - Добавить расход
- `/wallets` - Управление кошельками
- `/categories` - Управление категориями
- `/app` - Открыть веб-приложение
- `/help` - Справка по командам

## 🔒 Безопасность

- 🔐 Аутентификация через Telegram
- 🛡️ Валидация всех входящих данных
- 🔒 Изоляция данных по пользователям
- 🚫 Защита от SQL-инъекций
- 🔑 Безопасное хранение токенов

## 🚀 Развертывание

### Разработка
```bash
export DJANGO_SETTINGS_MODULE=core.settings.dev
python manage.py runserver
python manage.py run_bot
```

### Продакшен
```bash
# Backend и Mini App
export DJANGO_SETTINGS_MODULE=core.settings.production
python manage.py collectstatic
python manage.py makemigrations
python manage.py migrate
python manage.py run_bot --webhook

# Настройте веб-сервер (nginx/apache) для обслуживания Django
```

## 🤝 Участие в разработке

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/AmazingFeature`)
3. Зафиксируйте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Отправьте в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

## 📞 Поддержка

Если у вас возникли вопросы или проблемы:

1. 📖 Проверьте [документацию](README/)
2. 🔍 Поищите в [Issues](https://github.com/yourusername/HomeAccountingLegendary/issues)
3. 💬 Создайте новый Issue с подробным описанием проблемы

## 🎯 Планы развития

- [x] 📱 Telegram mini-app (Django)
- [ ] 📊 Расширенная аналитика и графики
- [ ] 🌐 Полноценный веб-интерфейс
- [ ] 📧 Email уведомления
- [ ] 💰 Инвестиционный трекинг
- [ ] 📈 Планирование бюджета
- [ ] 🔄 Синхронизация между устройствами
- [ ] 📱 Мобильное приложение

## 🙏 Благодарности

- Команде Django за отличный фреймворк
- Разработчикам aiogram за современную библиотеку для ботов
- Команде Bootstrap за отличный CSS фреймворк
- Сообществу Python и JavaScript за вдохновение и поддержку

---

**Сделано с ❤️ для управления личными финансами**
