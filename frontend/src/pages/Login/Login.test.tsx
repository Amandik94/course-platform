import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import Login from './Login';
import { authService } from '../../services/authService';
import { useAuthStore } from '../../store/authStore';

vi.mock('../../services/authService', () => ({
    authService: {
        login: vi.fn(),
    },
}));

describe('Login page', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        useAuthStore.setState({ user: null, accessToken: null, isAuthenticated: false });
    });

    const renderLogin = () =>
        render(
            <MemoryRouter>
                <Login />
            </MemoryRouter>,
        );

    it('renders email and password fields', () => {
        renderLogin();
        expect(screen.getByLabelText('Email')).toBeInTheDocument();
        expect(screen.getByLabelText('Пароль')).toBeInTheDocument();
    });

    it('submits credentials and updates auth store on success', async () => {
        const user = userEvent.setup();
        vi.mocked(authService.login).mockResolvedValue({
            user: {
                id: 1, email: 'test@test.com', first_name: 'Т', last_name: 'Т',
                full_name: 'Т Т', avatar: null, role: 'student', created_at: '2026-01-01',
            },
            access: 'fake-access-token',
            refresh: 'fake-refresh-token',
        });

        renderLogin();
        await user.type(screen.getByLabelText('Email'), 'test@test.com');
        await user.type(screen.getByLabelText('Пароль'), 'password123');
        await user.click(screen.getByRole('button', { name: 'Войти' }));

        await waitFor(() => {
            expect(authService.login).toHaveBeenCalledWith({
                email: 'test@test.com',
                password: 'password123',
            });
        });
        expect(useAuthStore.getState().isAuthenticated).toBe(true);
    });

    it('shows error message on invalid credentials', async () => {
        const user = userEvent.setup();
        vi.mocked(authService.login).mockRejectedValue({
            isAxiosError: true,
            response: { data: { detail: 'Неверный email или пароль' } },
        });

        renderLogin();
        await user.type(screen.getByLabelText('Email'), 'test@test.com');
        await user.type(screen.getByLabelText('Пароль'), 'wrongpass');
        await user.click(screen.getByRole('button', { name: 'Войти' }));

        expect(await screen.findByText('Неверный email или пароль')).toBeInTheDocument();
    });
});