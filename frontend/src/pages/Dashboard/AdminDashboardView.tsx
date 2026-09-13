import { Link } from 'react-router-dom';
import Button from '../../components/Button/Button';
import StatCard from '../../components/StatCard/StatCard';
import type { AdminDashboard } from '../../types/dashboard';
import styles from './Dashboard.module.css';

const AdminDashboardView = ({ data }: { data: AdminDashboard }) => (
    <>
        <div className={styles.statsGrid}>
            <StatCard value={data.users_count} label="Пользователи" />
            <StatCard value={data.students_count} label="Студенты" />
            <StatCard value={data.teachers_count} label="Преподаватели" />
            <StatCard value={data.courses_count} label="Курсы" />
            <StatCard value={data.active_courses_count} label="Опубликованные курсы" />
            <StatCard value={data.completed_enrollments_count} label="Завершённые обучения" />
            <StatCard value={`${data.average_progress}%`} label="Средний прогресс" />
        </div>
        <div className={styles.section}>
            <div className={styles.sectionHeader}>
                <h2>Инструменты администратора</h2>
                <div className={styles.actions}>
                    <Link to="/admin/courses"><Button type="button" variant="secondary">Курсы</Button></Link>
                    <Link to="/admin/users"><Button type="button" variant="secondary">Пользователи</Button></Link>
                    <Link to="/admin/categories"><Button type="button" variant="secondary">Категории</Button></Link>
                </div>
            </div>
        </div>
    </>
);

export default AdminDashboardView;
