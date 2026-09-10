from django.conf import settings
from django.db import models


class Quiz(models.Model):
    lesson = models.OneToOneField(
        'lessons.Lesson', on_delete=models.CASCADE, related_name='quiz',
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    passing_score = models.PositiveSmallIntegerField(default=70, verbose_name='Passing score, %')

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'
        constraints = [
            models.CheckConstraint(
                check=models.Q(passing_score__gte=0, passing_score__lte=100),
                name='quiz_passing_score_0_100',
            )
        ]

    def __str__(self):
        return self.title

    @property
    def max_points(self):
        return sum(self.questions.values_list('points', flat=True))


class Question(models.Model):
    class Type(models.TextChoices):
        SINGLE = 'single', 'Single choice'
        MULTIPLE = 'multiple', 'Multiple choice'
        TEXT = 'text', 'Text answer'

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question = models.CharField(max_length=500, verbose_name='Question text')
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.SINGLE)
    points = models.PositiveSmallIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    text_answer = models.CharField(max_length=500, blank=True, verbose_name='Expected text answer')

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['order', 'id']

    def __str__(self):
        return self.question[:50]


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Answer option'
        verbose_name_plural = 'Answer options'

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts',
    )
    score = models.PositiveSmallIntegerField(verbose_name='Score, %')
    passed = models.BooleanField(default=False)
    answers_snapshot = models.JSONField(default=dict, verbose_name='Submitted answers snapshot')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Quiz attempt'
        verbose_name_plural = 'Quiz attempts'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(score__gte=0, score__lte=100),
                name='quiz_attempt_score_0_100',
            )
        ]

    def __str__(self):
        return f'{self.student.email} - {self.quiz.title} ({self.score}%)'
