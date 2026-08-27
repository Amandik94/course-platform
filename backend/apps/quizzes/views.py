from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.enrollments.models import Enrollment
from .models import Answer, Question, Quiz, QuizAttempt
from .permissions import IsQuizTeacherOwner
from .serializers import (
    QuizAttemptResultSerializer, QuizPublicSerializer, QuizSerializer, SubmitQuizSerializer,
)


class QuizDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/quizzes/{id}/
    Преподаватель-владелец видит is_correct, студент — нет.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Quiz.objects.select_related('lesson__section__course').prefetch_related('questions__answers')
    lookup_url_kwarg = 'id'

    def get_serializer_class(self):
        quiz = self.get_object()
        user = self.request.user
        is_owner = user.is_admin_role or quiz.lesson.section.course.teacher == user
        return QuizSerializer if is_owner else QuizPublicSerializer


class SubmitQuizView(APIView):
    """
    POST /api/v1/quizzes/{id}/submit/
    Автоматическая проверка ответов и сохранение попытки.
    """
    permission_classes = [permissions.IsAuthenticated]

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