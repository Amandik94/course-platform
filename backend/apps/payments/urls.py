from django.urls import path

from .views import (
    CreatePaymentView,
    PaymentDetailView,
    PaymentListView,
    YooKassaWebhookView,
)


urlpatterns = [
    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('payments/create/', CreatePaymentView.as_view(), name='payment-create'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
    path(
        'payments/yookassa/webhook/',
        YooKassaWebhookView.as_view(),
        name='yookassa-webhook',
    ),
]
