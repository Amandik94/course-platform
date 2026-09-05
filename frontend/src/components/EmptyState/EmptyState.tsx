import styles from './EmptyState.module.css';

interface EmptyStateProps {
    title: string;
    description?: string;
}

const EmptyState = ({ title, description }: EmptyStateProps) => (
    <div className={styles.wrapper}>
        <p className={styles.title}>{title}</p>
        {description && <p>{description}</p>}
    </div>
);

export default EmptyState;