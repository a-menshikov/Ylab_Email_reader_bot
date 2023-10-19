from datetime import timedelta
import logging
import logging.config
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = os.getenv('ENVIRONMENT') == 'dev'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', default='*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'email_service',
    'user',
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

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE'),
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT')
    }
}


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

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/web-static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'web-static')

MEDIA_URL = '/web-media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'web-media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')

CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'

BEAT_SCHEDULE_TIMEOUT = int(os.getenv('BEAT_SCHEDULE_TIMEOUT', default=3600))

CELERY_BEAT_SCHEDULE = {
    'db_cache_synchronization': {
        'task': 'infrastructure.tasks.listening_status_synchronization',
        'schedule': timedelta(seconds=BEAT_SCHEDULE_TIMEOUT),
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'full' if DEBUG else 'simple',
        },
    },
    'loggers': {
        'imap': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
    },
    'formatters': {
        'full': {
            'format': '%(asctime)s.%(msecs)d %(levelname)s %(filename)s %(funcName)s %(message)s',
            'datefmt': '%d-%m-%Y %H:%M:%S',
        },
        'simple': {
            'format': '%(asctime)s.%(msecs)d %(levelname)s %(message)s',
            'datefmt': '%d-%m-%Y %H:%M:%S',
        }
    },
}

logging.config.dictConfig(LOGGING)

CRYPTO_KEY = os.getenv('CRYPTO_KEY')

ALL_DOMAINS_KEY = 'domains_all'
BOX_FULL_KEY = 'user_{telegram_id}_box_full_{box_id}'
BOX_SIMPLE_KEY = 'user_{telegram_id}_box_simple_{box_id}'
DOMAIN_KEY = 'domain_{id}'
FILTERS_VALUE_KEY = 'user_{telegram_id}_box_filter_values_{box_id}'
USER_EXISTS_KEY = 'user_{telegram_id}_exist'
USER_IS_ACTIVE_KEY = 'user_{telegram_id}_is_active'
USER_BOXES_KEY = 'user_{telegram_id}_boxes'
USER_KEY = 'user_{telegram_id}'
USER_KEYS_PATTERN = 'user_{telegram_id}*'

REDIS_KEY_FORMAT = 'user_{telegram_id}_{box_id}_status'
ACTIVE_VALUE = 'true'
NON_ACTIVE_VALUE = 'false'

CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', default=3600))

BOT_TOKEN = os.getenv('BOT_TOKEN')
TG_API_IMAGE = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'

IMAGE_MIN_WIDTH = 300
IMAGE_MIN_HEIGHT = 300
IMAGE_PADDING = 20
