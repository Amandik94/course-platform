export type UserRole = 'student' | 'teacher' | 'admin';

export interface User {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    full_name: string;
    avatar: string | null;
    role: UserRole;
    created_at: string;
}

export interface AuthTokens {
    access: string;
    refresh: string;
}

export interface LoginPayload {
    email: string;
    password: string;
}

export interface RegisterPayload {
    email: string;
    password: string;
    password_confirm: string;
    first_name: string;
    last_name: string;
}

export interface AuthResponse extends AuthTokens {
    user: User;
}