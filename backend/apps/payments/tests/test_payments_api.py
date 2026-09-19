import hashlib
import hmac
import json
import time
import urllib.error
from datetime import timedelta
from decimal import Decimal
from io import BytesIO

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.courses.models import Course
from apps.enrollments.models import Enrollment
from apps.payments.models import Payment, ProcessedWebhook
from apps.payments.services import PayBotClient, PayBotError


PAYBOT_SETTINGS = {
    'PAYBOT_API_KEY': 'kp_test_unit_tests',
    'PAYBOT_API_URL': 'https://api.paybot.kz',
    'PAYBOT_WEBHOOK_SECRET': 'whsec_test_secret',
    'PAYBOT_TIMEOUT_SECONDS': 2,
}


@pytest.fixture(autouse=True)
def paybot_settings(settings):
    for key, value in PAYBOT_SETTINGS.items():
        setattr(settings, key, value)


def make_paid_course(published_course, price='12000.00'):
    published_course.price = Decimal(price)
    published_course.save(update_fields=['price'])
    return published_course


def provider_response(operation_id='op-test-123'):
    return {
        'operation_id': operation_id,
        'deep_link': 'https://qr.kaspi.kz/pay/test',
        'expires_at': (timezone.now() + timedelta(minutes=5)).isoformat(),
        'status': 'QrTokenCreated',
    }


def make_paybot_payment(*, student, course, status_value=Payment.Status.PENDING):
    return Payment.objects.create(
        student=student,
        course=course,
        amount=course.price,
        currency='KZT',
        provider=Payment.Provider.PAYBOT,
        provider_payment_id='op-test-123',
        provider_redirect_url='https://qr.kaspi.kz/pay/test',
        idempotency_key='idem-test-123',
        order_id=f'LMS-{status_value}-test',
        status=status_value,
    )


def webhook_request(
    api_client,
    *,
    event='payment.completed',
    webhook_id='wh-test-1',
    operation_id='op-test-123',
    amount=12000,
    payment_status='paid',
    timestamp=None,
    signature_override=None,
):
    timestamp = str(timestamp or int(time.time()))
    body = json.dumps(
        {
            'id': f'event-{webhook_id}',
            'type': event,
            'created_at': timezone.now().isoformat(),
            'mode': 'test',
            'data': {
                'operation_id': operation_id,
                'amount': amount,
                'status': payment_status,
            },
        },
        separators=(',', ':'),
    ).encode('utf-8')
    digest = hmac.new(
        PAYBOT_SETTINGS['PAYBOT_WEBHOOK_SECRET'].encode(),
        timestamp.encode() + b'.' + body,
        hashlib.sha256,
    ).hexdigest()
    signature = signature_override or f'sha256={digest}'
    return api_client.generic(
        'POST',
        reverse('paybot-webhook'),
        body,
        content_type='application/json',
        HTTP_X_WEBHOOK_ID=webhook_id,
        HTTP_X_WEBHOOK_EVENT=event,
        HTTP_X_WEBHOOK_TIMESTAMP=timestamp,
        HTTP_X_WEBHOOK_SIGNATURE=signature,
    )


@pytest.mark.django_db
class TestPaymentCreate:
    def test_anonymous_cannot_create_payment(self, api_client, published_course):
        make_paid_course(published_course)
        response = api_client.post(reverse('payment-create'), {'course_id': published_course.id})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_wrong_role_cannot_create_payment(self, teacher_client, published_course):
        make_paid_course(published_course)
        response = teacher_client.post(reverse('payment-create'), {'course_id': published_course.id})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_student_payment_uses_database_price(
        self, student_client, published_course, monkeypatch,
    ):
        make_paid_course(published_course)
        captured = {}

        def fake_create_qr(self, *, payment):
            captured['amount'] = payment.amount
            captured['idempotency_key'] = payment.idempotency_key
            return provider_response()

        monkeypatch.setattr('apps.payments.views.PayBotClient.create_qr', fake_create_qr)
        response = student_client.post(
            reverse('payment-create'),
            {'course_id': published_course.id, 'amount': '1.00'},
        )

        assert response.status_code == status.HTTP_201_CREATED
        payment = Payment.objects.get()
        assert payment.amount == Decimal('12000.00')
        assert payment.provider == Payment.Provider.PAYBOT
        assert captured['amount'] == Decimal('12000.00')
        assert captured['idempotency_key'] == payment.idempotency_key
        assert response.data['deep_link'] == 'https://qr.kaspi.kz/pay/test'

    def test_fractional_kzt_price_is_rejected(self, student_client, published_course):
        make_paid_course(published_course, '12000.50')
        response = student_client.post(reverse('payment-create'), {'course_id': published_course.id})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Payment.objects.count() == 0

    def test_free_course_does_not_require_payment(self, student_client, published_course):
        response = student_client.post(reverse('payment-create'), {'course_id': published_course.id})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Payment.objects.count() == 0

    def test_already_enrolled_payment_not_created(
        self, student_client, student_user, published_course,
    ):
        make_paid_course(published_course)
        Enrollment.objects.create(student=student_user, course=published_course)
        response = student_client.post(reverse('payment-create'), {'course_id': published_course.id})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Payment.objects.count() == 0

    def test_duplicate_request_reuses_pending_payment(
        self, student_client, student_user, published_course, monkeypatch,
    ):
        make_paid_course(published_course)
        payment = make_paybot_payment(student=student_user, course=published_course)

        def provider_should_not_be_called(self, *, payment):
            raise AssertionError('provider must not be called')

        monkeypatch.setattr('apps.payments.views.PayBotClient.create_qr', provider_should_not_be_called)
        response = student_client.post(reverse('payment-create'), {'course_id': published_course.id})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == payment.id
        assert Payment.objects.count() == 1

    def test_retryable_provider_error_keeps_pending_payment(
        self, student_client, published_course, monkeypatch,
    ):
        make_paid_course(published_course)

        def timeout(self, *, payment):
            raise PayBotError('timeout', retryable=True)

        monkeypatch.setattr('apps.payments.views.PayBotClient.create_qr', timeout)
        response = student_client.post(reverse('payment-create'), {'course_id': published_course.id})

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert Payment.objects.get().status == Payment.Status.PENDING

    def test_provider_4xx_marks_payment_failed(
        self, student_client, published_course, monkeypatch,
    ):
        make_paid_course(published_course)

        def rejected(self, *, payment):
            raise PayBotError('Некорректный запрос.')

        monkeypatch.setattr('apps.payments.views.PayBotClient.create_qr', rejected)
        response = student_client.post(reverse('payment-create'), {'course_id': published_course.id})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Payment.objects.get().status == Payment.Status.FAILED


@pytest.mark.django_db
class TestPayBotClient:
    def test_successful_qr_response(self, student_user, published_course, monkeypatch):
        course = make_paid_course(published_course)
        payment = make_paybot_payment(student=student_user, course=course)

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return json.dumps({
                    'operation_id': 'op-success',
                    'deep_link': 'https://qr.kaspi.kz/pay/success',
                    'expires_at': '2026-09-17T16:00:00Z',
                    'status': 'pending',
                    'amount': 12000,
                }).encode()

        monkeypatch.setattr('urllib.request.urlopen', lambda request, timeout: FakeResponse())
        result = PayBotClient().create_qr(payment=payment)
        assert result['operation_id'] == 'op-success'

    def test_timeout_is_retryable(self, student_user, published_course, monkeypatch):
        payment = make_paybot_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )

        def raise_timeout(request, timeout):
            raise urllib.error.URLError('timeout')

        monkeypatch.setattr('urllib.request.urlopen', raise_timeout)
        with pytest.raises(PayBotError) as exc_info:
            PayBotClient().create_qr(payment=payment)
        assert exc_info.value.retryable is True

    @pytest.mark.parametrize(('status_code', 'retryable'), [(400, False), (500, True)])
    def test_http_errors(
        self, student_user, published_course, monkeypatch, status_code, retryable,
    ):
        payment = make_paybot_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )

        def raise_http_error(request, timeout):
            raise urllib.error.HTTPError(
                request.full_url,
                status_code,
                'error',
                {},
                BytesIO(b'{"error":{"message":"provider error"}}'),
            )

        monkeypatch.setattr('urllib.request.urlopen', raise_http_error)
        with pytest.raises(PayBotError) as exc_info:
            PayBotClient().create_qr(payment=payment)
        assert exc_info.value.retryable is retryable

    def test_live_key_is_rejected(self, settings, student_user, published_course):
        settings.PAYBOT_API_KEY = 'kp_live_forbidden'
        payment = make_paybot_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )
        with pytest.raises(PayBotError, match='kp_test_'):
            PayBotClient().create_qr(payment=payment)


@pytest.mark.django_db
class TestPayBotWebhook:
    def test_valid_completed_webhook_marks_paid_and_enrolls_once(
        self, api_client, student_user, published_course,
    ):
        payment = make_paybot_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )

        first = webhook_request(api_client)
        second = webhook_request(api_client)

        payment.refresh_from_db()
        assert first.status_code == status.HTTP_200_OK
        assert second.status_code == status.HTTP_200_OK
        assert second.data['status'] == 'duplicate'
        assert payment.status == Payment.Status.PAID
        assert Enrollment.objects.filter(student=student_user, course=published_course).count() == 1
        assert ProcessedWebhook.objects.count() == 1

    def test_invalid_signature_is_rejected(
        self, api_client, student_user, published_course,
    ):
        payment = make_paybot_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )
        response = webhook_request(api_client, signature_override='sha256=invalid')
        payment.refresh_from_db()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert payment.status == Payment.Status.PENDING
        assert ProcessedWebhook.objects.count() == 0

    def test_stale_webhook_is_rejected(self, api_client):
        response = webhook_request(api_client, timestamp=int(time.time()) - 301)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ProcessedWebhook.objects.count() == 0

    @pytest.mark.parametrize(
        ('event', 'expected_status'),
        [
            ('payment.cancelled', Payment.Status.CANCELLED),
            ('payment.expired', Payment.Status.EXPIRED),
        ],
    )
    def test_terminal_unpaid_events(
        self, api_client, student_user, published_course, event, expected_status,
    ):
        payment = make_paybot_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )
        response = webhook_request(api_client, event=event, webhook_id=f'wh-{expected_status}')
        payment.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert payment.status == expected_status
        assert not Enrollment.objects.exists()

    def test_refund_keeps_existing_enrollment(
        self, api_client, student_user, published_course,
    ):
        course = make_paid_course(published_course)
        payment = make_paybot_payment(
            student=student_user,
            course=course,
            status_value=Payment.Status.PAID,
        )
        Enrollment.objects.create(student=student_user, course=course)

        response = webhook_request(
            api_client,
            event='payment.refunded',
            webhook_id='wh-refunded',
        )

        payment.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert payment.status == Payment.Status.REFUNDED
        assert Enrollment.objects.filter(student=student_user, course=course).exists()

    def test_wrong_amount_does_not_complete_payment(
        self, api_client, student_user, published_course,
    ):
        payment = make_paybot_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )
        response = webhook_request(api_client, amount=1, webhook_id='wh-wrong-amount')
        payment.refresh_from_db()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert payment.status == Payment.Status.PENDING
        assert ProcessedWebhook.objects.count() == 0

    def test_unpaid_status_does_not_complete_payment(
        self, api_client, student_user, published_course,
    ):
        payment = make_paybot_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )
        response = webhook_request(
            api_client,
            payment_status='pending',
            webhook_id='wh-unpaid-status',
        )
        payment.refresh_from_db()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert payment.status == Payment.Status.PENDING
        assert ProcessedWebhook.objects.count() == 0

    def test_foreign_operation_is_not_accepted(self, api_client):
        response = webhook_request(
            api_client,
            operation_id='op-does-not-exist',
            webhook_id='wh-unknown-operation',
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert ProcessedWebhook.objects.count() == 0


@pytest.mark.django_db
def test_user_cannot_view_foreign_payment(
    api_client, student_user, published_course, django_user_model,
):
    other_student = django_user_model.objects.create_user(
        email='other-student@test.com',
        password='pass12345',
        role='student',
    )
    payment = make_paybot_payment(
        student=student_user,
        course=make_paid_course(published_course),
    )
    api_client.force_authenticate(other_student)
    response = api_client.get(reverse('payment-detail', kwargs={'pk': payment.pk}))
    assert response.status_code == status.HTTP_404_NOT_FOUND
