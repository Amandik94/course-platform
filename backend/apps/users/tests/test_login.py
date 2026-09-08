import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestLogin:
    def test_successful_login_returns_tokens(self, api_client, student_user):
        url = reverse('auth-login')
        response = api_client.post(url, {'email': student_user.email, 'password': 'testpass123'})

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_wrong_password_returns_400(self, api_client, student_user):
        url = reverse('auth-login')
        response = api_client.post(url, {'email': student_user.email, 'password': 'wrongpassword'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Неверный email или пароль' in str(response.data)

    def test_inactive_user_cannot_login(self, api_client, student_user):
        student_user.is_active = False
        student_user.save()

        url = reverse('auth-login')
        response = api_client.post(url, {'email': student_user.email, 'password': 'testpass123'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_token_refresh_flow(self, api_client, student_user):
        """Полный цикл: логин → получить refresh → обновить access."""
        login_response = api_client.post(
            reverse('auth-login'), {'email': student_user.email, 'password': 'testpass123'}
        )
        refresh_token = login_response.data['refresh']

        refresh_response = api_client.post(reverse('auth-refresh'), {'refresh': refresh_token})

        assert refresh_response.status_code == status.HTTP_200_OK
        assert 'access' in refresh_response.data

    def test_logout_blacklists_refresh_token(self, student_client, student_user):
        login_response = student_client.post(
            reverse('auth-login'), {'email': student_user.email, 'password': 'testpass123'}
        )
        refresh_token = login_response.data['refresh']

        logout_response = student_client.post(reverse('auth-logout'), {'refresh': refresh_token})
        assert logout_response.status_code == status.HTTP_205_RESET_CONTENT

        # повторное использование того же refresh должно провалиться — токен должен быть занесён в чёрный список
        second_refresh_attempt = student_client.post(reverse('auth-refresh'), {'refresh': refresh_token})
        assert second_refresh_attempt.status_code == status.HTTP_401_UNAUTHORIZED