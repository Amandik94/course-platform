import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../../components/Button/Button';
import EmptyState from '../../components/EmptyState/EmptyState';
import Loader from '../../components/Loader/Loader';
import Pagination from '../../components/Pagination/Pagination';
import { useNotifications } from '../../features/notifications/useNotifications';
import type { Notification } from '../../types/notification';
import { formatDateTime } from '../../utils/formatDate';
import { NOTIFICATION_TYPE_LABELS, pluralizeRu } from '../../utils/labels';
import styles from './NotificationsPage.module.css';

const PAGE_SIZE = 9;

const NotificationsPage = () => {
    const navigate = useNavigate();
    const [page, setPage] = useState(1);
    const {
        notifications,
        count,
        unreadCount,
        isLoading,
        error,
        markAsRead,
        markAllAsRead,
        deleteNotification,
    } = useNotifications({ page });

    const totalPages = Math.ceil(count / PAGE_SIZE);
    const hasUnreadNotifications = unreadCount > 0 || notifications.some((notification) => !notification.is_read);

    const openNotification = async (notification: Notification) => {
        try {
            await markAsRead(notification);
        } finally {
            if (notification.link) {
                navigate(notification.link);
            }
        }
    };

    return (
        <div className={`${styles.page} container`}>
            <div className={styles.header}>
                <div>
                    <h1>Уведомления</h1>
                    <p>
                        {unreadCount > 0
                            ? `${unreadCount} ${pluralizeRu(unreadCount, ['непрочитанное уведомление', 'непрочитанных уведомления', 'непрочитанных уведомлений'])}`
                            : 'Все уведомления прочитаны'}
                    </p>
                </div>
                <Button type="button" variant="secondary" disabled={!hasUnreadNotifications} onClick={() => void markAllAsRead()}>
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
                    {notifications.map((notification) => (
                        <article key={notification.id} className={`${styles.item} ${notification.is_read ? '' : styles.unread}`}>
                            <button type="button" className={styles.content} onClick={() => void openNotification(notification)}>
                                <span className={styles.type}>{NOTIFICATION_TYPE_LABELS[notification.type]}</span>
                                <h2>{notification.title}</h2>
                                <p>{notification.message}</p>
                                <time>{formatDateTime(notification.created_at)}</time>
                            </button>
                            <div className={styles.actions}>
                                {!notification.is_read && (
                                    <Button type="button" variant="secondary" onClick={() => void markAsRead(notification)}>
                                        Отметить прочитанным
                                    </Button>
                                )}
                                <Button type="button" variant="danger" onClick={() => void deleteNotification(notification.id)}>
                                    Удалить
                                </Button>
                            </div>
                        </article>
                    ))}
                </div>
            )}

            <Pagination currentPage={page} totalPages={totalPages} onPageChange={setPage} />
        </div>
    );
};

export default NotificationsPage;
