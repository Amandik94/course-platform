from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.enrollments.models import Enrollment
from .models import Assignment, AssignmentSubmission
from .permissions import IsAssignmentTeacherOwner
from .serializers import (
    AssignmentSerializer, AssignmentSubmissionSerializer,
    SubmissionReviewSerializer, SubmitAssignmentSerializer,
)


class AssignmentDetailView(generics.RetrieveAPIView):
    """GET /api/v1/assignments/{id}/ — условие задания"""
    permission_classes = [permissions.IsAuthenticated]
    queryset = Assignment.objects.select_related('lesson__section__course')
    serializer_class = AssignmentSerializer


class SubmitAssignmentView(APIView):
    """
    POST /api/v1/assignments/{id}/submit/
    Создаёт решение, либо обновляет существующее (повторная отправка
    после revision), переводя статус обратно в pending.
    """
    permission_classes = [permissions.IsAuthenticated]

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
        return Response(AssignmentSubmissionSerializer(submission).data, status=response_status)


class AssignmentSubmissionsListView(generics.ListAPIView):
    """
    GET /api/v1/assignments/{id}/submissions/
    Для преподавателя — список всех решений студентов по заданию.
    """
    permission_classes = [permissions.IsAuthenticated, IsAssignmentTeacherOwner]
    serializer_class = AssignmentSubmissionSerializer

    def get_queryset(self):
        assignment = generics.get_object_or_404(Assignment, id=self.kwargs['id'])
        self.check_object_permissions(self.request, assignment)
        return AssignmentSubmission.objects.filter(
            assignment=assignment
        ).select_related('student', 'assignment')


class SubmissionReviewView(generics.UpdateAPIView):
    """
    PATCH /api/v1/submissions/{id}/
    Преподаватель выставляет оценку и меняет статус.
    """
    permission_classes = [permissions.IsAuthenticated, IsAssignmentTeacherOwner]
    queryset = AssignmentSubmission.objects.select_related('assignment__lesson__section__course')
    serializer_class = SubmissionReviewSerializer