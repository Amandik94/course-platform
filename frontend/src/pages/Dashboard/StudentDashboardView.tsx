import StatCard from '../../components/StatCard/StatCard';
import type { StudentDashboard } from '../../types/dashboard';
import styles from './Dashboard.module.css';

const StudentDashboardView = ({ data }: { data: StudentDashboard }) => (
    <>
        <div className={styles.statsGrid}>
            <StatCard value={data.active_courses_count} label="Активные курсы" />
            <StatCard value={data.completed_courses_count} label="Завершённые курсы" />
            <StatCard value={`${data.average_progress}%`} label="Средний прогресс" />
            <StatCard value={data.certificates_count} label="Сертификаты" />
        </div>

        <div className={styles.section}>
            <h2>Последние результаты тестов</h2>
            {data.recent_quiz_results.length === 0 && <p>Тестов пока не было</p>}
            {data.recent_quiz_results.map((result, i) => (
                <div key={i} className={styles.tableRow}>
                    <span>{result.quiz_title}</span>
                    <span>{result.score}% — {result.passed ? 'Пройден' : 'Не пройден'}</span>
                </div>
            ))}
        </div>
    </>
);

export default StudentDashboardView;