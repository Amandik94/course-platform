from django.urls import path

from .views import CourseReviewListCreateView, ReviewDetailView

urlpatterns = [
    path('courses/<int:course_id>/reviews/', CourseReviewListCreateView.as_view(), name='course-review-list'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
]
