import StatCard from '../../components/StatCard/StatCard';
import type { AdminDashboard } from '../../types/dashboard';
import styles from './Dashboard.module.css';

const AdminDashboardView = ({ data }: { data: AdminDashboard }) => (
    <div className={styles.statsGrid}>
        <StatCard value={data.users_count} label="Всего пользователей" />
        <StatCard value={data.students_count} label="Студенты" />
        <StatCard value={data.teachers_count} label="Преподаватели" />
        <StatCard value={data.courses_count} label="Всего курсов" />
        <StatCard value={data.active_courses_count} label="Опубликованные курсы" />
        <StatCard value={data.completed_enrollments_count} label="Завершённые записи" />
        <StatCard value={`${data.average_progress}%`} label="Средний прогресс по платформе" />
    </div>
);

export default AdminDashboardView;