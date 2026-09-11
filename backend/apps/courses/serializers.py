from rest_framework import serializers

from apps.users.serializers import UserSerializer
from .models import Category, Course, Section


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description')
        read_only_fields = ('slug',)


class CourseListSerializer(serializers.ModelSerializer):
    """Компактная версия — для каталога (CourseCard на фронте)."""
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    teacher_id = serializers.IntegerField(source='teacher.id', read_only=True)
    category = CategorySerializer(read_only=True)
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            'id', 'title', 'slug', 'short_description', 'cover',
            'category', 'teacher_name', 'teacher_id', 'level', 'duration',
            'lessons_count', 'status',
        )

    def get_lessons_count(self, obj) -> int:
        annotated_count = getattr(obj, 'lessons_total', None)
        if annotated_count is not None:
            return annotated_count
        return obj.lessons_count


class CourseDetailSerializer(serializers.ModelSerializer):
    """Полная версия — для страницы курса."""
    teacher = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category', queryset=Category.objects.all(), write_only=True
    )
    lessons_count = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            'id', 'title', 'slug', 'description', 'short_description',
            'cover', 'category', 'category_id', 'teacher', 'level',
            'duration', 'status', 'lessons_count', 'is_enrolled',
            'created_at', 'updated_at',
        )
        read_only_fields = ('slug', 'teacher')

    def get_is_enrolled(self, obj) -> bool:
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        if not request.user.is_student:
            return False  # преподаватели/админы не записываются на курсы
        # избегаем импорта apps.enrollments в начале файла, чтобы не
        # создавать циклическую зависимость courses <-> enrollments
        from apps.enrollments.models import Enrollment
        return Enrollment.objects.filter(student=request.user, course=obj).exists()

    def get_lessons_count(self, obj) -> int:
        annotated_count = getattr(obj, 'lessons_total', None)
        if annotated_count is not None:
            return annotated_count
        return obj.lessons_count

    def create(self, validated_data):
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('id', 'course', 'title', 'description', 'order')
        read_only_fields = ('course',)  # course берём из URL, не из тела запроса
