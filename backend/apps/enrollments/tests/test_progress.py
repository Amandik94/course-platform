import pytest
from django.urls import reverse
from rest_framework import status

from apps.courses.models import Section
from apps.lessons.models import Lesson
from apps.enrollments.models import Enrollment, LessonProgress


@pytest.fixture
def course_with_lessons(published_course):
    section = Section.objects.create(course=published_course, title='Раздел 1', order=1)
    lessons = [
        Lesson.objects.create(section=section, title=f'Урок {i}', type='text', order=i)
        for i in range(1, 4)  # 3 урока
    ]
    return published_course, lessons


@pytest.mark.django_db
class TestLessonProgress:
    def test_complete_lesson_without_enrollment_returns_403(self, student_client, course_with_lessons):
        _, lessons = course_with_lessons
        response = student_client.post(reverse('lesson-complete', kwargs={'id': lessons[0].id}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_complete_lesson_creates_progress(self, student_client, student_user, course_with_lessons):
        course, lessons = course_with_lessons
        Enrollment.objects.create(student=student_user, course=course)

        response = student_client.post(reverse('lesson-complete', kwargs={'id': lessons[0].id}))

        assert response.status_code == status.HTTP_200_OK
        assert LessonProgress.objects.filter(
            student=student_user, lesson=lessons[0], is_completed=True
        ).exists()

    def test_progress_percentage_calculated_correctly(self, student_client, student_user, course_with_lessons):
        course, lessons = course_with_lessons  # 3 урока
        Enrollment.objects.create(student=student_user, course=course)

        student_client.post(reverse('lesson-complete', kwargs={'id': lessons[0].id}))
        response = student_client.post(reverse('lesson-complete', kwargs={'id': lessons[1].id}))

        # 2 из 3 уроков пройдено = 67% (округление round(2/3*100))
        assert response.data['enrollment_progress'] == 67

    def test_course_completion_at_100_percent(self, student_client, student_user, course_with_lessons):
        course, lessons = course_with_lessons

        enrollment = Enrollment.objects.create(student=student_user, course=course)
        assert enrollment.completed_at is None

        for lesson in lessons:
            response = student_client.post(reverse('lesson-complete', kwargs={'id': lesson.id}))

        assert response.data['course_completed'] is True
        assert response.data['enrollment_progress'] == 100

        enrollment.refresh_from_db()
        assert enrollment.completed_at is not None

    def test_repeated_completion_is_idempotent(self, student_client, student_user, course_with_lessons):
        """Повторное завершение уже пройденного урока не должно ломать
        прогресс или создавать дубликаты LessonProgress."""
        course, lessons = course_with_lessons
        Enrollment.objects.create(student=student_user, course=course)

        student_client.post(reverse('lesson-complete', kwargs={'id': lessons[0].id}))
        response = student_client.post(reverse('lesson-complete', kwargs={'id': lessons[0].id}))

        assert response.status_code == status.HTTP_200_OK
        assert LessonProgress.objects.filter(student=student_user, lesson=lessons[0]).count() == 1

    def test_certificate_issued_on_completion(self, student_client, student_user, course_with_lessons):
        """Сквозной тест интеграции с certificates app —
        проверяет, что модули действительно связаны корректно."""
        from apps.certificates.models import Certificate

        course, lessons = course_with_lessons
        Enrollment.objects.create(student=student_user, course=course)

        for lesson in lessons:
            student_client.post(reverse('lesson-complete', kwargs={'id': lesson.id}))

        assert Certificate.objects.filter(student=student_user, course=course).exists()