import { api } from './api';
import type { PaginatedResponse } from '../types/common';
import type { Notification, UnreadCountResponse } from '../types/notification';

export interface NotificationFilters {
    page?: number;
    is_read?: boolean;
}

export const notificationService = {
    getNotifications: (filters: NotificationFilters = {}) =>
        api
            .get<PaginatedResponse<Notification>>('notifications/', {
                params: {
                    ...filters,
                    is_read: typeof filters.is_read === 'boolean' ? String(filters.is_read) : undefined,
                },
            })
            .then((res) => res.data),

    getUnreadCount: () =>
        api.get<UnreadCountResponse>('notifications/unread-count/').then((res) => res.data),

    markAsRead: (id: number | string) =>
        api.patch<Notification>(`notifications/${id}/read/`).then((res) => res.data),

    markAllAsRead: () =>
        api.post<UnreadCountResponse>('notifications/read-all/').then((res) => res.data),

    deleteNotification: (id: number | string) =>
        api.delete(`notifications/${id}/`),
};
