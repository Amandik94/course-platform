import { useEffect, useRef, useState } from 'react';
import { useNotifications } from '../../features/notifications/useNotifications';
import { useAuthStore } from '../../store/authStore';
import NotificationDropdown from './NotificationDropdown';
import styles from './NotificationBell.module.css';

const NotificationBell = () => {
    const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
    const [isOpen, setIsOpen] = useState(false);
    const wrapperRef = useRef<HTMLDivElement | null>(null);
    const {
        notifications,
        unreadCount,
        isLoading,
        error,
        fetchNotifications,
        markAsRead,
        markAllAsRead,
    } = useNotifications({ autoLoad: false, pollUnread: true });

    useEffect(() => {
        if (!isOpen) return;
        void fetchNotifications({ page: 1 });
    }, [fetchNotifications, isOpen]);

    useEffect(() => {
        const handlePointerDown = (event: MouseEvent) => {
            if (!wrapperRef.current?.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') setIsOpen(false);
        };
        document.addEventListener('mousedown', handlePointerDown);
        document.addEventListener('keydown', handleKeyDown);
        return () => {
            document.removeEventListener('mousedown', handlePointerDown);
            document.removeEventListener('keydown', handleKeyDown);
        };
    }, []);

    if (!isAuthenticated) return null;

    return (
        <div className={styles.wrapper} ref={wrapperRef}>
            <button
                type="button"
                className={styles.bell}
                aria-label="Уведомления"
                aria-expanded={isOpen}
                aria-controls="notification-dropdown"
                onClick={() => setIsOpen((current) => !current)}
            >
                <span aria-hidden="true">🔔</span>
                {unreadCount > 0 && <span className={styles.badge}>{unreadCount > 99 ? '99+' : unreadCount}</span>}
            </button>

            {isOpen && (
                <NotificationDropdown
                    notifications={notifications}
                    isLoading={isLoading}
                    error={error}
                    unreadCount={unreadCount}
                    onMarkAsRead={markAsRead}
                    onMarkAllAsRead={markAllAsRead}
                    onClose={() => setIsOpen(false)}
                />
            )}
        </div>
    );
};

export default NotificationBell;
