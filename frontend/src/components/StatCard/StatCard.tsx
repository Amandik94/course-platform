import styles from './StatCard.module.css';

interface StatCardProps {
    value: number | string;
    label: string;
}

const StatCard = ({ value, label }: StatCardProps) => (
    <div className={styles.card}>
        <div className={styles.value}>{value}</div>
        <div className={styles.label}>{label}</div>
    </div>
);

export default StatCard;