import { type ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import Loader from '../../components/Loader/Loader';

interface PublicRouteProps {
    children: ReactNode;
}

/**
 * Обратная логика: страницы вроде /login и /register не должны
 * быть доступны уже авторизованному пользователю — редиректим на главную.
 */
const PublicRoute = ({ children }: PublicRouteProps) => {
    const { isAuthenticated, isInitializing } = useAuthStore();

    if (isInitializing) {
        return <Loader text="Проверяем сессию..." />;
    }

    if (isAuthenticated) {
        return <Navigate to="/" replace />;
    }

    return <>{children}</>;
};

export default PublicRoute;
