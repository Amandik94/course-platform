from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    link = serializers.CharField(allow_blank=True, allow_null=True, required=False)

    class Meta:
        model = Notification
        fields = (
            'id',
            'type',
            'title',
            'message',
            'is_read',
            'link',
            'created_at',
            'read_at',
        )
        read_only_fields = fields


class UnreadCountSerializer(serializers.Serializer):
    count = serializers.IntegerField()
