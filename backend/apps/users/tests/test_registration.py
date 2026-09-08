import pytest
from django.urls import reverse
from rest_framework import status

from apps.users.models import User


@pytest.mark.django_db
class TestRegistration:
    def test_successful_registration_returns_tokens(self, api_client):
        url = reverse('auth-register')
        payload = {
            'email': 'newuser@test.com',
            'password': 'strongpass123',
            'password_confirm': 'strongpass123',
            'first_name': 'Иван',
            'last_name': 'Иванов',
        }
        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == 'newuser@test.com'
        assert User.objects.filter(email='newuser@test.com').exists()

    def test_password_mismatch_returns_400(self, api_client):
        url = reverse('auth-register')
        payload = {
            'email': 'newuser@test.com',
            'password': 'strongpass123',
            'password_confirm': 'different123',
            'first_name': 'Иван',
            'last_name': 'Иванов',
        }
        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in response.data

    def test_duplicate_email_returns_400(self, api_client, student_user):
        url = reverse('auth-register')
        payload = {
            'email': student_user.email,  # уже занят фикстурой student_user
            'password': 'strongpass123',
            'password_confirm': 'strongpass123',
            'first_name': 'Иван',
            'last_name': 'Иванов',
        }
        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_register_as_admin(self, api_client):
        """Критичный security-тест: публичная регистрация не должна
        позволять создать администратора платформы."""
        url = reverse('auth-register')
        payload = {
            'email': 'hacker@test.com',
            'password': 'strongpass123',
            'password_confirm': 'strongpass123',
            'first_name': 'Х',
            'last_name': 'Х',
            'role': 'admin',
        }
        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST