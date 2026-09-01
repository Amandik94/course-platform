import { type ReactNode, useEffect } from 'react';
import { useAuthStore } from '../../store/authStore';
import { authService } from '../../services/authService';

interface AppProvidersProps {
    children: ReactNode;
}

/**
 * При первом рендере приложения:
 * если в localStorage есть access token — пытаемся получить
 * актуальный профиль пользователя (GET /auth/me/). Если токен
 * истёк, Axios interceptor (Этап 12) сам попробует его обновить
 * через refresh token — вся эта цепочка прозрачна для этого кода.
 * Если и refresh не сработал — interceptor вызовет logout() сам.
 */
const AppProviders = ({ children }: AppProvidersProps) => {
    const { accessToken, setUser, logout, finishInitializing } = useAuthStore();

    useEffect(() => {
        const initAuth = async () => {
            if (!accessToken) {
                finishInitializing();
                return;
            }

            try {
                const user = await authService.getMe();
                setUser(user);
                useAuthStore.setState({ isAuthenticated: true });
            } catch {
                logout();
            } finally {
                finishInitializing();
            }
        };

        initAuth();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return <>{children}</>;
};

export default AppProviders;