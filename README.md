# LMS Platform

Учебная платформа для онлайн-обучения программированию. Full-stack pet-проект уровня Junior+, построенный на Django REST Framework + React/TypeScript.

## Стек

**Backend:** Python 3.12, Django 5, DRF, PostgreSQL, SimpleJWT, drf-spectacular, pytest-django
**Frontend:** React 18, TypeScript, Vite, React Router, Axios, Zustand, CSS Modules
**Инфраструктура:** Docker, Docker Compose, Nginx

Без Tailwind/MUI/Bootstrap — вся стилизация через чистый CSS Modules с design tokens.

## Функциональность

- Регистрация/авторизация с ролями (student/teacher/admin) через JWT
- Каталог курсов с поиском, фильтрами, пагинацией
- Прохождение уроков (текст/видео/задания/тесты) с отслеживанием прогресса
- Практические задания с ручной проверкой преподавателем
- Тесты с автоматической проверкой (одиночный/множественный/текстовый выбор)
- Автоматическая выдача PDF-сертификатов при завершении курса
- Dashboard с разной статистикой для каждой роли
- Полная документация API через Swagger/Redoc

## Быстрый старт (Docker)

\`\`\`bash
git clone <repo>
cd lms-platform
cp .env.example .env
# отредактируйте .env — задайте DJANGO_SECRET_KEY и DB_PASSWORD

docker compose up --build
\`\`\`

Приложение будет доступно на **http://localhost/**

- API документация: http://localhost/api/docs/
- Django admin: http://localhost/admin/

Создать суперпользователя:

\`\`\`bash
docker compose exec backend python manage.py createsuperuser
\`\`\`

## Локальная разработка (без Docker)

### Backend

\`\`\`bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements/development.txt
cp .env.example .env
# настройте локальный PostgreSQL и подставьте данные в .env

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
\`\`\`

### Frontend

\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

Frontend откроется на http://localhost:5173/ с проксированием `/api/` на backend (localhost:8000).

## Тесты

\`\`\`bash
# Backend
cd backend
pytest
pytest --cov=apps --cov-report=term-missing

# Frontend
cd frontend
npm test
\`\`\`

## Роадмап (следующие этапы развития)

- Redis + Celery для асинхронной обработки (email-уведомления, генерация сертификатов)
- QR-код на сертификатах
- История всех попыток прохождения заданий
- CI/CD (GitHub Actions: lint + test на каждый PR)
- Полноценное мобильное меню Navbar
- Debounce на поиске по каталогу
## Docker Environments

Development compose runs PostgreSQL, Django runserver and Vite dev server:

```bash
docker compose -f docker-compose.dev.yml up --build
```

Production compose runs PostgreSQL, Django behind Nginx and a static React build:

```bash
docker compose -f docker-compose.prod.yml up --build
```

Required environment variables are documented in `.env.example` and `backend/.env.example`.
Use generated secrets for local `.env` files and never commit real production secrets.

## Health Checks

The public health endpoint is available at:

```text
GET /api/health/
```

It returns only a simple status payload and does not expose configuration, credentials or stack details.

## PostgreSQL Backup / Restore

Create a backup:

```bash
docker compose -f docker-compose.prod.yml exec postgres pg_dump -U "$DB_USER" "$DB_NAME" > backup.sql
```

Restore into a prepared database:

```bash
docker compose -f docker-compose.prod.yml exec -T postgres psql -U "$DB_USER" "$DB_NAME" < backup.sql
```

Review backups before restore and do not run restore against production without an explicit maintenance plan.
