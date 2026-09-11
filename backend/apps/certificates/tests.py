import pytest
from django.urls import reverse
from rest_framework import status

from apps.certificates.models import Certificate


@pytest.mark.django_db
class TestCertificateAccess:
    def test_student_sees_only_own_certificates(self, api_client, student_user, published_course, django_user_model):
        other_student = django_user_model.objects.create_user(
            email='cert-other@test.com',
            password='pass12345',
            first_name='Other',
            last_name='Student',
            role='student',
        )
        own = Certificate.objects.create(
            student=student_user,
            course=published_course,
            certificate_number='CERT-OWN',
        )
        Certificate.objects.create(
            student=other_student,
            course=published_course,
            certificate_number='CERT-OTHER',
        )
        api_client.force_authenticate(user=student_user)

        response = api_client.get(reverse('certificate-list'))

        assert response.status_code == status.HTTP_200_OK
        numbers = [item['certificate_number'] for item in response.data['results']]
        assert own.certificate_number in numbers
        assert 'CERT-OTHER' not in numbers

    def test_student_cannot_read_other_certificate_detail(self, api_client, student_user, published_course, django_user_model):
        other_student = django_user_model.objects.create_user(
            email='cert-detail-other@test.com',
            password='pass12345',
            first_name='Other',
            last_name='Student',
            role='student',
        )
        certificate = Certificate.objects.create(
            student=other_student,
            course=published_course,
            certificate_number='CERT-DETAIL-OTHER',
        )
        api_client.force_authenticate(user=student_user)

        response = api_client.get(reverse('certificate-detail', kwargs={'pk': certificate.id}))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_certificate_serializer_does_not_expose_pdf_field(self, student_client, student_user, published_course):
        Certificate.objects.create(
            student=student_user,
            course=published_course,
            certificate_number='CERT-NO-PDF-FIELD',
        )

        response = student_client.get(reverse('certificate-list'))

        assert response.status_code == status.HTTP_200_OK
        assert 'pdf' not in response.data['results'][0]
