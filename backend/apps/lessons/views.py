from rest_framework import generics

from apps.courses.models import Section
from apps.courses.permissions import IsTeacherOwnerOrReadOnly
from .models import Lesson
from .serializers import LessonSerializer


class LessonListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/sections/{section_id}/lessons/
    POST /api/v1/sections/{section_id}/lessons/
    """
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsTeacherOwnerOrReadOnly()]
        from rest_framework.permissions import AllowAny
        return [AllowAny()]

    def get_queryset(self):
        return Lesson.objects.filter(section_id=self.kwargs['section_id'])

    def perform_create(self, serializer):
        section = Section.objects.select_related('course').get(id=self.kwargs['section_id'])
        self.check_object_permissions(self.request, section)
        serializer.save(section=section)


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/lessons/{id}/
    PATCH  /api/v1/lessons/{id}/
    DELETE /api/v1/lessons/{id}/
    """
    permission_classes = [IsTeacherOwnerOrReadOnly]
    queryset = Lesson.objects.select_related('section__course')
    serializer_class = LessonSerializer