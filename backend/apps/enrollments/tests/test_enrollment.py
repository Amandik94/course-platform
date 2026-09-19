import pytest
from django.urls import reverse
from rest_framework import status

from apps.enrollments.models import Enrollment


@pytest.mark.django_db
class TestEnrollment:
    def test_student_can_enroll(self, student_client, published_course):
        response = student_client.post(
            reverse('course-enroll', kwargs={'id': published_course.id})
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Enrollment.objects.filter(
            student__email='student@test.com', course=published_course
        ).exists()

    def test_cannot_enroll_twice(self, student_client, published_course, student_user):
        Enrollment.objects.create(student=student_user, course=published_course)

        response = student_client.post(
            reverse('course-enroll', kwargs={'id': published_course.id})
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Enrollment.objects.filter(student=student_user, course=published_course).count() == 1

    def test_teacher_cannot_enroll(self, teacher_client, published_course):
        response = teacher_client.post(
            reverse('course-enroll', kwargs={'id': published_course.id})
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cannot_enroll_in_draft_course(self, student_client, teacher_user, category):
        from apps.courses.models import Course
        draft_course = Course.objects.create(
            title='Draft', short_description='...', description='...',
            category=category, teacher=teacher_user, status=Course.Status.DRAFT,
        )
        response = student_client.post(reverse('course-enroll', kwargs={'id': draft_course.id}))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_cannot_enroll_paid_course_without_payment(self, student_client, published_course):
        published_course.price = '12000.00'
        published_course.save(update_fields=['price'])

        response = student_client.post(
            reverse('course-enroll', kwargs={'id': published_course.id})
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Enrollment.objects.filter(course=published_course).count() == 0

    def test_unique_constraint_at_db_level(self, published_course, student_user):
        """Даже в обход API (например, прямой ORM-вызов), constraint 
        на уровне БД должен предотвращать дубликаты."""
        from django.db import IntegrityError

        Enrollment.objects.create(student=student_user, course=published_course)
        with pytest.raises(IntegrityError):
            Enrollment.objects.create(student=student_user, course=published_course)
