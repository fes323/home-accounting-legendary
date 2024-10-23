from core.settings.base import *


DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'HAL_2',
        'USER': config['DB']['username'],
        'PASSWORD': config['DB']['password'],
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
