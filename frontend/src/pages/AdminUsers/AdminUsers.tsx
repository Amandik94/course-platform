import { type FormEvent, useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import Button from '../../components/Button/Button';
import EmptyState from '../../components/EmptyState/EmptyState';
import Input from '../../components/Input/Input';
import Loader from '../../components/Loader/Loader';
import Pagination from '../../components/Pagination/Pagination';
import { adminService } from '../../services/adminService';
import type { AdminUser, AdminUserFilters, AdminUserUpdatePayload, UserRole } from '../../types/user';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';
import { ROLE_LABELS } from '../../utils/labels';
import styles from './AdminUsers.module.css';

const roleOptions: UserRole[] = ['student', 'teacher', 'admin'];

export const AdminUsersList = () => {
    const [users, setUsers] = useState<AdminUser[]>([]);
    const [filters, setFilters] = useState<AdminUserFilters>({ page: 1, role: '', is_active: '' });
    const [totalCount, setTotalCount] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const currentPage = filters.page ?? 1;
    const totalPages = useMemo(() => Math.ceil(totalCount / 9), [totalCount]);

    useEffect(() => {
        const loadUsers = async () => {
            setIsLoading(true);
            setError('');
            try {
                const data = await adminService.getUsers(filters);
                setUsers(data.results);
                setTotalCount(data.count);
            } catch (err) {
                setError(getApiErrorMessage(err));
            } finally {
                setIsLoading(false);
            }
        };

        void loadUsers();
    }, [filters]);

    const setFilter = (next: Partial<AdminUserFilters>) => {
        setFilters((current) => ({ ...current, ...next, page: next.page ?? 1 }));
    };

    const toggleActive = async (user: AdminUser) => {
        setIsSaving(true);
        setError('');
        setSuccess('');
        try {
            const updated = await adminService.updateUser(user.id, { is_active: !user.is_active });
            setUsers((items) => items.map((item) => (item.id === updated.id ? updated : item)));
            setSuccess(updated.is_active ? 'Пользователь разблокирован.' : 'Пользователь заблокирован.');
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) return <Loader />;

    return (
        <div className={`${styles.page} container`}>
            <div className={styles.header}>
                <div>
                    <h1>Пользователи</h1>
                    <p>Управление аккаунтами, ролями и доступом.</p>
                </div>
                <Link to="/dashboard/admin">
                    <Button type="button" variant="secondary">Панель управления</Button>
                </Link>
            </div>

            <div className={styles.filters}>
                <Input
                    label="Поиск"
                    value={filters.search ?? ''}
                    onChange={(event) => setFilter({ search: event.target.value })}
                />
                <label className={styles.field}>
                    <span>Роль</span>
                    <select value={filters.role ?? ''} onChange={(event) => setFilter({ role: event.target.value as UserRole | '' })}>
                        <option value="">Все роли</option>
                        {roleOptions.map((role) => <option key={role} value={role}>{ROLE_LABELS[role]}</option>)}
                    </select>
                </label>
                <label className={styles.field}>
                    <span>Статус</span>
                    <select value={filters.is_active ?? ''} onChange={(event) => setFilter({ is_active: event.target.value })}>
                        <option value="">Все</option>
                        <option value="true">Активен</option>
                        <option value="false">Заблокирован</option>
                    </select>
                </label>
            </div>

            {error && <EmptyState title="Не удалось загрузить пользователей" description={error} variant="error" />}
            {success && <p className={styles.success}>{success}</p>}

            {users.length === 0 && !error ? (
                <EmptyState title="Пользователей нет" />
            ) : (
                <div className={styles.table} role="table" aria-label="Пользователи">
                    <div className={styles.tableHead} role="row">
                        <span role="columnheader">Пользователь</span>
                        <span role="columnheader">Имя</span>
                        <span role="columnheader">Роль</span>
                        <span role="columnheader">Статус</span>
                        <span role="columnheader">Действия</span>
                    </div>
                    {users.map((user) => (
                        <div key={user.id} className={styles.tableRow} role="row">
                            <span role="cell" data-label="Пользователь">{user.email}</span>
                            <span role="cell" data-label="Имя">{user.full_name || '-'}</span>
                            <span role="cell" data-label="Роль">{ROLE_LABELS[user.role]}</span>
                            <span role="cell" data-label="Статус">{user.is_active ? 'Активен' : 'Заблокирован'}</span>
                            <div className={styles.actions} data-label="Действия" role="cell">
                                <Link to={`/admin/users/${user.id}`}>
                                    <Button type="button" variant="secondary">Открыть</Button>
                                </Link>
                                <Button
                                    type="button"
                                    variant={user.is_active ? 'danger' : 'secondary'}
                                    disabled={isSaving}
                                    onClick={() => void toggleActive(user)}
                                >
                                    {user.is_active ? 'Заблокировать' : 'Разблокировать'}
                                </Button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={(page) => setFilter({ page })} />
        </div>
    );
};

export const AdminUserDetail = () => {
    const { id } = useParams();
    const [user, setUser] = useState<AdminUser | null>(null);
    const [form, setForm] = useState<AdminUserUpdatePayload>({});
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        const loadUser = async () => {
            if (!id) return;
            setIsLoading(true);
            try {
                const data = await adminService.getUser(id);
                setUser(data);
                setForm({
                    first_name: data.first_name,
                    last_name: data.last_name,
                    role: data.role,
                    is_active: data.is_active,
                });
            } catch (err) {
                setError(getApiErrorMessage(err));
            } finally {
                setIsLoading(false);
            }
        };

        void loadUser();
    }, [id]);

    const submit = async (event: FormEvent) => {
        event.preventDefault();
        if (!id) return;
        setIsSaving(true);
        setError('');
        setSuccess('');
        try {
            const updated = await adminService.updateUser(id, form);
            setUser(updated);
            setSuccess('Пользователь обновлён.');
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) return <Loader />;
    if (!user) return <EmptyState title="Пользователь не найден" variant="error" />;

    return (
        <div className={`${styles.page} container`}>
            <div className={styles.header}>
                <div>
                    <h1>{user.email}</h1>
                    <p>Редактирование безопасных полей аккаунта.</p>
                </div>
                <Link to="/admin/users">
                    <Button type="button" variant="secondary">Назад</Button>
                </Link>
            </div>

            {error && <EmptyState title="Не удалось обновить пользователя" description={error} variant="error" />}
            {success && <p className={styles.success}>{success}</p>}

            <section className={styles.panel}>
                <form className={styles.form} onSubmit={(event) => void submit(event)}>
                    <Input label="Имя" value={form.first_name ?? ''} onChange={(event) => setForm({ ...form, first_name: event.target.value })} />
                    <Input label="Фамилия" value={form.last_name ?? ''} onChange={(event) => setForm({ ...form, last_name: event.target.value })} />
                    <label className={styles.field}>
                        <span>Роль</span>
                        <select value={form.role ?? 'student'} onChange={(event) => setForm({ ...form, role: event.target.value as UserRole })}>
                            {roleOptions.map((role) => <option key={role} value={role}>{ROLE_LABELS[role]}</option>)}
                        </select>
                    </label>
                    <label className={styles.field}>
                        <span>Статус</span>
                        <select value={String(form.is_active ?? true)} onChange={(event) => setForm({ ...form, is_active: event.target.value === 'true' })}>
                            <option value="true">Активен</option>
                            <option value="false">Заблокирован</option>
                        </select>
                    </label>
                    <p className={styles.muted}>Флаги staff и superuser защищены backend и не редактируются на этой странице.</p>
                    <div className={styles.formActions}>
                        <Button type="submit" isLoading={isSaving}>Сохранить пользователя</Button>
                    </div>
                </form>
            </section>
        </div>
    );
};
