from django.db.models import Avg, Count
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.assignments.models import AssignmentSubmission
from apps.certificates.models import Certificate
from apps.courses.models import Course
from apps.enrollments.models import Enrollment
from apps.quizzes.models import QuizAttempt
from apps.users.models import User
from apps.users.permissions import IsAdmin, IsStudent, IsTeacher
from .serializers import AdminDashboardSerializer, StudentDashboardSerializer, TeacherDashboardSerializer


class StudentDashboardView(APIView):
    """GET /api/v1/dashboard/student/"""
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    @extend_schema(responses={200: StudentDashboardSerializer}, summary='Дашборд студента', tags=['Панель управления'])
    def get(self, request):
        user = request.user
        enrollments = Enrollment.objects.filter(student=user)

        recent_attempts = QuizAttempt.objects.filter(
            student=user
        ).select_related('quiz').order_by('-created_at')[:5]

        data = {
            'active_courses_count': enrollments.filter(completed_at__isnull=True).count(),
            'completed_courses_count': enrollments.filter(completed_at__isnull=False).count(),
            'average_progress': round(enrollments.aggregate(avg=Avg('progress'))['avg'] or 0),
            'certificates_count': Certificate.objects.filter(student=user).count(),
            'recent_quiz_results': [
                {
                    'quiz_title': attempt.quiz.title,
                    'score': attempt.score,
                    'passed': attempt.passed,
                    'created_at': attempt.created_at,
                }
                for attempt in recent_attempts
            ],
        }
        return Response(StudentDashboardSerializer(data).data)


class TeacherDashboardView(APIView):
    """GET /api/v1/dashboard/teacher/"""
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    @extend_schema(responses={200: TeacherDashboardSerializer}, summary='Дашборд преподавателя', tags=['Панель управления'])
    def get(self, request):
        user = request.user
        courses = Course.objects.filter(teacher=user).annotate(
            students_count=Count('enrollments', distinct=True)
        )

        data = {
            'courses_count': courses.count(),
            'students_count': Enrollment.objects.filter(
                course__teacher=user
            ).values('student').distinct().count(),
            'pending_submissions_count': AssignmentSubmission.objects.filter(
                assignment__lesson__section__course__teacher=user,
                status=AssignmentSubmission.Status.PENDING,
            ).count(),
            'courses': [
                {'id': c.id, 'title': c.title, 'students_count': c.students_count, 'status': c.status}
                for c in courses
            ],
        }
        return Response(TeacherDashboardSerializer(data).data)


class AdminDashboardView(APIView):
    """GET /api/v1/dashboard/admin/"""
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    @extend_schema(responses={200: AdminDashboardSerializer}, summary='Дашборд администратора', tags=['Панель управления'])
    def get(self, request):
        data = {
            'users_count': User.objects.count(),
            'students_count': User.objects.filter(role=User.Role.STUDENT).count(),
            'teachers_count': User.objects.filter(role=User.Role.TEACHER).count(),
            'courses_count': Course.objects.count(),
            'active_courses_count': Course.objects.filter(status=Course.Status.PUBLISHED).count(),
            'completed_enrollments_count': Enrollment.objects.filter(completed_at__isnull=False).count(),
            'average_progress': round(
                Enrollment.objects.aggregate(avg=Avg('progress'))['avg'] or 0
            ),
        }
        return Response(AdminDashboardSerializer(data).data)
