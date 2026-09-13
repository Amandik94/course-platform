import { useCallback, useEffect, useState } from 'react';
import { notificationService, type NotificationFilters } from '../../services/notificationService';
import { useAuthStore } from '../../store/authStore';
import { useNotificationStore } from '../../store/notificationStore';
import type { PaginatedResponse } from '../../types/common';
import type { Notification } from '../../types/notification';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';

interface UseNotificationsOptions {
    autoLoad?: boolean;
    pollUnread?: boolean;
    page?: number;
}

const POLL_INTERVAL_MS = 45000;

const emptyPage: PaginatedResponse<Notification> = {
    count: 0,
    next: null,
    previous: null,
    results: [],
};

export function useNotifications(options: UseNotificationsOptions = {}) {
    const { autoLoad = true, pollUnread = false, page = 1 } = options;
    const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
    const unreadCount = useNotificationStore((state) => state.unreadCount);
    const setUnreadCount = useNotificationStore((state) => state.setUnreadCount);
    const decrementUnreadCount = useNotificationStore((state) => state.decrementUnreadCount);
    const resetNotifications = useNotificationStore((state) => state.resetNotifications);

    const [data, setData] = useState<PaginatedResponse<Notification>>(emptyPage);
    const [isLoading, setIsLoading] = useState(autoLoad);
    const [error, setError] = useState('');

    const refreshUnreadCount = useCallback(async () => {
        if (!isAuthenticated) {
            resetNotifications();
            return;
        }
        const response = await notificationService.getUnreadCount();
        setUnreadCount(response.count);
    }, [isAuthenticated, resetNotifications, setUnreadCount]);

    const fetchNotifications = useCallback(async (filters: NotificationFilters = {}) => {
        if (!isAuthenticated) {
            setData(emptyPage);
            setIsLoading(false);
            return emptyPage;
        }

        setIsLoading(true);
        setError('');
        try {
            const response = await notificationService.getNotifications({ page, ...filters });
            setData(response);
            return response;
        } catch (err) {
            setError(getApiErrorMessage(err));
            return emptyPage;
        } finally {
            setIsLoading(false);
        }
    }, [isAuthenticated, page]);

    const markAsRead = useCallback(async (notification: Notification) => {
        if (notification.is_read) return notification;
        const updated = await notificationService.markAsRead(notification.id);
        setData((current) => ({
            ...current,
            results: current.results.map((item) => (item.id === updated.id ? updated : item)),
        }));
        decrementUnreadCount();
        return updated;
    }, [decrementUnreadCount]);

    const markAllAsRead = useCallback(async () => {
        await notificationService.markAllAsRead();
        setData((current) => ({
            ...current,
            results: current.results.map((item) => ({
                ...item,
                is_read: true,
                read_at: item.read_at ?? new Date().toISOString(),
            })),
        }));
        setUnreadCount(0);
    }, [setUnreadCount]);

    const deleteNotification = useCallback(async (id: number) => {
        await notificationService.deleteNotification(id);
        setData((current) => {
            const deleted = current.results.find((item) => item.id === id);
            if (deleted && !deleted.is_read) {
                decrementUnreadCount();
            }
            return {
                ...current,
                count: Math.max(0, current.count - 1),
                results: current.results.filter((item) => item.id !== id),
            };
        });
    }, [decrementUnreadCount]);

    useEffect(() => {
        if (!autoLoad) return;
        queueMicrotask(() => {
            void fetchNotifications();
        });
    }, [autoLoad, fetchNotifications]);

    useEffect(() => {
        if (!pollUnread || !isAuthenticated) {
            resetNotifications();
            return;
        }

        void refreshUnreadCount();
        const interval = window.setInterval(() => {
            void refreshUnreadCount();
        }, POLL_INTERVAL_MS);

        return () => window.clearInterval(interval);
    }, [isAuthenticated, pollUnread, refreshUnreadCount, resetNotifications]);

    return {
        notifications: data.results,
        count: data.count,
        next: data.next,
        previous: data.previous,
        unreadCount,
        isLoading,
        error,
        fetchNotifications,
        refreshUnreadCount,
        markAsRead,
        markAllAsRead,
        deleteNotification,
    };
}
