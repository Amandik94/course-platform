import styles from './Pagination.module.css';

interface PaginationProps {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
}

const Pagination = ({ currentPage, totalPages, onPageChange }: PaginationProps) => {
    if (totalPages <= 1) return null;

    return (
        <nav className={styles.wrapper} aria-label="Постраничная навигация">
            <button
                type="button"
                className={styles.pageButton}
                disabled={currentPage === 1}
                onClick={() => onPageChange(currentPage - 1)}
                aria-label="Предыдущая страница"
            >
                ←
            </button>
            <span className={styles.pageStatus} aria-live="polite">
                Страница {currentPage} из {totalPages}
            </span>
            <button
                type="button"
                className={styles.pageButton}
                disabled={currentPage === totalPages}
                onClick={() => onPageChange(currentPage + 1)}
                aria-label="Следующая страница"
            >
                →
            </button>
        </nav>
    );
};

export default Pagination;
