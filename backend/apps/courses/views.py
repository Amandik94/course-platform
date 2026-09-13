from django.db.models import Avg, Count, FloatField, Value
from django.db.models.functions import Coalesce
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError

from drf_spectacular.utils import extend_schema, extend_schema_view

from .access import visible_courses_for_user
from .filters import CourseFilter
from .models import Category, Course, Section
from .permissions import IsTeacherOwnerOrReadOnly
from .serializers import (
    CategorySerializer,
    CourseDetailSerializer,
    CourseListSerializer,
    SectionSerializer,
)
from apps.users.permissions import IsAdmin


@extend_schema_view(
    get=extend_schema(tags=['Категории'], summary='Список категорий'),
    post=extend_schema(tags=['Категории'], summary='Создать категорию'),
)
class CategoryListView(generics.ListCreateAPIView):
    """GET/POST /api/v1/categories/."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsAdmin()]
        return [permissions.AllowAny()]


@extend_schema_view(
    get=extend_schema(tags=['Категории'], summary='Получить категорию'),
    patch=extend_schema(tags=['Категории'], summary='Обновить категорию'),
    delete=extend_schema(tags=['Категории'], summary='Удалить категорию'),
)
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/v1/categories/{id}/."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAdmin()]

    def perform_destroy(self, instance):
        if instance.courses.exists():
            raise ValidationError({
                'detail': 'Нельзя удалить категорию, к которой привязаны курсы.'
            })
        instance.delete()


@extend_schema_view(
    get=extend_schema(tags=['Курсы'], summary='Список курсов'),
    post=extend_schema(tags=['Курсы'], summary='Создать курс'),
)
class CourseListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/courses/."""
    permission_classes = [IsTeacherOwnerOrReadOnly]
    filterset_class = CourseFilter
    search_fields = ['title', 'short_description']
    ordering_fields = ['created_at', 'title', 'duration']

    def get_queryset(self):
        return (
            visible_courses_for_user(self.request.user)
            .select_related('category', 'teacher')
            .annotate(lessons_total=Count('sections__lessons', distinct=True))
            .annotate(
                average_rating=Coalesce(
                    Avg('reviews__rating'),
                    Value(0.0),
                    output_field=FloatField(),
                ),
                reviews_count=Count('reviews', distinct=True),
            )
            .order_by('-created_at')
        )

    def get_serializer_class(self):
        return CourseDetailSerializer if self.request.method == 'POST' else CourseListSerializer


@extend_schema_view(
    get=extend_schema(tags=['Курсы'], summary='Получить курс'),
    patch=extend_schema(tags=['Курсы'], summary='Обновить курс'),
    delete=extend_schema(tags=['Курсы'], summary='Удалить курс'),
)
class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/v1/courses/{id}/."""
    permission_classes = [IsTeacherOwnerOrReadOnly]
    serializer_class = CourseDetailSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return (
            visible_courses_for_user(self.request.user)
            .select_related('category', 'teacher')
            .prefetch_related('sections__lessons')
            .annotate(lessons_total=Count('sections__lessons', distinct=True))
            .annotate(
                average_rating=Coalesce(
                    Avg('reviews__rating'),
                    Value(0.0),
                    output_field=FloatField(),
                ),
                reviews_count=Count('reviews', distinct=True),
            )
            .order_by('-created_at')
        )

    def perform_destroy(self, instance):
        if instance.enrollments.exists():
            raise ValidationError({
                'detail': (
                    'Нельзя удалить курс, на который уже записаны студенты. '
                    'Перенесите курс в архив.'
                )
            })
        instance.delete()


@extend_schema_view(
    get=extend_schema(tags=['Разделы'], summary='Список разделов'),
    post=extend_schema(tags=['Разделы'], summary='Создать раздел'),
)
class SectionListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/v1/courses/{course_id}/sections/."""
    serializer_class = SectionSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsTeacherOwnerOrReadOnly()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Section.objects.none()
        course_ids = visible_courses_for_user(self.request.user).values('id')
        return Section.objects.filter(
            course_id=self.kwargs['course_id'],
            course_id__in=course_ids,
        ).select_related('course')

    def perform_create(self, serializer):
        course = generics.get_object_or_404(Course, id=self.kwargs['course_id'])
        self.check_object_permissions(self.request, course)
        serializer.save(course=course)


@extend_schema_view(
    get=extend_schema(tags=['Разделы'], summary='Получить раздел'),
    patch=extend_schema(tags=['Разделы'], summary='Обновить раздел'),
    delete=extend_schema(tags=['Разделы'], summary='Удалить раздел'),
)
class SectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/v1/sections/{id}/."""
    permission_classes = [IsTeacherOwnerOrReadOnly]
    serializer_class = SectionSerializer

    def get_queryset(self):
        course_ids = visible_courses_for_user(self.request.user).values('id')
        return Section.objects.filter(course_id__in=course_ids).select_related('course')
