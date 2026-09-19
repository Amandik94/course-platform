import { useEffect, useRef, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useLogout } from '../../features/auth/useLogout';
import Button from '../Button/Button';
import NotificationBell from '../Notifications/NotificationBell';
import styles from './Navbar.module.css';

const Navbar = () => {
    const { isAuthenticated, user } = useAuthStore();
    const logout = useLogout();
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const navbarRef = useRef<HTMLElement | null>(null);

    useEffect(() => {
        if (!isMenuOpen) return;

        const closeOnEscape = (event: KeyboardEvent) => {
            if (event.key === 'Escape') setIsMenuOpen(false);
        };
        const closeOnOutsideClick = (event: MouseEvent) => {
            if (!navbarRef.current?.contains(event.target as Node)) setIsMenuOpen(false);
        };

        document.addEventListener('keydown', closeOnEscape);
        document.addEventListener('mousedown', closeOnOutsideClick);
        return () => {
            document.removeEventListener('keydown', closeOnEscape);
            document.removeEventListener('mousedown', closeOnOutsideClick);
        };
    }, [isMenuOpen]);

    const navClassName = ({ isActive }: { isActive: boolean }) =>
        `${styles.link} ${isActive ? styles.activeLink : ''}`;

    const renderNavigationLinks = () => (
        <>
            <NavLink to="/courses" className={navClassName} onClick={() => setIsMenuOpen(false)}>Курсы</NavLink>

            {isAuthenticated && user?.role === 'student' && (
                <>
                    <NavLink to="/my-courses" className={navClassName} onClick={() => setIsMenuOpen(false)}>Мои курсы</NavLink>
                    <NavLink to="/certificates" className={navClassName} onClick={() => setIsMenuOpen(false)}>Сертификаты</NavLink>
                    <NavLink to="/payments" className={navClassName} onClick={() => setIsMenuOpen(false)}>Платежи</NavLink>
                    <NavLink to="/dashboard" className={navClassName} onClick={() => setIsMenuOpen(false)}>Панель управления</NavLink>
                </>
            )}

            {isAuthenticated && (user?.role === 'teacher' || user?.role === 'admin') && (
                <>
                    <NavLink to="/dashboard" className={navClassName} onClick={() => setIsMenuOpen(false)}>Панель управления</NavLink>
                    <NavLink to="/teacher/courses" className={navClassName} onClick={() => setIsMenuOpen(false)}>Мои курсы</NavLink>
                </>
            )}

            {isAuthenticated && user?.role === 'admin' && (
                <NavLink to="/admin/courses" className={navClassName} onClick={() => setIsMenuOpen(false)}>Администрирование</NavLink>
            )}
        </>
    );

    return (
        <nav className={styles.navbar} aria-label="Основная навигация" ref={navbarRef}>
            <div className={styles.navbarInner}>
                <NavLink to="/" className={styles.brand} aria-label="LMS Platform, главная" onClick={() => setIsMenuOpen(false)}>
                    <span className={styles.brandMark} aria-hidden="true">L</span>
                    <span>LMS Platform</span>
                </NavLink>

                <div className={styles.desktopLinks}>{renderNavigationLinks()}</div>

                <div className={styles.desktopActions}>
                    {isAuthenticated && user ? (
                        <>
                            <NotificationBell />
                            <NavLink to="/profile" className={styles.userName}>{user.full_name}</NavLink>
                            <Button variant="secondary" onClick={logout}>Выйти</Button>
                        </>
                    ) : (
                        <>
                            <NavLink to="/login" className={navClassName}>Войти</NavLink>
                            <NavLink to="/register" className={styles.registerLink}>Регистрация</NavLink>
                        </>
                    )}
                </div>

                <div className={styles.mobileActions}>
                    {isAuthenticated && <NotificationBell />}
                    <button
                        type="button"
                        className={styles.menuButton}
                        aria-label={isMenuOpen ? 'Закрыть меню' : 'Открыть меню'}
                        aria-expanded={isMenuOpen}
                        aria-controls="mobile-navigation"
                        onClick={() => setIsMenuOpen((current) => !current)}
                    >
                        <span className={styles.menuIcon} aria-hidden="true">
                            <span />
                            <span />
                            <span />
                        </span>
                    </button>
                </div>
            </div>

            {isMenuOpen && (
                <div id="mobile-navigation" className={styles.mobileMenu}>
                    <div className={styles.mobileLinks}>{renderNavigationLinks()}</div>
                    <div className={styles.mobileAccount}>
                        {isAuthenticated && user ? (
                            <>
                                <NavLink to="/profile" className={styles.profileLink} onClick={() => setIsMenuOpen(false)}>
                                    <span className={styles.profileName}>{user.full_name}</span>
                                    <span className={styles.profileHint}>Открыть профиль</span>
                                </NavLink>
                                <Button variant="secondary" fullWidth onClick={logout}>Выйти</Button>
                            </>
                        ) : (
                            <>
                                <NavLink to="/login" className={styles.mobileSecondaryAction} onClick={() => setIsMenuOpen(false)}>Войти</NavLink>
                                <NavLink to="/register" className={styles.mobilePrimaryAction} onClick={() => setIsMenuOpen(false)}>Регистрация</NavLink>
                            </>
                        )}
                    </div>
                </div>
            )}
        </nav>
    );
};

export default Navbar;
