from django.contrib import admin

from .models import Enrollment, LessonProgress


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'progress', 'created_at', 'completed_at')
    list_filter = ('completed_at',)
    search_fields = ('student__email', 'course__title')


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'is_completed', 'completed_at')
    list_filter = ('is_completed',)
    search_fields = ('student__email', 'lesson__title')