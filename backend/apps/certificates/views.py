from rest_framework import generics, permissions

from .models import Certificate
from .serializers import CertificateSerializer
from drf_spectacular.utils import extend_schema_view, extend_schema


@extend_schema_view(
    get=extend_schema(tags=['Certificates'], summary='Список сертификатов'),
)
class CertificateListView(generics.ListAPIView):
    """GET /api/v1/certificates/ — мои сертификаты"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CertificateSerializer

    def get_queryset(self):
        return Certificate.objects.filter(
            student=self.request.user
        ).select_related('course')

@extend_schema_view(
    get=extend_schema(tags=['Certificates'], summary='Сертификат по id'),
)

class CertificateDetailView(generics.RetrieveAPIView):
    """GET /api/v1/certificates/{id}/"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CertificateSerializer

    def get_queryset(self):
        # студент видит только свои сертификаты, admin — все
        user = self.request.user
        qs = Certificate.objects.select_related('course', 'student')
        if user.is_admin_role:
            return qs
        return qs.filter(student=user)