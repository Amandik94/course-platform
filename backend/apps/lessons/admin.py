from django.contrib import admin

from .models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'type', 'order', 'is_free')
    list_filter = ('type', 'is_free')
    search_fields = ('title',)