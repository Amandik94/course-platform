import { Outlet } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';

/**
 * Общий каркас для всех страниц: Navbar сверху + область контента
 * страницы через <Outlet/>. До этого этапа роутер рендерил страницы
 * "голыми", без навигации — с ростом числа страниц (my-courses,
 * dashboard, certificates) это стало неудобно для реального 
 * использования, поэтому вводим layout именно сейчас.
 */
const Layout = () => (
    <>
        <Navbar />
        <Outlet />
    </>
);

export default Layout;