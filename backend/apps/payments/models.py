from django.conf import settings
from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает оплаты'
        PAID = 'paid', 'Оплачен'
        FAILED = 'failed', 'Не оплачен'
        CANCELLED = 'cancelled', 'Отменен'
        EXPIRED = 'expired', 'Истек'
        REFUNDED = 'refunded', 'Возвращен'

    class Provider(models.TextChoices):
        FREEDOM_PAY = 'freedompay', 'Freedom Pay'
        PAYBOT = 'paybot', 'PayBot (архив)'
        YOOKASSA = 'yookassa', 'YooKassa'

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        limit_choices_to={'role': 'student'},
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.PROTECT,
        related_name='payments',
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='RUB')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    provider = models.CharField(
        max_length=30,
        choices=Provider.choices,
        default=Provider.YOOKASSA,
    )
    provider_payment_id = models.CharField(max_length=100, blank=True)
    provider_redirect_url = models.URLField(blank=True)
    idempotency_key = models.CharField(max_length=255, null=True, blank=True, unique=True)
    order_id = models.CharField(max_length=50, unique=True)
    failure_reason = models.TextField(blank=True)
    raw_callback = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['student', '-created_at'], name='payments_pa_student_7407eb_idx',
            ),
            models.Index(
                fields=['status', '-created_at'], name='payments_pa_status_23f8c5_idx',
            ),
            models.Index(fields=['order_id'], name='payments_pa_order_i_f6e1b3_idx'),
            models.Index(
                fields=['provider_payment_id'], name='payments_pa_provide_2dc293_idx',
            ),
        ]

    def __str__(self):
        return f'{self.order_id} - {self.course.title} - {self.status}'


class ProcessedWebhook(models.Model):
    provider = models.CharField(max_length=30, choices=Payment.Provider.choices)
    webhook_id = models.CharField(max_length=255)
    event_type = models.CharField(max_length=100)
    processed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-processed_at']
        constraints = [
            models.UniqueConstraint(
                fields=['provider', 'webhook_id'],
                name='unique_provider_webhook',
            ),
        ]

    def __str__(self):
        return f'{self.provider}:{self.webhook_id}'
