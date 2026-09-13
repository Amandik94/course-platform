from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.enrollments.models import Enrollment
from apps.courses.access import can_access_course_content
from apps.notifications.models import Notification
from apps.notifications.services import create_notification
from .models import Answer, Question, Quiz, QuizAttempt
from .permissions import IsQuizTeacherOwner
from .serializers import (
    QuizAttemptResultSerializer, QuizPublicSerializer, QuizSerializer, SubmitQuizSerializer,
)
from apps.lessons.models import Lesson
from apps.courses.permissions import IsTeacherOwnerOrReadOnly
from .serializers import QuizCreateSerializer, QuestionCreateSerializer, AnswerCreateSerializer
from drf_spectacular.utils import extend_schema_view, extend_schema

@extend_schema_view(
    get=extend_schema(tags=['Тесты'], summary='Детали теста'),
)

class QuizDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/quizzes/{id}/
    Преподаватель-владелец видит is_correct, студент — нет.
    """
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = 'submissions'
    queryset = Quiz.objects.select_related('lesson__section__course').prefetch_related('questions__answers')
    lookup_url_kwarg = 'id'

    def get_object(self):
        quiz = super().get_object()
        if not can_access_course_content(self.request.user, quiz.lesson.section.course):
            raise PermissionDenied('У вас нет доступа к этому тесту.')
        return quiz

    def get_serializer_class(self):
        if getattr(self, 'swagger_fake_view', False):
            return QuizSerializer
        quiz = self.get_object()
        user = self.request.user
        is_owner = user.is_admin_role or quiz.lesson.section.course.teacher == user
        return QuizSerializer if is_owner else QuizPublicSerializer

@extend_schema_view(
    post=extend_schema(tags=['Тесты'], summary='Отправить ответы на тест'),
)

class SubmitQuizView(APIView):
    """
    POST /api/v1/quizzes/{id}/submit/
    Автоматическая проверка ответов и сохранение попытки.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=SubmitQuizSerializer,
        responses={201: QuizAttemptResultSerializer},
        summary='Отправить ответы на тест',
        description='Автоматически проверяет ответы и возвращает результат прохождения.',
    )

    @transaction.atomic
    def post(self, request, id):
        quiz = generics.get_object_or_404(
            Quiz.objects.select_related('lesson__section__course').prefetch_related('questions__answers'),
            id=id,
        )
        course = quiz.lesson.section.course

        if not request.user.is_student:
            raise PermissionDenied('Проходить тесты могут только студенты')

        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            raise PermissionDenied('Вы не записаны на курс этого теста')

        serializer = SubmitQuizSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submitted_answers = {
            item['question_id']: item for item in serializer.validated_data['answers']
        }

        total_points = 0
        earned_points = 0
        snapshot = {}

        for question in quiz.questions.all():
            total_points += question.points
            submitted = submitted_answers.get(question.id)
            if not submitted:
                continue  # вопрос пропущен — 0 баллов за него

            is_correct = self._check_answer(question, submitted)
            if is_correct:
                earned_points += question.points

            snapshot[str(question.id)] = {
                'submitted': {
                    'answer_id': submitted.get('answer_id'),
                    'answer_ids': submitted.get('answer_ids'),
                    'text': submitted.get('text'),
                },
                'is_correct': is_correct,
            }

        score_percent = round((earned_points / total_points) * 100) if total_points else 0
        passed = score_percent >= quiz.passing_score

        attempt = QuizAttempt.objects.create(
            quiz=quiz, student=request.user, score=score_percent,
            passed=passed, answers_snapshot=snapshot,
        )
        create_notification(
            user=request.user,
            type=Notification.Type.QUIZ,
            title='Результат теста',
            message=f'Ваш результат по тесту «{quiz.title}»: {score_percent}%.',
            link=f'/quiz/{quiz.id}',
        )
        return Response(QuizAttemptResultSerializer(attempt).data, status=status.HTTP_201_CREATED)

    @staticmethod
    def _check_answer(question: Question, submitted: dict) -> bool:
        if question.type == Question.Type.SINGLE:
            answer_id = submitted.get('answer_id')
            if answer_id is None:
                return False
            return Answer.objects.filter(id=answer_id, question=question, is_correct=True).exists()

        if question.type == Question.Type.MULTIPLE:
            submitted_ids = set(submitted.get('answer_ids') or [])
            correct_ids = set(
                Answer.objects.filter(question=question, is_correct=True).values_list('id', flat=True)
            )
            # правильно только если множества совпадают ПОЛНОСТЬЮ
            return submitted_ids == correct_ids and len(submitted_ids) > 0

        if question.type == Question.Type.TEXT:
            submitted_text = (submitted.get('text') or '').strip().lower()
            expected_text = (question.text_answer or '').strip().lower()
            return bool(expected_text) and submitted_text == expected_text

        return False
    

@extend_schema_view(
    post=extend_schema(tags=['Тесты'], summary='Создать тест'),
)
    
class QuizCreateView(generics.CreateAPIView):
    """POST /api/v1/lessons/{lesson_id}/quiz/ — преподаватель создаёт тест для урока"""
    permission_classes = [permissions.IsAuthenticated, IsTeacherOwnerOrReadOnly]
    serializer_class = QuizCreateSerializer

    def perform_create(self, serializer):
        lesson = generics.get_object_or_404(
            Lesson.objects.select_related('section__course'), id=self.kwargs['lesson_id']
        )
        self.check_object_permissions(self.request, lesson)
        serializer.save(lesson=lesson)


@extend_schema_view(
    get=extend_schema(tags=['Тесты'], summary='Получить тест для управления'),
    patch=extend_schema(tags=['Тесты'], summary='Обновить тест'),
    delete=extend_schema(tags=['Тесты'], summary='Удалить тест'),
)
class QuizManageView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/v1/quizzes/{id}/manage/."""

    permission_classes = [permissions.IsAuthenticated, IsQuizTeacherOwner]
    queryset = Quiz.objects.select_related('lesson__section__course').prefetch_related('questions__answers')
    serializer_class = QuizSerializer
    lookup_url_kwarg = 'id'

    def perform_destroy(self, instance):
        if instance.attempts.exists():
            raise ValidationError({
                'detail': 'Нельзя удалить тест, по которому уже есть попытки студентов.'
            })
        instance.delete()

@extend_schema_view(
    post=extend_schema(tags=['Тесты'], summary='Создать ответ'),
)

class QuestionCreateView(generics.CreateAPIView):
    """POST /api/v1/quizzes/{quiz_id}/questions/"""
    permission_classes = [permissions.IsAuthenticated, IsQuizTeacherOwner]
    serializer_class = QuestionCreateSerializer

    def perform_create(self, serializer):
        quiz = generics.get_object_or_404(
            Quiz.objects.select_related('lesson__section__course'), id=self.kwargs['quiz_id']
        )
        self.check_object_permissions(self.request, quiz)
        serializer.save(quiz=quiz)

@extend_schema_view(
    post=extend_schema(tags=['Тесты'], summary='Создать вопрос'),
)

class AnswerCreateView(generics.CreateAPIView):
    """POST /api/v1/questions/{question_id}/answers/"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AnswerCreateSerializer

    def perform_create(self, serializer):
        question = generics.get_object_or_404(
            Question.objects.select_related('quiz__lesson__section__course'),
            id=self.kwargs['question_id'],
        )
        user = self.request.user
        is_owner = user.is_admin_role or question.quiz.lesson.section.course.teacher == user
        if not is_owner:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Вы не являетесь владельцем этого теста')
        serializer.save(question=question)

@extend_schema_view(
    patch=extend_schema(tags=['Тесты'], summary='Обновить ответ'),
    delete=extend_schema(tags=['Тесты'], summary='Удалить ответ'),
)

class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """PATCH/DELETE /api/v1/questions/{id}/"""
    permission_classes = [permissions.IsAuthenticated, IsQuizTeacherOwner]
    queryset = Question.objects.select_related('quiz__lesson__section__course')
    serializer_class = QuestionCreateSerializer

@extend_schema_view(
    patch=extend_schema(tags=['Тесты'], summary='Обновить вопрос'),
    delete=extend_schema(tags=['Тесты'], summary='Удалить вопрос'),
)

class AnswerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """PATCH/DELETE /api/v1/answers/{id}/"""
    permission_classes = [permissions.IsAuthenticated]
    queryset = Answer.objects.select_related('question__quiz__lesson__section__course')
    serializer_class = AnswerCreateSerializer

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        user = request.user
        is_owner = user.is_admin_role or obj.question.quiz.lesson.section.course.teacher == user
        if not is_owner:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Вы не являетесь владельцем этого теста')
