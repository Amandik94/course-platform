import StatCard from '../../components/StatCard/StatCard';
import type { TeacherDashboard } from '../../types/dashboard';
import styles from './Dashboard.module.css';

const TeacherDashboardView = ({ data }: { data: TeacherDashboard }) => (
    <>
        <div className={styles.statsGrid}>
            <StatCard value={data.courses_count} label="Мои курсы" />
            <StatCard value={data.students_count} label="Студенты" />
            <StatCard value={data.pending_submissions_count} label="Решения на проверке" />
        </div>

        <div className={styles.section}>
            <h2>Мои курсы</h2>
            {data.courses.map((course) => (
                <div key={course.id} className={styles.tableRow}>
                    <span>{course.title}</span>
                    <span>{course.students_count} студентов · {course.status}</span>
                </div>
            ))}
        </div>
    </>
);

export default TeacherDashboardView;