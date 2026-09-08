import pytest
from rest_framework.test import APIClient

from apps.users.models import User
from apps.courses.models import Category, Course


@pytest.fixture
def api_client():
    """Неавторизованный клиент — для тестов публичных эндпоинтов и регистрации."""
    return APIClient()


@pytest.fixture
def student_user(db):
    return User.objects.create_user(
        email='student@test.com',
        password='testpass123',
        first_name='Анна',
        last_name='Студентова',
        role=User.Role.STUDENT,
    )


@pytest.fixture
def teacher_user(db):
    return User.objects.create_user(
        email='teacher@test.com',
        password='testpass123',
        first_name='Пётр',
        last_name='Преподавателев',
        role=User.Role.TEACHER,
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        email='admin@test.com',
        password='testpass123',
        first_name='Админ',
        last_name='Админов',
        role=User.Role.ADMIN,
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def student_client(api_client, student_user):
    """API-клиент, уже авторизованный как студент."""
    api_client.force_authenticate(user=student_user)
    return api_client


@pytest.fixture
def teacher_client(api_client, teacher_user):
    api_client.force_authenticate(user=teacher_user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def category(db):
    return Category.objects.create(
        name='Python',
        description='Курсы по Python',
    )


@pytest.fixture
def published_course(db, teacher_user, category):
    return Course.objects.create(
        title='Django для начинающих',
        short_description='...',
        description='...',
        category=category,
        teacher=teacher_user,
        level='junior',
        status=Course.Status.PUBLISHED,
    )