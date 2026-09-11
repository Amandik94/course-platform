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
            setSuccess(updated.is_active ? 'User unblocked.' : 'User blocked.');
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) return <Loader />;

    return (
        <div className={styles.page}>
            <div className={styles.header}>
                <div>
                    <h1>Admin Users</h1>
                    <p>Review accounts, roles and access state.</p>
                </div>
                <Link to="/dashboard/admin">
                    <Button type="button" variant="secondary">Dashboard</Button>
                </Link>
            </div>

            <div className={styles.filters}>
                <Input
                    label="Search"
                    value={filters.search ?? ''}
                    onChange={(event) => setFilter({ search: event.target.value })}
                />
                <label className={styles.field}>
                    <span>Role</span>
                    <select value={filters.role ?? ''} onChange={(event) => setFilter({ role: event.target.value as UserRole | '' })}>
                        <option value="">All roles</option>
                        {roleOptions.map((role) => <option key={role} value={role}>{role}</option>)}
                    </select>
                </label>
                <label className={styles.field}>
                    <span>Status</span>
                    <select value={filters.is_active ?? ''} onChange={(event) => setFilter({ is_active: event.target.value })}>
                        <option value="">All</option>
                        <option value="true">Active</option>
                        <option value="false">Blocked</option>
                    </select>
                </label>
            </div>

            {error && <EmptyState title="Admin users failed" description={error} variant="error" />}
            {success && <p className={styles.success}>{success}</p>}

            {users.length === 0 && !error ? (
                <EmptyState title="No users" />
            ) : (
                <div className={styles.table}>
                    <div className={styles.tableHead}>
                        <span>User</span>
                        <span>Name</span>
                        <span>Role</span>
                        <span>Status</span>
                        <span>Actions</span>
                    </div>
                    {users.map((user) => (
                        <div key={user.id} className={styles.tableRow}>
                            <span>{user.email}</span>
                            <span>{user.full_name || '-'}</span>
                            <span>{user.role}</span>
                            <span>{user.is_active ? 'Active' : 'Blocked'}</span>
                            <div className={styles.actions}>
                                <Link to={`/admin/users/${user.id}`}>
                                    <Button type="button" variant="secondary">Open</Button>
                                </Link>
                                <Button
                                    type="button"
                                    variant={user.is_active ? 'danger' : 'secondary'}
                                    disabled={isSaving}
                                    onClick={() => void toggleActive(user)}
                                >
                                    {user.is_active ? 'Block' : 'Unblock'}
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
            setSuccess('User updated.');
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) return <Loader />;
    if (!user) return <EmptyState title="User not found" variant="error" />;

    return (
        <div className={styles.page}>
            <div className={styles.header}>
                <div>
                    <h1>{user.email}</h1>
                    <p>Manage safe account fields.</p>
                </div>
                <Link to="/admin/users">
                    <Button type="button" variant="secondary">Back</Button>
                </Link>
            </div>

            {error && <EmptyState title="Update failed" description={error} variant="error" />}
            {success && <p className={styles.success}>{success}</p>}

            <section className={styles.panel}>
                <form className={styles.form} onSubmit={(event) => void submit(event)}>
                    <Input label="First name" value={form.first_name ?? ''} onChange={(event) => setForm({ ...form, first_name: event.target.value })} />
                    <Input label="Last name" value={form.last_name ?? ''} onChange={(event) => setForm({ ...form, last_name: event.target.value })} />
                    <label className={styles.field}>
                        <span>Role</span>
                        <select value={form.role ?? 'student'} onChange={(event) => setForm({ ...form, role: event.target.value as UserRole })}>
                            {roleOptions.map((role) => <option key={role} value={role}>{role}</option>)}
                        </select>
                    </label>
                    <label className={styles.field}>
                        <span>Status</span>
                        <select value={String(form.is_active ?? true)} onChange={(event) => setForm({ ...form, is_active: event.target.value === 'true' })}>
                            <option value="true">Active</option>
                            <option value="false">Blocked</option>
                        </select>
                    </label>
                    <p className={styles.muted}>Staff and superuser flags are protected by backend and cannot be edited here.</p>
                    <div className={styles.formActions}>
                        <Button type="submit" isLoading={isSaving}>Save user</Button>
                    </div>
                </form>
            </section>
        </div>
    );
};
