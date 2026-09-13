import { useNavigate } from 'react-router-dom';
import { authService } from '../../services/authService';
import { useAuthStore } from '../../store/authStore';
import { useNotificationStore } from '../../store/notificationStore';

export function useLogout() {
    const navigate = useNavigate();
    const { refreshToken, logout } = useAuthStore();
    const resetNotifications = useNotificationStore((state) => state.resetNotifications);

    return async () => {
        try {
            if (refreshToken) {
                await authService.logout(refreshToken);
            }
        } catch {
            // сервер недоступен или токен уже невалиден — не блокируем локальный выход
        } finally {
            logout();
            resetNotifications();
            navigate('/login');
        }
    };
}
