from rest_framework import serializers

from apps.courses.models import Course
from .models import Payment


class CreatePaymentSerializer(serializers.Serializer):
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.filter(status=Course.Status.PUBLISHED),
        source='course',
    )


class PaymentCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'title', 'slug', 'price')


class PaymentSerializer(serializers.ModelSerializer):
    course = PaymentCourseSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = (
            'id', 'course', 'amount', 'currency', 'status',
            'provider', 'provider_payment_id', 'order_id',
            'created_at', 'updated_at', 'paid_at', 'expires_at',
        )
        read_only_fields = fields


class CreatePaymentResponseSerializer(PaymentSerializer):
    redirect_url = serializers.URLField()

    class Meta(PaymentSerializer.Meta):
        fields = PaymentSerializer.Meta.fields + ('redirect_url',)

    def to_representation(self, instance):
        payment, redirect_url = instance
        data = PaymentSerializer(payment, context=self.context).data
        data['redirect_url'] = redirect_url
        return data


class PaymentWebhookResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
