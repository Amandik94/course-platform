import pytest
from django.urls import reverse
from rest_framework import status

from apps.courses.models import Section
from apps.enrollments.models import Enrollment
from apps.lessons.models import Lesson


@pytest.fixture
def lessons_for_access(published_course):
    section = Section.objects.create(course=published_course, title='Access', order=1)
    public_lesson = Lesson.objects.create(
        section=section, title='Preview', type='text', content='Preview', order=1, is_free=True
    )
    private_lesson = Lesson.objects.create(
        section=section, title='Private', type='text', content='Private', order=2, is_free=False
    )
    return section, public_lesson, private_lesson


@pytest.mark.django_db
class TestLessonAccess:
    def test_anonymous_sees_only_free_lessons_in_list(self, api_client, lessons_for_access):
        section, public_lesson, private_lesson = lessons_for_access

        response = api_client.get(reverse('lesson-list', kwargs={'section_id': section.id}))

        assert response.status_code == status.HTTP_200_OK
        lesson_ids = {lesson['id'] for lesson in response.data}
        assert public_lesson.id in lesson_ids
        assert private_lesson.id not in lesson_ids

    def test_student_without_enrollment_cannot_read_private_lesson(self, student_client, lessons_for_access):
        _, _, private_lesson = lessons_for_access

        response = student_client.get(reverse('lesson-detail', kwargs={'pk': private_lesson.id}))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_enrolled_student_can_read_private_lesson(
        self, student_client, student_user, published_course, lessons_for_access,
    ):
        _, _, private_lesson = lessons_for_access
        Enrollment.objects.create(student=student_user, course=published_course)

        response = student_client.get(reverse('lesson-detail', kwargs={'pk': private_lesson.id}))

        assert response.status_code == status.HTTP_200_OK
