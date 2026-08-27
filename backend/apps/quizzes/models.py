from django.conf import settings
from django.db import models


class Quiz(models.Model):
    lesson = models.OneToOneField(
        'lessons.Lesson', on_delete=models.CASCADE, related_name='quiz',
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    passing_score = models.PositiveSmallIntegerField(
        default=70, verbose_name='Проходной балл, %'
    )

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

    def __str__(self):
        return self.title

    @property
    def max_points(self):
        return sum(self.questions.values_list('points', flat=True))


class Question(models.Model):
    class Type(models.TextChoices):
        SINGLE = 'single', 'Один вариант'
        MULTIPLE = 'multiple', 'Несколько вариантов'
        TEXT = 'text', 'Текстовый ответ'

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question = models.CharField(max_length=500, verbose_name='Текст вопроса')
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.SINGLE)
    points = models.PositiveSmallIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    # используется только для типа TEXT — эталонный ответ для автопроверки
    text_answer = models.CharField(max_length=500, blank=True, verbose_name='Эталонный текстовый ответ')

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['order', 'id']

    def __str__(self):
        return self.question[:50]


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    """
    Попытка прохождения теста студентом. Не описана явно в ТЗ как отдельная
    модель, но необходима технически: без неё нельзя хранить результат
    прохождения (баллы, пройден/не пройден, историю попыток).
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts',
    )
    score = models.PositiveSmallIntegerField(verbose_name='Набранный балл, %')
    passed = models.BooleanField(default=False)
    answers_snapshot = models.JSONField(
        default=dict, verbose_name='Ответы студента (снимок на момент прохождения)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Попытка прохождения теста'
        verbose_name_plural = 'Попытки прохождения тестов'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student.email} — {self.quiz.title} ({self.score}%)'