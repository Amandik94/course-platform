import { api } from './api';
import type { PaginatedResponse } from '../types/common';
import type { CreatePaymentResponse, Payment } from '../types/payment';

export const paymentService = {
    createPayment: (courseId: number | string) =>
        api
            .post<CreatePaymentResponse>('payments/create/', { course_id: courseId })
            .then((res) => res.data),

    getPayment: (paymentId: number | string) =>
        api.get<Payment>(`payments/${paymentId}/`).then((res) => res.data),

    getMyPayments: () =>
        api.get<PaginatedResponse<Payment>>('payments/').then((res) => res.data),
};

