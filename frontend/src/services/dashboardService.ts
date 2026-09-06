import { api } from './api';
import type { AdminDashboard, StudentDashboard, TeacherDashboard } from '../types/dashboard';

export const dashboardService = {
    getStudentDashboard: () =>
        api.get<StudentDashboard>('dashboard/student/').then((res) => res.data),

    getTeacherDashboard: () =>
        api.get<TeacherDashboard>('dashboard/teacher/').then((res) => res.data),

    getAdminDashboard: () =>
        api.get<AdminDashboard>('dashboard/admin/').then((res) => res.data),
};