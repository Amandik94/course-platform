import pytest
from django.urls import reverse
from rest_framework import status

from apps.courses.models import Section
from apps.lessons.models import Lesson
from apps.quizzes.models import Quiz, Question, Answer
from apps.enrollments.models import Enrollment


@pytest.fixture
def quiz_with_questions(published_course, student_user):
    Enrollment.objects.create(student=student_user, course=published_course)
    section = Section.objects.create(course=published_course, title='Раздел', order=1)
    lesson = Lesson.objects.create(section=section, title='Тест', type='quiz', order=1)
    quiz = Quiz.objects.create(lesson=lesson, title='Проверка знаний', passing_score=70)

    q_single = Question.objects.create(quiz=quiz, question='2+2=?', type='single', points=1, order=1)
    a_correct = Answer.objects.create(question=q_single, text='4', is_correct=True)
    Answer.objects.create(question=q_single, text='5', is_correct=False)

    q_multiple = Question.objects.create(
        quiz=quiz, question='Чётные числа?', type='multiple', points=2, order=2,
    )
    a_2 = Answer.objects.create(question=q_multiple, text='2', is_correct=True)
    a_4 = Answer.objects.create(question=q_multiple, text='4', is_correct=True)
    Answer.objects.create(question=q_multiple, text='3', is_correct=False)

    q_text = Question.objects.create(
        quiz=quiz, question='Столица Франции?', type='text', points=1, order=3,
        text_answer='Париж',
    )

    return {
        'quiz': quiz, 'q_single': q_single, 'a_correct': a_correct,
        'q_multiple': q_multiple, 'a_2': a_2, 'a_4': a_4, 'q_text': q_text,
    }


@pytest.mark.django_db
class TestQuizSubmission:
    def test_correct_answers_give_100_percent(self, student_client, quiz_with_questions):
        d = quiz_with_questions
        response = student_client.post(
            reverse('quiz-submit', kwargs={'id': d['quiz'].id}),
            {
                'answers': [
                    {'question_id': d['q_single'].id, 'answer_id': d['a_correct'].id},
                    {'question_id': d['q_multiple'].id, 'answer_ids': [d['a_2'].id, d['a_4'].id]},
                    {'question_id': d['q_text'].id, 'text': 'Париж'},
                ]
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['score'] == 100
        assert response.data['passed'] is True

    def test_partial_multiple_choice_counts_as_wrong(self, student_client, quiz_with_questions):
        """Выбор только ЧАСТИ правильных вариантов в multiple-choice
        не засчитывается — правило из Этапа 7."""
        d = quiz_with_questions
        response = student_client.post(
            reverse('quiz-submit', kwargs={'id': d['quiz'].id}),
            {
                'answers': [
                    {'question_id': d['q_single'].id, 'answer_id': d['a_correct'].id},
                    {'question_id': d['q_multiple'].id, 'answer_ids': [d['a_2'].id]},  # только один из двух
                    {'question_id': d['q_text'].id, 'text': 'Париж'},
                ]
            },
            format='json',
        )
        # 1 + 1 = 2 балла из 4 максимальных = 50%
        assert response.data['score'] == 50
        assert response.data['passed'] is False  # ниже passing_score=70

    def test_text_answer_case_insensitive(self, student_client, quiz_with_questions):
        d = quiz_with_questions
        response = student_client.post(
            reverse('quiz-submit', kwargs={'id': d['quiz'].id}),
            {
                'answers': [
                    {'question_id': d['q_single'].id, 'answer_id': d['a_correct'].id},
                    {'question_id': d['q_multiple'].id, 'answer_ids': [d['a_2'].id, d['a_4'].id]},
                    {'question_id': d['q_text'].id, 'text': '  париж  '},  # разный регистр + пробелы
                ]
            },
            format='json',
        )
        assert response.data['score'] == 100

    def test_skipped_question_scores_zero(self, student_client, quiz_with_questions):
        d = quiz_with_questions
        response = student_client.post(
            reverse('quiz-submit', kwargs={'id': d['quiz'].id}),
            {'answers': [{'question_id': d['q_single'].id, 'answer_id': d['a_correct'].id}]},
            format='json',
        )
        # только 1 балл из 4 = 25%
        assert response.data['score'] == 25

    def test_student_view_never_exposes_is_correct(self, student_client, quiz_with_questions):
        """Security-критичный тест: студент не должен видеть правильные 
        ответы ДО прохождения теста через API."""
        d = quiz_with_questions
        response = student_client.get(reverse('quiz-detail', kwargs={'id': d['quiz'].id}))

        response_str = str(response.data)
        assert 'is_correct' not in response_str
        assert 'text_answer' not in response_str

    def test_teacher_view_exposes_is_correct(self, teacher_client, quiz_with_questions, teacher_user):
        d = quiz_with_questions
        d['quiz'].lesson.section.course.teacher = teacher_user
        d['quiz'].lesson.section.course.save()

        response = teacher_client.get(reverse('quiz-detail', kwargs={'id': d['quiz'].id}))
        assert 'is_correct' in str(response.data)