from django.contrib import admin

from .models import Payment, ProcessedWebhook


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'order_id', 'student', 'course', 'amount', 'currency',
        'status', 'provider', 'provider_payment_id', 'created_at', 'paid_at',
    )
    list_filter = ('status', 'provider', 'currency', 'created_at', 'paid_at')
    search_fields = (
        'order_id', 'provider_payment_id', 'student__email', 'course__title',
    )
    readonly_fields = (
        'student', 'course', 'amount', 'currency', 'provider',
        'provider_payment_id', 'order_id', 'raw_callback',
        'created_at', 'updated_at', 'paid_at',
    )


@admin.register(ProcessedWebhook)
class ProcessedWebhookAdmin(admin.ModelAdmin):
    list_display = ('webhook_id', 'provider', 'event_type', 'processed_at')
    list_filter = ('provider', 'event_type', 'processed_at')
    search_fields = ('webhook_id',)
    readonly_fields = ('provider', 'webhook_id', 'event_type', 'processed_at')
