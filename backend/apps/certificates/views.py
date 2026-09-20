from django.http import FileResponse, Http404
from rest_framework import generics, permissions

from .models import Certificate
from .serializers import CertificateSerializer
from drf_spectacular.utils import extend_schema_view, extend_schema


@extend_schema_view(
    get=extend_schema(tags=['Сертификаты'], summary='Список сертификатов'),
)
class CertificateListView(generics.ListAPIView):
    """GET /api/v1/certificates/ — мои сертификаты"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CertificateSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Certificate.objects.none()
        return Certificate.objects.filter(
            student=self.request.user
        ).select_related('course')

@extend_schema_view(
    get=extend_schema(tags=['Сертификаты'], summary='Сертификат по id'),
)

class CertificateDetailView(generics.RetrieveAPIView):
    """GET /api/v1/certificates/{id}/"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CertificateSerializer

    def get_queryset(self):
        # студент видит только свои сертификаты, admin — все
        if getattr(self, 'swagger_fake_view', False):
            return Certificate.objects.none()
        user = self.request.user
        qs = Certificate.objects.select_related('course', 'student')
        if user.is_admin_role:
            return qs
        return qs.filter(student=user)


class CertificateDownloadView(CertificateDetailView):
    """GET /api/v1/certificates/{id}/download/."""

    def get(self, request, *args, **kwargs):
        certificate = self.get_object()
        if not certificate.pdf:
            raise Http404
        try:
            pdf_file = certificate.pdf.open('rb')
        except (FileNotFoundError, OSError):
            raise Http404('Файл сертификата не найден.')
        return FileResponse(
            pdf_file,
            as_attachment=True,
            filename=f'{certificate.certificate_number}.pdf',
        )
