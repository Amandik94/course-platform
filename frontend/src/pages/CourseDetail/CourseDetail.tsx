import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Button from '../../components/Button/Button';
import Loader from '../../components/Loader/Loader';
import EmptyState from '../../components/EmptyState/EmptyState';
import { courseService } from '../../services/courseService';
import { useEnroll } from '../../features/courses/useEnroll';
import { useAuthStore } from '../../store/authStore';
import type { CourseDetail as CourseDetailType, Section } from '../../types/course';
import styles from './CourseDetail.module.css';

const LEVEL_LABELS: Record<string, string> = {
    beginner: 'Начинающий', junior: 'Junior', middle: 'Middle', advanced: 'Advanced',
};

const CourseDetail = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { isAuthenticated, user } = useAuthStore();
    const { enroll, isEnrolling, error: enrollError } = useEnroll();

    const [course, setCourse] = useState<CourseDetailType | null>(null);
    const [sections, setSections] = useState<Section[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [loadError, setLoadError] = useState<string | null>(null);

    useEffect(() => {
        if (!id) return;
        setIsLoading(true);
        setLoadError(null);

        Promise.all([courseService.getCourseById(id), courseService.getCourseSections(id)])
            .then(([courseData, sectionsData]) => {
                setCourse(courseData);
                setSections(sectionsData);
            })
            .catch(() => setLoadError('Не удалось загрузить курс. Возможно, он не существует.'))
            .finally(() => setIsLoading(false));
    }, [id]);

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
        });
    };

    if (isLoading) return <Loader text="Загрузка курса..." />;
    if (loadError || !course) return <EmptyState title="Курс не найден" description={loadError ?? undefined} />;

    return (
        <div className={`${styles.page} container`}>
            <div className={styles.header}>
                {course.cover ? (
                    <img src={course.cover} alt={course.title} className={styles.cover} />
                ) : null}

                <div className={styles.info}>
                    <div className={styles.badges}>
                        <span className={styles.badge}>{LEVEL_LABELS[course.level]}</span>
                        <span className={styles.badge}>{course.category.name}</span>
                        <span className={styles.badge}>{course.duration} ч</span>
                        <span className={styles.badge}>{course.lessons_count} уроков</span>
                    </div>

                    <h1>{course.title}</h1>
                    <p className={styles.teacher}>Преподаватель: {course.teacher.full_name}</p>
                    <p>{course.short_description}</p>

                    <div className={styles.actionRow}>
                        {user?.role === 'student' && !course.is_enrolled && (
                            <Button onClick={handleEnroll} isLoading={isEnrolling}>
                                Записаться на курс
                            </Button>
                        )}
                        {course.is_enrolled && (
                            <Button onClick={() => navigate(`/my-courses`)}>
                                Продолжить обучение
                            </Button>
                        )}
                        {enrollError && <span className={styles.errorText}>{enrollError}</span>}
                    </div>
                </div>
            </div>

            <h2>Описание</h2>
            <p>{course.description}</p>

            <h2 style={{ marginTop: 'var(--spacing-lg)' }}>Программа курса</h2>
            <div className={styles.sections}>
                {sections.map((section) => (
                    <div key={section.id} className={styles.section}>
                        <div className={styles.sectionTitle}>{section.title}</div>
                        {section.description && <p>{section.description}</p>}
                    </div>
                ))}
                {sections.length === 0 && <p>Программа курса пока не наполнена.</p>}
            </div>
        </div>
    );
};

export default CourseDetail;