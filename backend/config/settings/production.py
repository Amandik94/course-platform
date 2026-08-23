from .base import *  # noqa
from decouple import config

DEBUG = False

ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS').split(',')

CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGIN').split(',')

# Security-заголовки для продакшена
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'