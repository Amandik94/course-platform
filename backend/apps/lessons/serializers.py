from rest_framework import serializers

from .models import Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = (
            'id', 'section', 'title', 'description', 'type', 'content',
            'video_url', 'duration', 'order', 'is_free',
        )
        read_only_fields = ('section',)

    def validate(self, attrs):
        lesson_type = attrs.get('type', getattr(self.instance, 'type', None))
        if lesson_type == Lesson.Type.VIDEO and not attrs.get('video_url', getattr(self.instance, 'video_url', '')):
            raise serializers.ValidationError({'video_url': 'Обязательно для урока типа video'})
        return attrs


class LessonListSerializer(serializers.ModelSerializer):
    """Урезанная версия для сайдбара Learn Page — без полного content."""
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'type', 'duration', 'order', 'is_free')