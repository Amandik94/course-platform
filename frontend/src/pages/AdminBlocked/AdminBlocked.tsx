import { Link, useParams } from 'react-router-dom';
import Button from '../../components/Button/Button';
import EmptyState from '../../components/EmptyState/EmptyState';
import styles from './AdminBlocked.module.css';

const MESSAGES: Record<string, string> = {
    users: 'User list, detail, role update and block/unblock need dedicated admin user API endpoints.',
    categories: 'Category create, update and delete need dedicated admin category API endpoints. Backend currently exposes read-only category listing.',
};

const AdminBlocked = () => {
    const { area } = useParams();
    const key = area ?? '';
    const description = MESSAGES[key] ?? 'This admin area is not backed by an API endpoint yet.';

    return (
        <div className={styles.page}>
            <EmptyState title="BLOCKED BY BACKEND API" description={description} variant="error" />
            <Link to="/dashboard">
                <Button type="button" variant="secondary">Back to dashboard</Button>
            </Link>
        </div>
    );
};

export default AdminBlocked;
