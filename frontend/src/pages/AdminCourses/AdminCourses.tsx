import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Button from '../../components/Button/Button';
import EmptyState from '../../components/EmptyState/EmptyState';
import Loader from '../../components/Loader/Loader';
import { courseService } from '../../services/courseService';
import type { CourseListItem, CourseStatus } from '../../types/course';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';
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
            setSuccess('Course status updated.');
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    const deleteCourse = async (course: CourseListItem) => {
        if (!window.confirm(`Delete course "${course.title}"?`)) return;
        setIsSaving(true);
        setError('');
        setSuccess('');
        try {
            await courseService.deleteCourse(course.id);
            setCourses((items) => items.filter((item) => item.id !== course.id));
            setSuccess('Course deleted.');
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) return <Loader />;

    return (
        <div className={styles.page}>
            <div className={styles.header}>
                <div>
                    <h1>Admin Courses</h1>
                    <p>Moderate course visibility and remove courses when backend allows it.</p>
                </div>
                <Link to="/dashboard">
                    <Button type="button" variant="secondary">Dashboard</Button>
                </Link>
            </div>

            {error && <EmptyState title="Admin action failed" description={error} variant="error" />}
            {success && <p className={styles.success}>{success}</p>}

            {courses.length === 0 && !error ? (
                <EmptyState title="No courses" />
            ) : (
                <div className={styles.table}>
                    <div className={styles.tableHead}>
                        <span>Course</span>
                        <span>Teacher</span>
                        <span>Status</span>
                        <span>Actions</span>
                    </div>
                    {courses.map((course) => (
                        <div key={course.id} className={styles.tableRow}>
                            <span>{course.title}</span>
                            <span>{course.teacher_name}</span>
                            <label className={styles.statusSelect}>
                                <select
                                    value={course.status}
                                    disabled={isSaving}
                                    onChange={(event) => void updateStatus(course, event.target.value as CourseStatus)}
                                >
                                    <option value="draft">Draft</option>
                                    <option value="published">Published</option>
                                    <option value="archived">Archived</option>
                                </select>
                            </label>
                            <div className={styles.actions}>
                                <Link to={`/courses/${course.id}`}>
                                    <Button type="button" variant="secondary">View</Button>
                                </Link>
                                <Link to={`/teacher/courses/${course.id}/manage`}>
                                    <Button type="button" variant="secondary">Manage</Button>
                                </Link>
                                <Button type="button" variant="danger" disabled={isSaving} onClick={() => void deleteCourse(course)}>
                                    Delete
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
