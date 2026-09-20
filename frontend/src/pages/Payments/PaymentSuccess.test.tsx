import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { paymentService } from '../../services/paymentService';
import PaymentSuccess from './PaymentSuccess';

vi.mock('../../services/paymentService', () => ({
    paymentService: {
        getPayment: vi.fn(),
    },
}));

describe('PaymentSuccess', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        sessionStorage.clear();
    });

    it('shows confirmed YooKassa payment in RUB', async () => {
        vi.mocked(paymentService.getPayment).mockResolvedValue({
            id: 1,
            course: { id: 2, title: 'React + TypeScript', slug: 'react-typescript', price: '2990.00' },
            amount: '2990.00',
            currency: 'RUB',
            status: 'paid',
            provider: 'yookassa',
            provider_payment_id: 'yk-test-123',
            order_id: 'LMS-test',
            created_at: '2026-09-20T12:00:00Z',
            updated_at: '2026-09-20T12:01:00Z',
            paid_at: '2026-09-20T12:01:00Z',
            expires_at: null,
        });

        render(
            <MemoryRouter initialEntries={['/payment/success?payment_id=1&course_id=2']}>
                <PaymentSuccess />
            </MemoryRouter>,
        );

        expect(await screen.findByRole('heading', { name: 'Оплата прошла успешно' })).toBeInTheDocument();
        expect(screen.getByText(/2\s?990/)).toBeInTheDocument();
        expect(screen.getByText(/₽|руб/)).toBeInTheDocument();
        expect(paymentService.getPayment).toHaveBeenCalledWith('1');
    });
});
