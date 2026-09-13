from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('student__email', 'student__first_name', 'student__last_name', 'course__title')
    readonly_fields = ('created_at', 'updated_at')
