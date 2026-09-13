import pytest
from django.urls import reverse
from rest_framework import status

from apps.assignments.models import Assignment, AssignmentSubmission
from apps.courses.models import Course, Section
from apps.enrollments.models import Enrollment
from apps.lessons.models import Lesson
from apps.notifications.models import Notification


@pytest.fixture
def other_student(django_user_model):
    return django_user_model.objects.create_user(
        email='other-student@test.com',
        password='testpass123',
        role='student',
    )


@pytest.fixture
def course_with_assignment(published_course):
    section = Section.objects.create(course=published_course, title='Basics', order=1)
    lesson = Lesson.objects.create(
        section=section,
        title='Homework',
        type=Lesson.Type.ASSIGNMENT,
        content='Solve the task',
        order=1,
    )
    assignment = Assignment.objects.create(
        lesson=lesson,
        title='First task',
        description='Submit code',
        max_score=100,
    )
    return published_course, assignment


@pytest.mark.django_db
class TestNotificationsApi:
    def test_anonymous_cannot_get_notifications(self, api_client):
        response = api_client.get(reverse('notification-list'))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_sees_only_own_notifications(self, student_client, student_user, other_student):
        own = Notification.objects.create(user=student_user, type=Notification.Type.SYSTEM, title='Own')
        Notification.objects.create(user=other_student, type=Notification.Type.SYSTEM, title='Other')

        response = student_client.get(reverse('notification-list'))

        assert response.status_code == status.HTTP_200_OK
        titles = [item['title'] for item in response.data['results']]
        assert titles == [own.title]

    def test_user_cannot_mark_foreign_notification_read(self, student_client, other_student):
        notification = Notification.objects.create(
            user=other_student,
            type=Notification.Type.SYSTEM,
            title='Private',
        )

        response = student_client.patch(reverse('notification-read', kwargs={'pk': notification.id}))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unread_count_returns_current_user_count(self, student_client, student_user, other_student):
        Notification.objects.create(user=student_user, type=Notification.Type.SYSTEM, title='Unread')
        Notification.objects.create(user=student_user, type=Notification.Type.SYSTEM, title='Read', is_read=True)
        Notification.objects.create(user=other_student, type=Notification.Type.SYSTEM, title='Foreign')

        response = student_client.get(reverse('notification-unread-count'))

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'count': 1}

    def test_mark_as_read_sets_read_at(self, student_client, student_user):
        notification = Notification.objects.create(
            user=student_user,
            type=Notification.Type.SYSTEM,
            title='Unread',
        )

        response = student_client.patch(reverse('notification-read', kwargs={'pk': notification.id}))

        assert response.status_code == status.HTTP_200_OK
        notification.refresh_from_db()
        assert notification.is_read is True
        assert notification.read_at is not None

    def test_mark_all_as_read_only_affects_current_user(self, student_client, student_user, other_student):
        own = Notification.objects.create(user=student_user, type=Notification.Type.SYSTEM, title='Own')
        foreign = Notification.objects.create(user=other_student, type=Notification.Type.SYSTEM, title='Foreign')

        response = student_client.post(reverse('notification-read-all'))

        assert response.status_code == status.HTTP_200_OK
        own.refresh_from_db()
        foreign.refresh_from_db()
        assert own.is_read is True
        assert own.read_at is not None
        assert foreign.is_read is False

    def test_user_can_delete_own_notification(self, student_client, student_user):
        notification = Notification.objects.create(user=student_user, type=Notification.Type.SYSTEM, title='Delete me')

        response = student_client.delete(reverse('notification-detail', kwargs={'pk': notification.id}))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Notification.objects.filter(id=notification.id).exists()


@pytest.mark.django_db
class TestNotificationEvents:
    def test_assignment_review_creates_student_notification(
        self, teacher_client, student_user, course_with_assignment,
    ):
        course, assignment = course_with_assignment
        Enrollment.objects.create(student=student_user, course=course)
        submission = AssignmentSubmission.objects.create(
            assignment=assignment,
            student=student_user,
            code='print("ok")',
        )

        response = teacher_client.patch(
            reverse('submission-review', kwargs={'pk': submission.id}),
            {'status': AssignmentSubmission.Status.ACCEPTED, 'score': 90, 'teacher_comment': 'Good'},
        )

        assert response.status_code == status.HTTP_200_OK
        assert Notification.objects.filter(
            user=student_user,
            type=Notification.Type.ASSIGNMENT,
            link=f'/assignment/{assignment.id}',
        ).exists()

    def test_certificate_notification_created_on_course_completion(
        self, student_client, student_user, published_course,
    ):
        section = Section.objects.create(course=published_course, title='Basics', order=1)
        lesson = Lesson.objects.create(
            section=section,
            title='Intro',
            type=Lesson.Type.TEXT,
            content='Intro',
            order=1,
        )
        Enrollment.objects.create(student=student_user, course=published_course)

        response = student_client.post(reverse('lesson-complete', kwargs={'id': lesson.id}))

        assert response.status_code == status.HTTP_200_OK
        assert response.data['course_completed'] is True
        assert Notification.objects.filter(
            user=student_user,
            type=Notification.Type.CERTIFICATE,
            link='/certificates',
        ).exists()
