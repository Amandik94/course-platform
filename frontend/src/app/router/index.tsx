import { createBrowserRouter } from 'react-router-dom';
import Layout from '../layout/Layout';
import ProtectedRoute from './ProtectedRoute';
import PublicRoute from './PublicRoute';
import RoleRoute from './RoleRoute';
import NotFound from './NotFound';

import Home from '../../pages/Home/Home';
import Login from '../../pages/Login/Login';
import Register from '../../pages/Register/Register';
import Profile from '../../pages/Profile/Profile';
import Courses from '../../pages/Courses/Courses';
import CourseDetail from '../../pages/CourseDetail/CourseDetail';
import Learn from '../../pages/Learn/Learn';
import AssignmentPage from '../../pages/Assignments/Assignments';
import QuizPage from '../../pages/Quizzes/Quizzes';
import MyCourses from '../../pages/MyCourses/MyCourses';
import Dashboard from '../../pages/Dashboard/Dashboard';
import Certificates from '../../pages/Certificates/Certificates';
import TeacherCourses from '../../pages/TeacherCourses/TeacherCourses';
import CourseForm from '../../pages/CourseForm/CourseForm';
import CourseManage from '../../pages/CourseManage/CourseManage';
import AdminCourses from '../../pages/AdminCourses/AdminCourses';
import AdminCategories from '../../pages/AdminCategories/AdminCategories';
import { AdminUserDetail, AdminUsersList } from '../../pages/AdminUsers/AdminUsers';
import AdminBlocked from '../../pages/AdminBlocked/AdminBlocked';
import TeacherSubmissions from '../../pages/TeacherSubmissions/TeacherSubmissions';
import NotificationsPage from '../../pages/Notifications/NotificationsPage';

export const router = createBrowserRouter([
    {
        path: '/',
        element: <Layout />,
        children: [
            { index: true, element: <Home /> },
            { path: 'courses', element: <Courses /> },
            { path: 'courses/:id', element: <CourseDetail /> },
            { path: 'login', element: <PublicRoute><Login /></PublicRoute> },
            { path: 'register', element: <PublicRoute><Register /></PublicRoute> },
            { path: 'profile', element: <ProtectedRoute><Profile /></ProtectedRoute> },
            { path: 'my-courses', element: <ProtectedRoute><MyCourses /></ProtectedRoute> },
            {
                path: 'learn/:courseId/:lessonId',
                element: <ProtectedRoute><Learn /></ProtectedRoute>,
            },
            { path: 'quiz/:id', element: <ProtectedRoute><QuizPage /></ProtectedRoute> },
            { path: 'assignment/:id', element: <ProtectedRoute><AssignmentPage /></ProtectedRoute> },
            { path: 'certificates', element: <ProtectedRoute><Certificates /></ProtectedRoute> },
            { path: 'notifications', element: <ProtectedRoute><NotificationsPage /></ProtectedRoute> },
            { path: 'dashboard', element: <ProtectedRoute><Dashboard /></ProtectedRoute> },
            { path: 'dashboard/teacher', element: <RoleRoute allowedRoles={['teacher', 'admin']}><Dashboard /></RoleRoute> },
            { path: 'teacher/courses', element: <RoleRoute allowedRoles={['teacher', 'admin']}><TeacherCourses /></RoleRoute> },
            { path: 'teacher/courses/new', element: <RoleRoute allowedRoles={['teacher', 'admin']}><CourseForm /></RoleRoute> },
            { path: 'teacher/courses/:id/edit', element: <RoleRoute allowedRoles={['teacher', 'admin']}><CourseForm /></RoleRoute> },
            { path: 'teacher/courses/:id/manage', element: <RoleRoute allowedRoles={['teacher', 'admin']}><CourseManage /></RoleRoute> },
            { path: 'teacher/assignments/:id/submissions', element: <RoleRoute allowedRoles={['teacher', 'admin']}><TeacherSubmissions /></RoleRoute> },
            { path: 'dashboard/admin', element: <RoleRoute allowedRoles={['admin']}><Dashboard /></RoleRoute> },
            { path: 'admin/users', element: <RoleRoute allowedRoles={['admin']}><AdminUsersList /></RoleRoute> },
            { path: 'admin/users/:id', element: <RoleRoute allowedRoles={['admin']}><AdminUserDetail /></RoleRoute> },
            { path: 'admin/courses', element: <RoleRoute allowedRoles={['admin']}><AdminCourses /></RoleRoute> },
            { path: 'admin/categories', element: <RoleRoute allowedRoles={['admin']}><AdminCategories /></RoleRoute> },
            { path: 'admin/:area', element: <RoleRoute allowedRoles={['admin']}><AdminBlocked /></RoleRoute> },
            { path: '*', element: <NotFound /> },
        ],
    },
]);
