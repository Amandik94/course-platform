from .base import *  # noqa
from decouple import config

DEBUG = False

ALLOWED_HOSTS = [host.strip() for host in config('DJANGO_ALLOWED_HOSTS').split(',') if host.strip()]

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default=config('CORS_ALLOWED_ORIGIN', default=''),
)
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in CORS_ALLOWED_ORIGINS.split(',')
    if origin.strip()
]

INSECURE_SECRET_KEY_PLACEHOLDERS = {
    'change-me-to-a-random-secret-key',
    'replace-with-secure-secret',
    'secret',
    'changeme',
    'your-secret-key',
}

if SECRET_KEY in INSECURE_SECRET_KEY_PLACEHOLDERS:
    raise RuntimeError('DJANGO_SECRET_KEY must be changed for production.')

# Настройки работы за Nginx с поддержкой SSL в продакшене
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage',
    },
}
