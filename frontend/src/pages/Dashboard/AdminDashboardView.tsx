import { Link } from 'react-router-dom';
import Button from '../../components/Button/Button';
import StatCard from '../../components/StatCard/StatCard';
import type { AdminDashboard } from '../../types/dashboard';
import styles from './Dashboard.module.css';

const AdminDashboardView = ({ data }: { data: AdminDashboard }) => (
    <>
        <div className={styles.statsGrid}>
            <StatCard value={data.users_count} label="Users" />
            <StatCard value={data.students_count} label="Students" />
            <StatCard value={data.teachers_count} label="Teachers" />
            <StatCard value={data.courses_count} label="Courses" />
            <StatCard value={data.active_courses_count} label="Published courses" />
            <StatCard value={data.completed_enrollments_count} label="Completed enrollments" />
            <StatCard value={`${data.average_progress}%`} label="Average progress" />
        </div>
        <div className={styles.section}>
            <div className={styles.sectionHeader}>
                <h2>Admin tools</h2>
                <div className={styles.actions}>
                    <Link to="/admin/courses"><Button type="button" variant="secondary">Courses</Button></Link>
                    <Link to="/admin/users"><Button type="button" variant="secondary">Users</Button></Link>
                    <Link to="/admin/categories"><Button type="button" variant="secondary">Categories</Button></Link>
                </div>
            </div>
        </div>
    </>
);

export default AdminDashboardView;
