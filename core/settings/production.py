import os
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Загружаем переменные окружения из .env файла
load_dotenv(BASE_DIR / '.env')

# ===========================================
# PRODUCTION SETTINGS
# ===========================================

# Режим отладки
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Секретный ключ из переменных окружения
SECRET_KEY = os.getenv(
    'SECRET_KEY', 'django-insecure-change-this-in-production')

# Разрешенные хосты
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

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
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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

# ===========================================
# DATABASE CONFIGURATION
# ===========================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'HAL_production'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Password validation
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
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ===========================================
# STATIC FILES CONFIGURATION
# ===========================================
STATIC_URL = 'static/'
STATIC_ROOT = os.getenv('STATIC_ROOT', '/var/www/wallet/static/')
MEDIA_ROOT = os.getenv('MEDIA_ROOT', '/var/www/wallet/media/')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===========================================
# TELEGRAM BOT SETTINGS
# ===========================================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL', '')
TELEGRAM_WEBHOOK_SECRET = os.getenv('TELEGRAM_WEBHOOK_SECRET', '')
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
# SECURITY SETTINGS
# ===========================================
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS настройки
SECURE_SSL_REDIRECT = os.getenv(
    'SECURE_SSL_REDIRECT', 'True').lower() == 'true'
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'True').lower() == 'true'
SESSION_COOKIE_SECURE = os.getenv(
    'SESSION_COOKIE_SECURE', 'True').lower() == 'true'

# ===========================================
# LOGGING CONFIGURATION
# ===========================================
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', '/var/log/django/wallet_app.log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.FileHandler',
            'filename': LOG_FILE_PATH,
            'formatter': 'verbose',
        },
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'telegram_bot': {
            'handlers': ['file', 'console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}

# ===========================================
# CACHE CONFIGURATION
# ===========================================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f"redis://{os.getenv('REDIS_HOST', '127.0.0.1')}:{os.getenv('REDIS_PORT', '6379')}/{os.getenv('REDIS_DB', '0')}",
        'OPTIONS': {
            'PASSWORD': os.getenv('REDIS_PASSWORD', ''),
        }
    }
}

# ===========================================
# EMAIL CONFIGURATION
# ===========================================
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', '')

# ===========================================
# CELERY CONFIGURATION
# ===========================================
CELERY_BROKER_URL = os.getenv(
    'CELERY_BROKER_URL', f"redis://{os.getenv('REDIS_HOST', '127.0.0.1')}:{os.getenv('REDIS_PORT', '6379')}/1")
CELERY_RESULT_BACKEND = os.getenv(
    'CELERY_RESULT_BACKEND', f"redis://{os.getenv('REDIS_HOST', '127.0.0.1')}:{os.getenv('REDIS_PORT', '6379')}/1")
