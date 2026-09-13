import { Link, useParams } from 'react-router-dom';
import Button from '../../components/Button/Button';
import EmptyState from '../../components/EmptyState/EmptyState';
import styles from './AdminBlocked.module.css';

const MESSAGES: Record<string, string> = {
    users: 'Для списка пользователей, карточки пользователя, смены роли и блокировки нужны отдельные admin API endpoints.',
    categories: 'Для создания, обновления и удаления категорий нужны отдельные admin API endpoints. Сейчас backend предоставляет только чтение списка категорий.',
};

const AdminBlocked = () => {
    const { area } = useParams();
    const key = area ?? '';
    const description = MESSAGES[key] ?? 'Для этого раздела администрирования пока нет backend API endpoint.';

    return (
        <div className={styles.page}>
            <EmptyState title="Заблокировано backend API" description={description} variant="error" />
            <Link to="/dashboard">
                <Button type="button" variant="secondary">Назад к панели управления</Button>
            </Link>
        </div>
    );
};

export default AdminBlocked;
