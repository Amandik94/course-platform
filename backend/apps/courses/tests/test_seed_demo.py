from io import StringIO

import pytest
from django.core.management import call_command

from apps.assignments.models import Assignment
from apps.certificates.models import Certificate
from apps.courses.models import Category, Course, Section
from apps.enrollments.models import Enrollment, LessonProgress
from apps.lessons.models import Lesson
from apps.notifications.models import Notification
from apps.payments.models import Payment
from apps.quizzes.models import Question, Quiz
from apps.reviews.models import Review
from apps.users.models import User


DEMO_COURSE_SLUGS = [
    'demo-python-start',
    'demo-algorithms',
    'demo-html-css',
    'demo-python-oop',
    'demo-django-start',
    'demo-drf-api',
    'demo-modern-javascript',
    'demo-react-typescript',
    'demo-postgresql',
    'demo-git-github',
    'demo-docker-junior',
    'demo-fullstack-django-react',
]


def demo_counts():
    course_filter = {'course__slug__in': DEMO_COURSE_SLUGS}
    return {
        'users': User.objects.filter(email__endswith='.demo@example.com').count(),
        'courses': Course.objects.filter(slug__in=DEMO_COURSE_SLUGS).count(),
        'sections': Section.objects.filter(**course_filter).count(),
        'lessons': Lesson.objects.filter(section__course__slug__in=DEMO_COURSE_SLUGS).count(),
        'assignments': Assignment.objects.filter(
            lesson__section__course__slug__in=DEMO_COURSE_SLUGS
        ).count(),
        'quizzes': Quiz.objects.filter(
            lesson__section__course__slug__in=DEMO_COURSE_SLUGS
        ).count(),
        'questions': Question.objects.filter(
            quiz__lesson__section__course__slug__in=DEMO_COURSE_SLUGS
        ).count(),
        'enrollments': Enrollment.objects.filter(**course_filter).count(),
        'progress': LessonProgress.objects.filter(
            lesson__section__course__slug__in=DEMO_COURSE_SLUGS
        ).count(),
        'reviews': Review.objects.filter(**course_filter).count(),
        'notifications': Notification.objects.filter(
            metadata__seed_key__startswith='demo:'
        ).count(),
        'certificates': Certificate.objects.filter(**course_filter).count(),
    }


@pytest.mark.django_db
def test_seed_demo_is_idempotent_and_does_not_create_payments(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    existing_category = Category.objects.create(
        name='Пользовательская категория',
        slug='user-owned-category',
    )
    payments_before = Payment.objects.count()

    call_command('seed_demo', stdout=StringIO())

    teacher = User.objects.get(email='teacher.python.demo@example.com')
    first_counts = demo_counts()

    assert teacher.role == User.Role.TEACHER
    assert teacher.check_password('Demo12345!')
    assert first_counts['users'] == 14
    assert first_counts['courses'] == 12
    assert first_counts['sections'] == 48
    assert first_counts['lessons'] == 96
    assert first_counts['assignments'] == 12
    assert first_counts['quizzes'] == 12
    assert first_counts['questions'] == 48
    assert first_counts['reviews'] >= 20
    assert first_counts['certificates'] == 1
    assert Payment.objects.count() == payments_before
    assert Category.objects.filter(pk=existing_category.pk).exists()

    call_command('seed_demo', stdout=StringIO())

    assert demo_counts() == first_counts
    assert Payment.objects.count() == payments_before
