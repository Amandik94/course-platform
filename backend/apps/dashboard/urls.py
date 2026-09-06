from django.urls import path

from .views import AdminDashboardView, StudentDashboardView, TeacherDashboardView

urlpatterns = [
    path('dashboard/student/', StudentDashboardView.as_view(), name='dashboard-student'),
    path('dashboard/teacher/', TeacherDashboardView.as_view(), name='dashboard-teacher'),
    path('dashboard/admin/', AdminDashboardView.as_view(), name='dashboard-admin'),
]