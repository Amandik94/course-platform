import json
from datetime import timezone as datetime_timezone
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
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
from .services import (
    PayBotClient,
    PayBotError,
    is_fresh_webhook_timestamp,
    verify_paybot_webhook_signature,
)


class PayBotUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'PayBot временно недоступен. Повторите попытку позже.'


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


class CreatePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Платежи'],
        summary='Создать Sandbox-платеж PayBot',
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
            if course.price != course.price.to_integral_value():
                raise ValidationError({
                    'detail': 'Цена для оплаты через PayBot должна быть указана в целых тенге.'
                })

            payment = (
                Payment.objects.filter(
                    student=request.user,
                    course=course,
                    provider=Payment.Provider.PAYBOT,
                    status=Payment.Status.PENDING,
                )
                .order_by('-created_at')
                .first()
            )
            if payment and payment.expires_at and payment.expires_at <= timezone.now():
                payment.status = Payment.Status.EXPIRED
                payment.save(update_fields=['status', 'updated_at'])
                payment = None

            if payment is None:
                payment = Payment.objects.create(
                    student=request.user,
                    course=course,
                    amount=course.price,
                    currency='KZT',
                    provider=Payment.Provider.PAYBOT,
                    idempotency_key=str(uuid4()),
                    order_id=f'LMS-{uuid4().hex}',
                )

        if payment.provider_redirect_url:
            response_serializer = CreatePaymentResponseSerializer(
                (payment, payment.provider_redirect_url),
                context={'request': request},
            )
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        try:
            provider_response = PayBotClient().create_qr(payment=payment)
        except PayBotError as exc:
            payment.failure_reason = str(exc)
            update_fields = ['failure_reason', 'updated_at']
            if not exc.retryable:
                payment.status = Payment.Status.FAILED
                update_fields.append('status')
            payment.save(update_fields=update_fields)
            if exc.retryable:
                raise PayBotUnavailable(str(exc))
            raise ValidationError({'detail': str(exc)})

        expires_at = parse_datetime(provider_response['expires_at'])
        if expires_at is None:
            payment.status = Payment.Status.FAILED
            payment.failure_reason = 'PayBot вернул некорректный срок действия QR.'
            payment.save(update_fields=['status', 'failure_reason', 'updated_at'])
            raise ValidationError({'detail': payment.failure_reason})
        if timezone.is_naive(expires_at):
            expires_at = timezone.make_aware(expires_at, datetime_timezone.utc)

        payment.provider_payment_id = provider_response['operation_id']
        payment.provider_redirect_url = provider_response['deep_link']
        payment.expires_at = expires_at
        payment.failure_reason = ''
        payment.save(
            update_fields=[
                'provider_payment_id',
                'provider_redirect_url',
                'expires_at',
                'failure_reason',
                'updated_at',
            ]
        )

        response_serializer = CreatePaymentResponseSerializer(
            (payment, payment.provider_redirect_url),
            context={'request': request},
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class PayBotWebhookView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Платежи'],
        summary='Webhook PayBot',
        request=None,
        responses={200: PaymentWebhookResponseSerializer},
        auth=[],
    )
    def post(self, request):
        webhook_id = request.headers.get('X-Webhook-ID', '')
        event_header = request.headers.get('X-Webhook-Event', '')
        timestamp = request.headers.get('X-Webhook-Timestamp', '')
        signature = request.headers.get('X-Webhook-Signature', '')
        raw_body = request.body

        if not all((webhook_id, event_header, timestamp, signature)):
            raise ValidationError({'detail': 'Отсутствуют обязательные заголовки webhook.'})
        if not is_fresh_webhook_timestamp(timestamp):
            raise ValidationError({'detail': 'Webhook timestamp устарел или некорректен.'})
        if not settings.PAYBOT_WEBHOOK_SECRET:
            raise PayBotUnavailable('Не настроена переменная PAYBOT_WEBHOOK_SECRET.')
        if not verify_paybot_webhook_signature(
            timestamp=timestamp,
            raw_body=raw_body,
            signature=signature,
            secret=settings.PAYBOT_WEBHOOK_SECRET,
        ):
            return Response(
                {'detail': 'Некорректная подпись webhook.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            payload = json.loads(raw_body.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ValidationError({'detail': 'Некорректный JSON webhook.'})
        if not isinstance(payload, dict):
            raise ValidationError({'detail': 'Некорректный формат webhook.'})

        event_type = payload.get('event') or payload.get('type')
        if event_type != event_header:
            raise ValidationError({'detail': 'Тип события webhook не совпадает с заголовком.'})
        supported_events = {
            'payment.completed',
            'payment.cancelled',
            'payment.expired',
            'payment.refunded',
            'webhook.test',
        }
        if event_type not in supported_events:
            raise ValidationError({'detail': 'Неподдерживаемый тип события webhook.'})

        with transaction.atomic():
            _, created = ProcessedWebhook.objects.get_or_create(
                provider=Payment.Provider.PAYBOT,
                webhook_id=webhook_id,
                defaults={'event_type': event_type},
            )
            if not created:
                return Response({'status': 'duplicate'}, status=status.HTTP_200_OK)
            if event_type == 'webhook.test':
                return Response({'status': 'ok'}, status=status.HTTP_200_OK)

            data = payload.get('data')
            if not isinstance(data, dict):
                raise ValidationError({'detail': 'Webhook не содержит payment data.'})
            operation_id = str(data.get('operation_id') or '')
            if not operation_id:
                raise ValidationError({'detail': 'Webhook не содержит operation_id.'})
            if event_type == 'payment.completed' and data.get('status') != 'paid':
                raise ValidationError({
                    'detail': 'Статус операции не подтверждает успешную оплату.'
                })

            try:
                payment = (
                    Payment.objects.select_for_update()
                    .select_related('student', 'course')
                    .get(
                        provider=Payment.Provider.PAYBOT,
                        provider_payment_id=operation_id,
                    )
                )
            except Payment.DoesNotExist:
                raise NotFound('Платеж PayBot не найден.')

            if event_type in {'payment.completed', 'payment.refunded'}:
                try:
                    event_amount = Decimal(str(data.get('amount', '')))
                except (InvalidOperation, TypeError):
                    raise ValidationError({'detail': 'Некорректная сумма webhook.'})
                if event_amount.quantize(Decimal('0.01')) != payment.amount:
                    raise ValidationError({'detail': 'Сумма webhook не совпадает с платежом.'})

            sanitized_callback = {
                'id': payload.get('id'),
                'event': event_type,
                'created_at': payload.get('created_at'),
                'data': {
                    'operation_id': operation_id,
                    'amount': data.get('amount'),
                    'status': data.get('status'),
                },
            }
            self._apply_event(payment, event_type, sanitized_callback)

        return Response({'status': 'ok'}, status=status.HTTP_200_OK)

    @staticmethod
    def _apply_event(payment, event_type, callback):
        update_fields = ['status', 'raw_callback', 'failure_reason', 'updated_at']
        notify_student = False

        if event_type == 'payment.completed':
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
        elif event_type == 'payment.cancelled':
            if payment.status not in {Payment.Status.PAID, Payment.Status.REFUNDED}:
                payment.status = Payment.Status.CANCELLED
                payment.failure_reason = 'Платеж отменен.'
        elif event_type == 'payment.expired':
            if payment.status not in {Payment.Status.PAID, Payment.Status.REFUNDED}:
                payment.status = Payment.Status.EXPIRED
                payment.failure_reason = 'Срок действия QR истек.'
        elif event_type == 'payment.refunded':
            if payment.status not in {Payment.Status.PAID, Payment.Status.REFUNDED}:
                raise ValidationError({'detail': 'Возврат допустим только для оплаченного платежа.'})
            payment.status = Payment.Status.REFUNDED
            payment.failure_reason = ''

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
