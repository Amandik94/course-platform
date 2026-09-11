import { type FormEvent, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import Button from '../../components/Button/Button';
import EmptyState from '../../components/EmptyState/EmptyState';
import Input from '../../components/Input/Input';
import Loader from '../../components/Loader/Loader';
import { courseService } from '../../services/courseService';
import type { Category } from '../../types/course';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';
import styles from './AdminCategories.module.css';

const EMPTY_CATEGORY = { name: '', description: '' };

const AdminCategories = () => {
    const [categories, setCategories] = useState<Category[]>([]);
    const [form, setForm] = useState(EMPTY_CATEGORY);
    const [editingId, setEditingId] = useState<number | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const loadCategories = async () => {
        setIsLoading(true);
        setError('');
        try {
            setCategories(await courseService.getCategories());
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        queueMicrotask(() => {
            void loadCategories();
        });
    }, []);

    const submit = async (event: FormEvent) => {
        event.preventDefault();
        if (!form.name.trim()) {
            setError('Category name is required.');
            return;
        }
        setIsSaving(true);
        setError('');
        setSuccess('');
        try {
            if (editingId) {
                await courseService.updateCategory(editingId, form);
                setSuccess('Category updated.');
            } else {
                await courseService.createCategory(form);
                setSuccess('Category created.');
            }
            setForm(EMPTY_CATEGORY);
            setEditingId(null);
            await loadCategories();
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    const editCategory = (category: Category) => {
        setEditingId(category.id);
        setForm({ name: category.name, description: category.description });
    };

    const deleteCategory = async (category: Category) => {
        if (!window.confirm(`Delete category "${category.name}"?`)) return;
        setIsSaving(true);
        setError('');
        setSuccess('');
        try {
            await courseService.deleteCategory(category.id);
            setSuccess('Category deleted.');
            await loadCategories();
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
                    <h1>Admin Categories</h1>
                    <p>Manage catalog categories used by courses.</p>
                </div>
                <Link to="/dashboard/admin">
                    <Button type="button" variant="secondary">Dashboard</Button>
                </Link>
            </div>

            {error && <EmptyState title="Category action failed" description={error} variant="error" />}
            {success && <p className={styles.success}>{success}</p>}

            <div className={styles.columns}>
                <section className={styles.panel}>
                    <h2>{editingId ? 'Edit Category' : 'Create Category'}</h2>
                    <form className={styles.form} onSubmit={(event) => void submit(event)}>
                        <Input label="Name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
                        <label className={styles.field}>
                            <span>Description</span>
                            <textarea rows={4} value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} />
                        </label>
                        <div className={styles.actions}>
                            <Button type="submit" isLoading={isSaving}>{editingId ? 'Save category' : 'Create category'}</Button>
                            {editingId && (
                                <Button type="button" variant="secondary" onClick={() => { setEditingId(null); setForm(EMPTY_CATEGORY); }}>
                                    Cancel
                                </Button>
                            )}
                        </div>
                    </form>
                </section>

                <section className={styles.panel}>
                    <h2>Categories</h2>
                    {categories.length === 0 ? (
                        <EmptyState title="No categories" />
                    ) : (
                        <div className={styles.list}>
                            {categories.map((category) => (
                                <div key={category.id} className={styles.row}>
                                    <div>
                                        <strong>{category.name}</strong>
                                        <p>{category.description || 'No description'}</p>
                                    </div>
                                    <div className={styles.actions}>
                                        <Button type="button" variant="secondary" onClick={() => editCategory(category)}>Edit</Button>
                                        <Button type="button" variant="danger" disabled={isSaving} onClick={() => void deleteCategory(category)}>Delete</Button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </section>
            </div>
        </div>
    );
};

export default AdminCategories;
