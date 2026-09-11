from django.urls import path, include

from apps.users.views import AdminUserDetailView, AdminUserListView

urlpatterns = [
    path('auth/', include('apps.users.urls')),
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/users/<int:id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('', include('apps.courses.urls')),
    path('', include('apps.lessons.urls')),
    path('', include('apps.enrollments.urls')),
    path('', include('apps.assignments.urls')),
    path('', include('apps.quizzes.urls')),
    path('', include('apps.certificates.urls')),
    path('', include('apps.dashboard.urls')),
]
