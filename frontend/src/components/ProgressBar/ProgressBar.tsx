import styles from './ProgressBar.module.css';

interface ProgressBarProps {
    value: number; // 0-100
}

const ProgressBar = ({ value }: ProgressBarProps) => {
    const clamped = Math.min(100, Math.max(0, value));

    return (
        <div className={styles.wrapper}>
            <div className={styles.track}>
                <div className={styles.fill} style={{ width: `${clamped}%` }} />
            </div>
            <span className={styles.label}>{clamped}%</span>
        </div>
    );
};

export default ProgressBar;