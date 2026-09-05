import styles from './Skeleton.module.css';

interface SkeletonProps {
    variant?: 'card';
    count?: number;
}

const Skeleton = ({ variant = 'card', count = 1 }: SkeletonProps) => {
    return (
        <>
            {Array.from({ length: count }).map((_, i) => (
                <div key={i} className={`${styles.skeleton} ${styles[variant]}`} />
            ))}
        </>
    );
};

export default Skeleton;