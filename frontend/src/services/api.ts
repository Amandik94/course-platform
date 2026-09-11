import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { getAuthState } from '../store/authStore';

const API_BASE_URL = `${import.meta.env.VITE_API_URL || '/api/v1/'}`.replace(/\/?$/, '/');

export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.request.use((config) => {
    const { accessToken } = getAuthState();
    if (accessToken && config.headers) {
        config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
});

let isRefreshing = false;
let refreshQueue: Array<{
    resolve: (token: string) => void;
    reject: (error: unknown) => void;
}> = [];

function waitForRefresh() {
    return new Promise<string>((resolve, reject) => {
        refreshQueue.push({ resolve, reject });
    });
}

function resolveRefreshQueue(token: string) {
    refreshQueue.forEach((subscriber) => subscriber.resolve(token));
    refreshQueue = [];
}

function rejectRefreshQueue(error: unknown) {
    refreshQueue.forEach((subscriber) => subscriber.reject(error));
    refreshQueue = [];
}

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
    _retry?: boolean;
}

api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        const originalRequest = error.config as RetryableRequestConfig | undefined;
        const isAuthEndpoint = originalRequest?.url?.includes('/auth/');

        if (!originalRequest) {
            return Promise.reject(error);
        }

        if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
            const { refreshToken, setAccessToken, setRefreshToken, logout } = getAuthState();

            if (!refreshToken) {
                logout();
                window.location.href = '/login';
                return Promise.reject(error);
            }

            originalRequest._retry = true;

            if (isRefreshing) {
                const newToken = await waitForRefresh();
                originalRequest.headers.Authorization = `Bearer ${newToken}`;
                return api(originalRequest);
            }

            isRefreshing = true;
            try {
                const { data } = await axios.post<{ access: string; refresh?: string }>(
                    `${API_BASE_URL}auth/refresh/`,
                    { refresh: refreshToken },
                );

                setAccessToken(data.access);
                if (data.refresh) {
                    setRefreshToken(data.refresh);
                }
                resolveRefreshQueue(data.access);

                originalRequest.headers.Authorization = `Bearer ${data.access}`;
                return api(originalRequest);
            } catch (refreshError) {
                rejectRefreshQueue(refreshError);
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
