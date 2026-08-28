from django.urls import path

from .views import CertificateListView, CertificateDetailView

urlpatterns = [
    path('certificates/', CertificateListView.as_view(), name='certificate-list'),
    path('certificates/<int:pk>/', CertificateDetailView.as_view(), name='certificate-detail'),
]