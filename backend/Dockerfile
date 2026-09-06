FROM python:3.12-slim

# Отключаем создание .pyc файлов и буферизацию stdout —
# в контейнере они не нужны и мешают видеть логи в реальном времени
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Системные зависимости для psycopg2 (компиляция C-расширения)
# и для сборки некоторых Python-пакетов из исходников
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements ОТДЕЛЬНО от остального кода — так Docker
# закэширует этот слой, и при изменении только кода (без изменения
# зависимостей) пересборка образа не будет заново качать пакеты
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

# Теперь копируем весь остальной код проекта
COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]