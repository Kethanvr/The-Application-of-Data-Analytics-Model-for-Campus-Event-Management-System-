"""
Django settings for dems project.
MongoDB edition — all data stored in MongoDB via MongoEngine.
"""

from pathlib import Path
import os
import mongoengine
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-66x(#mhqecm-pdt25!0y39j%jdg-k@4dx2g3*2-b&c_1a^vh3z')

DEBUG = os.environ.get('RENDER') is None

ALLOWED_HOSTS = ['*']
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# ─── MongoDB connection ────────────────────────────────────────────────────────
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/eventwebsite')

_mongo_kwargs = {'host': MONGODB_URI}
if not DEBUG:
    _mongo_kwargs['tls'] = True
    _mongo_kwargs['tlsAllowInvalidCertificates'] = False

mongoengine.connect(**_mongo_kwargs)

# ─── Minimal SQLite for Django internals (sessions, messages) ─────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ─── Installed apps ───────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap4',
    'users.apps.UsersConfig',
    'events.apps.EventsConfig',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

# ─── Auth ─────────────────────────────────────────────────────────────────────
AUTHENTICATION_BACKENDS = ['users.backends.MongoEngineBackend']
LOGIN_URL = 'login'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'users.middleware.MongoAuthMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_session_timeout.middleware.SessionTimeoutMiddleware',
    'users.middleware.FileIntegrityMiddleware',
]

# Session: database-backed (SQLite) so it survives server restarts
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_EXPIRE_SECONDS = 1800
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_TIMEOUT_REDIRECT = 'login'

ROOT_URLCONF = 'dems.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
                'django.template.context_processors.media',
                'users.context_processors.mongo_user',
            ],
        },
    },
]

WSGI_APPLICATION = 'dems.wsgi.application'

# ─── Static & Media ───────────────────────────────────────────────────────────
STATIC_URL = '/static/'
_static_dir = BASE_DIR / 'static'
STATICFILES_DIRS = [_static_dir] if _static_dir.exists() else []
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR

# ─── i18n ─────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
