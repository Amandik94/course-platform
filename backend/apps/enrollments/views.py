from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import Course
from apps.lessons.models import Lesson
from .models import Enrollment, LessonProgress
from .permissions import IsEnrollmentOwner
from .serializers import EnrollmentSerializer, LessonProgressSerializer
from apps.certificates.services import issue_certificate
from drf_spectacular.utils import extend_schema
from rest_framework import filters
from drf_spectacular.utils import extend_schema_view, extend_schema


@extend_schema_view(
    post=extend_schema(tags=['Enrollments'], summary='Записаться на курс'),
)
class EnrollView(APIView):
    """POST /api/v1/courses/{id}/enroll/ — записаться на курс"""
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=None,
        responses={201: EnrollmentSerializer, 400: dict},
        summary='Записаться на курс',
        description='Доступно только студентам. Курс должен быть в статусе published.',
    )

    def post(self, request, id):
        course = generics.get_object_or_404(Course, id=id, status=Course.Status.PUBLISHED)

        if not request.user.is_student:
            raise PermissionDenied('Записываться на курсы могут только студенты')

        if Enrollment.objects.filter(student=request.user, course=course).exists():
            raise ValidationError({'detail': 'Вы уже записаны на этот курс'})

        enrollment = Enrollment.objects.create(student=request.user, course=course)
        return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED)

@extend_schema_view(
    get=extend_schema(tags=['Enrollments'], summary='Мои курсы'),
)

class MyCoursesView(generics.ListAPIView):
    """GET /api/v1/my-courses/ — курсы, на которые записан текущий студент"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EnrollmentSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'progress', 'completed_at']
    ordering = ['-created_at']  # сортировка по умолчанию

    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user
        ).select_related('course', 'course__category', 'course__teacher')


@extend_schema_view(
    get=extend_schema(tags=['Enrollments'], summary='Прогресс по урокам'),
)
class ProgressListView(generics.ListAPIView):
    """GET /api/v1/progress/ — весь прогресс текущего студента по урокам"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LessonProgressSerializer

    def get_queryset(self):
        return LessonProgress.objects.filter(
            student=self.request.user
        ).select_related('lesson')

@extend_schema_view(
    post=extend_schema(tags=['Lessons'], summary='Завершить урок'),
)

class CompleteLessonView(APIView):
    """
    POST /api/v1/lessons/{id}/complete/
    Отмечает урок пройденным, пересчитывает прогресс курса,
    и при 100% автоматически завершает Enrollment.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=None,
        responses={200: dict},
        summary='Завершить урок',
        description=(
            'Отмечает урок пройденным, пересчитывает прогресс курса. '
            'При достижении 100% автоматически завершает курс и выдаёт сертификат.'
        ),
    )

    @transaction.atomic
    def post(self, request, id):
        lesson = generics.get_object_or_404(
            Lesson.objects.select_related('section__course'), id=id
        )
        course = lesson.section.course

        enrollment = Enrollment.objects.filter(
            student=request.user, course=course
        ).select_for_update().first()  # блокируем строку на время транзакции

        if enrollment is None:
            raise PermissionDenied('Вы не записаны на этот курс')

        lesson_progress, _ = LessonProgress.objects.get_or_create(
            student=request.user, lesson=lesson,
        )
        if not lesson_progress.is_completed:
            lesson_progress.is_completed = True
            lesson_progress.completed_at = timezone.now()
            lesson_progress.save()

        # пересчитываем прогресс курса
        total_lessons = Lesson.objects.filter(section__course=course).count()
        completed_lessons = LessonProgress.objects.filter(
            student=request.user, lesson__section__course=course, is_completed=True,
        ).count()

        new_progress = round((completed_lessons / total_lessons) * 100) if total_lessons else 0
        enrollment.progress = new_progress

        course_completed = False
        if new_progress == 100 and enrollment.completed_at is None:
            enrollment.completed_at = timezone.now()
            course_completed = True

        enrollment.save()
        
        if course_completed:
            issue_certificate(student=request.user, course=course)


        return Response({
            'lesson_progress': LessonProgressSerializer(lesson_progress).data,
            'enrollment_progress': enrollment.progress,
            'course_completed': course_completed,
        })