import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../../services/authService';
import { useAuthStore } from '../../store/authStore';
import type { LoginPayload, RegisterPayload } from '../../types/user';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';

/**
 * Инкапсулирует бизнес-логику авторизации: вызов API, запись в store,
 * навигацию после успеха, извлечение читаемой ошибки из ответа сервера.
 * Страницы Login/Register используют только то, что этот хук отдаёт.
 */
export function useAuth() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const setAuth = useAuthStore((state) => state.setAuth);
    const navigate = useNavigate();


    const login = async (payload: LoginPayload) => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await authService.login(payload);
            setAuth(response.user, { access: response.access, refresh: response.refresh });
            navigate('/');
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsLoading(false);
        }
    };

    const register = async (payload: RegisterPayload) => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await authService.register(payload);
            setAuth(response.user, { access: response.access, refresh: response.refresh });
            navigate('/');
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsLoading(false);
        }
    };

    return { login, register, isLoading, error };
}