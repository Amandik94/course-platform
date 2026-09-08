import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestMeEndpoint:
    def test_unauthenticated_cannot_access_me(self, api_client):
        response = api_client.get(reverse('auth-me'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_gets_own_profile(self, student_client, student_user):
        response = student_client.get(reverse('auth-me'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == student_user.email

    def test_user_cannot_change_own_role_via_me(self, student_client, student_user):
        """Критичный тест: read_only_fields на role должны реально работать,
        не только теоретически быть объявлены в сериализаторе."""
        response = student_client.patch(reverse('auth-me'), {'role': 'admin'})

        student_user.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK  # запрос не падает...
        assert student_user.role == 'student'  # ...но роль не изменилась

    def test_user_cannot_change_email_via_me(self, student_client, student_user):
        response = student_client.patch(reverse('auth-me'), {'email': 'newmail@test.com'})

        student_user.refresh_from_db()
        assert student_user.email != 'newmail@test.com'