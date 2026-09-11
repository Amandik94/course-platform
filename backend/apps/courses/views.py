from django.db.models import Count
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
    get=extend_schema(tags=['Categories'], summary='List categories'),
    post=extend_schema(tags=['Categories'], summary='Create category'),
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
    get=extend_schema(tags=['Categories'], summary='Retrieve category'),
    patch=extend_schema(tags=['Categories'], summary='Update category'),
    delete=extend_schema(tags=['Categories'], summary='Delete category'),
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
                'detail': 'Cannot delete a category that still has courses.'
            })
        instance.delete()


@extend_schema_view(
    get=extend_schema(tags=['Courses'], summary='List courses'),
    post=extend_schema(tags=['Courses'], summary='Create course'),
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
            .order_by('-created_at')
        )

    def get_serializer_class(self):
        return CourseDetailSerializer if self.request.method == 'POST' else CourseListSerializer


@extend_schema_view(
    get=extend_schema(tags=['Courses'], summary='Retrieve course'),
    patch=extend_schema(tags=['Courses'], summary='Update course'),
    delete=extend_schema(tags=['Courses'], summary='Delete course'),
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
            .order_by('-created_at')
        )

    def perform_destroy(self, instance):
        if instance.enrollments.exists():
            raise ValidationError({
                'detail': (
                    'Cannot delete a course with enrolled students. '
                    'Archive the course instead.'
                )
            })
        instance.delete()


@extend_schema_view(
    get=extend_schema(tags=['Sections'], summary='List sections'),
    post=extend_schema(tags=['Sections'], summary='Create section'),
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
    get=extend_schema(tags=['Sections'], summary='Retrieve section'),
    patch=extend_schema(tags=['Sections'], summary='Update section'),
    delete=extend_schema(tags=['Sections'], summary='Delete section'),
)
class SectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/v1/sections/{id}/."""
    permission_classes = [IsTeacherOwnerOrReadOnly]
    serializer_class = SectionSerializer

    def get_queryset(self):
        course_ids = visible_courses_for_user(self.request.user).values('id')
        return Section.objects.filter(course_id__in=course_ids).select_related('course')
