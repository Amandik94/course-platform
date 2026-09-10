from django.urls import path

from .views import CertificateDetailView, CertificateDownloadView, CertificateListView

urlpatterns = [
    path('certificates/', CertificateListView.as_view(), name='certificate-list'),
    path('certificates/<int:pk>/', CertificateDetailView.as_view(), name='certificate-detail'),
    path('certificates/<int:pk>/download/', CertificateDownloadView.as_view(), name='certificate-download'),
]
