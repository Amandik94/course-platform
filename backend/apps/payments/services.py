import hashlib
import hmac
import json
import time
import urllib.error
import urllib.request
from decimal import Decimal
from typing import Any

from django.conf import settings


class PayBotError(Exception):
    def __init__(self, message: str, *, retryable: bool = False):
        super().__init__(message)
        self.retryable = retryable


def verify_paybot_webhook_signature(
    *,
    timestamp: str,
    raw_body: bytes,
    signature: str,
    secret: str,
) -> bool:
    if not timestamp or not signature.startswith('sha256=') or not secret:
        return False
    signed_payload = timestamp.encode('utf-8') + b'.' + raw_body
    digest = hmac.new(secret.encode('utf-8'), signed_payload, hashlib.sha256).hexdigest()
    expected = f'sha256={digest}'
    return hmac.compare_digest(expected, signature)


def is_fresh_webhook_timestamp(timestamp: str, *, tolerance_seconds: int = 300) -> bool:
    try:
        value = int(timestamp)
    except (TypeError, ValueError):
        return False
    return abs(int(time.time()) - value) <= tolerance_seconds


class PayBotClient:
    def __init__(self):
        self.api_key = settings.PAYBOT_API_KEY
        self.api_url = settings.PAYBOT_API_URL.rstrip('/')
        self.timeout = settings.PAYBOT_TIMEOUT_SECONDS

    def _ensure_configured(self) -> None:
        if not self.api_key:
            raise PayBotError('Не настроена переменная окружения PAYBOT_API_KEY.')
        if not self.api_key.startswith('kp_test_'):
            raise PayBotError(
                'Для этой LMS разрешен только Sandbox-ключ PayBot с префиксом kp_test_.'
            )
        if not self.api_url.startswith('https://'):
            raise PayBotError('PAYBOT_API_URL должен использовать HTTPS.')

    def create_qr(self, *, payment) -> dict[str, Any]:
        self._ensure_configured()
        amount = Decimal(payment.amount)
        if amount != amount.to_integral_value() or amount <= 0:
            raise PayBotError('PayBot принимает сумму курса в целых тенге.')
        if not payment.idempotency_key:
            raise PayBotError('Для платежа отсутствует idempotency key.')

        payload = {
            'amount': int(amount),
            'description': f'Оплата курса «{payment.course.title}»',
            'metadata': {
                'order_id': payment.order_id,
                'payment_id': payment.id,
                'course_id': payment.course_id,
            },
        }
        request = urllib.request.Request(
            f'{self.api_url}/v2/qr',
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
            headers={
                'X-API-Key': self.api_key,
                'Idempotency-Key': payment.idempotency_key,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            method='POST',
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                response_body = response.read()
        except urllib.error.HTTPError as exc:
            message = self._extract_error_message(exc.read())
            if 500 <= exc.code < 600:
                raise PayBotError(
                    'PayBot временно недоступен. Повторите попытку позже.',
                    retryable=True,
                ) from exc
            raise PayBotError(message or 'PayBot отклонил создание платежа.') from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise PayBotError(
                'Не удалось связаться с PayBot. Повторите попытку позже.',
                retryable=True,
            ) from exc

        try:
            data = json.loads(response_body.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PayBotError(
                'PayBot вернул некорректный ответ.',
                retryable=True,
            ) from exc

        return self._validate_create_response(data, expected_amount=int(amount))

    @staticmethod
    def _extract_error_message(response_body: bytes) -> str:
        try:
            data = json.loads(response_body.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return ''
        error = data.get('error')
        if isinstance(error, dict):
            return str(error.get('message') or error.get('detail') or '')
        return str(data.get('message') or data.get('detail') or '')

    @staticmethod
    def _validate_create_response(data: Any, *, expected_amount: int) -> dict[str, Any]:
        if not isinstance(data, dict):
            raise PayBotError('PayBot вернул некорректный формат ответа.', retryable=True)

        operation_id = data.get('operation_id')
        deep_link = data.get('deep_link')
        if not deep_link:
            qr_token = data.get('qr_token')
            if isinstance(qr_token, str) and qr_token.startswith(('https://', 'kaspi://')):
                deep_link = qr_token
        expires_at = data.get('expires_at') or data.get('expire_date')
        provider_status = data.get('status')

        if not operation_id or not isinstance(deep_link, str) or not deep_link:
            raise PayBotError('PayBot не вернул идентификатор операции или ссылку оплаты.')
        if not expires_at or not provider_status:
            raise PayBotError('PayBot не вернул срок действия или статус QR.')
        if data.get('amount') is not None:
            try:
                response_amount = int(data['amount'])
            except (TypeError, ValueError) as exc:
                raise PayBotError('PayBot вернул некорректную сумму.') from exc
            if response_amount != expected_amount:
                raise PayBotError('PayBot вернул сумму, не совпадающую с ценой курса.')

        return {
            'operation_id': str(operation_id),
            'deep_link': deep_link,
            'expires_at': str(expires_at),
            'status': str(provider_status),
        }
