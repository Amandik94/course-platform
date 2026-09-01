import { create } from 'zustand';
import type { AuthTokens, User } from '../types/user';

const ACCESS_TOKEN_KEY = 'lms_access_token';
const REFRESH_TOKEN_KEY = 'lms_refresh_token';

interface AuthState {
    user: User | null;
    accessToken: string | null;
    refreshToken: string | null;
    isAuthenticated: boolean;
    isInitializing: boolean;   // true пока проверяем токен из localStorage при загрузке
    setAuth: (user: User, tokens: AuthTokens) => void;
    setUser: (user: User) => void;
    setAccessToken: (accessToken: string) => void;
    logout: () => void;
    finishInitializing: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
    user: null,
    accessToken: localStorage.getItem(ACCESS_TOKEN_KEY),
    refreshToken: localStorage.getItem(REFRESH_TOKEN_KEY),
    isAuthenticated: false,
    isInitializing: true,

    setAuth: (user, tokens) => {
        localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access);
        localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh);
        set({
            user,
            accessToken: tokens.access,
            refreshToken: tokens.refresh,
            isAuthenticated: true,
        });
    },

    setUser: (user) => set({ user }),

    setAccessToken: (accessToken) => {
        localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
        set({ accessToken });
    },

    logout: () => {
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
        });
    },

    finishInitializing: () => set({ isInitializing: false }),
}));

// Функции для доступа к состоянию store ВНЕ React-компонентов
// (нужны в Axios interceptor, который не может использовать хук useAuthStore()
// напрямую — interceptor это не компонент и не хук).
export const getAuthState = () => useAuthStore.getState();