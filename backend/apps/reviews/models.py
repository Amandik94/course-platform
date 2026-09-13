from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        limit_choices_to={'role': 'student'},
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'student'],
                name='unique_student_course_review',
            )
        ]
        indexes = [
            models.Index(fields=['course', '-created_at']),
            models.Index(fields=['student', '-created_at']),
        ]

    def __str__(self):
        return f'{self.course.title} - {self.student.email} ({self.rating}/5)'
