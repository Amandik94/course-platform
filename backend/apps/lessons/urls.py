from django.urls import path

from .views import LessonListCreateView, LessonDetailView

urlpatterns = [
    path('sections/<int:section_id>/lessons/', LessonListCreateView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
]