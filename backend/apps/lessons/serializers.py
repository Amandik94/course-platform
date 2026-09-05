from rest_framework import serializers

from .models import Lesson


class LessonSerializer(serializers.ModelSerializer):
    assignment_id = serializers.SerializerMethodField()
    quiz_id = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            'id', 'section', 'title', 'description', 'type', 'content',
            'video_url', 'duration', 'order', 'is_free',
            'assignment_id', 'quiz_id',
        )
        read_only_fields = ('section',)

    def get_assignment_id(self, obj):
        # OneToOneField создаёт обратную связь obj.assignment,
        # которая бросает Lesson.assignment.RelatedObjectDoesNotExist,
        # если задания ещё нет — ловим это явно, а не полагаемся на None
        try:
            return obj.assignment.id
        except Lesson.assignment.RelatedObjectDoesNotExist:
            return None

    def get_quiz_id(self, obj):
        try:
            return obj.quiz.id
        except Lesson.quiz.RelatedObjectDoesNotExist:
            return None

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