from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.access import can_access_course_content
from apps.enrollments.models import Enrollment
from apps.notifications.models import Notification
from apps.notifications.services import create_notification
from .models import Assignment, AssignmentSubmission
from apps.lessons.models import Lesson
from .permissions import IsAssignmentTeacherOwner
from apps.courses.permissions import IsTeacherOwnerOrReadOnly
from .serializers import (
    AssignmentSerializer, AssignmentSubmissionSerializer,
    SubmissionReviewSerializer, SubmitAssignmentSerializer,
    AssignmentCreateSerializer,
)
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import filters


@extend_schema_view(
    get=extend_schema(tags=['Задания'], summary='Условие задания'),
)
class AssignmentDetailView(generics.RetrieveAPIView):
    """GET /api/v1/assignments/{id}/ — условие задания"""
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = 'submissions'
    queryset = Assignment.objects.select_related('lesson__section__course')
    serializer_class = AssignmentSerializer
    lookup_url_kwarg = 'id'

    def get_object(self):
        assignment = super().get_object()
        if not can_access_course_content(self.request.user, assignment.lesson.section.course):
            raise PermissionDenied('У вас нет доступа к этому заданию.')
        return assignment

@extend_schema_view(
    post=extend_schema(tags=['Задания'], summary='Отправить решение задания'),
)

class SubmitAssignmentView(APIView):
    """
    POST /api/v1/assignments/{id}/submit/
    Создаёт решение, либо обновляет существующее (повторная отправка
    после revision), переводя статус обратно в pending.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=SubmitAssignmentSerializer,
        responses={200: AssignmentSubmissionSerializer, 201: AssignmentSubmissionSerializer},
        summary='Отправить решение задания',
        description='Повторная отправка обновляет существующее решение и сбрасывает оценку.',
    )

    def post(self, request, id):
        assignment = generics.get_object_or_404(
            Assignment.objects.select_related('lesson__section__course'), id=id
        )
        course = assignment.lesson.section.course

        if not request.user.is_student:
            raise PermissionDenied('Отправлять решения могут только студенты')

        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            raise PermissionDenied('Вы не записаны на курс этого задания')

        serializer = SubmitAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        submission, created = AssignmentSubmission.objects.update_or_create(
            assignment=assignment, student=request.user,
            defaults={
                'code': serializer.validated_data['code'],
                'status': AssignmentSubmission.Status.PENDING,
                # при повторной отправке сбрасываем прошлую оценку/комментарий —
                # решение будет проверено заново
                'score': None,
                'teacher_comment': '',
            },
        )
        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        create_notification(
            user=course.teacher,
            type=Notification.Type.SUBMISSION,
            title='Новое решение задания',
            message=f'{request.user.full_name or request.user.email} отправил(а) решение задания «{assignment.title}».',
            link=f'/teacher/assignments/{assignment.id}/submissions',
        )
        return Response(AssignmentSubmissionSerializer(submission).data, status=response_status)

@extend_schema_view(
    get=extend_schema(tags=['Задания'], summary='Список решений студентов'),
)

class AssignmentSubmissionsListView(generics.ListAPIView):
    """
    GET /api/v1/assignments/{id}/submissions/
    Для преподавателя — список всех решений студентов по заданию.
    """
    permission_classes = [permissions.IsAuthenticated, IsAssignmentTeacherOwner]
    serializer_class = AssignmentSubmissionSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'updated_at', 'status', 'score']
    ordering = ['-updated_at']

    def get_queryset(self):
        assignment = generics.get_object_or_404(Assignment, id=self.kwargs['id'])
        self.check_object_permissions(self.request, assignment)
        return AssignmentSubmission.objects.filter(
            assignment=assignment
        ).select_related('student', 'assignment')

@extend_schema_view(
    patch=extend_schema(tags=['Задания'], summary='Проверить решение задания'),
)

class SubmissionReviewView(generics.UpdateAPIView):
    """
    PATCH /api/v1/submissions/{id}/
    Преподаватель выставляет оценку и меняет статус.
    """
    permission_classes = [permissions.IsAuthenticated, IsAssignmentTeacherOwner]
    queryset = AssignmentSubmission.objects.select_related('assignment__lesson__section__course')
    serializer_class = SubmissionReviewSerializer

    def perform_update(self, serializer):
        submission = serializer.save()
        assignment = submission.assignment
        if submission.status == AssignmentSubmission.Status.REVISION:
            title = 'Задание отправлено на доработку'
            message = f'Задание «{assignment.title}» нужно доработать.'
        else:
            title = 'Задание проверено'
            score = 'не выставлена' if submission.score is None else f'{submission.score}/{assignment.max_score}'
            message = f'Задание «{assignment.title}» проверено. Оценка: {score}.'

        create_notification(
            user=submission.student,
            type=Notification.Type.ASSIGNMENT,
            title=title,
            message=message,
            link=f'/assignment/{assignment.id}',
        )
    
@extend_schema_view(
    post=extend_schema(tags=['Задания'], summary='Создать задание для урока'),
)    

class AssignmentCreateView(generics.CreateAPIView):
    """POST /api/v1/lessons/{lesson_id}/assignment/ — создать задание для урока"""
    permission_classes = [permissions.IsAuthenticated, IsTeacherOwnerOrReadOnly]
    serializer_class = AssignmentCreateSerializer

    def perform_create(self, serializer):
        lesson = generics.get_object_or_404(
            Lesson.objects.select_related('section__course'), id=self.kwargs['lesson_id']
        )
        self.check_object_permissions(self.request, lesson)
        serializer.save(lesson=lesson)

@extend_schema_view(
    patch=extend_schema(tags=['Задания'], summary='Обновить условие задания'),
    delete=extend_schema(tags=['Задания'], summary='Удалить условие задания'),
)

class AssignmentUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """PATCH/DELETE /api/v1/assignments/{id}/manage/ — редактирование условия задания"""
    permission_classes = [permissions.IsAuthenticated, IsAssignmentTeacherOwner]
    queryset = Assignment.objects.select_related('lesson__section__course')
    serializer_class = AssignmentCreateSerializer
    
    

@extend_schema_view(
    get=extend_schema(tags=['Задания'], summary='Посмотреть своё решение задания'),
)

class MySubmissionView(generics.RetrieveAPIView):
    """
    GET /api/v1/assignments/{id}/my-submission/
    Студент смотрит своё решение (если оно есть) по конкретному заданию.
    Возвращает 404, если студент ещё не отправлял решение — это ожидаемо,
    фронтенд трактует 404 здесь как "not_submitted", а не как ошибку.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssignmentSubmissionSerializer

    def get_object(self):
        assignment = generics.get_object_or_404(Assignment, id=self.kwargs['id'])
        submission = generics.get_object_or_404(
            AssignmentSubmission, assignment=assignment, student=self.request.user
        )
        return submission
