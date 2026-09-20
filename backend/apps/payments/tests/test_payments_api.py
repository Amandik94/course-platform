import json
import urllib.error
from decimal import Decimal
from io import BytesIO

import pytest
from django.urls import reverse
from rest_framework import status

from apps.enrollments.models import Enrollment
from apps.payments.models import Payment, ProcessedWebhook
from apps.payments.services import YooKassaClient, YooKassaError


YOOKASSA_SETTINGS = {
    'YOOKASSA_SHOP_ID': 'test-shop-id',
    'YOOKASSA_SECRET_KEY': 'test-secret-key',
    'YOOKASSA_API_URL': 'https://api.yookassa.ru/v3',
    'YOOKASSA_TIMEOUT_SECONDS': 2,
    'PUBLIC_FRONTEND_URL': 'https://lms.example.test',
}


@pytest.fixture(autouse=True)
def yookassa_settings(settings):
    for key, value in YOOKASSA_SETTINGS.items():
        setattr(settings, key, value)


def make_paid_course(published_course, price='1490.00'):
    published_course.price = Decimal(price)
    published_course.save(update_fields=['price'])
    return published_course


def created_payment_response(payment=None):
    amount = payment.amount if payment else Decimal('1490.00')
    return {
        'id': 'yk-test-123',
        'status': 'pending',
        'paid': False,
        'amount': {'value': format(amount, '.2f'), 'currency': 'RUB'},
        'confirmation': {
            'type': 'redirect',
            'confirmation_url': 'https://yoomoney.ru/api-pages/v2/payment-confirm/test',
        },
        'test': True,
    }


def make_yookassa_payment(*, student, course, status_value=Payment.Status.PENDING):
    return Payment.objects.create(
        student=student,
        course=course,
        amount=course.price,
        currency='RUB',
        provider=Payment.Provider.YOOKASSA,
        provider_payment_id='yk-test-123',
        provider_redirect_url='https://yoomoney.ru/api-pages/v2/payment-confirm/test',
        idempotency_key='idem-test-123',
        order_id=f'LMS-{status_value}-test',
        status=status_value,
    )


def verified_provider_payment(payment, *, provider_status='succeeded', **overrides):
    data = {
        'id': payment.provider_payment_id,
        'status': provider_status,
        'paid': provider_status == 'succeeded',
        'amount': {'value': format(payment.amount, '.2f'), 'currency': 'RUB'},
        'metadata': {
            'payment_id': str(payment.id),
            'order_id': payment.order_id,
            'course_id': str(payment.course_id),
        },
        'test': True,
    }
    data.update(overrides)
    return data


def send_notification(api_client, monkeypatch, payment, *, event='payment.succeeded', provider=None):
    provider = provider or verified_provider_payment(
        payment,
        provider_status='succeeded' if event == 'payment.succeeded' else 'canceled',
    )
    monkeypatch.setattr(
        'apps.payments.views.YooKassaClient.get_payment',
        lambda self, provider_payment_id: provider,
    )
    return api_client.post(
        reverse('yookassa-webhook'),
        {'event': event, 'object': {'id': payment.provider_payment_id}},
        format='json',
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

    def test_nonexistent_course_is_rejected(self, student_client):
        response = student_client.post(reverse('payment-create'), {'course_id': 999999})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Payment.objects.count() == 0

    def test_draft_course_is_rejected(self, student_client, published_course):
        published_course.status = 'draft'
        published_course.price = Decimal('1490.00')
        published_course.save(update_fields=['status', 'price'])
        response = student_client.post(
            reverse('payment-create'), {'course_id': published_course.id}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Payment.objects.count() == 0

    def test_student_payment_uses_database_price_and_rub(
        self, student_client, published_course, monkeypatch,
    ):
        make_paid_course(published_course)
        captured = {}

        def fake_create(self, *, payment, return_url):
            captured['amount'] = payment.amount
            captured['currency'] = payment.currency
            captured['idempotency_key'] = payment.idempotency_key
            captured['return_url'] = return_url
            return {
                'provider_payment_id': 'yk-test-123',
                'redirect_url': 'https://yoomoney.ru/api-pages/v2/payment-confirm/test',
                'status': 'pending',
            }

        monkeypatch.setattr('apps.payments.views.YooKassaClient.create_payment', fake_create)
        response = student_client.post(
            reverse('payment-create'),
            {'course_id': published_course.id, 'amount': '1.00', 'currency': 'USD'},
        )

        assert response.status_code == status.HTTP_201_CREATED
        payment = Payment.objects.get()
        assert payment.amount == Decimal('1490.00')
        assert payment.currency == 'RUB'
        assert payment.provider == Payment.Provider.YOOKASSA
        assert captured['amount'] == Decimal('1490.00')
        assert captured['currency'] == 'RUB'
        assert captured['idempotency_key'] == payment.idempotency_key
        assert captured['return_url'].startswith('https://lms.example.test/payment/success')
        assert response.data['redirect_url'].startswith('https://yoomoney.ru/')

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
        payment = make_yookassa_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )

        def provider_should_not_be_called(self, *, payment, return_url):
            raise AssertionError('provider must not be called')

        monkeypatch.setattr(
            'apps.payments.views.YooKassaClient.create_payment',
            provider_should_not_be_called,
        )
        response = student_client.post(reverse('payment-create'), {'course_id': published_course.id})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == payment.id
        assert Payment.objects.count() == 1

    def test_retryable_provider_error_keeps_pending_payment(
        self, student_client, published_course, monkeypatch,
    ):
        make_paid_course(published_course)

        def timeout(self, *, payment, return_url):
            raise YooKassaError('timeout', retryable=True)

        monkeypatch.setattr('apps.payments.views.YooKassaClient.create_payment', timeout)
        response = student_client.post(reverse('payment-create'), {'course_id': published_course.id})
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert Payment.objects.get().status == Payment.Status.PENDING

    def test_provider_rejection_marks_payment_failed(
        self, student_client, published_course, monkeypatch,
    ):
        make_paid_course(published_course)

        def rejected(self, *, payment, return_url):
            raise YooKassaError('Некорректный запрос.')

        monkeypatch.setattr('apps.payments.views.YooKassaClient.create_payment', rejected)
        response = student_client.post(reverse('payment-create'), {'course_id': published_course.id})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Payment.objects.get().status == Payment.Status.FAILED


@pytest.mark.django_db
class TestYooKassaClient:
    def test_successful_create_payment(self, student_user, published_course, monkeypatch):
        payment = make_yookassa_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return json.dumps(created_payment_response(payment)).encode()

        captured = {}

        def fake_urlopen(request, timeout):
            captured['request'] = request
            captured['timeout'] = timeout
            return FakeResponse()

        monkeypatch.setattr('urllib.request.urlopen', fake_urlopen)
        result = YooKassaClient().create_payment(
            payment=payment,
            return_url='https://lms.example.test/payment/success',
        )
        request_payload = json.loads(captured['request'].data.decode())
        assert result['provider_payment_id'] == 'yk-test-123'
        assert request_payload['amount'] == {'value': '1490.00', 'currency': 'RUB'}
        assert request_payload['capture'] is True
        assert captured['request'].headers['Idempotence-key'] == payment.idempotency_key

    def test_timeout_is_retryable(self, student_user, published_course, monkeypatch):
        payment = make_yookassa_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )
        monkeypatch.setattr(
            'urllib.request.urlopen',
            lambda request, timeout: (_ for _ in ()).throw(urllib.error.URLError('timeout')),
        )
        with pytest.raises(YooKassaError) as exc_info:
            YooKassaClient().create_payment(
                payment=payment,
                return_url='https://lms.example.test/payment/success',
            )
        assert exc_info.value.retryable is True

    @pytest.mark.parametrize(('status_code', 'retryable'), [(400, False), (500, True)])
    def test_http_errors(
        self, student_user, published_course, monkeypatch, status_code, retryable,
    ):
        payment = make_yookassa_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )

        def raise_http_error(request, timeout):
            raise urllib.error.HTTPError(
                request.full_url,
                status_code,
                'error',
                {},
                BytesIO(b'{"description":"provider error"}'),
            )

        monkeypatch.setattr('urllib.request.urlopen', raise_http_error)
        with pytest.raises(YooKassaError) as exc_info:
            YooKassaClient().create_payment(
                payment=payment,
                return_url='https://lms.example.test/payment/success',
            )
        assert exc_info.value.retryable is retryable

    def test_non_test_payment_is_rejected(self, student_user, published_course):
        payment = make_yookassa_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )
        data = created_payment_response(payment)
        data['test'] = False
        with pytest.raises(YooKassaError, match='тестовом магазине'):
            YooKassaClient._validate_created_payment(data, payment=payment)

    def test_api_url_is_not_accepted_as_confirmation(self):
        with pytest.raises(YooKassaError, match='недопустимую ссылку'):
            YooKassaClient._validate_confirmation_url('https://api.yookassa.ru/v3/payments/1')


@pytest.mark.django_db
class TestYooKassaWebhook:
    def test_succeeded_marks_paid_and_enrolls_once(
        self, api_client, student_user, published_course, monkeypatch,
    ):
        payment = make_yookassa_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )
        first = send_notification(api_client, monkeypatch, payment)
        second = send_notification(api_client, monkeypatch, payment)

        payment.refresh_from_db()
        assert first.status_code == status.HTTP_200_OK
        assert second.status_code == status.HTTP_200_OK
        assert second.data['status'] == 'duplicate'
        assert payment.status == Payment.Status.PAID
        assert Enrollment.objects.filter(student=student_user, course=published_course).count() == 1
        assert ProcessedWebhook.objects.count() == 1

    def test_amount_mismatch_is_rejected(
        self, api_client, student_user, published_course, monkeypatch,
    ):
        payment = make_yookassa_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )
        provider = verified_provider_payment(payment)
        provider['amount']['value'] = '1.00'
        response = send_notification(api_client, monkeypatch, payment, provider=provider)
        payment.refresh_from_db()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert payment.status == Payment.Status.PENDING
        assert not Enrollment.objects.exists()

    def test_currency_mismatch_is_rejected(
        self, api_client, student_user, published_course, monkeypatch,
    ):
        payment = make_yookassa_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )
        provider = verified_provider_payment(payment)
        provider['amount']['currency'] = 'USD'
        response = send_notification(api_client, monkeypatch, payment, provider=provider)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Enrollment.objects.exists()

    def test_canceled_updates_local_status(
        self, api_client, student_user, published_course, monkeypatch,
    ):
        payment = make_yookassa_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )
        response = send_notification(
            api_client, monkeypatch, payment, event='payment.canceled'
        )
        payment.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert payment.status == Payment.Status.CANCELLED
        assert not Enrollment.objects.exists()

    def test_provider_status_must_confirm_event(
        self, api_client, student_user, published_course, monkeypatch,
    ):
        payment = make_yookassa_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )
        provider = verified_provider_payment(payment, provider_status='pending')
        response = send_notification(api_client, monkeypatch, payment, provider=provider)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Enrollment.objects.exists()

    def test_metadata_mismatch_is_rejected(
        self, api_client, student_user, published_course, monkeypatch,
    ):
        payment = make_yookassa_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )
        provider = verified_provider_payment(payment)
        provider['metadata']['payment_id'] = '999999'
        response = send_notification(api_client, monkeypatch, payment, provider=provider)
        payment.refresh_from_db()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert payment.status == Payment.Status.PENDING
        assert not Enrollment.objects.exists()

    def test_unknown_provider_payment_is_safe(self, api_client, monkeypatch):
        provider = {
            'id': 'unknown',
            'status': 'succeeded',
            'paid': True,
            'amount': {'value': '1490.00', 'currency': 'RUB'},
            'metadata': {'payment_id': '999', 'order_id': 'unknown'},
            'test': True,
        }
        monkeypatch.setattr(
            'apps.payments.views.YooKassaClient.get_payment',
            lambda self, provider_payment_id: provider,
        )
        response = api_client.post(
            reverse('yookassa-webhook'),
            {'event': 'payment.succeeded', 'object': {'id': 'unknown'}},
            format='json',
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert ProcessedWebhook.objects.count() == 0


@pytest.mark.django_db
class TestPaymentStatusReconciliation:
    def test_owner_status_sync_enrolls_after_verified_provider_success(
        self, student_client, student_user, published_course, monkeypatch,
    ):
        payment = make_yookassa_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )
        provider = verified_provider_payment(payment)
        monkeypatch.setattr(
            'apps.payments.views.YooKassaClient.get_payment',
            lambda self, provider_payment_id: provider,
        )

        response = student_client.get(reverse('payment-detail', kwargs={'pk': payment.pk}))
        repeated_response = student_client.get(
            reverse('payment-detail', kwargs={'pk': payment.pk})
        )

        payment.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert repeated_response.status_code == status.HTTP_200_OK
        assert response.data['status'] == Payment.Status.PAID
        assert payment.status == Payment.Status.PAID
        assert Enrollment.objects.filter(
            student=student_user,
            course=published_course,
        ).count() == 1

        my_courses = student_client.get(reverse('my-courses'))
        assert my_courses.status_code == status.HTTP_200_OK
        assert published_course.id in {
            item['course']['id'] for item in my_courses.data['results']
        }

    def test_pending_provider_status_does_not_create_enrollment(
        self, student_client, student_user, published_course, monkeypatch,
    ):
        payment = make_yookassa_payment(
            student=student_user,
            course=make_paid_course(published_course),
        )
        provider = verified_provider_payment(payment, provider_status='pending')
        monkeypatch.setattr(
            'apps.payments.views.YooKassaClient.get_payment',
            lambda self, provider_payment_id: provider,
        )

        response = student_client.get(reverse('payment-detail', kwargs={'pk': payment.pk}))

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == Payment.Status.PENDING
        assert not Enrollment.objects.exists()


@pytest.mark.django_db
def test_user_cannot_view_foreign_payment(
    api_client, student_user, published_course, django_user_model,
):
    other_student = django_user_model.objects.create_user(
        email='other-student@test.com',
        password='pass12345',
        role='student',
    )
    payment = make_yookassa_payment(
        student=student_user,
        course=make_paid_course(published_course),
    )
    api_client.force_authenticate(other_student)
    response = api_client.get(reverse('payment-detail', kwargs={'pk': payment.pk}))
    assert response.status_code == status.HTTP_404_NOT_FOUND
