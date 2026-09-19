import { Link } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import styles from './Footer.module.css';

const Footer = () => {
    const { isAuthenticated, user } = useAuthStore();

    return (
        <footer className={styles.footer}>
            <div className={styles.inner}>
                <div>
                    <Link to="/" className={styles.brand}>LMS Platform</Link>
                    <p className={styles.description}>Практическое обучение программированию в удобном темпе.</p>
                </div>
                <nav className={styles.links} aria-label="Дополнительная навигация">
                    <Link to="/">Главная</Link>
                    <Link to="/courses">Курсы</Link>
                    {isAuthenticated ? (
                        <>
                            <Link to="/dashboard">Панель управления</Link>
                            {user?.role === 'student' && <Link to="/my-courses">Мои курсы</Link>}
                            <Link to="/profile">Профиль</Link>
                        </>
                    ) : (
                        <Link to="/login">Войти</Link>
                    )}
                </nav>
                <p className={styles.copyright}>© {new Date().getFullYear()} LMS Platform</p>
            </div>
        </footer>
    );
};

export default Footer;
