from django.urls import path

from .views import (
    CategoryListView, CourseListCreateView, CourseDetailView,
    SectionListCreateView, SectionDetailView,
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),

    path('courses/', CourseListCreateView.as_view(), name='course-list'),
    path('courses/<int:id>/', CourseDetailView.as_view(), name='course-detail'),
    path('courses/<int:course_id>/sections/', SectionListCreateView.as_view(), name='section-list'),

    path('sections/<int:pk>/', SectionDetailView.as_view(), name='section-detail'),
]