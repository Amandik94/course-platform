import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from decimal import Decimal, InvalidOperation
from typing import Any

from django.conf import settings


class YooKassaError(Exception):
    def __init__(self, message: str, *, retryable: bool = False):
        super().__init__(message)
        self.retryable = retryable


class YooKassaClient:
    def __init__(self):
        self.shop_id = settings.YOOKASSA_SHOP_ID
        self.secret_key = settings.YOOKASSA_SECRET_KEY
        self.api_url = settings.YOOKASSA_API_URL.rstrip('/')
        self.timeout = settings.YOOKASSA_TIMEOUT_SECONDS

    def _ensure_configured(self) -> None:
        if not self.shop_id or not self.secret_key:
            raise YooKassaError(
                'Не настроены тестовые реквизиты YooKassa. '
                'Укажите YOOKASSA_SHOP_ID и YOOKASSA_SECRET_KEY.'
            )
        parsed_url = urllib.parse.urlparse(self.api_url)
        if parsed_url.scheme != 'https' or parsed_url.hostname != 'api.yookassa.ru':
            raise YooKassaError(
                'YOOKASSA_API_URL должен указывать на официальный HTTPS API YooKassa.'
            )

    def create_payment(self, *, payment, return_url: str) -> dict[str, Any]:
        if not payment.idempotency_key:
            raise YooKassaError('Для платежа отсутствует ключ идемпотентности.')
        if payment.currency != 'RUB':
            raise YooKassaError('YooKassa-платёж должен быть создан в RUB.')

        payload = {
            'amount': {
                'value': self._format_amount(payment.amount),
                'currency': 'RUB',
            },
            'capture': True,
            'confirmation': {
                'type': 'redirect',
                'return_url': return_url,
            },
            'description': f'Оплата курса «{payment.course.title}»'[:128],
            'metadata': {
                'order_id': payment.order_id,
                'payment_id': str(payment.id),
                'course_id': str(payment.course_id),
            },
        }
        data = self._request(
            'POST',
            '/payments',
            payload=payload,
            idempotency_key=payment.idempotency_key,
        )
        return self._validate_created_payment(data, payment=payment)

    def get_payment(self, provider_payment_id: str) -> dict[str, Any]:
        if not provider_payment_id:
            raise YooKassaError('Не указан идентификатор платежа YooKassa.')
        safe_id = urllib.parse.quote(provider_payment_id, safe='')
        data = self._request('GET', f'/payments/{safe_id}')
        if str(data.get('id') or '') != provider_payment_id:
            raise YooKassaError('YooKassa вернула другой идентификатор платежа.')
        if data.get('test') is not True:
            raise YooKassaError('Получен не тестовый объект платежа YooKassa.')
        return data

    def _request(
        self,
        method: str,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        self._ensure_configured()
        credentials = base64.b64encode(
            f'{self.shop_id}:{self.secret_key}'.encode('utf-8')
        ).decode('ascii')
        headers = {
            'Authorization': f'Basic {credentials}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        if idempotency_key:
            headers['Idempotence-Key'] = idempotency_key
        request = urllib.request.Request(
            f'{self.api_url}{path}',
            data=(
                json.dumps(payload, ensure_ascii=False).encode('utf-8')
                if payload is not None
                else None
            ),
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                response_body = response.read()
        except urllib.error.HTTPError as exc:
            exc.read()
            if exc.code >= 500:
                raise YooKassaError(
                    'YooKassa временно недоступна. Повторите попытку позже.',
                    retryable=True,
                ) from exc
            raise YooKassaError('YooKassa отклонила запрос на оплату.') from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise YooKassaError(
                'Не удалось связаться с YooKassa. Повторите попытку позже.',
                retryable=True,
            ) from exc

        try:
            data = json.loads(response_body.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise YooKassaError(
                'YooKassa вернула некорректный ответ.', retryable=True
            ) from exc
        if not isinstance(data, dict):
            raise YooKassaError(
                'YooKassa вернула некорректный формат ответа.', retryable=True
            )
        return data

    @staticmethod
    def _format_amount(amount: Decimal) -> str:
        value = Decimal(amount)
        if value <= 0:
            raise YooKassaError('Сумма платежа должна быть больше нуля.')
        return format(value.quantize(Decimal('0.01')), 'f')

    @classmethod
    def _validate_created_payment(cls, data: dict[str, Any], *, payment) -> dict[str, Any]:
        provider_payment_id = str(data.get('id') or '')
        confirmation = data.get('confirmation')
        redirect_url = confirmation.get('confirmation_url') if isinstance(confirmation, dict) else ''

        if not provider_payment_id or not isinstance(redirect_url, str):
            raise YooKassaError(
                'YooKassa не вернула идентификатор платежа или ссылку подтверждения.'
            )
        cls._validate_confirmation_url(redirect_url)
        if data.get('status') != 'pending':
            raise YooKassaError('YooKassa вернула неожиданный статус нового платежа.')
        if data.get('test') is not True:
            raise YooKassaError('Создание платежей разрешено только в тестовом магазине YooKassa.')
        cls._validate_amount(data.get('amount'), expected=payment.amount)

        return {
            'provider_payment_id': provider_payment_id,
            'redirect_url': redirect_url,
            'status': 'pending',
        }

    @staticmethod
    def _validate_confirmation_url(url: str) -> None:
        parsed = urllib.parse.urlparse(url)
        hostname = (parsed.hostname or '').lower()
        allowed = (
            hostname == 'yookassa.ru'
            or hostname.endswith('.yookassa.ru')
            or hostname == 'yoomoney.ru'
            or hostname.endswith('.yoomoney.ru')
        )
        if parsed.scheme != 'https' or not allowed or hostname == 'api.yookassa.ru':
            raise YooKassaError('YooKassa вернула недопустимую ссылку подтверждения.')

    @staticmethod
    def _validate_amount(amount: Any, *, expected: Decimal) -> None:
        if not isinstance(amount, dict) or amount.get('currency') != 'RUB':
            raise YooKassaError('Валюта платежа YooKassa не совпадает с RUB.')
        try:
            provider_amount = Decimal(str(amount.get('value'))).quantize(Decimal('0.01'))
        except (InvalidOperation, TypeError):
            raise YooKassaError('YooKassa вернула некорректную сумму платежа.')
        if provider_amount != Decimal(expected).quantize(Decimal('0.01')):
            raise YooKassaError('Сумма платежа YooKassa не совпадает с ценой курса.')
