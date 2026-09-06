#!/bin/sh
set -e

echo "Ожидание готовности PostgreSQL..."
# healthcheck в docker-compose.yml уже гарантирует, что postgres готов
# к моменту старта backend, но эта проверка — дополнительная страховка
# на случай прямого запуска контейнера в обход compose (например, 
# в CI/CD на будущих этапах)
until python manage.py check --database default > /dev/null 2>&1; do
    echo "PostgreSQL пока недоступен — ждём..."
    sleep 2
done

echo "Применение миграций..."
python manage.py migrate --noinput

echo "Сбор статических файлов..."
python manage.py collectstatic --noinput --clear

echo "Запуск Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -