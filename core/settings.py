"""
Django settings for the food delivery project.

This configuration file defines the core settings used throughout the
application. It intentionally avoids hard-coded secrets and assumes
the developer will provide environment variables or override values in
a production deployment. The default configuration uses SQLite for
storage and is suitable for development and demonstration purposes.
"""
from __future__ import annotations

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR: Path = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY: str = os.environ.get('DJANGO_SECRET_KEY', 'change-me-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG: bool = os.environ.get('DJANGO_DEBUG', '1') == '1'

ALLOWED_HOSTS: list[str] = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local apps
    'accounts',
    'restaurants',
    'orders',
    'payments',
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

ROOT_URLCONF: str = 'core.urls'

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
                'core.context_processors.stripe_public_key',  # <-- add this line
            ],
        },
    },
]

WSGI_APPLICATION: str = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(BASE_DIR / 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/
LANGUAGE_CODE: str = 'en-us'
TIME_ZONE: str = 'UTC'
USE_I18N: bool = True
USE_TZ: bool = True

# Static files (CSS, JavaScript, Images)
STATIC_URL: str = '/static/'
STATIC_ROOT: Path = BASE_DIR / 'staticfiles'
STATICFILES_DIRS: list[Path] = [BASE_DIR / 'static']

MEDIA_URL: str = '/media/'
MEDIA_ROOT: Path = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD: str = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL: str = 'accounts.User'

# Stripe configuration (test keys from the original backend)
STRIPE_PUBLIC_KEY: str = os.environ.get(
    'STRIPE_PUBLIC_KEY',
    'pk_test_51S0LPxISIz2c7ED1kvux04tVOZWothXvPPC664G8ob5m0bfUO8dl8Jv4JzbIIMAQRJ1FPJ8aae3cr1IZPdFBJkH200XCUEHZcd',
)
STRIPE_SECRET_KEY: str = os.environ.get(
    'STRIPE_SECRET_KEY',
    'sk_test_51S0LPxISIz2c7ED1ibtNR7LSQkqDizaWVJwByGfoGy0OZ2kV0dnLmgEuv1BFauTtnc9jvIRB74eGMzFnbKQKbrsE000zt0avdC',
)

# For local dev: allow CSRF for localhost if you see CSRF warnings with fetch()
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

# Login and logout redirects
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
