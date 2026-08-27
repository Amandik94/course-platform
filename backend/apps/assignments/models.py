from django.conf import settings
from django.db import models


class Assignment(models.Model):
    lesson = models.OneToOneField(
        'lessons.Lesson', on_delete=models.CASCADE, related_name='assignment',
    )
    title = models.CharField(max_length=200)
    description = models.TextField(verbose_name='Условие задания')
    starter_code = models.TextField(blank=True, verbose_name='Начальный код')
    max_score = models.PositiveIntegerField(default=100)
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'

    def __str__(self):
        return self.title


class AssignmentSubmission(models.Model):
    class Status(models.TextChoices):
        NOT_SUBMITTED = 'not_submitted', 'Не отправлено'
        PENDING = 'pending', 'На проверке'
        ACCEPTED = 'accepted', 'Принято'
        REVISION = 'revision', 'На доработку'

    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name='submissions',
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='submissions', limit_choices_to={'role': 'student'},
    )
    code = models.TextField(verbose_name='Код решения')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    score = models.PositiveIntegerField(null=True, blank=True)
    teacher_comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Решение задания'
        verbose_name_plural = 'Решения заданий'
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['assignment', 'student'], name='unique_assignment_student_submission'
            )
        ]

    def __str__(self):
        return f'{self.student.email} — {self.assignment.title} ({self.status})'