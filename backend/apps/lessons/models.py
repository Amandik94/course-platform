from django.db import models


class Lesson(models.Model):
    class Type(models.TextChoices):
        TEXT = 'text', 'Текст'
        VIDEO = 'video', 'Видео'
        ASSIGNMENT = 'assignment', 'Задание'
        QUIZ = 'quiz', 'Тест'
        FILE = 'file', 'Файл'
        PROJECT = 'project', 'Проект'

    section = models.ForeignKey(
        'courses.Section', on_delete=models.CASCADE, related_name='lessons', verbose_name='Раздел'
    )
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.TEXT)
    content = models.TextField(blank=True, verbose_name='Текстовый контент')
    video_url = models.URLField(blank=True, verbose_name='Ссылка на видео')
    duration = models.PositiveIntegerField(default=0, verbose_name='Длительность (мин)')
    order = models.PositiveIntegerField(default=0)
    is_free = models.BooleanField(default=False, verbose_name='Бесплатный урок (превью)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.section.course.title} — {self.title}'