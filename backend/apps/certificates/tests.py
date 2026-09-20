import pytest
from django.core.files.base import ContentFile
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

    def test_owner_can_download_certificate_pdf(
        self, student_client, student_user, published_course, settings, tmp_path,
    ):
        settings.MEDIA_ROOT = tmp_path
        certificate = Certificate.objects.create(
            student=student_user,
            course=published_course,
            certificate_number='CERT-DOWNLOAD',
        )
        certificate.pdf.save('certificate.pdf', ContentFile(b'%PDF-1.4 test'), save=True)

        response = student_client.get(
            reverse('certificate-download', kwargs={'pk': certificate.pk})
        )

        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'application/pdf'
        assert 'attachment' in response['Content-Disposition']
        assert b''.join(response.streaming_content).startswith(b'%PDF-1.4')

    def test_student_cannot_download_another_students_certificate(
        self, api_client, student_user, published_course, django_user_model,
    ):
        other_student = django_user_model.objects.create_user(
            email='cert-download-other@test.com',
            password='pass12345',
            role='student',
        )
        certificate = Certificate.objects.create(
            student=other_student,
            course=published_course,
            certificate_number='CERT-DOWNLOAD-OTHER',
            pdf='certificates/other.pdf',
        )
        api_client.force_authenticate(user=student_user)

        response = api_client.get(
            reverse('certificate-download', kwargs={'pk': certificate.pk})
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_anonymous_cannot_download_certificate(self, api_client, student_user, published_course):
        certificate = Certificate.objects.create(
            student=student_user,
            course=published_course,
            certificate_number='CERT-DOWNLOAD-AUTH',
            pdf='certificates/auth.pdf',
        )

        response = api_client.get(
            reverse('certificate-download', kwargs={'pk': certificate.pk})
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_missing_certificate_file_returns_404(
        self, student_client, student_user, published_course, settings, tmp_path,
    ):
        settings.MEDIA_ROOT = tmp_path
        certificate = Certificate.objects.create(
            student=student_user,
            course=published_course,
            certificate_number='CERT-MISSING-FILE',
            pdf='certificates/missing.pdf',
        )

        response = student_client.get(
            reverse('certificate-download', kwargs={'pk': certificate.pk})
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_nonexistent_certificate_download_returns_404(self, student_client):
        response = student_client.get(
            reverse('certificate-download', kwargs={'pk': 999999})
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
