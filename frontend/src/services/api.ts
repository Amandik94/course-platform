import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { getAuthState } from '../store/authStore';

export const api = axios.create({
    baseURL: '/api/v1/',
    headers: {
        'Content-Type': 'application/json',
    },
});

// --- REQUEST interceptor: подставляем access token в каждый запрос ---
api.interceptors.request.use((config) => {
    const { accessToken } = getAuthState();
    if (accessToken && config.headers) {
        config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
});

// --- RESPONSE interceptor: обновляем access token при 401 ---

// Флаг + очередь нужны, чтобы избежать ситуации, когда несколько
// запросов одновременно словили 401 и каждый пытается обновить токен
// параллельно — вместо этого только первый запускает refresh,
// остальные ждут его результата.
let isRefreshing = false;
let refreshQueue: Array<(token: string) => void> = [];

function subscribeToRefresh(callback: (token: string) => void) {
    refreshQueue.push(callback);
}

function notifyRefreshSubscribers(token: string) {
    refreshQueue.forEach((callback) => callback(token));
    refreshQueue = [];
}

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
    _retry?: boolean;
}

api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        const originalRequest = error.config as RetryableRequestConfig;

        // Не пытаемся обновить токен для самих auth-эндпоинтов —
        // иначе можно попасть в бесконечный цикл при неверном пароле и т.д.
        const isAuthEndpoint = originalRequest?.url?.includes('/auth/');

        if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
            const { refreshToken, setAccessToken, logout } = getAuthState();

            if (!refreshToken) {
                logout();
                window.location.href = '/login';
                return Promise.reject(error);
            }

            originalRequest._retry = true;

            if (isRefreshing) {
                // уже идёт обновление токена — ждём его результата
                return new Promise((resolve) => {
                    subscribeToRefresh((newToken: string) => {
                        originalRequest.headers.Authorization = `Bearer ${newToken}`;
                        resolve(api(originalRequest));
                    });
                });
            }

            isRefreshing = true;
            try {
                const { data } = await axios.post('/api/v1/auth/refresh/', {
                    refresh: refreshToken,
                });
                const newAccessToken = data.access;

                setAccessToken(newAccessToken);
                notifyRefreshSubscribers(newAccessToken);

                originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
                return api(originalRequest);
            } catch (refreshError) {
                logout();
                window.location.href = '/login';
                return Promise.reject(refreshError);
            } finally {
                isRefreshing = false;
            }
        }

        return Promise.reject(error);
    },
);