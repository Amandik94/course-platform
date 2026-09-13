import { Link } from 'react-router-dom';
import Button from '../../components/Button/Button';
import StatCard from '../../components/StatCard/StatCard';
import type { TeacherDashboard } from '../../types/dashboard';
import { COURSE_STATUS_LABELS, pluralizeRu } from '../../utils/labels';
import styles from './Dashboard.module.css';

const TeacherDashboardView = ({ data }: { data: TeacherDashboard }) => (
    <>
        <div className={styles.statsGrid}>
            <StatCard value={data.courses_count} label="Мои курсы" />
            <StatCard value={data.students_count} label="Студенты" />
            <StatCard value={data.pending_submissions_count} label="Решения на проверке" />
        </div>

        <div className={styles.section}>
            <div className={styles.sectionHeader}>
                <h2>Мои курсы</h2>
                <Link to="/teacher/courses">
                    <Button type="button" variant="secondary">Управлять курсами</Button>
                </Link>
            </div>
            {data.courses.map((course) => (
                <div key={course.id} className={styles.tableRow}>
                    <span>{course.title}</span>
                    <span>
                        {course.students_count} {pluralizeRu(course.students_count, ['студент', 'студента', 'студентов'])} - {COURSE_STATUS_LABELS[course.status]}
                    </span>
                </div>
            ))}
        </div>
    </>
);

export default TeacherDashboardView;
