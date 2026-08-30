from rest_framework import serializers

from .models import Answer, Question, Quiz, QuizAttempt


class AnswerPublicSerializer(serializers.ModelSerializer):
    """Для студента ДО прохождения — без is_correct!"""
    class Meta:
        model = Answer
        fields = ('id', 'text')


class QuestionPublicSerializer(serializers.ModelSerializer):
    """Для студента — вопрос без правильных ответов/эталонного текста."""
    answers = AnswerPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'question', 'type', 'points', 'order', 'answers')


class QuizPublicSerializer(serializers.ModelSerializer):
    """GET /quizzes/{id}/ — то, что видит студент перед прохождением."""
    questions = QuestionPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ('id', 'lesson', 'title', 'description', 'passing_score', 'questions')


# --- сериализаторы для управления тестом преподавателем ---

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'question', 'text', 'is_correct')
        read_only_fields = ('question',)


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'quiz', 'question', 'type', 'points', 'order', 'text_answer', 'answers')
        read_only_fields = ('quiz',)


class QuizSerializer(serializers.ModelSerializer):
    """Для преподавателя — создание/редактирование теста (с is_correct)."""
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ('id', 'lesson', 'title', 'description', 'passing_score', 'questions')
        read_only_fields = ('lesson',)


# --- прохождение теста ---

class SubmitAnswerItemSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    # для single: answer_id (int); для multiple: answer_ids (list[int]);
    # для text: text (str). Валидируем гибко на уровне view/логики.
    answer_id = serializers.IntegerField(required=False)
    answer_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    text = serializers.CharField(required=False, allow_blank=True)


class SubmitQuizSerializer(serializers.Serializer):
    answers = SubmitAnswerItemSerializer(many=True)


class QuizAttemptResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = ('id', 'quiz', 'score', 'passed', 'answers_snapshot', 'created_at')
        read_only_fields = fields
        
        
class QuizCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ('id', 'lesson', 'title', 'description', 'passing_score')
        read_only_fields = ('lesson',)


class QuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'quiz', 'question', 'type', 'points', 'order', 'text_answer')
        read_only_fields = ('quiz',)


class AnswerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'question', 'text', 'is_correct')
        read_only_fields = ('question',)