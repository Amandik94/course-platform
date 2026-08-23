from .base import *  # noqa
from decouple import config

DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

CORS_ALLOWED_ORIGINS = [
    config('CORS_ALLOWED_ORIGIN', default='http://localhost:5173'),
]

# Более щадящий вывод ошибок для разработки
INSTALLED_APPS += ['django_extensions']