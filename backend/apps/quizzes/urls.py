from django.urls import path

from .views import QuizDetailView, SubmitQuizView

urlpatterns = [
    path('quizzes/<int:id>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/<int:id>/submit/', SubmitQuizView.as_view(), name='quiz-submit'),
]