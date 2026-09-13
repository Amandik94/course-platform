import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { notificationService } from '../../services/notificationService';
import { useAuthStore } from '../../store/authStore';
import { useNotificationStore } from '../../store/notificationStore';
import NotificationsPage from './NotificationsPage';

vi.mock('../../services/notificationService', () => ({
    notificationService: {
        getUnreadCount: vi.fn(),
        getNotifications: vi.fn(),
        markAsRead: vi.fn(),
        markAllAsRead: vi.fn(),
        deleteNotification: vi.fn(),
    },
}));

const notification = {
    id: 1,
    type: 'course' as const,
    title: 'Запись на курс подтверждена',
    message: 'Вы записались на курс Django.',
    is_read: false,
    link: '/courses/1',
    created_at: '2026-09-12T10:00:00Z',
    read_at: null,
};

describe('NotificationsPage', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        useAuthStore.setState({
            user: {
                id: 1,
                email: 'student@test.com',
                first_name: 'Student',
                last_name: 'User',
                full_name: 'Student User',
                avatar: null,
                role: 'student',
                created_at: '2026-01-01',
            },
            accessToken: 'token',
            refreshToken: 'refresh',
            isAuthenticated: true,
            isInitializing: false,
        });
        useNotificationStore.getState().setUnreadCount(1);
        vi.mocked(notificationService.getNotifications).mockResolvedValue({
            count: 1,
            next: null,
            previous: null,
            results: [notification],
        });
        vi.mocked(notificationService.markAsRead).mockResolvedValue({ ...notification, is_read: true, read_at: '2026-09-12T10:01:00Z' });
        vi.mocked(notificationService.markAllAsRead).mockResolvedValue({ count: 1 });
        vi.mocked(notificationService.deleteNotification).mockResolvedValue({} as never);
    });

    it('renders paginated notifications', async () => {
        render(<MemoryRouter><NotificationsPage /></MemoryRouter>);

        expect(await screen.findByText('Запись на курс подтверждена')).toBeInTheDocument();
        expect(screen.getByText('Вы записались на курс Django.')).toBeInTheDocument();
    });

    it('marks one notification as read', async () => {
        const user = userEvent.setup();
        render(<MemoryRouter><NotificationsPage /></MemoryRouter>);
        await screen.findByText('Запись на курс подтверждена');

        await user.click(screen.getByRole('button', { name: 'Отметить прочитанным' }));

        await waitFor(() => expect(notificationService.markAsRead).toHaveBeenCalledWith(1));
    });

    it('marks all notifications as read', async () => {
        const user = userEvent.setup();
        render(<MemoryRouter><NotificationsPage /></MemoryRouter>);
        await screen.findByText('Запись на курс подтверждена');

        await user.click(screen.getByRole('button', { name: 'Прочитать все' }));

        await waitFor(() => expect(notificationService.markAllAsRead).toHaveBeenCalled());
    });
});
