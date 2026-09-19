import type { CourseListItem } from './course';

export type PaymentStatus =
    | 'pending'
    | 'paid'
    | 'failed'
    | 'cancelled'
    | 'expired'
    | 'refunded';
export type PaymentProvider = 'paybot' | 'freedompay';

export interface PaymentCourse {
    id: number;
    title: string;
    slug: string;
    price: string;
}

export interface Payment {
    id: number;
    course: PaymentCourse;
    amount: string;
    currency: 'KZT';
    status: PaymentStatus;
    provider: PaymentProvider;
    provider_payment_id: string;
    order_id: string;
    created_at: string;
    updated_at: string;
    paid_at: string | null;
    expires_at: string | null;
}

export interface CreatePaymentResponse extends Payment {
    deep_link: string;
}

export interface PaymentPageState {
    paymentId?: number;
    course?: CourseListItem | PaymentCourse;
}
