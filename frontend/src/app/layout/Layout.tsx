import { Outlet } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import styles from './Layout.module.css';

/**
 * Общий каркас для всех страниц: Navbar сверху + область контента
 * страницы через <Outlet/>. До этого этапа роутер рендерил страницы
 * "голыми", без навигации — с ростом числа страниц (my-courses,
 * dashboard, certificates) это стало неудобно для реального 
 * использования, поэтому вводим layout именно сейчас.
 */
const Layout = () => (
    <div className={styles.appShell}>
        <a className={styles.skipLink} href="#main-content">
            Перейти к содержимому
        </a>
        <Navbar />
        <main id="main-content" className={styles.main}>
            <Outlet />
        </main>
        <Footer />
    </div>
);

export default Layout;
