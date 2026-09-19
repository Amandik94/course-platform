from collections import defaultdict
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.assignments.models import Assignment, AssignmentSubmission
from apps.certificates.models import Certificate
from apps.certificates.services import issue_certificate
from apps.courses.models import Category, Course, Section
from apps.enrollments.models import Enrollment, LessonProgress
from apps.lessons.models import Lesson
from apps.notifications.models import Notification
from apps.quizzes.models import Answer, Question, Quiz, QuizAttempt
from apps.reviews.models import Review
from apps.users.models import User


DEMO_PASSWORD = 'Demo12345!'

CATEGORIES = (
    ('Основы программирования', 'demo-programming-basics', 'Алгоритмы, логика и базовые принципы разработки.'),
    ('Python', 'demo-python', 'Разработка приложений и автоматизация на Python.'),
    ('Django', 'demo-django', 'Создание веб-приложений на Django и Django REST Framework.'),
    ('Frontend', 'demo-frontend', 'Современная клиентская веб-разработка.'),
    ('JavaScript', 'demo-javascript', 'Язык JavaScript и экосистема браузерной разработки.'),
    ('React', 'demo-react', 'Интерфейсы на React и TypeScript.'),
    ('Backend', 'demo-backend', 'Архитектура серверных приложений и REST API.'),
    ('Базы данных', 'demo-databases', 'Проектирование и работа с PostgreSQL.'),
    ('DevOps', 'demo-devops', 'Контейнеризация и поставка приложений.'),
    ('Git и GitHub', 'demo-version-control', 'Контроль версий и командная разработка.'),
)

TEACHERS = (
    ('teacher.python.demo@example.com', 'Алексей', 'Смирнов'),
    ('teacher.frontend.demo@example.com', 'Анна', 'Ким'),
    ('teacher.backend.demo@example.com', 'Данияр', 'Ахметов'),
    ('teacher.web.demo@example.com', 'Мария', 'Иванова'),
)

STUDENTS = tuple(
    (f'student{number:02d}.demo@example.com', first_name, last_name)
    for number, (first_name, last_name) in enumerate(
        (
            ('Алина', 'Соколова'),
            ('Максим', 'Орлов'),
            ('София', 'Кузнецова'),
            ('Тимур', 'Нурланов'),
            ('Елена', 'Волкова'),
            ('Арман', 'Сериков'),
            ('Виктория', 'Морозова'),
            ('Илья', 'Петров'),
            ('Диана', 'Абдуллина'),
            ('Никита', 'Лебедев'),
        ),
        start=1,
    )
)


def section(title, *lessons):
    return {'title': title, 'lessons': lessons}


COURSES = (
    {
        'title': 'Python с нуля', 'slug': 'demo-python-start', 'category': 'demo-python',
        'teacher': 0, 'level': 'beginner', 'duration': 32, 'price': '0', 'track': 'python',
        'short': 'Практический старт в Python: синтаксис, коллекции, функции и первый проект.',
        'description': 'Курс знакомит с основами Python через короткие уроки и практические задачи. Студент последовательно создаст консольные программы и итоговый мини-проект.',
        'sections': (
            section('Знакомство с Python', 'Как устроен курс', 'Установка Python и редактора'),
            section('Основы языка', 'Переменные и типы данных', 'Практика: калькулятор'),
            section('Управление программой', 'Условия и циклы', 'Тест: основы Python'),
            section('Функции и проект', 'Функции и области видимости', 'Итоговый мини-проект'),
        ),
    },
    {
        'title': 'Алгоритмы и основы программирования', 'slug': 'demo-algorithms',
        'category': 'demo-programming-basics', 'teacher': 0, 'level': 'beginner',
        'duration': 28, 'price': '0', 'track': 'algorithms',
        'short': 'Алгоритмическое мышление, структуры данных и оценка эффективности решений.',
        'description': 'Курс помогает научиться разбивать задачу на шаги, выбирать структуру данных и оценивать сложность алгоритма на понятных практических примерах.',
        'sections': (
            section('Алгоритмическое мышление', 'Что такое алгоритм', 'Псевдокод и блок-схемы'),
            section('Структуры данных', 'Массивы и списки', 'Практика: поиск элемента'),
            section('Оценка решений', 'Временная сложность', 'Тест: алгоритмы'),
            section('Базовые алгоритмы', 'Сортировка и поиск', 'Итоговая задача'),
        ),
    },
    {
        'title': 'HTML и CSS: современная вёрстка', 'slug': 'demo-html-css',
        'category': 'demo-frontend', 'teacher': 1, 'level': 'beginner',
        'duration': 30, 'price': '0', 'track': 'html_css',
        'short': 'Семантическая разметка, Flexbox, Grid и адаптивные страницы.',
        'description': 'Практический курс по созданию доступных адаптивных интерфейсов. В результате студент сверстает полноценную страницу образовательного сервиса.',
        'sections': (
            section('Семантический HTML', 'Структура HTML-документа', 'Семантические элементы'),
            section('Основы CSS', 'Каскад и селекторы', 'Практика: карточка курса'),
            section('Адаптивная раскладка', 'Flexbox и Grid', 'Тест: HTML и CSS'),
            section('Финальная страница', 'Медиа-запросы', 'Адаптивный лендинг'),
        ),
    },
    {
        'title': 'Python: ООП и чистый код', 'slug': 'demo-python-oop', 'category': 'demo-python',
        'teacher': 0, 'level': 'junior', 'duration': 36, 'price': '4990', 'track': 'python_oop',
        'short': 'Классы, композиция, исключения, типизация и поддерживаемый Python-код.',
        'description': 'Продолжение базового курса Python с акцентом на объектную модель, декомпозицию и практики написания понятного, тестируемого кода.',
        'sections': (
            section('Объектная модель', 'Классы и экземпляры', 'Атрибуты и методы'),
            section('Проектирование', 'Наследование и композиция', 'Практика: модель заказа'),
            section('Надёжный код', 'Исключения и типизация', 'Тест: ООП Python'),
            section('Архитектура проекта', 'Модули и зависимости', 'Рефакторинг приложения'),
        ),
    },
    {
        'title': 'Django для начинающих', 'slug': 'demo-django-start', 'category': 'demo-django',
        'teacher': 2, 'level': 'junior', 'duration': 42, 'price': '7990', 'track': 'django',
        'short': 'Модели, представления, шаблоны и авторизация в Django.',
        'description': 'Курс проводит от создания проекта до готового веб-приложения с базой данных, формами и разграничением доступа пользователей.',
        'sections': (
            section('Старт проекта', 'Архитектура Django', 'Проект и приложения'),
            section('Работа с данными', 'Модели и миграции', 'Практика: модель курса'),
            section('HTTP и интерфейс', 'URL и представления', 'Тест: основы Django'),
            section('Готовое приложение', 'Формы и авторизация', 'Итоговый Django-проект'),
        ),
    },
    {
        'title': 'Django REST Framework: создание REST API', 'slug': 'demo-drf-api',
        'category': 'demo-django', 'teacher': 2, 'level': 'middle', 'duration': 46,
        'price': '9990', 'track': 'drf',
        'short': 'Serializer, ViewSet, permissions, JWT и документирование API.',
        'description': 'Углублённый практический курс по разработке безопасного REST API на Django REST Framework с тестами и OpenAPI-документацией.',
        'sections': (
            section('Контракт API', 'Принципы REST', 'Serializer и валидация'),
            section('Endpoints', 'APIView и ViewSet', 'Практика: API каталога'),
            section('Безопасность', 'JWT и permissions', 'Тест: Django REST Framework'),
            section('Качество API', 'Фильтрация и документация', 'Итоговый REST API'),
        ),
    },
    {
        'title': 'Современный JavaScript', 'slug': 'demo-modern-javascript',
        'category': 'demo-javascript', 'teacher': 3, 'level': 'junior', 'duration': 38,
        'price': '6990', 'track': 'javascript',
        'short': 'ES-модули, DOM, асинхронность и работа с HTTP API.',
        'description': 'Курс систематизирует знания JavaScript и учит создавать интерактивные интерфейсы, работать с событиями, Promise и сетевыми запросами.',
        'sections': (
            section('Язык JavaScript', 'Переменные и функции', 'Объекты и массивы'),
            section('Браузер', 'DOM и события', 'Практика: интерактивный список'),
            section('Асинхронность', 'Promise и async/await', 'Тест: JavaScript'),
            section('Работа с API', 'Fetch и обработка ошибок', 'Мини-приложение с API'),
        ),
    },
    {
        'title': 'React + TypeScript', 'slug': 'demo-react-typescript', 'category': 'demo-react',
        'teacher': 1, 'level': 'middle', 'duration': 48, 'price': '12990', 'track': 'react',
        'short': 'Компоненты, hooks, маршрутизация, типизация и интеграция с REST API.',
        'description': 'Практический курс по созданию масштабируемого frontend-приложения на React и TypeScript с формами, состоянием и API-интеграцией.',
        'sections': (
            section('Компонентный подход', 'JSX и компоненты', 'Props и TypeScript'),
            section('Состояние', 'useState и события', 'Практика: CourseCard'),
            section('Данные и эффекты', 'useEffect и Axios', 'Тест: React'),
            section('Приложение', 'Router и состояние', 'Итоговый React-проект'),
        ),
    },
    {
        'title': 'PostgreSQL для разработчиков', 'slug': 'demo-postgresql',
        'category': 'demo-databases', 'teacher': 2, 'level': 'middle', 'duration': 34,
        'price': '7990', 'track': 'postgresql',
        'short': 'SQL, связи, индексы, транзакции и анализ запросов PostgreSQL.',
        'description': 'Курс учит проектировать реляционную базу данных и писать эффективные запросы, опираясь на реальные задачи backend-разработки.',
        'sections': (
            section('Реляционная модель', 'Таблицы и типы данных', 'Ключи и ограничения'),
            section('SQL-запросы', 'SELECT и JOIN', 'Практика: отчёт по курсам'),
            section('Производительность', 'Индексы и EXPLAIN', 'Тест: PostgreSQL'),
            section('Надёжность данных', 'Транзакции', 'Проектирование схемы LMS'),
        ),
    },
    {
        'title': 'Git и GitHub для разработчика', 'slug': 'demo-git-github',
        'category': 'demo-version-control', 'teacher': 3, 'level': 'beginner',
        'duration': 18, 'price': '4990', 'track': 'git',
        'short': 'Коммиты, ветки, merge, pull request и командный workflow.',
        'description': 'Курс объясняет ежедневную работу с Git и безопасное взаимодействие команды через GitHub на примере учебного проекта.',
        'sections': (
            section('Локальный репозиторий', 'Инициализация и status', 'Коммиты и история'),
            section('Ветки', 'Создание веток', 'Практика: объединение изменений'),
            section('Удалённая работа', 'Remote и push', 'Тест: Git'),
            section('Командный процесс', 'Pull request и review', 'Workflow учебного проекта'),
        ),
    },
    {
        'title': 'Docker для Junior-разработчика', 'slug': 'demo-docker-junior',
        'category': 'demo-devops', 'teacher': 2, 'level': 'junior', 'duration': 26,
        'price': '8990', 'track': 'docker',
        'short': 'Образы, контейнеры, volumes, сети и Docker Compose.',
        'description': 'Практический курс по упаковке Django и React приложений в контейнеры и организации локального окружения через Docker Compose.',
        'sections': (
            section('Основы контейнеров', 'Образы и контейнеры', 'Команды Docker CLI'),
            section('Сборка образа', 'Dockerfile', 'Практика: контейнер приложения'),
            section('Данные и сеть', 'Volumes и networks', 'Тест: Docker'),
            section('Несколько сервисов', 'Docker Compose', 'Контейнеризация LMS'),
        ),
    },
    {
        'title': 'Full-Stack Django + React', 'slug': 'demo-fullstack-django-react',
        'category': 'demo-backend', 'teacher': 3, 'level': 'advanced', 'duration': 72,
        'price': '14990', 'track': 'fullstack', 'status': 'draft',
        'short': 'Полный цикл разработки LMS: REST API, React UI и Docker.',
        'description': 'Проектный курс объединяет Django REST Framework, React, PostgreSQL и Docker. Студент проектирует контракт и собирает приложение по слоям.',
        'sections': (
            section('Проектирование', 'Требования и роли', 'Модель данных'),
            section('Backend', 'REST API и permissions', 'Практика: endpoint курса'),
            section('Frontend', 'React и API-клиент', 'Тест: full-stack архитектура'),
            section('Интеграция', 'Docker и Nginx', 'Защита итогового проекта'),
        ),
    },
)


QUIZ_BANK = {
    'python': [('Какое ключевое слово объявляет функцию?', 'def', 'func', 'function', 'method'), ('Какой тип хранит целые числа?', 'int', 'str', 'float', 'bool'), ('Какая коллекция изменяема?', 'list', 'tuple', 'str', 'frozenset'), ('Какой оператор проверяет равенство?', '==', '=', '!=', 'is not')],
    'algorithms': [('Как работает стек?', 'LIFO', 'FIFO', 'Random', 'Sorted'), ('Что требуется бинарному поиску?', 'Отсортированные данные', 'Только строки', 'Хеш-таблица', 'Рекурсия'), ('Что описывает O(n)?', 'Линейный рост операций', 'Постоянное время', 'Квадратичный рост', 'Ошибку алгоритма'), ('Алгоритм должен быть...', 'Конечным', 'Случайным', 'Бесконечным', 'Графическим')],
    'html_css': [('Какой тег содержит основное содержимое?', 'main', 'meta', 'style', 'script'), ('Что создаёт CSS Grid?', 'Двумерную раскладку', 'HTTP-запрос', 'Базу данных', 'JS-модуль'), ('Для чего нужен media query?', 'Для адаптивных стилей', 'Для загрузки видео', 'Для SQL', 'Для JWT'), ('Какой атрибут описывает изображение?', 'alt', 'href', 'target', 'method')],
    'python_oop': [('Что создаёт class?', 'Новый тип объектов', 'SQL-таблицу', 'HTTP-маршрут', 'CSS-класс'), ('Что предпочтительно для отношения «содержит»?', 'Композиция', 'Наследование', 'Глобальная переменная', 'Рекурсия'), ('Как обозначается конструктор?', '__init__', '__start__', '__newclass__', '__main__'), ('Для чего нужны type hints?', 'Для описания ожидаемых типов', 'Для шифрования', 'Для миграций', 'Для CSS')],
    'django': [('Что описывает ORM-модель?', 'Структуру данных', 'CSS-тему', 'JWT-токен', 'Docker image'), ('Что применяет миграции?', 'migrate', 'runserver', 'collectstatic', 'testserver'), ('Где сопоставляются URL?', 'urls.py', 'models.py', 'admin.py', 'apps.py'), ('Что защищает пароль пользователя?', 'Хеширование', 'Base64', 'Slug', 'Cookie name')],
    'drf': [('Что преобразует model в API-данные?', 'Serializer', 'Middleware', 'Migration', 'Template'), ('Где проверяют объектный доступ?', 'Permission', 'Pagination', 'Renderer', 'Filter'), ('Какой заголовок несёт JWT?', 'Authorization', 'Accept-Language', 'Referer', 'ETag'), ('Какой метод частично обновляет ресурс?', 'PATCH', 'GET', 'HEAD', 'OPTIONS')],
    'javascript': [('Что возвращает async-функция?', 'Promise', 'DOM', 'CSSRule', 'Cookie'), ('Как объявить неизменяемую ссылку?', 'const', 'var', 'static', 'final'), ('Что выбирает элемент DOM?', 'querySelector', 'fetch', 'parseInt', 'setTimeout'), ('Как обработать ошибку Promise?', 'catch', 'map', 'filter', 'join')],
    'react': [('Что хранит локальное состояние?', 'useState', 'useEffect', 'useMemo', 'useId'), ('Что передаётся компоненту извне?', 'props', 'migration', 'cookie', 'queryset'), ('Для чего нужен key в списке?', 'Для стабильной идентификации', 'Для CSS', 'Для JWT', 'Для маршрута API'), ('Что описывает интерфейс TypeScript?', 'Форму данных', 'SQL-индекс', 'Docker volume', 'HTML-тег')],
    'postgresql': [('Что объединяет строки таблиц?', 'JOIN', 'ORDER', 'LIMIT', 'VACUUM'), ('Что ускоряет поиск по колонке?', 'Индекс', 'Триггер', 'View', 'Sequence'), ('Что обеспечивает атомарность группы операций?', 'Транзакция', 'Pagination', 'Serializer', 'Cache-Control'), ('Что показывает план запроса?', 'EXPLAIN', 'GRANT', 'COMMIT', 'CREATE USER')],
    'git': [('Что сохраняет снимок изменений?', 'commit', 'status', 'diff', 'clone'), ('Что создаёт новую линию разработки?', 'branch', 'tag', 'remote', 'stash list'), ('Что объединяет ветки?', 'merge', 'init', 'log', 'add'), ('Что используется для обсуждения изменений на GitHub?', 'Pull request', 'Volume', 'Migration', 'Serializer')],
    'docker': [('Что является шаблоном контейнера?', 'Image', 'Volume', 'Network', 'Process ID'), ('Где описывается сборка образа?', 'Dockerfile', 'package.json', 'urls.py', 'README only'), ('Что сохраняет данные вне контейнера?', 'Volume', 'Layer cache only', 'Port', 'Label'), ('Что запускает набор сервисов?', 'Docker Compose', 'Git merge', 'Vite', 'pytest')],
    'fullstack': [('Что фиксирует формат обмена frontend и backend?', 'API-контракт', 'CSS Module', 'Docker volume', 'Git tag'), ('Где должна проверяться авторизация?', 'На backend', 'Только в Navbar', 'Только в CSS', 'В README'), ('Что хранит данные LMS?', 'PostgreSQL', 'Nginx', 'Vite', 'Axios'), ('Кто проксирует HTTP-запросы в production-like схеме?', 'Nginx', 'Pillow', 'pytest', 'Zustand')],
}


ASSIGNMENTS = {
    'python': ('Консольный калькулятор', 'Реализуйте функцию, которая выполняет выбранную арифметическую операцию и корректно обрабатывает деление на ноль.', "def calculate(a, b, operation):\n    # Напишите решение\n    pass"),
    'algorithms': ('Поиск элемента', 'Реализуйте линейный поиск и верните индекс первого найденного элемента или -1.', "def find_index(items, target):\n    pass"),
    'html_css': ('Карточка курса', 'Сверстайте адаптивную карточку курса с заголовком, описанием и доступной кнопкой.', '<article class="course-card">\n  <!-- Добавьте разметку -->\n</article>'),
    'python_oop': ('Модель заказа', 'Создайте классы Order и OrderItem, вычисляющие итоговую стоимость заказа.', 'class Order:\n    def __init__(self):\n        self.items = []'),
    'django': ('Модель Course', 'Создайте Django-модель курса с названием, описанием и датами создания и обновления.', 'class Course(models.Model):\n    # Добавьте поля\n    pass'),
    'drf': ('API каталога', 'Реализуйте serializer и read-only endpoint для списка опубликованных курсов.', 'class CourseSerializer(serializers.ModelSerializer):\n    pass'),
    'javascript': ('Интерактивный список', 'Добавьте элементы списка из формы и реализуйте удаление по кнопке.', 'const items = [];\n\nfunction renderItems() {\n  // Напишите решение\n}'),
    'react': ('Компонент CourseCard', 'Создайте типизированный компонент карточки курса с названием, уровнем и кнопкой перехода.', 'interface CourseCardProps {\n  title: string;\n}\n\nexport function CourseCard(props: CourseCardProps) {\n  return null;\n}'),
    'postgresql': ('Отчёт по курсам', 'Напишите SQL-запрос, который выводит курсы и количество записанных студентов.', 'SELECT c.title\nFROM courses_course AS c\n-- Добавьте JOIN и группировку'),
    'git': ('История feature-ветки', 'Создайте feature-ветку, выполните два логичных коммита и подготовьте описание pull request.', '# Опишите последовательность команд и решения'),
    'docker': ('Контейнер приложения', 'Подготовьте Dockerfile для Python-приложения без запуска от root в итоговом образе.', 'FROM python:3.12-slim\n\n# Продолжите Dockerfile'),
    'fullstack': ('Endpoint курса', 'Спроектируйте защищённый endpoint создания курса и подключите его к типизированному frontend service.', '# Backend и frontend части решения'),
}


class Command(BaseCommand):
    help = 'Добавляет идемпотентный набор демонстрационных данных для локальной разработки.'

    def handle(self, *args, **options):
        self._ensure_safe_environment()
        self.stats = defaultdict(lambda: {'created': 0, 'existing': 0})
        self.stdout.write('Создание демонстрационных данных...')

        with transaction.atomic():
            categories = self._create_categories()
            teachers = self._create_users(TEACHERS, User.Role.TEACHER, 'Teachers')
            students = self._create_users(STUDENTS, User.Role.STUDENT, 'Students')
            courses = self._create_courses(categories, teachers)
            course_lessons = self._create_curriculum(courses)
            self._create_learning_activity(courses, course_lessons, students)
            self._create_notifications(students, courses)

        for label in (
            'Categories', 'Teachers', 'Students', 'Courses', 'Sections', 'Lessons',
            'Assignments', 'Quizzes', 'Questions', 'Answers', 'Enrollments',
            'Lesson progress', 'Submissions', 'Quiz attempts', 'Reviews',
            'Notifications', 'Certificates',
        ):
            values = self.stats[label]
            self.stdout.write(self.style.SUCCESS(
                f'[OK] {label}: created {values["created"]}, existing {values["existing"]}'
            ))
        self.stdout.write(self.style.SUCCESS('Демонстрационные данные готовы.'))
        self.stdout.write(self.style.WARNING(
            'DEVELOPMENT ONLY: пароль demo-аккаунтов нельзя использовать в production.'
        ))

    def _ensure_safe_environment(self):
        settings_module = settings.SETTINGS_MODULE or ''
        database_name = str(settings.DATABASES['default'].get('NAME') or '')
        is_test_database = database_name.startswith('test_')
        if settings_module.endswith('.production'):
            raise CommandError('SEED BLOCKED: PRODUCTION DATABASE DETECTED')
        if not settings_module.endswith('.development') and not is_test_database:
            raise CommandError(
                'SEED BLOCKED: окружение не распознано как development/test.'
            )

    def _record(self, label, created):
        key = 'created' if created else 'existing'
        self.stats[label][key] += 1

    def _create_categories(self):
        result = {}
        for name, slug, description in CATEGORIES:
            category = Category.objects.filter(slug=slug).first()
            if category is None:
                category = Category.objects.filter(name=name).first()
            created = category is None
            if created:
                category = Category.objects.create(name=name, slug=slug, description=description)
            self._record('Categories', created)
            result[slug] = category
        return result

    def _create_users(self, definitions, role, label):
        users = []
        for email, first_name, last_name in definitions:
            user = User.objects.filter(email=email).first()
            created = user is None
            if created:
                user = User.objects.create_user(
                    email=email,
                    password=DEMO_PASSWORD,
                    first_name=first_name,
                    last_name=last_name,
                    role=role,
                )
            elif user.role != role:
                raise CommandError(
                    f'Существующий пользователь {email} имеет другую роль; данные не изменены.'
                )
            self._record(label, created)
            users.append(user)
        return users

    def _create_courses(self, categories, teachers):
        result = {}
        for definition in COURSES:
            course, created = Course.objects.get_or_create(
                slug=definition['slug'],
                defaults={
                    'title': definition['title'],
                    'short_description': definition['short'],
                    'description': definition['description'],
                    'category': categories[definition['category']],
                    'teacher': teachers[definition['teacher']],
                    'level': definition['level'],
                    'duration': definition['duration'],
                    'price': Decimal(definition['price']),
                    'status': definition.get('status', Course.Status.PUBLISHED),
                },
            )
            self._record('Courses', created)
            result[definition['slug']] = (course, definition)
        return result

    def _create_curriculum(self, courses):
        course_lessons = {}
        for slug, (course, definition) in courses.items():
            ordered_lessons = []
            for section_order, section_definition in enumerate(definition['sections'], start=1):
                course_section, created = Section.objects.get_or_create(
                    course=course,
                    title=section_definition['title'],
                    defaults={
                        'description': f'Раздел курса «{course.title}»: {section_definition["title"]}.',
                        'order': section_order,
                    },
                )
                self._record('Sections', created)
                for local_order, lesson_title in enumerate(section_definition['lessons'], start=1):
                    global_order = (section_order - 1) * 2 + local_order
                    lesson_type = Lesson.Type.TEXT
                    if global_order == 4:
                        lesson_type = Lesson.Type.ASSIGNMENT
                    elif global_order == 6:
                        lesson_type = Lesson.Type.QUIZ
                    lesson, created = Lesson.objects.get_or_create(
                        section=course_section,
                        title=lesson_title,
                        defaults={
                            'description': f'Практический урок по теме «{lesson_title}».',
                            'type': lesson_type,
                            'content': (
                                f'В этом уроке курса «{course.title}» вы разберёте тему '
                                f'«{lesson_title}», изучите основные понятия и закрепите их на примере.'
                            ),
                            'duration': 20 + global_order * 3,
                            'order': local_order,
                            'is_free': global_order == 1,
                        },
                    )
                    self._record('Lessons', created)
                    ordered_lessons.append(lesson)

                    if global_order == 4:
                        title, description, starter_code = ASSIGNMENTS[definition['track']]
                        _, assignment_created = Assignment.objects.get_or_create(
                            lesson=lesson,
                            defaults={
                                'title': title,
                                'description': description,
                                'starter_code': starter_code,
                                'max_score': 100,
                            },
                        )
                        self._record('Assignments', assignment_created)
                    elif global_order == 6:
                        quiz, quiz_created = Quiz.objects.get_or_create(
                            lesson=lesson,
                            defaults={
                                'title': f'Проверка знаний: {course.title}',
                                'description': 'Ответьте на вопросы по пройденным темам.',
                                'passing_score': 70,
                            },
                        )
                        self._record('Quizzes', quiz_created)
                        self._create_questions(quiz, definition['track'])
            course_lessons[slug] = ordered_lessons
        return course_lessons

    def _create_questions(self, quiz, track):
        for order, (text, correct, *incorrect) in enumerate(QUIZ_BANK[track], start=1):
            question, created = Question.objects.get_or_create(
                quiz=quiz,
                question=text,
                defaults={'type': Question.Type.SINGLE, 'points': 1, 'order': order},
            )
            self._record('Questions', created)
            for answer_text in (correct, *incorrect):
                _, answer_created = Answer.objects.get_or_create(
                    question=question,
                    text=answer_text,
                    defaults={'is_correct': answer_text == correct},
                )
                self._record('Answers', answer_created)

    def _create_learning_activity(self, courses, course_lessons, students):
        free_slugs = ('demo-python-start', 'demo-algorithms', 'demo-html-css')
        enrollment_limits = (10, 7, 6)
        completion_steps = (8, 6, 4, 3, 7, 2, 5, 1, 4, 3)
        review_comments = (
            'Отличный курс для старта. Особенно понравились практические задания.',
            'Материал объясняется понятно, хотелось бы немного больше примеров.',
            'Хорошая структура курса и удобная последовательность уроков.',
            'Курс помог систематизировать знания и увереннее решать задачи.',
            'Полезные задания и понятные объяснения без лишней теории.',
        )

        for course_index, (slug, limit) in enumerate(zip(free_slugs, enrollment_limits)):
            course = courses[slug][0]
            lessons = course_lessons[slug]
            assignment = Assignment.objects.get(lesson=lessons[3])
            quiz = Quiz.objects.get(lesson=lessons[5])

            for student_index, student in enumerate(students[:limit]):
                enrollment, enrollment_created = Enrollment.objects.get_or_create(
                    student=student, course=course
                )
                self._record('Enrollments', enrollment_created)

                completed_count = min(
                    len(lessons),
                    max(1, completion_steps[(student_index + course_index) % len(completion_steps)] - course_index),
                )
                for lesson in lessons[:completed_count]:
                    progress, progress_created = LessonProgress.objects.get_or_create(
                        student=student,
                        lesson=lesson,
                        defaults={'is_completed': True, 'completed_at': timezone.now()},
                    )
                    self._record('Lesson progress', progress_created)

                if enrollment_created:
                    enrollment.progress = round(completed_count / len(lessons) * 100)
                    if completed_count == len(lessons):
                        enrollment.completed_at = timezone.now()
                    enrollment.save(update_fields=['progress', 'completed_at'])

                if student_index < 4:
                    statuses = (
                        AssignmentSubmission.Status.PENDING,
                        AssignmentSubmission.Status.ACCEPTED,
                        AssignmentSubmission.Status.REVISION,
                        AssignmentSubmission.Status.PENDING,
                    )
                    submission_status = statuses[(student_index + course_index) % len(statuses)]
                    score = 88 if submission_status == AssignmentSubmission.Status.ACCEPTED else None
                    _, submission_created = AssignmentSubmission.objects.get_or_create(
                        assignment=assignment,
                        student=student,
                        defaults={
                            'code': self._submission_code(course_index),
                            'status': submission_status,
                            'score': score,
                            'teacher_comment': (
                                'Хорошая работа, требования выполнены.' if score is not None
                                else 'Решение принято на проверку.'
                            ),
                        },
                    )
                    self._record('Submissions', submission_created)

                attempt_key = f'demo:{slug}:{student.email}'
                _, attempt_created = QuizAttempt.objects.get_or_create(
                    quiz=quiz,
                    student=student,
                    answers_snapshot={'demo_seed_key': attempt_key},
                    defaults={
                        'score': 65 + ((student_index + course_index) % 4) * 10,
                        'passed': ((65 + ((student_index + course_index) % 4) * 10) >= quiz.passing_score),
                    },
                )
                self._record('Quiz attempts', attempt_created)

                if student_index < limit - 1:
                    _, review_created = Review.objects.get_or_create(
                        course=course,
                        student=student,
                        defaults={
                            'rating': (5, 4, 5, 3, 4)[(student_index + course_index) % 5],
                            'comment': review_comments[(student_index + course_index) % len(review_comments)],
                        },
                    )
                    self._record('Reviews', review_created)

            first_student = students[0]
            completed = LessonProgress.objects.filter(
                student=first_student,
                lesson__in=lessons,
                is_completed=True,
            ).count()
            enrollment = Enrollment.objects.get(student=first_student, course=course)
            if completed == len(lessons) and enrollment.completed_at:
                existed = Certificate.objects.filter(student=first_student, course=course).exists()
                issue_certificate(first_student, course)
                self._record('Certificates', not existed)

    def _submission_code(self, course_index):
        examples = (
            "def calculate(a, b, operation):\n    return a + b if operation == '+' else a - b",
            'def find_index(items, target):\n    return items.index(target) if target in items else -1',
            '<article class="course-card"><h2>Курс</h2><button>Открыть</button></article>',
        )
        return examples[course_index]

    def _create_notifications(self, students, courses):
        python_course = courses['demo-python-start'][0]
        for index, student in enumerate(students):
            notifications = (
                (
                    Notification.Type.COURSE,
                    'Добро пожаловать в обучение',
                    f'Курс «{python_course.title}» добавлен в раздел «Мои курсы».',
                    '/my-courses',
                    index > 2,
                ),
                (
                    Notification.Type.ASSIGNMENT,
                    'Доступно новое практическое задание',
                    'Откройте урок и закрепите материал на практике.',
                    f'/courses/{python_course.id}',
                    index % 2 == 0,
                ),
            )
            for notification_index, (type_, title, message, link, is_read) in enumerate(notifications):
                seed_key = f'demo:{index}:{notification_index}'
                notification = Notification.objects.filter(
                    user=student,
                    metadata__seed_key=seed_key,
                ).first()
                created = notification is None
                if created:
                    Notification.objects.create(
                        user=student,
                        type=type_,
                        title=title,
                        message=message,
                        link=link,
                        is_read=is_read,
                        read_at=timezone.now() if is_read else None,
                        metadata={'seed_key': seed_key},
                    )
                self._record('Notifications', created)
