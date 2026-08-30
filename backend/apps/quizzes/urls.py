from django.urls import path

from .views import ( 
    QuizDetailView, SubmitQuizView, QuizDetailView, SubmitQuizView, QuizCreateView,
    QuestionCreateView, QuestionDetailView,
    AnswerCreateView, AnswerDetailView ,
    )

urlpatterns = [
    path('quizzes/<int:id>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/<int:id>/submit/', SubmitQuizView.as_view(), name='quiz-submit'),
    path('lessons/<int:lesson_id>/quiz/', QuizCreateView.as_view(), name='quiz-create'),
    path('quizzes/<int:id>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/<int:id>/submit/', SubmitQuizView.as_view(), name='quiz-submit'),
    path('quizzes/<int:quiz_id>/questions/', QuestionCreateView.as_view(), name='question-create'),
    path('questions/<int:pk>/', QuestionDetailView.as_view(), name='question-detail'),
    path('questions/<int:question_id>/answers/', AnswerCreateView.as_view(), name='answer-create'),
    path('answers/<int:pk>/', AnswerDetailView.as_view(), name='answer-detail'),
]