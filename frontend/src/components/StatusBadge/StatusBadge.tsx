import type { SubmissionStatus } from '../../types/assignment';
import styles from './StatusBadge.module.css';

const LABELS: Record<SubmissionStatus, string> = {
    pending: 'На проверке',
    accepted: 'Принято',
    revision: 'На доработку',
};

interface StatusBadgeProps {
    status: SubmissionStatus;
}

const StatusBadge = ({ status }: StatusBadgeProps) => (
    <span className={`${styles.badge} ${styles[status]}`}>{LABELS[status]}</span>
);

export default StatusBadge;