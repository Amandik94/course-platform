import { Link } from 'react-router-dom';
import Button from '../../components/Button/Button';
import StatCard from '../../components/StatCard/StatCard';
import type { TeacherDashboard } from '../../types/dashboard';
import styles from './Dashboard.module.css';

const TeacherDashboardView = ({ data }: { data: TeacherDashboard }) => (
    <>
        <div className={styles.statsGrid}>
            <StatCard value={data.courses_count} label="My courses" />
            <StatCard value={data.students_count} label="Students" />
            <StatCard value={data.pending_submissions_count} label="Pending submissions" />
        </div>

        <div className={styles.section}>
            <div className={styles.sectionHeader}>
                <h2>My courses</h2>
                <Link to="/teacher/courses">
                    <Button type="button" variant="secondary">Manage courses</Button>
                </Link>
            </div>
            {data.courses.map((course) => (
                <div key={course.id} className={styles.tableRow}>
                    <span>{course.title}</span>
                    <span>{course.students_count} students - {course.status}</span>
                </div>
            ))}
        </div>
    </>
);

export default TeacherDashboardView;
