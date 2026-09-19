from django.urls import path

from .views import (
    CreatePaymentView,
    PayBotWebhookView,
    PaymentDetailView,
    PaymentListView,
)


urlpatterns = [
    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('payments/create/', CreatePaymentView.as_view(), name='payment-create'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
    path(
        'payments/paybot/webhook/',
        PayBotWebhookView.as_view(),
        name='paybot-webhook',
    ),
]
