import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import Button from '../../components/Button/Button';
import EmptyState from '../../components/EmptyState/EmptyState';
import Loader from '../../components/Loader/Loader';
import { courseService } from '../../services/courseService';
import { useAuthStore } from '../../store/authStore';
import type { CourseListItem } from '../../types/course';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';
import { COURSE_LEVEL_LABELS, COURSE_STATUS_LABELS, pluralizeRu } from '../../utils/labels';
import styles from './TeacherCourses.module.css';

const TeacherCourses = () => {
    const user = useAuthStore((state) => state.user);
    const [courses, setCourses] = useState<CourseListItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const teacherCourses = useMemo(
        () => courses.filter((course) => course.teacher_id === user?.id),
        [courses, user?.id],
    );

    useEffect(() => {
        const loadInitialCourses = async () => {
            try {
                const data = await courseService.getCourses({});
                setCourses(data.results);
            } catch (err) {
                setError(getApiErrorMessage(err));
            } finally {
                setIsLoading(false);
            }
        };

        void loadInitialCourses();
    }, []);

    const handleDelete = async (course: CourseListItem) => {
        const confirmed = window.confirm(`Удалить курс «${course.title}»?`);
        if (!confirmed) return;

        setError('');
        setSuccess('');
        try {
            await courseService.deleteCourse(course.id);
            setCourses((items) => items.filter((item) => item.id !== course.id));
            setSuccess('Курс удалён.');
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    };

    if (isLoading) return <Loader />;

    return (
        <div className={styles.page}>
            <div className={styles.header}>
                <div>
                    <h1>Мои курсы</h1>
                    <p>Управление курсами, разделами, уроками, заданиями и тестами.</p>
                </div>
                <Link to="/teacher/courses/new">
                    <Button type="button">Новый курс</Button>
                </Link>
            </div>

            {error && <EmptyState title="Не удалось загрузить курсы" description={error} variant="error" />}
            {success && <p className={styles.success}>{success}</p>}

            {teacherCourses.length === 0 && !error ? (
                <EmptyState title="Курсов пока нет" description="Создайте первый курс, чтобы начать наполнять обучение." />
            ) : (
                <div className={styles.grid}>
                    {teacherCourses.map((course) => (
                        <article key={course.id} className={styles.card}>
                            <div>
                                <p className={styles.meta}>{course.category.name} - {COURSE_LEVEL_LABELS[course.level]}</p>
                                <h2>{course.title}</h2>
                                <p>{course.short_description}</p>
                            </div>
                            <div className={styles.footer}>
                                <span className={styles.status}>{COURSE_STATUS_LABELS[course.status]}</span>
                                <span>{course.lessons_count} {pluralizeRu(course.lessons_count, ['урок', 'урока', 'уроков'])}</span>
                            </div>
                            <div className={styles.actions}>
                                <Link to={`/teacher/courses/${course.id}/manage`}>
                                    <Button type="button" variant="secondary">Управлять</Button>
                                </Link>
                                <Link to={`/teacher/courses/${course.id}/edit`}>
                                    <Button type="button" variant="secondary">Редактировать</Button>
                                </Link>
                                <Button type="button" variant="danger" onClick={() => void handleDelete(course)}>
                                    Удалить
                                </Button>
                            </div>
                        </article>
                    ))}
                </div>
            )}
        </div>
    );
};

export default TeacherCourses;
