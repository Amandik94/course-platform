import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { notificationService } from '../../services/notificationService';
import { useAuthStore } from '../../store/authStore';
import { useNotificationStore } from '../../store/notificationStore';
import NotificationBell from './NotificationBell';

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
    type: 'assignment' as const,
    title: 'Задание проверено',
    message: 'Оценка: 90/100',
    is_read: false,
    link: '/assignment/1',
    created_at: '2026-09-12T10:00:00Z',
    read_at: null,
};

describe('NotificationBell', () => {
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
        useNotificationStore.getState().resetNotifications();
        vi.mocked(notificationService.getUnreadCount).mockResolvedValue({ count: 3 });
        vi.mocked(notificationService.getNotifications).mockResolvedValue({
            count: 1,
            next: null,
            previous: null,
            results: [notification],
        });
        vi.mocked(notificationService.markAsRead).mockResolvedValue({ ...notification, is_read: true, read_at: '2026-09-12T10:01:00Z' });
        vi.mocked(notificationService.markAllAsRead).mockResolvedValue({ count: 1 });
    });

    it('shows unread count badge', async () => {
        render(<MemoryRouter><NotificationBell /></MemoryRouter>);

        expect(await screen.findByText('3')).toBeInTheDocument();
    });

    it('hides zero badge', async () => {
        vi.mocked(notificationService.getUnreadCount).mockResolvedValue({ count: 0 });

        render(<MemoryRouter><NotificationBell /></MemoryRouter>);

        await waitFor(() => expect(notificationService.getUnreadCount).toHaveBeenCalled());
        expect(screen.queryByText('0')).not.toBeInTheDocument();
    });

    it('loads dropdown notifications and marks all as read', async () => {
        const user = userEvent.setup();
        render(<MemoryRouter><NotificationBell /></MemoryRouter>);

        await user.click(screen.getByRole('button', { name: 'Уведомления' }));

        expect(await screen.findByText('Задание проверено')).toBeInTheDocument();
        await user.click(screen.getByRole('button', { name: 'Прочитать все' }));

        await waitFor(() => expect(notificationService.markAllAsRead).toHaveBeenCalled());
    });
});
