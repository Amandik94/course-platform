import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Button from '../../components/Button/Button';
import EmptyState from '../../components/EmptyState/EmptyState';
import Loader from '../../components/Loader/Loader';
import { courseService } from '../../services/courseService';
import type { CourseListItem, CourseStatus } from '../../types/course';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';
import { COURSE_STATUS_LABELS } from '../../utils/labels';
import styles from './AdminCourses.module.css';

const AdminCourses = () => {
    const [courses, setCourses] = useState<CourseListItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

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

    const updateStatus = async (course: CourseListItem, status: CourseStatus) => {
        setIsSaving(true);
        setError('');
        setSuccess('');
        try {
            await courseService.updateCourse(course.id, { status });
            setCourses((items) => items.map((item) => (
                item.id === course.id ? { ...item, status } : item
            )));
            setSuccess('Статус курса обновлён.');
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    const deleteCourse = async (course: CourseListItem) => {
        if (!window.confirm(`Удалить курс «${course.title}»?`)) return;
        setIsSaving(true);
        setError('');
        setSuccess('');
        try {
            await courseService.deleteCourse(course.id);
            setCourses((items) => items.filter((item) => item.id !== course.id));
            setSuccess('Курс удалён.');
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) return <Loader />;

    return (
        <div className={`${styles.page} container`}>
            <div className={styles.header}>
                <div>
                    <h1>Курсы</h1>
                    <p>Модерация видимости курсов и удаление, если backend разрешает это действие.</p>
                </div>
                <Link to="/dashboard">
                    <Button type="button" variant="secondary">Панель управления</Button>
                </Link>
            </div>

            {error && <EmptyState title="Не удалось выполнить действие" description={error} variant="error" />}
            {success && <p className={styles.success}>{success}</p>}

            {courses.length === 0 && !error ? (
                <EmptyState title="Курсов пока нет" />
            ) : (
                <div className={styles.table} role="table" aria-label="Курсы">
                    <div className={styles.tableHead} role="row">
                        <span role="columnheader">Курс</span>
                        <span role="columnheader">Преподаватель</span>
                        <span role="columnheader">Статус</span>
                        <span role="columnheader">Действия</span>
                    </div>
                    {courses.map((course) => (
                        <div key={course.id} className={styles.tableRow} role="row">
                            <span role="cell" data-label="Курс">{course.title}</span>
                            <span role="cell" data-label="Преподаватель">{course.teacher_name}</span>
                            <label className={styles.statusSelect} role="cell" data-label="Статус">
                                <select
                                    value={course.status}
                                    disabled={isSaving}
                                    onChange={(event) => void updateStatus(course, event.target.value as CourseStatus)}
                                >
                                    <option value="draft">{COURSE_STATUS_LABELS.draft}</option>
                                    <option value="published">{COURSE_STATUS_LABELS.published}</option>
                                    <option value="archived">{COURSE_STATUS_LABELS.archived}</option>
                                </select>
                            </label>
                            <div className={styles.actions} data-label="Действия" role="cell">
                                <Link to={`/courses/${course.id}`}>
                                    <Button type="button" variant="secondary">Открыть</Button>
                                </Link>
                                <Link to={`/teacher/courses/${course.id}/manage`}>
                                    <Button type="button" variant="secondary">Управлять</Button>
                                </Link>
                                <Button type="button" variant="danger" disabled={isSaving} onClick={() => void deleteCourse(course)}>
                                    Удалить
                                </Button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default AdminCourses;
