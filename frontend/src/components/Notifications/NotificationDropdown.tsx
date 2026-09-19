import { Link, useNavigate } from 'react-router-dom';
import Button from '../Button/Button';
import EmptyState from '../EmptyState/EmptyState';
import Loader from '../Loader/Loader';
import type { Notification } from '../../types/notification';
import { formatDateTime } from '../../utils/formatDate';
import { pluralizeRu } from '../../utils/labels';
import styles from './NotificationDropdown.module.css';

interface NotificationDropdownProps {
    notifications: Notification[];
    isLoading: boolean;
    error: string;
    unreadCount: number;
    onMarkAsRead: (notification: Notification) => Promise<Notification>;
    onMarkAllAsRead: () => Promise<void>;
    onClose: () => void;
}

const NotificationDropdown = ({
    notifications,
    isLoading,
    error,
    unreadCount,
    onMarkAsRead,
    onMarkAllAsRead,
    onClose,
}: NotificationDropdownProps) => {
    const navigate = useNavigate();
    const hasUnreadNotifications = unreadCount > 0 || notifications.some((notification) => !notification.is_read);

    const openNotification = async (notification: Notification) => {
        try {
            await onMarkAsRead(notification);
        } finally {
            onClose();
            if (notification.link) {
                navigate(notification.link);
            }
        }
    };

    return (
        <div id="notification-dropdown" className={styles.dropdown} aria-label="Последние уведомления">
            <div className={styles.header}>
                <div>
                    <h2>Уведомления</h2>
                    <span>
                        {unreadCount > 0
                            ? `${unreadCount} ${pluralizeRu(unreadCount, ['непрочитанное', 'непрочитанных', 'непрочитанных'])}`
                            : 'Все прочитано'}
                    </span>
                </div>
                <Button type="button" variant="secondary" disabled={!hasUnreadNotifications} onClick={() => void onMarkAllAsRead()}>
                    Прочитать все
                </Button>
            </div>

            {isLoading && <Loader text="Загрузка уведомлений..." />}
            {error && <EmptyState title="Не удалось загрузить уведомления" description={error} variant="error" />}

            {!isLoading && !error && notifications.length === 0 && (
                <EmptyState title="Уведомлений пока нет" />
            )}

            {!isLoading && !error && notifications.length > 0 && (
                <div className={styles.list}>
                    {notifications.slice(0, 5).map((notification) => (
                        <button
                            type="button"
                            key={notification.id}
                            className={`${styles.item} ${notification.is_read ? '' : styles.unread}`}
                            onClick={() => void openNotification(notification)}
                        >
                            <span className={styles.title}>{notification.title}</span>
                            <span className={styles.message}>{notification.message}</span>
                            <span className={styles.date}>{formatDateTime(notification.created_at)}</span>
                        </button>
                    ))}
                </div>
            )}

            <Link to="/notifications" className={styles.allLink} onClick={onClose}>
                Все уведомления
            </Link>
        </div>
    );
};

export default NotificationDropdown;
