import { createBrowserRouter } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';
import PublicRoute from './PublicRoute';
import RoleRoute from './RoleRoute';

import Home from '../../pages/Home/Home';
import Login from '../../pages/Login/Login';
import Register from '../../pages/Register/Register';
import Profile from '../../pages/Profile/Profile';
import Courses from '../../pages/Courses/Courses';
import CourseDetail from '../../pages/CourseDetail/CourseDetail';
import Learn from '../../pages/Learn/Learn';
import AssignmentPage from '../../pages/Assignments/Assignments';
import QuizPage from '../../pages/Quizzes/Quizzes';

const Placeholder = ({ title }: { title: string }) => <div className="container"><h1>{title}</h1></div>;

export const router = createBrowserRouter([
    { path: '/', element: <Home /> },
    { path: '/courses', element: <Courses /> },
    { path: '/courses/:id', element: <CourseDetail /> },
    {
        path: '/login',
        element: (
            <PublicRoute>
                <Login />
            </PublicRoute>
        ),
    },
    {
        path: '/register',
        element: (
            <PublicRoute>
                <Register />
            </PublicRoute>
        ),
    },
    {
        path: '/profile',
        element: (
            <ProtectedRoute>
                <Profile />
            </ProtectedRoute>
        ),
    },
    {
        path: '/my-courses',
        element: (
            <ProtectedRoute>
                <Placeholder title="Мои курсы" />
            </ProtectedRoute>
        ),
    },
    {
        path: '/learn/:courseId/:lessonId',
        element: (
            <ProtectedRoute>
                <Learn />
            </ProtectedRoute>
        ),
    },
    { path: '/quiz/:id', element: <ProtectedRoute><QuizPage /></ProtectedRoute> },
    { path: '/assignment/:id', element: <ProtectedRoute><AssignmentPage /></ProtectedRoute> },
    { path: '/certificates', element: <ProtectedRoute><Placeholder title="Сертификаты" /></ProtectedRoute> },
    {
        path: '/dashboard',
        element: (
            <RoleRoute allowedRoles={['teacher', 'admin']}>
                <Placeholder title="Dashboard" />
            </RoleRoute>
        ),
    },
    { path: '*', element: <Placeholder title="404 — Страница не найдена" /> },
]);