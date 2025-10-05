import os

from core.settings.base import *

# ===========================================
# DEVELOPMENT SETTINGS
# ===========================================

# Режим отладки
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# База данных для разработки
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'HAL_development'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# ===========================================
# STATIC FILES CONFIGURATION
# ===========================================
STATIC_ROOT = os.getenv('STATIC_ROOT', BASE_DIR / 'staticfiles')
MEDIA_ROOT = os.getenv('MEDIA_ROOT', BASE_DIR / 'media')

# ===========================================
# LOGGING CONFIGURATION
# ===========================================
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', BASE_DIR / 'logs' / 'dev.log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
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
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'telegram_bot': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}

# ===========================================
# DEVELOPMENT-SPECIFIC SETTINGS
# ===========================================

# Отключаем HTTPS редиректы в разработке
SECURE_SSL_REDIRECT = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Настройки для разработки
INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Отключаем кеширование в разработке
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
