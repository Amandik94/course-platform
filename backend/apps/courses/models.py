from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    class Level(models.TextChoices):
        BEGINNER = 'beginner', 'Начинающий'
        JUNIOR = 'junior', 'Junior'
        MIDDLE = 'middle', 'Middle'
        ADVANCED = 'advanced', 'Advanced'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        PUBLISHED = 'published', 'Опубликован'
        ARCHIVED = 'archived', 'Архив'

    title = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(verbose_name='Полное описание')
    short_description = models.CharField(max_length=300, verbose_name='Краткое описание')
    cover = models.ImageField(upload_to='courses/covers/', null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='courses', verbose_name='Категория'
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='courses', verbose_name='Преподаватель',
        limit_choices_to={'role': 'teacher'},
    )
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.BEGINNER)
    duration = models.PositiveIntegerField(
        default=0, verbose_name='Длительность (в часах)'
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'level']),  # часто фильтруем по этой паре
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def lessons_count(self):
        return Lesson.objects.filter(section__course=self).count()


class Section(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='sections', verbose_name='Курс'
    )
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Раздел'
        verbose_name_plural = 'Разделы'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.course.title} — {self.title}'


# Lesson объявлена в apps/lessons/models.py, но Course.lessons_count
# выше уже на неё ссылается — импортируем в конце файла, чтобы избежать
# циклического импорта на этапе загрузки модуля.
from apps.lessons.models import Lesson  # noqa: E402