import { Link } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useLogout } from '../../features/auth/useLogout';
import Button from '../Button/Button';
import styles from './Navbar.module.css';

const Navbar = () => {
    const { isAuthenticated, user } = useAuthStore();
    const logout = useLogout();

    return (
        <nav className={styles.navbar}>
            <Link to="/" className={styles.brand}>LMS Platform</Link>

            <div className={styles.links}>
                <Link to="/courses" className={styles.link}>Курсы</Link>

                {isAuthenticated && user?.role === 'student' && (
                    <>
                        <Link to="/my-courses" className={styles.link}>Мои курсы</Link>
                        <Link to="/certificates" className={styles.link}>Сертификаты</Link>
                    </>
                )}

                {isAuthenticated && (user?.role === 'teacher' || user?.role === 'admin') && (
                    <Link to="/dashboard" className={styles.link}>Dashboard</Link>
                )}

                {isAuthenticated && user?.role === 'student' && (
                    <Link to="/dashboard" className={styles.link}>Dashboard</Link>
                )}
            </div>

            <div className={styles.actions}>
                {isAuthenticated && user ? (
                    <>
                        <Link to="/profile" className={styles.userName}>{user.full_name}</Link>
                        <Button variant="secondary" onClick={logout}>Выйти</Button>
                    </>
                ) : (
                    <>
                        <Link to="/login" className={styles.link}>Вход</Link>
                        <Button variant="primary" onClick={() => (window.location.href = '/register')}>
                            Регистрация
                        </Button>
                    </>
                )}
            </div>
        </nav>
    );
};

export default Navbar;