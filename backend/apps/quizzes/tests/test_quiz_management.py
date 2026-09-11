import pytest
from django.urls import reverse
from rest_framework import status

from apps.courses.models import Section
from apps.lessons.models import Lesson
from apps.quizzes.models import Answer, Question, Quiz, QuizAttempt


@pytest.fixture
def teacher_quiz(published_course):
    section = Section.objects.create(course=published_course, title='Basics', order=1)
    lesson = Lesson.objects.create(section=section, title='Quiz lesson', type='quiz', order=1)
    return Quiz.objects.create(lesson=lesson, title='Initial quiz', passing_score=60)


@pytest.mark.django_db
class TestQuizManagementApi:
    def test_teacher_owner_can_update_quiz(self, teacher_client, teacher_quiz):
        response = teacher_client.patch(
            reverse('quiz-manage', kwargs={'id': teacher_quiz.id}),
            {'title': 'Updated quiz', 'passing_score': 80},
        )

        assert response.status_code == status.HTTP_200_OK
        teacher_quiz.refresh_from_db()
        assert teacher_quiz.title == 'Updated quiz'
        assert teacher_quiz.passing_score == 80

    def test_other_teacher_cannot_update_quiz(self, api_client, teacher_quiz, django_user_model):
        other_teacher = django_user_model.objects.create_user(
            email='quiz-other@test.com',
            password='pass12345',
            first_name='Other',
            last_name='Teacher',
            role='teacher',
        )
        api_client.force_authenticate(user=other_teacher)

        response = api_client.patch(
            reverse('quiz-manage', kwargs={'id': teacher_quiz.id}),
            {'title': 'Hacked'},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_student_cannot_delete_quiz(self, student_client, teacher_quiz):
        response = student_client.delete(reverse('quiz-manage', kwargs={'id': teacher_quiz.id}))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_teacher_owner_can_manage_questions_and_answers(self, teacher_client, teacher_quiz):
        question_response = teacher_client.post(
            reverse('question-create', kwargs={'quiz_id': teacher_quiz.id}),
            {'question': '2+2?', 'type': 'single', 'points': 1, 'order': 1, 'text_answer': ''},
        )
        assert question_response.status_code == status.HTTP_201_CREATED

        question_id = question_response.data['id']
        answer_response = teacher_client.post(
            reverse('answer-create', kwargs={'question_id': question_id}),
            {'text': '4', 'is_correct': True},
        )
        assert answer_response.status_code == status.HTTP_201_CREATED
        assert answer_response.data['is_correct'] is True

        update_response = teacher_client.patch(
            reverse('question-detail', kwargs={'pk': question_id}),
            {'question': '3+1?'},
        )
        assert update_response.status_code == status.HTTP_200_OK

    def test_student_does_not_see_correct_answers(self, student_client, teacher_quiz, student_user):
        from apps.enrollments.models import Enrollment

        Enrollment.objects.create(student=student_user, course=teacher_quiz.lesson.section.course)
        question = Question.objects.create(
            quiz=teacher_quiz, question='2+2?', type='single', points=1, order=1,
        )
        Answer.objects.create(question=question, text='4', is_correct=True)

        response = student_client.get(reverse('quiz-detail', kwargs={'id': teacher_quiz.id}))

        assert response.status_code == status.HTTP_200_OK
        assert 'is_correct' not in str(response.data)

    def test_cannot_delete_quiz_with_attempts(self, teacher_client, teacher_quiz, student_user):
        QuizAttempt.objects.create(quiz=teacher_quiz, student=student_user, score=0, passed=False)

        response = teacher_client.delete(reverse('quiz-manage', kwargs={'id': teacher_quiz.id}))

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Quiz.objects.filter(id=teacher_quiz.id).exists()
