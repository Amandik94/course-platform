import { useEffect, useState } from 'react';
import { useAuthStore } from '../../store/authStore';
import { dashboardService } from '../../services/dashboardService';
import Loader from '../../components/Loader/Loader';
import EmptyState from '../../components/EmptyState/EmptyState';
import StudentDashboardView from './StudentDashboardView';
import TeacherDashboardView from './TeacherDashboardView';
import AdminDashboardView from './AdminDashboardView';
import type { AdminDashboard, StudentDashboard, TeacherDashboard } from '../../types/dashboard';
import styles from './Dashboard.module.css';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';

type DashboardData =
    | { role: 'student'; data: StudentDashboard }
    | { role: 'teacher'; data: TeacherDashboard }
    | { role: 'admin'; data: AdminDashboard };

const Dashboard = () => {
    const { user } = useAuthStore();
    const [dashboard, setDashboard] = useState<DashboardData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!user) return;

        const load = async () => {
            setIsLoading(true);
            setError(null);
            try {
                if (user.role === 'student') {
                    const data = await dashboardService.getStudentDashboard();
                    setDashboard({ role: 'student', data });
                } else if (user.role === 'teacher') {
                    const data = await dashboardService.getTeacherDashboard();
                    setDashboard({ role: 'teacher', data });
                } else {
                    const data = await dashboardService.getAdminDashboard();
                    setDashboard({ role: 'admin', data });
                }
            } catch (err) {
                setError(getApiErrorMessage(err));
            } finally {
                setIsLoading(false);
            }
        };

        load();
    }, [user]);

    if (isLoading) return <Loader text="Загрузка дашборда..." />;
    if (error || !dashboard) return <EmptyState variant="error" title="Ошибка" description={error ?? undefined} />;

    return (
        <div className={`${styles.page} container`}>
            <h1>Dashboard</h1>
            {dashboard.role === 'student' && <StudentDashboardView data={dashboard.data} />}
            {dashboard.role === 'teacher' && <TeacherDashboardView data={dashboard.data} />}
            {dashboard.role === 'admin' && <AdminDashboardView data={dashboard.data} />}
        </div>
    );
};

export default Dashboard;