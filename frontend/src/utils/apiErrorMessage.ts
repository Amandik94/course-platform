import { isAxiosError } from 'axios';
import type { ApiError } from '../types/common';

const STATUS_MESSAGES: Record<number, string> = {
    401: 'Сессия истекла. Войдите снова.',
    403: 'У вас нет доступа.',
    404: 'Страница не найдена.',
    500: 'Ошибка сервера.',
};

/**
 * Единая точка превращения любой ошибки API в читаемое сообщение.
 * Порядок приоритета:
 * 1. detail из ответа сервера (самое специфичное и точное)
 * 2. первая ошибка валидации поля
 * 3. стандартная формулировка по HTTP-статусу (ТЗ п.38)
 * 4. общий fallback
 */
export function getApiErrorMessage(err: unknown): string {
    if (isAxiosError<ApiError>(err)) {
        const data = err.response?.data;
        const status = err.response?.status;

        if (data?.detail && typeof data.detail === 'string') {
            return data.detail;
        }

        if (data) {
            const firstFieldError = Object.values(data).find(
                (value) => Array.isArray(value) && value.length > 0,
            );
            if (firstFieldError) return String(firstFieldError[0]);
        }

        if (status && STATUS_MESSAGES[status]) {
            return STATUS_MESSAGES[status];
        }

        if (!err.response) {
            return 'Не удалось подключиться к серверу. Проверьте интернет-соединение.';
        }
    }

    return 'Произошла непредвиденная ошибка. Попробуйте позже.';
}