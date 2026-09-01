import { api } from './api';
import type { AuthResponse, LoginPayload, RegisterPayload, User } from '../types/user';

export const authService = {
    register: (payload: RegisterPayload) =>
        api.post<AuthResponse>('auth/register/', payload).then((res) => res.data),

    login: (payload: LoginPayload) =>
        api.post<AuthResponse>('auth/login/', payload).then((res) => res.data),

    logout: (refreshToken: string) =>
        api.post('auth/logout/', { refresh: refreshToken }),

    getMe: () =>
        api.get<User>('auth/me/').then((res) => res.data),

    updateMe: (payload: Partial<Pick<User, 'first_name' | 'last_name'>>) =>
        api.patch<User>('auth/me/', payload).then((res) => res.data),
};