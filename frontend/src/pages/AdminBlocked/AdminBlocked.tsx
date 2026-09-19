import { Link, useParams } from 'react-router-dom';
import Button from '../../components/Button/Button';
import EmptyState from '../../components/EmptyState/EmptyState';
import styles from './AdminBlocked.module.css';

const MESSAGES: Record<string, string> = {
    users: 'Управление пользователями в этом разделе пока недоступно.',
    categories: 'Изменение категорий пока недоступно. Сейчас можно только просматривать их список.',
};

const AdminBlocked = () => {
    const { area } = useParams();
    const key = area ?? '';
    const description = MESSAGES[key] ?? 'Этот раздел администрирования пока недоступен.';

    return (
        <div className={`${styles.page} container`}>
            <EmptyState title="Раздел временно недоступен" description={description} variant="error" />
            <Link to="/dashboard">
                <Button type="button" variant="secondary">Назад к панели управления</Button>
            </Link>
        </div>
    );
};

export default AdminBlocked;
