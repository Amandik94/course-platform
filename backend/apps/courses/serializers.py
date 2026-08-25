from rest_framework import serializers

from apps.users.serializers import UserSerializer
from .models import Category, Course, Section


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description')


class CourseListSerializer(serializers.ModelSerializer):
    """Компактная версия — для каталога (CourseCard на фронте)."""
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    category = CategorySerializer(read_only=True)
    lessons_count = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = (
            'id', 'title', 'slug', 'short_description', 'cover',
            'category', 'teacher_name', 'level', 'duration',
            'lessons_count', 'status',
        )


class CourseDetailSerializer(serializers.ModelSerializer):
    """Полная версия — для страницы курса."""
    teacher = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category', queryset=Category.objects.all(), write_only=True
    )
    lessons_count = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = (
            'id', 'title', 'slug', 'description', 'short_description',
            'cover', 'category', 'category_id', 'teacher', 'level',
            'duration', 'status', 'lessons_count', 'created_at', 'updated_at',
        )
        read_only_fields = ('slug', 'teacher')

    def create(self, validated_data):
        # teacher = текущий пользователь, а не то, что прислали в запросе —
        # иначе преподаватель мог бы создать курс от имени другого
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('id', 'course', 'title', 'description', 'order')
        read_only_fields = ('course',)  # course берём из URL, не из тела запроса