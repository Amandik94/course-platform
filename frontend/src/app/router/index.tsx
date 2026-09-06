import { createBrowserRouter } from 'react-router-dom';
import Layout from '../layout/Layout';
import ProtectedRoute from './ProtectedRoute';
import PublicRoute from './PublicRoute';

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

const NotFound = () => <div className="container"><h1>404 — Страница не найдена</h1></div>;

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
            { path: 'learn/:courseId/:lessonId',element: <ProtectedRoute><Learn /></ProtectedRoute>,},
            { path: 'quiz/:id', element: <ProtectedRoute><QuizPage /></ProtectedRoute> },
            { path: 'assignment/:id', element: <ProtectedRoute><AssignmentPage /></ProtectedRoute> },
            { path: 'certificates', element: <ProtectedRoute><Certificates /></ProtectedRoute> },
            { path: 'dashboard', element: <ProtectedRoute><Dashboard /></ProtectedRoute> },
            { path: '*', element: <NotFound /> },
        ],
    },
]);