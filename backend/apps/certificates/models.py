from django.conf import settings
from django.db import models


class Certificate(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates',
    )
    course = models.ForeignKey(
        'courses.Course', on_delete=models.CASCADE, related_name='certificates',
    )
    certificate_number = models.CharField(max_length=30, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    pdf = models.FileField(upload_to='certificates/', null=True, blank=True)

    class Meta:
        verbose_name = 'Сертификат'
        verbose_name_plural = 'Сертификаты'
        ordering = ['-issued_at']
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'course'], name='unique_student_course_certificate'
            )
        ]

    def __str__(self):
        return f'{self.certificate_number} — {self.student.email} — {self.course.title}'