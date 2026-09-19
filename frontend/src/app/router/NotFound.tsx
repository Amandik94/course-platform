import { Link } from 'react-router-dom';
import Button from '../../components/Button/Button';
import EmptyState from '../../components/EmptyState/EmptyState';
import styles from './NotFound.module.css';

const NotFound = () => (
    <div className={`container ${styles.page}`}>
        <EmptyState
            variant="error"
            title="Страница не найдена"
            description="Проверьте адрес или вернитесь на главную страницу."
        />
        <div className={styles.action}>
            <Link to="/"><Button type="button">На главную</Button></Link>
        </div>
    </div>
);

export default NotFound;
