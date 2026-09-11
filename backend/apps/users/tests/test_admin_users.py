import pytest
from django.urls import reverse
from rest_framework import status

from apps.users.models import User


@pytest.mark.django_db
class TestAdminUsersApi:
    def test_anonymous_denied(self, api_client):
        response = api_client.get(reverse('admin-user-list'))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_student_denied(self, student_client):
        response = student_client.get(reverse('admin-user-list'))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_teacher_denied(self, teacher_client):
        response = teacher_client.get(reverse('admin-user-list'))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_list_and_filter_users(self, admin_client, student_user, teacher_user):
        response = admin_client.get(reverse('admin-user-list'), {'role': User.Role.TEACHER})

        assert response.status_code == status.HTTP_200_OK
        emails = [item['email'] for item in response.data['results']]
        assert teacher_user.email in emails
        assert student_user.email not in emails

    def test_admin_can_block_and_unblock_user(self, admin_client, student_user):
        detail_url = reverse('admin-user-detail', kwargs={'id': student_user.id})

        blocked = admin_client.patch(detail_url, {'is_active': False})
        assert blocked.status_code == status.HTTP_200_OK
        student_user.refresh_from_db()
        assert student_user.is_active is False

        unblocked = admin_client.patch(detail_url, {'is_active': True})
        assert unblocked.status_code == status.HTTP_200_OK
        student_user.refresh_from_db()
        assert student_user.is_active is True

    def test_admin_cannot_change_superuser_or_staff_flags(self, admin_client, student_user):
        response = admin_client.patch(
            reverse('admin-user-detail', kwargs={'id': student_user.id}),
            {'is_superuser': True, 'is_staff': True},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        student_user.refresh_from_db()
        assert student_user.is_superuser is False
        assert student_user.is_staff is False

    def test_admin_cannot_block_self(self, admin_client, admin_user):
        response = admin_client.patch(
            reverse('admin-user-detail', kwargs={'id': admin_user.id}),
            {'is_active': False},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        admin_user.refresh_from_db()
        assert admin_user.is_active is True
