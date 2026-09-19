import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Button from '../../components/Button/Button';
import Loader from '../../components/Loader/Loader';
import EmptyState from '../../components/EmptyState/EmptyState';
import { courseService } from '../../services/courseService';
import { paymentService } from '../../services/paymentService';
import { useEnroll } from '../../features/courses/useEnroll';
import { useAuthStore } from '../../store/authStore';
import type { CourseDetail as CourseDetailType, Section } from '../../types/course';
import styles from './CourseDetail.module.css';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';
import { useToast } from '../../components/Toast/useToast';
import CourseReviews from '../../features/reviews/CourseReviews';
import { COURSE_LEVEL_LABELS, pluralizeRu } from '../../utils/labels';
import { formatKzt, isPaidAmount } from '../../utils/formatMoney';

const CourseDetail = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { isAuthenticated, user } = useAuthStore();
    const { enroll, isEnrolling, error: enrollError } = useEnroll();
    const { showToast } = useToast();

    const [course, setCourse] = useState<CourseDetailType | null>(null);
    const [sections, setSections] = useState<Section[]>([]);
    const [loadedId, setLoadedId] = useState<string | undefined>();
    const [loadError, setLoadError] = useState<string | null>(null);
    const [paymentError, setPaymentError] = useState<string | null>(null);
    const [isCreatingPayment, setIsCreatingPayment] = useState(false);

    useEffect(() => {
    if (!id) return;

    let cancelled = false;

    const loadCourse = async () => {
        try {
            const [courseData, sectionsData] = await Promise.all([
                courseService.getCourseById(id),
                courseService.getCourseSections(id),
            ]);

            if (cancelled) return;

            setCourse(courseData);
            setSections(sectionsData);
            setLoadError(null);
            setLoadedId(id);
        } catch (err) {
            if (cancelled) return;

            setLoadError(getApiErrorMessage(err));
            setLoadedId(id);
        }
    };

    loadCourse();

    return () => {
        cancelled = true;
    };
}, [id]);

    const isLoading = Boolean(id && loadedId !== id);

        useEffect(() => {
        if (enrollError) {
            showToast(enrollError, 'error');
        }
    }, [enrollError, showToast]);

    const handleEnroll = () => {
        if (!isAuthenticated) {
            navigate('/login');
            return;
        }
        if (!course) return;
        enroll(course.id, () => {
            // оптимистично обновляем локальное состояние курса,
            // не делая повторный запрос ради одного изменившегося поля
            setCourse((prev) => (prev ? { ...prev, is_enrolled: true } : prev));
            showToast('Вы успешно записались на курс!', 'success');
        });
    };

    const handleBuyCourse = async () => {
        if (!isAuthenticated) {
            navigate('/login');
            return;
        }
        if (!course) return;

        setIsCreatingPayment(true);
        setPaymentError(null);
        try {
            const payment = await paymentService.createPayment(course.id);
            sessionStorage.setItem('lastPaymentId', String(payment.id));
            sessionStorage.setItem('lastPaymentCourseId', String(course.id));
            window.location.assign(payment.deep_link);
        } catch (err) {
            const message = getApiErrorMessage(err) || 'Не удалось создать платеж. Попробуйте еще раз.';
            setPaymentError(message);
            showToast(message, 'error');
        } finally {
            setIsCreatingPayment(false);
        }
    };

    if (isLoading) return <Loader text="Загрузка курса..." />;
    if (loadError || !course) return <EmptyState variant="error" title="Курс не найден" description={loadError ?? undefined} />;

    return (
        <div className={`${styles.page} container`}>
            <div className={styles.header}>
                {course.cover ? (
                    <img src={course.cover} alt={course.title} className={styles.cover} />
                ) : null}

                <div className={styles.info}>
                    <div className={styles.badges}>
                        <span className={styles.badge}>{COURSE_LEVEL_LABELS[course.level]}</span>
                        <span className={styles.badge}>{course.category.name}</span>
                        <span className={styles.badge}>{course.duration} ч</span>
                        <span className={styles.badge}>
                            {course.lessons_count} {pluralizeRu(course.lessons_count, ['урок', 'урока', 'уроков'])}
                        </span>
                        <span className={styles.badge}>{formatKzt(course.price)}</span>
                    </div>

                    <h1>{course.title}</h1>
                    <p className={styles.teacher}>Преподаватель: {course.teacher.full_name}</p>
                    <p>{course.short_description}</p>
                    <p className={styles.priceLine}>
                        Цена: <strong>{formatKzt(course.price)}</strong>
                    </p>

                    <div className={styles.actionRow}>
                        {!isAuthenticated && !course.is_enrolled && (
                            <Button onClick={() => navigate('/login')} variant="secondary">
                                Войти, чтобы записаться
                            </Button>
                        )}
                        {isAuthenticated && user?.role === 'student' && !course.is_enrolled && !isPaidAmount(course.price) && (
                            <Button onClick={handleEnroll} isLoading={isEnrolling}>
                                Записаться бесплатно
                            </Button>
                        )}
                        {isAuthenticated && user?.role === 'student' && !course.is_enrolled && isPaidAmount(course.price) && (
                            <Button onClick={() => void handleBuyCourse()} isLoading={isCreatingPayment}>
                                Купить курс — {formatKzt(course.price)}
                            </Button>
                        )}
                        {course.is_enrolled && (
                            <Button onClick={() => navigate(`/my-courses`)}>
                                Продолжить обучение
                            </Button>
                        )}
                        {(enrollError || paymentError) && (
                            <span className={styles.errorText}>{enrollError || paymentError}</span>
                        )}
                    </div>
                </div>
            </div>

            <h2>Описание</h2>
            <p>{course.description}</p>

            <h2 className={styles.sectionHeading}>Программа курса</h2>
            <div className={styles.sections}>
                {sections.map((section) => (
                    <div key={section.id} className={styles.section}>
                        <div className={styles.sectionTitle}>{section.title}</div>
                        {section.description && <p>{section.description}</p>}
                    </div>
                ))}
                {sections.length === 0 && <p>Программа курса пока не наполнена.</p>}
            </div>

            <CourseReviews course={course} onCourseUpdated={setCourse} />
        </div>
    );
};

export default CourseDetail;
