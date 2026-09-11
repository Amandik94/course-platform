from rest_framework import serializers

from .models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = (
            'id', 'course', 'course_title', 'certificate_number',
            'issued_at', 'download_url',
        )
        read_only_fields = fields

    def get_download_url(self, obj) -> str | None:
        request = self.context.get('request')
        if not obj.pdf:
            return None
        path = f'/api/v1/certificates/{obj.pk}/download/'
        return request.build_absolute_uri(path) if request else path
