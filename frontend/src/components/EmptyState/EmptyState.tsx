import styles from './EmptyState.module.css';

interface EmptyStateProps {
    title: string;
    description?: string;
    variant?: 'empty' | 'error';
}

const EmptyState = ({ title, description, variant = 'empty' }: EmptyStateProps) => (
    <div className={styles.wrapper}>
        <div className={styles.icon}>{variant === 'error' ? '⚠️' : '📭'}</div>
        <p className={`${styles.title} ${variant === 'error' ? styles.errorTitle : ''}`}>{title}</p>
        {description && <p>{description}</p>}
    </div>
);

export default EmptyState;