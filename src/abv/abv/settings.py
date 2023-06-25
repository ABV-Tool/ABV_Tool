"""
Django settings for abv project.

Generated by 'django-admin startproject' using Django 4.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

# Umgebungsvariablen laden
dotenv_path = os.path.join(BASE_DIR, '../../.env')
load_dotenv(dotenv_path)


# ENV: DEVELOPMENT / PRODUCTION
ENV ='PRODUCTION'

if ENV == 'DEVELOPMENT':
    MESSAGE_LEVEL = 10 # DEBUG
    DEBUG = True
elif ENV == 'PRODUCTION':
    MESSAGE_LEVEL = 20 # INFO
    DEBUG = True
    ALLOWED_HOSTS = [
        'localhost', 'localhost:8020', 'http://localhost:8020', 'https://localhost:8020'
        '127.0.0.1', '127.0.0.1:8020', 'http://127.0.0.1:8020', 'https://127.0.0.1:8020',
        '0.0.0.0', '0.0.0.0:8020', 'http://0.0.0.0:8020', 'https://0.0.0.0:8020',
    ]
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:8010",
        "http://localhost:8020"
    ]
    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:8010",
        "http://localhost:8020"
    ]


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djmoney',
    'django_extensions',
    'fontawesomefree',
    'tailwind',
    'django_browser_reload',
    'Antragstool'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_browser_reload.middleware.BrowserReloadMiddleware"
]

ROOT_URLCONF = 'abv.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'abv.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT')
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators
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


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/
LANGUAGE_CODE = 'de-DE'
TIME_ZONE = 'Europe/Berlin'
USE_TZ = True
USE_L10N = True
USE_I18N = True
DECIMAL_SEPARATOR = ','
DATETIME_FORMAT = 'd.m.Y H:i'
DATE_FORMAT = 'd.m.Y'
TIME_FORMAT = 'H:i'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '../static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, '../Antragstool/static'),
)

# File-Upload Settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, '../media')
DATA_UPLOAD_MAX_MEMORY_SIZE=10240000 # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE=10240000 # 10MB


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Standard Login/Logout-Redirect
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# Development: Tailwind settings
TAILWIND_APP_NAME = 'Antragstool'
INTERNAL_IPS = [
    "127.0.0.1",
]
NPM_BIN_PATH=r"C:\Program Files\nodejs\npm.cmd"


# E-Mail Settings
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = False
EMAIL_TOOL = 'abv@stura.htw-dresden.de'


# Etherpad Settings
ETHERPAD_API_KEY = os.environ.get('ETHERPAD_API_KEY')
ETHERPAD_HOST = 'https://pad.htw.stura-dresden.de'
ETHERPAD_API_ENDPOINT = ETHERPAD_HOST + '/api/1.2.15/'
ETHERPAD_PAD_ENDPOINT = ETHERPAD_HOST + '/p/'