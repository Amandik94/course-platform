from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError

from .filters import CourseFilter
from .models import Category, Course, Section
from .permissions import IsTeacherOwnerOrReadOnly
from .serializers import (
    CategorySerializer, CourseDetailSerializer, CourseListSerializer, SectionSerializer,
)
from drf_spectacular.utils import extend_schema_view, extend_schema


@extend_schema_view(
    get=extend_schema(tags=['Categories'], summary='Список категорий'),
)

class CategoryListView(generics.ListAPIView):
    """GET /api/v1/categories/ — публичный список категорий для фильтра"""
    permission_classes = [permissions.AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@extend_schema_view(
    get=extend_schema(tags=['Courses'], summary='Список курсов (каталог)'),
    post=extend_schema(tags=['Courses'], summary='Создать курс (только teacher/admin)'),
)

class CourseListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/courses/  — публичный каталог (только published для анонимов)
    POST /api/v1/courses/  — создание курса (только teacher/admin)
    """
    permission_classes = [IsTeacherOwnerOrReadOnly]
    filterset_class = CourseFilter
    search_fields = ['title', 'short_description']
    ordering_fields = ['created_at', 'title', 'duration']

    def get_queryset(self):
        qs = Course.objects.select_related('category', 'teacher')
        user = self.request.user
        if user.is_authenticated and (user.is_teacher or user.is_admin_role):
            if user.is_teacher and not user.is_admin_role:
                # преподаватель видит свои курсы (в т.ч. draft) + все published
                from django.db.models import Q
                return qs.filter(Q(status=Course.Status.PUBLISHED) | Q(teacher=user))
            return qs  # admin видит всё
        return qs.filter(status=Course.Status.PUBLISHED)

    def get_serializer_class(self):
        return CourseDetailSerializer if self.request.method == 'POST' else CourseListSerializer

@extend_schema_view(
    get=extend_schema(tags=['Courses'], summary='Детали курса'),
    patch=extend_schema(tags=['Courses'], summary='Обновить курс'),
    delete=extend_schema(tags=['Courses'], summary='Удалить курс'),
)

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/courses/{id}/
    PATCH  /api/v1/courses/{id}/
    DELETE /api/v1/courses/{id}/
    """
    permission_classes = [IsTeacherOwnerOrReadOnly]
    queryset = Course.objects.select_related('category', 'teacher')
    serializer_class = CourseDetailSerializer
    lookup_field = 'id'

    def perform_destroy(self, instance):
        if instance.enrollments.exists():
            raise ValidationError({
                'detail': 'Нельзя удалить курс, на который уже записаны студенты. '
                        'Переведите курс в статус archived вместо удаления.'
            })
        instance.delete()
        

@extend_schema_view(
    get=extend_schema(tags=['Sections'], summary='Список разделов'),
    post=extend_schema(tags=['Sections'], summary='Создать раздел'),
)    

class SectionListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/courses/{course_id}/sections/
    POST /api/v1/courses/{course_id}/sections/
    """
    serializer_class = SectionSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsTeacherOwnerOrReadOnly()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        return Section.objects.filter(course_id=self.kwargs['course_id'])

    def perform_create(self, serializer):
        course = Course.objects.get(id=self.kwargs['course_id'])
        # object-level проверка владения курсом — вызываем вручную,
        # т.к. ListCreateAPIView.create() не вызывает check_object_permissions
        self.check_object_permissions(self.request, course)
        serializer.save(course=course)

@extend_schema_view(
    patch=extend_schema(tags=['Sections'], summary='Обновить раздел'),
    delete=extend_schema(tags=['Sections'], summary='Удалить раздел'),
)

class SectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    PATCH  /api/v1/sections/{id}/
    DELETE /api/v1/sections/{id}/
    """
    permission_classes = [IsTeacherOwnerOrReadOnly]
    queryset = Section.objects.select_related('course')
    serializer_class = SectionSerializer