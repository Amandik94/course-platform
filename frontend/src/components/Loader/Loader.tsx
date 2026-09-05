import styles from './Loader.module.css';

interface LoaderProps {
    text?: string;
}

const Loader = ({ text = 'Загрузка...' }: LoaderProps) => (
    <div className={styles.wrapper}>
        <span className={styles.spinner} />
        <span>{text}</span>
    </div>
);

export default Loader;