# LMS-платформа для обучения программированию

Полнофункциональная LMS-платформа для онлайн-обучения программированию. Backend построен на Django REST Framework, frontend - на React, TypeScript и Vite. Проект поддерживает роли студента, преподавателя и администратора, JWT-аутентификацию, курсы, уроки, задания, тесты, сертификаты, уведомления и отзывы.

## О проекте

Проект предназначен для организации онлайн-обучения: студенты проходят курсы и выполняют задания, преподаватели управляют учебными материалами и проверяют решения, администраторы управляют пользователями, категориями и курсами.

Архитектура разделена на:

- `backend/` - Django REST API, бизнес-логика, PostgreSQL, JWT, OpenAPI-документация.
- `frontend/` - React SPA, маршрутизация, Axios-сервисы, Zustand-состояние, CSS Modules.
- `nginx/` - production-like reverse proxy для React, Django API, static и media.
- `docker-compose*.yml` - локальные Docker-сценарии для development и production-like окружений.

Проект находится в активной разработке. Основные LMS-сценарии реализованы, но production-внедрение требует отдельной настройки секретов, доменов, HTTPS, бэкапов и мониторинга.

## Возможности

### Студент

- Регистрация, вход, выход и получение текущего профиля через JWT.
- Просмотр каталога курсов, поиск, фильтрация и пагинация.
- Просмотр детальной страницы курса, разделов и уроков.
- Запись на курс и просмотр списка "Мои курсы".
- Прохождение уроков и отметка урока завершенным.
- Отправка решений по заданиям.
- Прохождение тестов и получение результата.
- Просмотр сертификатов и скачивание PDF-сертификата.
- Просмотр уведомлений, счетчика непрочитанных, отметка одного или всех уведомлений прочитанными.
- Просмотр отзывов курса, создание, редактирование и удаление своего отзыва при наличии записи на курс.

### Преподаватель

- Dashboard преподавателя.
- Просмотр своих курсов.
- Создание, редактирование и удаление курсов.
- Управление разделами и уроками курса.
- Управление заданиями.
- Создание и редактирование тестов, вопросов и ответов.
- Просмотр решений студентов по заданиям.
- Выставление оценки, статуса и комментария к решению.
- Просмотр уведомлений.

### Администратор

- Admin dashboard.
- Управление пользователями: список, просмотр, фильтрация, поиск, изменение допустимых административных полей, блокировка и разблокировка.
- Управление категориями.
- Просмотр и управление курсами через admin-интерфейс frontend.
- Доступ к Django admin.
- Просмотр уведомлений.

## Технологии

### Backend

- Python 3.12+
- Django 5
- Django REST Framework
- PostgreSQL
- SimpleJWT
- django-filter
- drf-spectacular
- Pillow
- reportlab
- pytest / pytest-django

### Frontend

- React
- TypeScript
- Vite
- React Router
- Axios
- Zustand
- CSS Modules
- Vitest / Testing Library

### Infrastructure

- Docker
- Docker Compose
- Nginx
- PostgreSQL
- Gunicorn

## Архитектура

Development без Docker:

```text
Browser -> Vite dev server -> Django REST API -> PostgreSQL
```

Vite проксирует запросы `/api` на `http://localhost:8000`.

Development через Docker:

```text
Browser -> Vite dev container :5173 -> Django runserver :8000 -> PostgreSQL
```

Production-like Docker:

```text
Browser -> Nginx :80
             ├── / -> React static build
             ├── /api/ -> Django + Gunicorn
             ├── /admin/ -> Django admin
             ├── /static/ -> Django static files
             └── /media/ -> uploaded media
                         -> PostgreSQL
```

## Структура проекта

```text
study_platforma/
├── backend/
│   ├── apps/
│   │   ├── assignments/
│   │   ├── certificates/
│   │   ├── courses/
│   │   ├── dashboard/
│   │   ├── enrollments/
│   │   ├── lessons/
│   │   ├── notifications/
│   │   ├── quizzes/
│   │   ├── reviews/
│   │   └── users/
│   ├── config/
│   │   ├── settings/
│   │   ├── api_urls.py
│   │   └── urls.py
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── development.txt
│   │   └── production.txt
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── manage.py
│   └── pytest.ini
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── features/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── store/
│   │   ├── styles/
│   │   ├── types/
│   │   └── utils/
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
├── nginx/
│   ├── Dockerfile
│   └── nginx.conf
├── .env.example
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.prod.yml
└── README.md
```

## Требования

Для локальной разработки без Docker:

- Python 3.12+
- Node.js и npm
- PostgreSQL

Для запуска через контейнеры:

- Docker
- Docker Compose

## Переменные окружения

Шаблоны переменных находятся в:

- `.env.example`
- `backend/.env.example`
- `frontend/.env.example`

Не коммитьте реальные `.env` файлы, пароли, токены и production-секреты.

| Переменная | Назначение | Пример |
| ---------- | ---------- | ------ |
| `DJANGO_SECRET_KEY` | Секретный ключ Django | `replace-with-secure-secret` |
| `DJANGO_DEBUG` | Режим отладки Django | `True` для разработки, `False` для production |
| `DJANGO_ALLOWED_HOSTS` | Разрешенные hosts Django | `localhost,127.0.0.1,backend` |
| `DB_NAME` | Имя базы PostgreSQL | `lms_db` |
| `DB_USER` | Пользователь PostgreSQL | `lms_user` |
| `DB_PASSWORD` | Пароль PostgreSQL | `replace-with-secure-password` |
| `DB_HOST` | Host PostgreSQL | `localhost` локально, `postgres` в Docker |
| `DB_PORT` | Порт PostgreSQL | `5432` |
| `CORS_ALLOWED_ORIGINS` | Разрешенные origins frontend | `http://localhost:5173` |
| `VITE_API_URL` | Base URL frontend для API | `/api/v1/` |

## Локальный запуск backend

Команды ниже приведены для Windows PowerShell.

```powershell
cd backend

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements/development.txt
Copy-Item .env.example .env
```

Проверьте значения в `backend/.env`: для локального запуска PostgreSQL обычно используется `DB_HOST=localhost`.

Примените существующие миграции и запустите сервер:

```powershell
python manage.py migrate
python manage.py runserver
```

Создание администратора:

```powershell
python manage.py createsuperuser
```

### PostgreSQL для локального запуска

В `.env.example` используется база `lms_db` и пользователь `lms_user`. Создайте их в PostgreSQL вручную или используйте свои значения в `.env`.

Пример создания базы от имени пользователя `postgres`:

```powershell
createdb -U postgres lms_db
```

Если локальный PostgreSQL использует другого пользователя или пароль, обновите `DB_USER`, `DB_PASSWORD`, `DB_HOST` и `DB_PORT`.

## Локальный запуск frontend

```powershell
cd frontend

npm install
Copy-Item .env.example .env
npm run dev
```

По умолчанию Vite запускается на `http://localhost:5173` и проксирует `/api` на backend `http://localhost:8000`.

## Локальные URL

| Сервис | URL |
| ------ | --- |
| Frontend dev server | http://localhost:5173 |
| Backend dev server | http://localhost:8000 |
| API v1 | http://localhost:8000/api/v1/ |
| Health check | http://localhost:8000/api/health/ |
| Swagger UI | http://localhost:8000/api/docs/ |
| ReDoc | http://localhost:8000/api/redoc/ |
| OpenAPI schema | http://localhost:8000/api/schema/ |
| Django admin | http://localhost:8000/admin/ |

## Запуск через Docker

Перед запуском создайте локальный `.env` из корневого шаблона:

```powershell
Copy-Item .env.example .env
```

### Development compose

Поднимает PostgreSQL, Django runserver и Vite dev server:

```powershell
docker compose -f docker-compose.dev.yml up --build
```

Основные URL:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/v1/
- PostgreSQL: `localhost:5432`

### Production-like compose

Поднимает PostgreSQL, Django + Gunicorn, сборку React и Nginx:

```powershell
docker compose -f docker-compose.prod.yml up --build
```

Приложение будет доступно на:

- Frontend через Nginx: http://localhost/
- API через Nginx: http://localhost/api/v1/
- Swagger UI: http://localhost/api/docs/

### Основной docker-compose.yml

Файл `docker-compose.yml` также описывает production-like схему с Nginx на порту `80`:

```powershell
docker compose up --build
```

Остановка контейнеров:

```powershell
docker compose down
```

ВНИМАНИЕ: не используйте `docker compose down -v` как обычную команду остановки. Флаг `-v` удаляет Docker volumes и может удалить локальную базу PostgreSQL.

## API документация

Проект использует `drf-spectacular`.

- OpenAPI schema: `/api/schema/`
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`

## Основные API endpoints

Все endpoints ниже находятся под префиксом `/api/v1/`, если не указано иначе.

| Группа | Endpoint | Назначение |
| ------ | -------- | ---------- |
| Auth | `auth/register/` | Регистрация |
| Auth | `auth/login/` | Login и получение JWT |
| Auth | `auth/refresh/` | Обновление JWT |
| Auth | `auth/logout/` | Logout с blacklist refresh token |
| Auth | `auth/me/` | Текущий пользователь |
| Admin users | `admin/users/` | Список и фильтрация пользователей |
| Admin users | `admin/users/<id>/` | Просмотр и изменение пользователя |
| Categories | `categories/` | Список и создание категорий |
| Categories | `categories/<id>/` | Детали, изменение и удаление категории |
| Courses | `courses/` | Каталог и создание курсов |
| Courses | `courses/<id>/` | Детали, изменение и удаление курса |
| Sections | `courses/<course_id>/sections/` | Разделы курса |
| Sections | `sections/<pk>/` | Детали, изменение и удаление раздела |
| Lessons | `sections/<section_id>/lessons/` | Уроки раздела |
| Lessons | `lessons/<pk>/` | Детали, изменение и удаление урока |
| Enrollment | `courses/<id>/enroll/` | Запись на курс |
| Enrollment | `my-courses/` | Курсы текущего студента |
| Progress | `progress/` | Прогресс текущего пользователя |
| Progress | `lessons/<id>/complete/` | Завершение урока |
| Assignments | `lessons/<lesson_id>/assignment/` | Создание задания для урока |
| Assignments | `assignments/<id>/` | Детали задания |
| Assignments | `assignments/<id>/manage/` | Управление заданием |
| Assignments | `assignments/<id>/submit/` | Отправка решения |
| Assignments | `assignments/<id>/my-submission/` | Решение текущего студента |
| Assignments | `assignments/<id>/submissions/` | Решения студентов для преподавателя |
| Assignments | `submissions/<pk>/` | Проверка решения |
| Quizzes | `lessons/<lesson_id>/quiz/` | Создание теста |
| Quizzes | `quizzes/<id>/` | Детали теста |
| Quizzes | `quizzes/<id>/manage/` | Управление тестом |
| Quizzes | `quizzes/<id>/submit/` | Отправка ответов |
| Questions | `quizzes/<quiz_id>/questions/` | Создание вопроса |
| Questions | `questions/<pk>/` | Изменение и удаление вопроса |
| Answers | `questions/<question_id>/answers/` | Создание ответа |
| Answers | `answers/<pk>/` | Изменение и удаление ответа |
| Certificates | `certificates/` | Список сертификатов |
| Certificates | `certificates/<pk>/` | Детали сертификата |
| Certificates | `certificates/<pk>/download/` | Скачивание PDF |
| Dashboard | `dashboard/student/` | Dashboard студента |
| Dashboard | `dashboard/teacher/` | Dashboard преподавателя |
| Dashboard | `dashboard/admin/` | Dashboard администратора |
| Notifications | `notifications/` | Список уведомлений |
| Notifications | `notifications/unread-count/` | Количество непрочитанных |
| Notifications | `notifications/<pk>/read/` | Отметить уведомление прочитанным |
| Notifications | `notifications/read-all/` | Прочитать все |
| Notifications | `notifications/<pk>/` | Детали или удаление своего уведомления |
| Reviews | `courses/<course_id>/reviews/` | Отзывы курса и создание отзыва |
| Reviews | `reviews/<pk>/` | Изменение и удаление своего отзыва |

Health endpoint находится вне `/api/v1/`:

```text
GET /api/health/
```

## Аутентификация

API использует JWT через SimpleJWT.

После входа frontend сохраняет `access` и `refresh` token и отправляет защищенные запросы с заголовком:

```text
Authorization: Bearer <access_token>
```

В настройках SimpleJWT включены:

- access token lifetime: 30 минут;
- refresh token lifetime: 7 дней;
- refresh token rotation;
- blacklist after rotation.

## Роли пользователей

В проекте используются роли:

- `student` - проходит курсы, выполняет задания и тесты, получает сертификаты, оставляет отзывы.
- `teacher` - управляет своими курсами, уроками, заданиями, тестами и проверяет решения студентов.
- `admin` - управляет пользователями, категориями, курсами и имеет доступ к административным разделам.

Ограничения доступа реализованы на backend через permissions и фильтрацию queryset. Frontend role routes используются для UX-навигации, но не являются единственной защитой.

## Основные страницы frontend

| Route | Назначение |
| ----- | ---------- |
| `/` | Главная страница |
| `/courses` | Каталог курсов |
| `/courses/:id` | Детальная страница курса |
| `/login` | Вход |
| `/register` | Регистрация |
| `/profile` | Профиль |
| `/my-courses` | Мои курсы |
| `/learn/:courseId/:lessonId` | Прохождение урока |
| `/quiz/:id` | Прохождение теста |
| `/assignment/:id` | Задание |
| `/certificates` | Сертификаты |
| `/notifications` | Уведомления |
| `/dashboard` | Dashboard по роли пользователя |
| `/dashboard/teacher` | Dashboard преподавателя |
| `/teacher/courses` | Курсы преподавателя |
| `/teacher/courses/new` | Создание курса |
| `/teacher/courses/:id/edit` | Редактирование курса |
| `/teacher/courses/:id/manage` | Управление контентом курса |
| `/teacher/assignments/:id/submissions` | Проверка решений |
| `/dashboard/admin` | Dashboard администратора |
| `/admin/users` | Пользователи |
| `/admin/users/:id` | Пользователь |
| `/admin/courses` | Курсы для администратора |
| `/admin/categories` | Категории |
| `/admin/:area` | Заглушка для недоступного admin-раздела |

## Уведомления

Приложение `notifications` реализует:

- список уведомлений текущего пользователя;
- пагинацию и фильтр `is_read`;
- счетчик непрочитанных;
- отметку одного уведомления прочитанным;
- отметку всех уведомлений прочитанными;
- удаление своего уведомления;
- создание уведомлений из backend-событий через `create_notification(...)`.

Frontend содержит `NotificationBell`, dropdown, страницу `/notifications`, `notificationService`, `useNotifications` и Zustand store для счетчика.

## Отзывы

Приложение `reviews` реализует отзывы студентов о курсах:

- список отзывов курса;
- создание отзыва студентом, записанным на курс;
- один отзыв на пару студент + курс;
- рейтинг от 1 до 5;
- редактирование и удаление своего отзыва;
- расчет `average_rating` и `reviews_count` для курсов;
- отображение отзывов на странице курса.

## Локализация

Пользовательский интерфейс и основные backend-сообщения локализованы на русский язык. Технические identifiers, API URLs, JSON keys, названия библиотек и стек технологий остаются на английском.

## Static и media

- Static files собираются в `backend/staticfiles`.
- Uploaded media хранятся в `backend/media` локально или в Docker volume.
- В development Django отдает media при `DEBUG=True`.
- В Docker production-like окружении static и media отдает Nginx.
- Доступ к `/media/certificates/` в Nginx запрещен напрямую; сертификаты скачиваются через API endpoint.

## Миграции

Для обычного запуска проекта применяются уже существующие миграции:

```powershell
cd backend
python manage.py migrate
```

Команда `makemigrations` создает новые migration files и нужна только при изменении моделей:

```powershell
python manage.py makemigrations
```

Не запускайте `makemigrations` как стандартный шаг старта приложения, если модели не менялись.

## Тестирование

### Backend

```powershell
cd backend
pytest
```

Можно запускать тесты отдельного приложения:

```powershell
pytest apps/courses/
pytest apps/notifications/
pytest apps/reviews/
```

### Frontend

```powershell
cd frontend
npm run test
```

Watch-режим:

```powershell
npm run test:watch
```

## Проверка frontend

```powershell
cd frontend
npx tsc --noEmit
npm run lint
npm run build
```

`npm run build` выполняет TypeScript build (`tsc -b`) и сборку Vite.

## Проверка backend

```powershell
cd backend
python manage.py check
```

## PostgreSQL backup / restore

Пример backup для production-like Docker:

```powershell
docker compose -f docker-compose.prod.yml exec postgres pg_dump -U $env:DB_USER $env:DB_NAME > backup.sql
```

Пример restore в заранее подготовленную базу:

```powershell
Get-Content backup.sql | docker compose -f docker-compose.prod.yml exec -T postgres psql -U $env:DB_USER $env:DB_NAME
```

Перед restore проверьте backup и не выполняйте восстановление на production без отдельного плана обслуживания.

## Частые проблемы

### PostgreSQL authentication failed

Проверьте `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` и существование базы `DB_NAME`.

Для локальной базы PostgreSQL команда `createdb` может использовать текущего Windows-пользователя. При необходимости укажите пользователя явно:

```powershell
createdb -U postgres lms_db
```

### Port already in use

Проверьте занятые порты:

- `5173` - Vite;
- `8000` - Django;
- `5432` - PostgreSQL;
- `80` - Nginx.

### Frontend не видит API

Проверьте:

- backend запущен на `http://localhost:8000`;
- `frontend/.env` содержит корректный `VITE_API_URL`;
- Vite proxy в `frontend/vite.config.ts`;
- Nginx proxy для `/api/`, если используется Docker production-like запуск.

### Docker entrypoint и переносы строк

Файл `backend/entrypoint.sh` должен сохраняться с Unix line endings (`LF`). CRLF может приводить к ошибкам запуска shell script в Linux-контейнере.

## Статус проекта

### Реализовано

- Auth и роли `student`, `teacher`, `admin`.
- Курсы, категории, разделы и уроки.
- Запись на курсы и прогресс по урокам.
- Задания и проверка решений.
- Тесты, вопросы, ответы и отправка результатов.
- Сертификаты и PDF download.
- Dashboard для ролей.
- Уведомления.
- Отзывы и рейтинг курсов.
- Frontend страницы для основных student, teacher и admin-сценариев.
- Docker dev/prod split и Nginx reverse proxy.

### В работе / требует дальнейшего усиления

- Расширение тестового покрытия dashboard, frontend routes и сложных role flows.
- Дополнительная оптимизация тяжелых teacher/admin страниц.
- Production hardening: HTTPS, реальные домены, секреты, мониторинг, backup-процедуры.
- CI/CD.

## Roadmap

- Усилить security production-конфигурации: секреты, HTTPS, cookie/token policy.
- Расширить backend и frontend тесты для role-based сценариев.
- Добавить query-count/performance tests для крупных списков.
- Улучшить UX teacher/admin страниц и заменить browser confirmations на модальные окна.
- Настроить CI/CD для lint, typecheck, backend tests и frontend tests.
- Подготовить production-документацию для deploy, backup и restore.
- Рассмотреть S3-compatible storage для media как будущий production-этап.

## Проверенные по конфигурации команды

Команды ниже соответствуют текущим файлам проекта:

```powershell
cd backend
pip install -r requirements/development.txt
python manage.py check
python manage.py migrate
python manage.py runserver
pytest
```

```powershell
cd frontend
npm install
npm run dev
npm run test
npm run test:watch
npm run lint
npm run build
npx tsc --noEmit
```

```powershell
docker compose up --build
docker compose -f docker-compose.dev.yml up --build
docker compose -f docker-compose.prod.yml up --build
docker compose down
```
