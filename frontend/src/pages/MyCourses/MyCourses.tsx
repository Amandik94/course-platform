import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Button from '../../components/Button/Button';
import ProgressBar from '../../components/ProgressBar/ProgressBar';
import Loader from '../../components/Loader/Loader';
import EmptyState from '../../components/EmptyState/EmptyState';
import { enrollmentService } from '../../services/enrollmentService';
import type { Enrollment } from '../../types/enrollment';
import styles from './MyCourses.module.css';

const MyCourses = () => {
    const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        enrollmentService
            .getMyCourses()
            .then((data) => setEnrollments(data.results))
            .catch(() => setError('Не удалось загрузить ваши курсы.'))
            .finally(() => setIsLoading(false));
    }, []);

    if (isLoading) return <Loader text="Загрузка курсов..." />;
    if (error) return <EmptyState title="Ошибка" description={error} />;
    if (enrollments.length === 0) {
        return (
            <EmptyState
                title="У вас пока нет курсов"
                description="Загляните в каталог, чтобы найти что-нибудь интересное"
            />
        );
    }

    return (
        <div className={`${styles.page} container`}>
            <h1>Мои курсы</h1>
            <div className={styles.grid} style={{ marginTop: 'var(--spacing-lg)' }}>
                {enrollments.map((enrollment) => (
                    <div key={enrollment.id} className={styles.card}>
                        {enrollment.course.cover && (
                            <img src={enrollment.course.cover} alt={enrollment.course.title} className={styles.cover} />
                        )}
                        <div className={styles.body}>
                            {enrollment.completed_at && (
                                <span className={styles.completedBadge}>Завершён</span>
                            )}
                            <h3>{enrollment.course.title}</h3>
                            <ProgressBar value={enrollment.progress} />

                            {enrollment.next_lesson_id ? (
                                <Link to={`/learn/${enrollment.course.id}/${enrollment.next_lesson_id}`}>
                                    <Button fullWidth variant={enrollment.completed_at ? 'secondary' : 'primary'}>
                                        {enrollment.completed_at ? 'Повторить' : 'Продолжить'}
                                    </Button>
                                </Link>
                            ) : (
                                <Button fullWidth disabled>Курс без уроков</Button>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default MyCourses;