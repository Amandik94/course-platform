import pytest
from django.urls import reverse
from rest_framework import status

from apps.courses.models import Section
from apps.lessons.models import Lesson
from apps.assignments.models import Assignment, AssignmentSubmission
from apps.enrollments.models import Enrollment


@pytest.fixture
def assignment_fixture(published_course, student_user):
    Enrollment.objects.create(student=student_user, course=published_course)
    section = Section.objects.create(course=published_course, title='Раздел', order=1)
    lesson = Lesson.objects.create(section=section, title='Задание', type='assignment', order=1)
    return Assignment.objects.create(
        lesson=lesson, title='Реализуйте функцию', description='...', max_score=100,
    )


@pytest.mark.django_db
class TestAssignmentSubmission:
    def test_submit_creates_pending_submission(self, student_client, assignment_fixture, student_user):
        response = student_client.post(
            reverse('assignment-submit', kwargs={'id': assignment_fixture.id}),
            {'code': 'def f(): pass'},
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'pending'

    def test_resubmit_updates_existing_not_duplicates(self, student_client, assignment_fixture, student_user):
        student_client.post(
            reverse('assignment-submit', kwargs={'id': assignment_fixture.id}), {'code': 'v1'}
        )
        student_client.post(
            reverse('assignment-submit', kwargs={'id': assignment_fixture.id}), {'code': 'v2'}
        )

        assert AssignmentSubmission.objects.filter(
            assignment=assignment_fixture, student=student_user
        ).count() == 1
        submission = AssignmentSubmission.objects.get(assignment=assignment_fixture, student=student_user)
        assert submission.code == 'v2'

    def test_resubmit_resets_score_and_status(self, student_client, assignment_fixture, student_user):
        submission = AssignmentSubmission.objects.create(
            assignment=assignment_fixture, student=student_user, code='v1',
            status='accepted', score=90, teacher_comment='Good',
        )
        student_client.post(
            reverse('assignment-submit', kwargs={'id': assignment_fixture.id}), {'code': 'v2 improved'}
        )

        submission.refresh_from_db()
        assert submission.status == 'pending'
        assert submission.score is None
        assert submission.teacher_comment == ''

    def test_student_cannot_set_own_score(self, student_client, assignment_fixture):
        """Студент физически не может передать score/status через свой
        сериализатор — read_only_fields должны их игнорировать."""
        response = student_client.post(
            reverse('assignment-submit', kwargs={'id': assignment_fixture.id}),
            {'code': 'x', 'score': 100, 'status': 'accepted'},
        )
        assert response.data['status'] == 'pending'
        assert response.data['score'] is None

    def test_teacher_can_review_submission(self, teacher_client, assignment_fixture, student_user, teacher_user):
        assignment_fixture.lesson.section.course.teacher = teacher_user
        assignment_fixture.lesson.section.course.save()
        submission = AssignmentSubmission.objects.create(
            assignment=assignment_fixture, student=student_user, code='x', status='pending',
        )

        response = teacher_client.patch(
            reverse('submission-review', kwargs={'pk': submission.id}),
            {'status': 'accepted', 'score': 95, 'teacher_comment': 'Отлично'},
        )
        assert response.status_code == status.HTTP_200_OK
        submission.refresh_from_db()
        assert submission.status == 'accepted'
        assert submission.score == 95

    def test_other_teacher_cannot_review(self, api_client, assignment_fixture, student_user, django_user_model):
        other_teacher = django_user_model.objects.create_user(
            email='other@test.com', password='pass12345', role='teacher',
        )
        submission = AssignmentSubmission.objects.create(
            assignment=assignment_fixture, student=student_user, code='x', status='pending',
        )
        api_client.force_authenticate(user=other_teacher)

        response = api_client.patch(
            reverse('submission-review', kwargs={'pk': submission.id}),
            {'status': 'accepted', 'score': 100},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_accepted_status_requires_score(self, teacher_client, assignment_fixture, student_user, teacher_user):
        assignment_fixture.lesson.section.course.teacher = teacher_user
        assignment_fixture.lesson.section.course.save()
        submission = AssignmentSubmission.objects.create(
            assignment=assignment_fixture, student=student_user, code='x', status='pending',
        )

        response = teacher_client.patch(
            reverse('submission-review', kwargs={'pk': submission.id}), {'status': 'accepted'},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST