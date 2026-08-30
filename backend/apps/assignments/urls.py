from django.urls import path

from .views import (
    AssignmentDetailView, SubmitAssignmentView,
    AssignmentSubmissionsListView, SubmissionReviewView,
    AssignmentCreateView, AssignmentUpdateView,
)

urlpatterns = [
    path('lessons/<int:lesson_id>/assignment/', AssignmentCreateView.as_view(), name='assignment-create'),
    path('assignments/<int:id>/', AssignmentDetailView.as_view(), name='assignment-detail'),
    path('assignments/<int:id>/manage/', AssignmentUpdateView.as_view(), name='assignment-manage'),
    path('assignments/<int:id>/submit/', SubmitAssignmentView.as_view(), name='assignment-submit'),
    path('assignments/<int:id>/submissions/', AssignmentSubmissionsListView.as_view(), name='assignment-submissions'),
    path('submissions/<int:pk>/', SubmissionReviewView.as_view(), name='submission-review'),
]