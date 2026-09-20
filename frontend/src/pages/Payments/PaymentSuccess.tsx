import { useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import Button from '../../components/Button/Button';
import EmptyState from '../../components/EmptyState/EmptyState';
import Loader from '../../components/Loader/Loader';
import { paymentService } from '../../services/paymentService';
import type { Payment } from '../../types/payment';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';
import { formatMoney } from '../../utils/formatMoney';
import styles from './PaymentStatusPages.module.css';

const MAX_ATTEMPTS = 8;
const POLL_INTERVAL_MS = 3000;

const PaymentSuccess = () => {
    const [searchParams] = useSearchParams();
    const paymentId = useMemo(
        () => searchParams.get('payment_id') ?? sessionStorage.getItem('lastPaymentId'),
        [searchParams],
    );
    const courseId = searchParams.get('course_id') ?? sessionStorage.getItem('lastPaymentCourseId');
    const [payment, setPayment] = useState<Payment | null>(null);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!paymentId) return undefined;

        let cancelled = false;
        let timer: number | undefined;
        let attemptCount = 0;

        const loadPayment = async () => {
            try {
                const data = await paymentService.getPayment(paymentId);
                if (cancelled) return;
                setPayment(data);
                setError('');
                attemptCount += 1;

                if (data.status === 'pending' && attemptCount < MAX_ATTEMPTS) {
                    timer = window.setTimeout(loadPayment, POLL_INTERVAL_MS);
                }
            } catch (err) {
                if (!cancelled) {
                    setError(getApiErrorMessage(err));
                }
            }
        };

        void loadPayment();

        return () => {
            cancelled = true;
            if (timer) window.clearTimeout(timer);
        };
    }, [paymentId]);

    if (!paymentId) {
        return (
            <div className={`${styles.page} container`}>
                <EmptyState
                    variant="error"
                    title="Не удалось определить платеж"
                    description="Откройте историю платежей или вернитесь к курсу."
                />
            </div>
        );
    }

    if (error) {
        return (
            <div className={`${styles.page} container`}>
                <EmptyState variant="error" title="Не удалось проверить оплату" description={error} />
            </div>
        );
    }

    if (!payment) {
        return <Loader text="Проверяем оплату..." />;
    }

    const isPaid = payment.status === 'paid';
    const isFailed = ['failed', 'cancelled', 'expired'].includes(payment.status);
    const isRefunded = payment.status === 'refunded';

    return (
        <div className={`${styles.page} container`}>
            <section className={styles.panel}>
                <h1>
                    {isPaid
                        ? 'Оплата прошла успешно'
                        : isRefunded
                            ? 'Средства возвращены'
                            : isFailed
                                ? 'Оплата не завершена'
                                : 'Проверяем оплату'}
                </h1>
                <p>
                    {isPaid
                        ? 'Курс добавлен в раздел «Мои курсы».'
                        : isRefunded
                            ? 'Платёж возвращён. Доступ к курсу регулируется правилами возврата платформы.'
                            : isFailed
                                ? 'Платёж не был завершён. Вернитесь к курсу, чтобы попробовать снова.'
                                : 'Платёж обрабатывается. Доступ появится после подтверждения от YooKassa.'}
                </p>
                <div className={`${styles.status} ${isPaid ? styles.success : ''} ${isFailed ? styles.error : ''}`}>
                    {isPaid
                        ? 'Оплачено'
                        : isRefunded
                            ? 'Средства возвращены'
                            : isFailed
                                ? 'Оплата не завершена'
                                : 'Платёж обрабатывается'}
                </div>
                <p className={styles.muted}>
                    {payment.course.title} · {formatMoney(payment.amount, payment.currency)}
                </p>
                <div className={styles.actions}>
                    {isPaid && (
                        <Link to="/my-courses">
                            <Button>Перейти к моим курсам</Button>
                        </Link>
                    )}
                    {courseId && (
                        <Link to={`/courses/${courseId}`}>
                            <Button variant="secondary">Вернуться к курсу</Button>
                        </Link>
                    )}
                    <Link to="/payments">
                        <Button variant="secondary">История платежей</Button>
                    </Link>
                </div>
            </section>
        </div>
    );
};

export default PaymentSuccess;
