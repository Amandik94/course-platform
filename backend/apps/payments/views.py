import json
import logging
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions, status
from rest_framework.exceptions import APIException, NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import Course
from apps.enrollments.models import Enrollment
from apps.notifications.models import Notification
from apps.notifications.services import create_notification
from .models import Payment, ProcessedWebhook
from .permissions import IsPaymentOwnerOrAdmin
from .serializers import (
    CreatePaymentResponseSerializer,
    CreatePaymentSerializer,
    PaymentSerializer,
    PaymentWebhookResponseSerializer,
)
from .services import YooKassaClient, YooKassaError


logger = logging.getLogger(__name__)


class YooKassaUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'YooKassa временно недоступна. Повторите попытку позже.'


def validate_provider_payment(provider_payment, payment):
    if provider_payment.get('test') is not True:
        raise ValidationError({'detail': 'Получен не тестовый платеж YooKassa.'})
    amount = provider_payment.get('amount')
    if not isinstance(amount, dict) or amount.get('currency') != 'RUB':
        raise ValidationError({'detail': 'Валюта платежа YooKassa не совпадает с RUB.'})
    try:
        provider_amount = Decimal(str(amount.get('value'))).quantize(Decimal('0.01'))
    except (InvalidOperation, TypeError):
        raise ValidationError({'detail': 'Некорректная сумма платежа YooKassa.'})
    if provider_amount != payment.amount.quantize(Decimal('0.01')):
        raise ValidationError({'detail': 'Сумма YooKassa не совпадает с локальным платежом.'})
    if payment.currency != 'RUB':
        raise ValidationError({'detail': 'Локальный платеж создан не в RUB.'})

    metadata = provider_payment.get('metadata')
    if not isinstance(metadata, dict):
        raise ValidationError({'detail': 'Платеж YooKassa не содержит metadata.'})
    if str(metadata.get('payment_id') or '') != str(payment.id):
        raise ValidationError({'detail': 'Идентификатор локального платежа не совпадает.'})
    if str(metadata.get('order_id') or '') != payment.order_id:
        raise ValidationError({'detail': 'Номер заказа YooKassa не совпадает.'})
    if str(metadata.get('course_id') or '') != str(payment.course_id):
        raise ValidationError({'detail': 'Идентификатор курса YooKassa не совпадает.'})


def apply_payment_event(payment, event_type, callback):
    update_fields = ['status', 'raw_callback', 'failure_reason', 'updated_at']
    notify_student = False

    if event_type == 'payment.succeeded':
        if payment.status == Payment.Status.REFUNDED:
            raise ValidationError({'detail': 'Возвращенный платеж нельзя снова завершить.'})
        notify_student = payment.status != Payment.Status.PAID
        payment.status = Payment.Status.PAID
        payment.paid_at = payment.paid_at or timezone.now()
        payment.failure_reason = ''
        update_fields.append('paid_at')
        Enrollment.objects.get_or_create(
            student=payment.student,
            course=payment.course,
        )
    elif event_type == 'payment.canceled':
        if payment.status not in {Payment.Status.PAID, Payment.Status.REFUNDED}:
            payment.status = Payment.Status.CANCELLED
            payment.failure_reason = 'Платеж отменен.'

    payment.raw_callback = callback
    payment.save(update_fields=list(dict.fromkeys(update_fields)))

    if notify_student:
        create_notification(
            user=payment.student,
            type=Notification.Type.COURSE,
            title='Оплата курса успешно завершена',
            message=f'Курс «{payment.course.title}» добавлен в раздел «Мои курсы».',
            link='/my-courses',
        )


def reconcile_yookassa_payment(payment):
    """Synchronize a pending payment using YooKassa as the source of truth."""
    if (
        payment.status != Payment.Status.PENDING
        or payment.provider != Payment.Provider.YOOKASSA
        or not payment.provider_payment_id
    ):
        return payment

    try:
        provider_payment = YooKassaClient().get_payment(payment.provider_payment_id)
    except YooKassaError as exc:
        logger.warning('YooKassa payment status sync failed for payment %s: %s', payment.pk, exc)
        return payment

    provider_status = provider_payment.get('status')
    event_type = {
        'succeeded': 'payment.succeeded',
        'canceled': 'payment.canceled',
    }.get(provider_status)
    if event_type is None:
        return payment
    if event_type == 'payment.succeeded' and provider_payment.get('paid') is not True:
        raise ValidationError({'detail': 'YooKassa не подтвердила оплату платежа.'})

    with transaction.atomic():
        locked_payment = (
            Payment.objects.select_for_update()
            .select_related('student', 'course')
            .get(pk=payment.pk)
        )
        validate_provider_payment(provider_payment, locked_payment)
        callback = {
            'event': event_type,
            'source': 'status_sync',
            'object': {
                'id': payment.provider_payment_id,
                'status': provider_status,
                'paid': provider_payment.get('paid'),
                'amount': provider_payment.get('amount'),
                'test': provider_payment.get('test'),
            },
        }
        apply_payment_event(locked_payment, event_type, callback)
        return locked_payment


@extend_schema_view(
    get=extend_schema(tags=['Платежи'], summary='Мои платежи'),
)
class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Payment.objects.none()
        queryset = Payment.objects.select_related('student', 'course')
        if self.request.user.is_admin_role:
            return queryset
        return queryset.filter(student=self.request.user)


@extend_schema_view(
    get=extend_schema(tags=['Платежи'], summary='Статус платежа'),
)
class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsPaymentOwnerOrAdmin]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Payment.objects.none()
        queryset = Payment.objects.select_related('student', 'course')
        if self.request.user.is_admin_role:
            return queryset
        return queryset.filter(student=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        payment = reconcile_yookassa_payment(self.get_object())
        serializer = self.get_serializer(payment)
        return Response(serializer.data)


class CreatePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Платежи'],
        summary='Создать тестовый платеж YooKassa',
        request=CreatePaymentSerializer,
        responses={201: CreatePaymentResponseSerializer, 200: CreatePaymentResponseSerializer},
    )
    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.validated_data['course']

        if not request.user.is_student:
            raise PermissionDenied('Покупать курсы могут только студенты.')

        with transaction.atomic():
            course = Course.objects.select_for_update().get(pk=course.pk)
            if course.status != Course.Status.PUBLISHED:
                raise NotFound('Курс не найден.')
            if Enrollment.objects.filter(student=request.user, course=course).exists():
                raise ValidationError({'detail': 'Вы уже записаны на этот курс.'})
            if course.price <= Decimal('0.00'):
                raise ValidationError({
                    'detail': 'Этот курс бесплатный. Используйте обычную запись на курс.'
                })

            payment = (
                Payment.objects.filter(
                    student=request.user,
                    course=course,
                    provider=Payment.Provider.YOOKASSA,
                    status=Payment.Status.PENDING,
                )
                .order_by('-created_at')
                .first()
            )
            if payment is None:
                payment = Payment.objects.create(
                    student=request.user,
                    course=course,
                    amount=course.price,
                    currency='RUB',
                    provider=Payment.Provider.YOOKASSA,
                    idempotency_key=str(uuid4()),
                    order_id=f'LMS-{uuid4().hex}',
                )

        if payment.provider_redirect_url:
            response_serializer = CreatePaymentResponseSerializer(
                (payment, payment.provider_redirect_url),
                context={'request': request},
            )
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        return_url = (
            f'{settings.PUBLIC_FRONTEND_URL.rstrip("/")}/payment/success'
            f'?payment_id={payment.id}&course_id={course.id}'
        )
        try:
            provider_response = YooKassaClient().create_payment(
                payment=payment,
                return_url=return_url,
            )
        except YooKassaError as exc:
            payment.failure_reason = str(exc)
            update_fields = ['failure_reason', 'updated_at']
            if not exc.retryable:
                payment.status = Payment.Status.FAILED
                update_fields.append('status')
            payment.save(update_fields=update_fields)
            if exc.retryable:
                raise YooKassaUnavailable(str(exc))
            raise ValidationError({'detail': str(exc)})

        payment.provider_payment_id = provider_response['provider_payment_id']
        payment.provider_redirect_url = provider_response['redirect_url']
        payment.failure_reason = ''
        payment.save(
            update_fields=[
                'provider_payment_id',
                'provider_redirect_url',
                'failure_reason',
                'updated_at',
            ]
        )

        response_serializer = CreatePaymentResponseSerializer(
            (payment, payment.provider_redirect_url),
            context={'request': request},
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class YooKassaWebhookView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Платежи'],
        summary='HTTP-уведомление YooKassa',
        request=None,
        responses={200: PaymentWebhookResponseSerializer},
        auth=[],
    )
    def post(self, request):
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ValidationError({'detail': 'Некорректный JSON уведомления.'})
        if not isinstance(payload, dict):
            raise ValidationError({'detail': 'Некорректный формат уведомления.'})

        event_type = payload.get('event')
        if event_type not in {'payment.succeeded', 'payment.canceled'}:
            return Response({'status': 'ignored'}, status=status.HTTP_200_OK)
        notification_object = payload.get('object')
        if not isinstance(notification_object, dict):
            raise ValidationError({'detail': 'Уведомление не содержит объект платежа.'})
        provider_payment_id = str(notification_object.get('id') or '')
        if not provider_payment_id:
            raise ValidationError({'detail': 'Уведомление не содержит идентификатор платежа.'})

        try:
            provider_payment = YooKassaClient().get_payment(provider_payment_id)
        except YooKassaError as exc:
            raise YooKassaUnavailable(str(exc))

        expected_provider_status = {
            'payment.succeeded': 'succeeded',
            'payment.canceled': 'canceled',
        }[event_type]
        if provider_payment.get('status') != expected_provider_status:
            raise ValidationError({'detail': 'Статус платежа YooKassa не подтверждает событие.'})
        if event_type == 'payment.succeeded' and provider_payment.get('paid') is not True:
            raise ValidationError({'detail': 'YooKassa не подтвердила оплату платежа.'})

        with transaction.atomic():
            try:
                payment = (
                    Payment.objects.select_for_update()
                    .select_related('student', 'course')
                    .get(
                        provider=Payment.Provider.YOOKASSA,
                        provider_payment_id=provider_payment_id,
                    )
                )
            except Payment.DoesNotExist:
                raise NotFound('Платеж YooKassa не найден.')

            validate_provider_payment(provider_payment, payment)
            webhook_id = f'{event_type}:{provider_payment_id}'
            _, created = ProcessedWebhook.objects.get_or_create(
                provider=Payment.Provider.YOOKASSA,
                webhook_id=webhook_id,
                defaults={'event_type': event_type},
            )
            if not created:
                return Response({'status': 'duplicate'}, status=status.HTTP_200_OK)

            callback = {
                'event': event_type,
                'object': {
                    'id': provider_payment_id,
                    'status': provider_payment.get('status'),
                    'paid': provider_payment.get('paid'),
                    'amount': provider_payment.get('amount'),
                    'test': provider_payment.get('test'),
                },
            }
            apply_payment_event(payment, event_type, callback)

        return Response({'status': 'ok'}, status=status.HTTP_200_OK)
