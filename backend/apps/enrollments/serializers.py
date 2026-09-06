from rest_framework import serializers

from apps.courses.serializers import CourseListSerializer
from .models import Enrollment, LessonProgress


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    next_lesson_id = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ('id', 'course', 'progress', 'next_lesson_id', 'created_at', 'completed_at')
        read_only_fields = fields

    def get_next_lesson_id(self, obj):
        from apps.lessons.models import Lesson  # локальный импорт — избегаем циклической зависимости

        lesson_ids = list(
            Lesson.objects.filter(section__course=obj.course)
            .order_by('section__order', 'order')
            .values_list('id', flat=True)
        )
        if not lesson_ids:
            return None

        completed_ids = set(
            LessonProgress.objects.filter(
                student=obj.student, lesson_id__in=lesson_ids, is_completed=True,
            ).values_list('lesson_id', flat=True)
        )

        for lesson_id in lesson_ids:
            if lesson_id not in completed_ids:
                return lesson_id

        return lesson_ids[-1]  # всё пройдено — ведём на последний урок для повторного просмотра


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