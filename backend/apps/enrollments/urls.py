from django.urls import path

from .views import EnrollView, MyCoursesView, ProgressListView, CompleteLessonView

urlpatterns = [
    path('courses/<int:id>/enroll/', EnrollView.as_view(), name='course-enroll'),
    path('my-courses/', MyCoursesView.as_view(), name='my-courses'),
    path('progress/', ProgressListView.as_view(), name='progress-list'),
    path('lessons/<int:id>/complete/', CompleteLessonView.as_view(), name='lesson-complete'),
]