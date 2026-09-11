import pytest
from django.urls import reverse
from rest_framework import status

from apps.courses.models import Category


@pytest.mark.django_db
class TestCategoryApi:
    def test_public_can_read_categories(self, api_client, category):
        response = api_client.get(reverse('category-list'))

        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['name'] == category.name

    def test_non_admin_cannot_create_category(self, teacher_client):
        response = teacher_client.post(reverse('category-list'), {'name': 'JS'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_create_update_delete_category(self, admin_client):
        created = admin_client.post(
            reverse('category-list'),
            {'name': 'Frontend', 'description': 'React courses'},
        )
        assert created.status_code == status.HTTP_201_CREATED

        category_id = created.data['id']
        updated = admin_client.patch(
            reverse('category-detail', kwargs={'id': category_id}),
            {'description': 'React and TypeScript'},
        )
        assert updated.status_code == status.HTTP_200_OK
        assert updated.data['description'] == 'React and TypeScript'

        deleted = admin_client.delete(reverse('category-detail', kwargs={'id': category_id}))
        assert deleted.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(id=category_id).exists()

    def test_cannot_delete_category_with_courses(self, admin_client, published_course, category):
        response = admin_client.delete(reverse('category-detail', kwargs={'id': category.id}))

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Category.objects.filter(id=category.id).exists()
