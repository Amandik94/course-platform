import { Link, useSearchParams } from 'react-router-dom';
import Button from '../../components/Button/Button';
import styles from './PaymentStatusPages.module.css';

const PaymentFailure = () => {
    const [searchParams] = useSearchParams();
    const courseId = searchParams.get('course_id') ?? sessionStorage.getItem('lastPaymentCourseId');

    return (
        <div className={`${styles.page} container`}>
            <section className={styles.panel}>
                <h1>Оплата не завершена</h1>
                <p>Средства не были подтверждены. Вы можете попробовать снова или вернуться к курсу.</p>
                <div className={`${styles.status} ${styles.error}`}>Не оплачено</div>
                <div className={styles.actions}>
                    {courseId && (
                        <Link to={`/courses/${courseId}`}>
                            <Button>Попробовать снова</Button>
                        </Link>
                    )}
                    <Link to="/courses">
                        <Button variant="secondary">К каталогу курсов</Button>
                    </Link>
                </div>
            </section>
        </div>
    );
};

export default PaymentFailure;

