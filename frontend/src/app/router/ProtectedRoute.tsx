import { type ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

interface ProtectedRouteProps {
    children: ReactNode;
}

/**
 * Пропускает только авторизованных пользователей.
 * Неавторизованных отправляет на /login, запоминая, откуда пришли
 * (чтобы после логина вернуть обратно на исходную страницу).
 */
const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
    const { isAuthenticated, isInitializing } = useAuthStore();
    const location = useLocation();

    if (isInitializing) {
        return null; // либо компонент Loader — подключим на Этапе 18
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    return <>{children}</>;
};

export default ProtectedRoute;