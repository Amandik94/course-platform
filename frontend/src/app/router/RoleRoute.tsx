import { type ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import type { UserRole } from '../../types/user';

interface RoleRouteProps {
    children: ReactNode;
    allowedRoles: UserRole[];
}

/**
 * Пропускает только пользователей с определённой ролью (например,
 * /dashboard доступен только teacher/admin).
 * ВАЖНО: это UX-удобство, не защита данных — реальная проверка прав
 * всегда происходит на Django через permissions.
 * Если злоумышленник обойдёт эту проверку через DevTools, он всё равно
 * получит 403 от backend при попытке получить/изменить данные.
 */
const RoleRoute = ({ children, allowedRoles }: RoleRouteProps) => {
    const { user, isAuthenticated, isInitializing } = useAuthStore();

    if (isInitializing) {
        return null;
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    if (!user || !allowedRoles.includes(user.role)) {
        return <Navigate to="/" replace />;
    }

    return <>{children}</>;
};

export default RoleRoute;