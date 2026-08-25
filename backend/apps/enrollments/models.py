from django.conf import settings
from django.db import models


class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='enrollments', limit_choices_to={'role': 'student'},
    )
    course = models.ForeignKey(
        'courses.Course', on_delete=models.CASCADE, related_name='enrollments',
    )
    progress = models.PositiveSmallIntegerField(default=0, verbose_name='Прогресс, %')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата записи')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата завершения')

    class Meta:
        verbose_name = 'Запись на курс'
        verbose_name_plural = 'Записи на курсы'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'course'], name='unique_student_course_enrollment'
            )
        ]

    def __str__(self):
        return f'{self.student.email} → {self.course.title}'

    @property
    def is_completed(self):
        return self.completed_at is not None


class LessonProgress(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_progress',
    )
    lesson = models.ForeignKey(
        'lessons.Lesson', on_delete=models.CASCADE, related_name='progress_entries',
    )
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Прогресс по уроку'
        verbose_name_plural = 'Прогресс по урокам'
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'lesson'], name='unique_student_lesson_progress'
            )
        ]

    def __str__(self):
        return f'{self.student.email} — {self.lesson.title} ({"done" if self.is_completed else "in progress"})'