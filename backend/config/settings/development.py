from .base import *  # noqa
from decouple import config

DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config(
    'DJANGO_ALLOWED_HOSTS', 
    default='localhost,127.0.0.1,backend,nginx,web'
).split(',')

# ❌ ОТКЛЮЧАЕМ ПОДМЕНУ HTTPS ДЛЯ ЛОКАЛЬНОЙ РАЗРАБОТКИ
# SECURE_PROXY_SSL_HEADER удален, чтобы Django не редиректил на https://

USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:5173",
    "http://localhost:3000",
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:3000",
    "http://localhost:5173",
]

# Расширения для разработки
try:
    import django_extensions
    INSTALLED_APPS += ['django_extensions']
except ImportError:
    pass