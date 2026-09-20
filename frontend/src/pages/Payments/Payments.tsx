import { useEffect, useState } from 'react';
import EmptyState from '../../components/EmptyState/EmptyState';
import Loader from '../../components/Loader/Loader';
import { paymentService } from '../../services/paymentService';
import type { Payment } from '../../types/payment';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';
import { formatDateTime } from '../../utils/formatDate';
import { formatMoney } from '../../utils/formatMoney';
import styles from './PaymentStatusPages.module.css';

const PAYMENT_STATUS_LABELS: Record<Payment['status'], string> = {
    pending: 'Ожидает оплаты',
    paid: 'Оплачено',
    failed: 'Не оплачено',
    cancelled: 'Отменено',
    expired: 'Срок оплаты истёк',
    refunded: 'Возвращено',
};

const Payments = () => {
    const [payments, setPayments] = useState<Payment[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        let cancelled = false;

        const loadPayments = async () => {
            try {
                const data = await paymentService.getMyPayments();
                if (!cancelled) {
                    setPayments(data.results);
                    setError('');
                }
            } catch (err) {
                if (!cancelled) {
                    setError(getApiErrorMessage(err));
                }
            } finally {
                if (!cancelled) {
                    setIsLoading(false);
                }
            }
        };

        void loadPayments();

        return () => {
            cancelled = true;
        };
    }, []);

    if (isLoading) return <Loader text="Загрузка платежей..." />;

    return (
        <div className={`${styles.page} container`}>
            <h1>История платежей</h1>

            {error && <EmptyState variant="error" title="Не удалось загрузить платежи" description={error} />}

            {!error && payments.length === 0 && (
                <EmptyState title="Платежей пока нет" description="После покупки курса платеж появится здесь." />
            )}

            {!error && payments.length > 0 && (
                <div className={styles.list}>
                    {payments.map((payment) => (
                        <article key={payment.id} className={styles.paymentItem}>
                            <div>
                                <strong>{payment.course.title}</strong>
                                <div className={styles.muted}>{formatDateTime(payment.created_at)}</div>
                            </div>
                            <span>{formatMoney(payment.amount, payment.currency)}</span>
                            <span>{PAYMENT_STATUS_LABELS[payment.status]}</span>
                        </article>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Payments;
