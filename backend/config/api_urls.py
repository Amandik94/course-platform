from django.urls import path, include

urlpatterns = [
    path('auth/', include('apps.users.urls')),
    path('', include('apps.courses.urls')),
    path('', include('apps.lessons.urls')),
    path('', include('apps.enrollments.urls')),
    path('', include('apps.assignments.urls')),
    path('', include('apps.quizzes.urls')),
    path('', include('apps.certificates.urls')),
]