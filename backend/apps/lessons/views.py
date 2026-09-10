from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from apps.courses.models import Section
from apps.courses.permissions import IsTeacherOwnerOrReadOnly
from apps.courses.access import can_access_course_content
from .models import Lesson
from .serializers import LessonSerializer
from drf_spectacular.utils import extend_schema_view, extend_schema


@extend_schema_view(
    get=extend_schema(tags=['Lessons'], summary='Список уроков'),
    post=extend_schema(tags=['Lessons'], summary='Создать урок'),
)
class LessonListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/sections/{section_id}/lessons/
    POST /api/v1/sections/{section_id}/lessons/
    """
    serializer_class = LessonSerializer
    pagination_class = None

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsTeacherOwnerOrReadOnly()]
        from rest_framework.permissions import AllowAny
        return [AllowAny()]

    def get_queryset(self):
        section = generics.get_object_or_404(
            Section.objects.select_related('course'), id=self.kwargs['section_id']
        )
        self.check_object_permissions(self.request, section)
        qs = Lesson.objects.filter(section=section).select_related('section__course')
        if can_access_course_content(self.request.user, section.course):
            return qs
        if section.course.status == section.course.Status.PUBLISHED:
            return qs.filter(is_free=True)
        return qs.none()

    def perform_create(self, serializer):
        section = Section.objects.select_related('course').get(id=self.kwargs['section_id'])
        self.check_object_permissions(self.request, section)
        serializer.save(section=section)

@extend_schema_view(
    get=extend_schema(tags=['Lessons'], summary='Детали урока'),
    patch=extend_schema(tags=['Lessons'], summary='Обновить урок'),
    delete=extend_schema(tags=['Lessons'], summary='Удалить урок'),
)

class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/lessons/{id}/
    PATCH  /api/v1/lessons/{id}/
    DELETE /api/v1/lessons/{id}/
    """
    permission_classes = [IsTeacherOwnerOrReadOnly]
    serializer_class = LessonSerializer

    def get_queryset(self):
        return Lesson.objects.select_related('section__course')

    def get_object(self):
        lesson = super().get_object()
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            course = lesson.section.course
            if can_access_course_content(self.request.user, course):
                return lesson
            if course.status == course.Status.PUBLISHED and lesson.is_free:
                return lesson
            raise PermissionDenied('You do not have access to this lesson.')
        return lesson
