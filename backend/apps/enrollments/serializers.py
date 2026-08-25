from rest_framework import serializers

from apps.courses.serializers import CourseListSerializer
from .models import Enrollment, LessonProgress


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ('id', 'course', 'progress', 'created_at', 'completed_at')
        read_only_fields = fields


class LessonProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = LessonProgress
        fields = ('id', 'lesson', 'lesson_title', 'is_completed', 'completed_at')
        read_only_fields = fields


class LessonCompleteResponseSerializer(serializers.Serializer):
    """Не привязан к модели — просто формирует ответ POST /lessons/{id}/complete/"""
    lesson_progress = LessonProgressSerializer()
    enrollment_progress = serializers.IntegerField()
    course_completed = serializers.BooleanField()