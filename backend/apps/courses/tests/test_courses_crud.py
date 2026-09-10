import pytest
from django.urls import reverse
from rest_framework import status

from apps.courses.models import Course


@pytest.mark.django_db
class TestCourseList:
    def test_anonymous_sees_only_published_courses(self, api_client, teacher_user, category):
        Course.objects.create(
            title='Published', short_description='...', description='...',
            category=category, teacher=teacher_user, status=Course.Status.PUBLISHED,
        )
        Course.objects.create(
            title='Draft', short_description='...', description='...',
            category=category, teacher=teacher_user, status=Course.Status.DRAFT,
        )

        response = api_client.get(reverse('course-list'))

        titles = [c['title'] for c in response.data['results']]
        assert 'Published' in titles
        assert 'Draft' not in titles

    def test_teacher_sees_own_drafts_but_not_others(
        self, api_client, teacher_user, category, django_user_model,
    ):
        other_teacher = django_user_model.objects.create_user(
            email='other@test.com', password='pass12345', role='teacher',
        )
        Course.objects.create(
            title='My Draft', short_description='...', description='...',
            category=category, teacher=teacher_user, status=Course.Status.DRAFT,
        )
        Course.objects.create(
            title='Their Draft', short_description='...', description='...',
            category=category, teacher=other_teacher, status=Course.Status.DRAFT,
        )
        api_client.force_authenticate(user=teacher_user)

        response = api_client.get(reverse('course-list'))
        titles = [c['title'] for c in response.data['results']]

        assert 'My Draft' in titles
        assert 'Their Draft' not in titles

    def test_anonymous_cannot_retrieve_draft_course_detail(self, api_client, teacher_user, category):
        draft = Course.objects.create(
            title='Hidden Draft', short_description='...', description='...',
            category=category, teacher=teacher_user, status=Course.Status.DRAFT,
        )

        response = api_client.get(reverse('course-detail', kwargs={'id': draft.id}))

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCourseCreate:
    def test_student_cannot_create_course(self, student_client, category):
        response = student_client.post(reverse('course-list'), {
            'title': 'Hack Course', 'short_description': '...', 'description': '...',
            'category_id': category.id, 'level': 'junior',
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_teacher_can_create_course(self, teacher_client, category, teacher_user):
        response = teacher_client.post(reverse('course-list'), {
            'title': 'New Course', 'short_description': '...', 'description': '...',
            'category_id': category.id, 'level': 'junior',
        })
        assert response.status_code == status.HTTP_201_CREATED
        # проверяем, что teacher выставился из request.user, а не мог быть подменён
        assert response.data['teacher']['email'] == teacher_user.email

    def test_unauthenticated_cannot_create_course(self, api_client, category):
        response = api_client.post(reverse('course-list'), {'title': 'X'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCourseOwnership:
    def test_teacher_cannot_edit_others_course(
        self, api_client, published_course, django_user_model,
    ):
        other_teacher = django_user_model.objects.create_user(
            email='other@test.com', password='pass12345', role='teacher',
        )
        api_client.force_authenticate(user=other_teacher)

        response = api_client.patch(
            reverse('course-detail', kwargs={'id': published_course.id}),
            {'title': 'Hacked title'},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_teacher_can_edit_own_course(self, teacher_client, published_course):
        response = teacher_client.patch(
            reverse('course-detail', kwargs={'id': published_course.id}),
            {'title': 'Updated title'},
        )
        assert response.status_code == status.HTTP_200_OK
        published_course.refresh_from_db()
        assert published_course.title == 'Updated title'

    def test_cannot_delete_course_with_enrollments(
        self, teacher_client, published_course, student_user,
    ):
        from apps.enrollments.models import Enrollment
        Enrollment.objects.create(student=student_user, course=published_course)

        response = teacher_client.delete(
            reverse('course-detail', kwargs={'id': published_course.id})
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Course.objects.filter(id=published_course.id).exists()
