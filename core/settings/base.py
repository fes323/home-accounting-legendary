import os
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Загружаем переменные окружения из .env файла
load_dotenv(BASE_DIR / '.env')

# Секретный ключ из переменных окружения
SECRET_KEY = os.getenv(
    'SECRET_KEY', 'django-insecure-change-this-in-production')

# Разрешенные хосты
ALLOWED_HOSTS = os.getenv(
    'ALLOWED_HOSTS', 'localhost,127.0.0.1,www.wallet.my-bucket.ru,wallet.my-bucket.ru').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'mptt',
    'rest_framework',
    'django_filters',

    'core',
    'users',
    'accounting',
    'telegram_bot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # Кастомный CSRF middleware для Telegram
    'telegram_bot.middleware_telegram.TelegramWebAppMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Безопасность для Telegram WebApp
    'telegram_bot.middleware_telegram.TelegramWebAppSecurityMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = ["users.backends.auth.AuthBackend"]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===========================================
# TELEGRAM BOT SETTINGS
# ===========================================

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL', '')
TELEGRAM_WEBHOOK_SECRET = os.getenv('TELEGRAM_WEBHOOK_SECRET', '')

# Bot settings
BOT_USERNAME = os.getenv('BOT_USERNAME', '')
BOT_DESCRIPTION = "Личный помощник для учета финансов"

# Mini App settings
TELEGRAM_MINIAPP_URL = os.getenv('TELEGRAM_MINIAPP_URL', '')
TELEGRAM_MINIAPP_DEBUG_MODE = os.getenv(
    'TELEGRAM_MINIAPP_DEBUG_MODE', 'False').lower() == 'true'

# Webhook settings
TELEGRAM_WEBHOOK_PATH = '/telegram/webhook/'
TELEGRAM_WEBHOOK_FULL_URL = f"{TELEGRAM_WEBHOOK_URL}{TELEGRAM_WEBHOOK_PATH}" if TELEGRAM_WEBHOOK_URL else ''

# Bot commands
TELEGRAM_BOT_COMMANDS = [
    {
        "command": "start",
        "description": "Начать работу с ботом"
    },
    {
        "command": "balance",
        "description": "Показать баланс кошельков"
    },
    {
        "command": "income",
        "description": "Добавить доход"
    },
    {
        "command": "expense",
        "description": "Добавить расход"
    },
    {
        "command": "wallets",
        "description": "Управление кошельками"
    },
    {
        "command": "categories",
        "description": "Управление категориями"
    },
    {
        "command": "help",
        "description": "Помощь по командам"
    }
]

# ===========================================
# REDIS CONFIGURATION (Optional)
# ===========================================
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_DB = int(os.getenv('REDIS_DB', '0'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

# ===========================================
# EMAIL CONFIGURATION (Optional)
# ===========================================
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', '')

# ===========================================
# CELERY CONFIGURATION (Optional)
# ===========================================
CELERY_BROKER_URL = os.getenv(
    'CELERY_BROKER_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/1')
CELERY_RESULT_BACKEND = os.getenv(
    'CELERY_RESULT_BACKEND', f'redis://{REDIS_HOST}:{REDIS_PORT}/1')
