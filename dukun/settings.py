"""
Django settings for dukun project.
"""
from pathlib import Path
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-#w2reu-_&_4(b61hyfc0s&5r2@y3^f3!y&cv-#@&swjgc9!g)6'
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [h.strip() for h in os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'healers',
    'bookings',
    'payments',
    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'dukun.middleware.SecurityHeadersMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dukun.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'accounts.context_processors.notification_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'dukun.wsgi.application'

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    try:
        import dj_database_url
        DATABASES = {
            'default': dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
            )
        }
    except ImportError:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
                'OPTIONS': {'timeout': 20},
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'OPTIONS': {
                'timeout': 20,
            },
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'id'
TIME_ZONE = 'Asia/Makassar'
USE_I18N = True
USE_L10N = True
USE_TZ = True

from django.utils.translation import gettext_lazy as _

LANGUAGES = [
    ('id', _('Indonesia')),
    ('en', _('English')),
    ('zh-hans', _('简体中文')),
    ('zh-hant', _('繁體中文')),
    ('ja', _('日本語')),
    ('ko', _('한국어')),
    ('ru', _('Русский')),
    ('ar', _('العربية')),
    ('es', _('Español')),
    ('fr', _('Français')),
    ('de', _('Deutsch')),
    ('pt', _('Português')),
    ('it', _('Italiano')),
    ('nl', _('Nederlands')),
    ('th', _('ไทย')),
    ('vi', _('Tiếng Việt')),
    ('tr', _('Türkçe')),
    ('pl', _('Polski')),
    ('hi', _('हिन्दी')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'bali-healer-cache',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        },
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
SILENCED_SYSTEM_CHECKS = [
    'staticfiles.E002',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Supabase Storage (REST API) — used when service key is set
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
STORAGES = {
    'default': {
        'BACKEND': 'storage.SupabaseStorage' if SUPABASE_SERVICE_KEY else 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_REFERRER_POLICY = 'same-origin'
