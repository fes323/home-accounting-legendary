# 🏠 Home Accounting Legendary

**Легендарная система домашнего учета с Telegram ботом и React Mini App**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.1.2-green.svg)](https://djangoproject.com)
[![React](https://img.shields.io/badge/React-18.2.0-blue.svg)](https://reactjs.org)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://telegram.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue.svg)](https://postgresql.org)

## 📋 Описание проекта

Home Accounting Legendary — это современная система управления личными финансами, построенная на Django с интеграцией Telegram бота и React Mini App. Проект позволяет пользователям вести учет доходов и расходов через удобный интерфейс мессенджера и веб-приложение, управлять несколькими кошельками и получать детальную аналитику своих финансов.

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
- 🌐 React Mini App для расширенного функционала

### 🌐 Веб-приложение (React Mini App)
- 📱 Минималистичный интерфейс для Telegram
- 📊 Просмотр и редактирование транзакций с историей
- 📁 Управление категориями в виде дерева
- 🔐 Авторизация через Telegram
- 📈 Детальная статистика доходов и расходов

## 🚀 Быстрый старт

### Предварительные требования
- Python 3.11+
- Node.js 16+
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

5. **Настройте и запустите React приложение:**
   ```bash
   cd frontend
   npm install
   cp env.example .env
   # Отредактируйте .env файл с настройками API
   npm start
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
- 🌐 **[Настройка Telegram Mini App](TELEGRAM_MINIAPP_SETUP.md)** - Развертывание React приложения

### Дополнительные материалы
- 🔧 **[Настройка переменных окружения](README/DOTENV_SETUP.md)** - Работа с .env файлами
- 🚨 **[Решение конфликтов бота](README/BOT_CONFLICT_SOLUTION.md)** - Устранение проблем
- 🔄 **[Исправление бота](README/RUN_BOT_FIX.md)** - Диагностика и исправление

## 🏗️ Архитектура проекта

```
backend/
├── accounting/          # Модуль учета финансов
│   ├── models/         # Модели данных
│   ├── views/          # API представления
│   ├── serializers.py  # Сериализаторы DRF
│   └── management/     # Команды управления
├── telegram_bot/       # Telegram бот
│   ├── bot.py          # Основной файл бота
│   ├── handlers/       # Обработчики команд
│   ├── keyboards.py    # Клавиатуры интерфейса
│   └── middleware.py  # Middleware
├── users/              # Модуль пользователей
│   ├── models/         # Модели пользователей
│   ├── views/          # API пользователей
│   └── serializers.py  # Сериализаторы
├── core/               # Основные настройки Django
│   └── settings/       # Конфигурация для разных сред
├── frontend/           # React Mini App
│   ├── src/
│   │   ├── components/ # React компоненты
│   │   ├── pages/      # Страницы приложения
│   │   ├── services/   # API сервисы
│   │   └── contexts/   # React контексты
│   └── public/         # Статические файлы
└── README/             # Документация проекта
```

## 🛠️ Технологический стек

### Backend
- **Django 5.1.2** - Веб-фреймворк
- **Django REST Framework** - API
- **PostgreSQL** - База данных
- **Django MPTT** - Иерархические структуры

### Frontend (React Mini App)
- **React 18.2.0** - Библиотека для UI
- **React Router** - Маршрутизация
- **React Hook Form** - Управление формами
- **Axios** - HTTP клиент
- **Telegram WebApp SDK** - Интеграция с Telegram
- **Lucide React** - Иконки
- **date-fns** - Работа с датами

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

### Команды React приложения
```bash
# Установка зависимостей
npm install

# Запуск в режиме разработки
npm start

# Сборка для продакшена
npm run build

# Запуск тестов
npm test
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
# Backend
export DJANGO_SETTINGS_MODULE=core.settings.production
python manage.py collectstatic
python manage.py makemigrations
python manage.py migrate
python manage.py run_bot --webhook

# Frontend
cd frontend
npm run build
# Разместите файлы из build/ на веб-сервере
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

- [x] 📱 Telegram mini-app
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
- Команде React за мощную библиотеку для UI
- Сообществу Python и JavaScript за вдохновение и поддержку

---

**Сделано с ❤️ для управления личными финансами**
