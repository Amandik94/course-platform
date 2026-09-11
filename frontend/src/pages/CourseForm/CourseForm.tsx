import { type FormEvent, useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import Button from '../../components/Button/Button';
import EmptyState from '../../components/EmptyState/EmptyState';
import Input from '../../components/Input/Input';
import Loader from '../../components/Loader/Loader';
import { courseService } from '../../services/courseService';
import type { Category, CourseLevel, CourseStatus, CourseUpsertPayload } from '../../types/course';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';
import styles from './CourseForm.module.css';

const EMPTY_FORM: CourseUpsertPayload = {
    title: '',
    description: '',
    short_description: '',
    category_id: 0,
    level: 'beginner',
    duration: 1,
    status: 'draft',
};

const CourseForm = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const isEdit = Boolean(id);
    const [categories, setCategories] = useState<Category[]>([]);
    const [form, setForm] = useState<CourseUpsertPayload>(EMPTY_FORM);
    const [isLoading, setIsLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        const load = async () => {
            setIsLoading(true);
            setError('');
            try {
                const [categoryItems, course] = await Promise.all([
                    courseService.getCategories(),
                    id ? courseService.getCourseById(id) : Promise.resolve(null),
                ]);
                setCategories(categoryItems);
                if (course) {
                    setForm({
                        title: course.title,
                        description: course.description,
                        short_description: course.short_description,
                        category_id: course.category.id,
                        level: course.level,
                        duration: course.duration,
                        status: course.status,
                    });
                } else if (categoryItems[0]) {
                    setForm((current) => ({ ...current, category_id: categoryItems[0].id }));
                }
            } catch (err) {
                setError(getApiErrorMessage(err));
            } finally {
                setIsLoading(false);
            }
        };

        void load();
    }, [id]);

    const updateField = <K extends keyof CourseUpsertPayload>(key: K, value: CourseUpsertPayload[K]) => {
        setForm((current) => ({ ...current, [key]: value }));
    };

    const validate = () => {
        if (!form.title.trim()) return 'Title is required.';
        if (!form.short_description.trim()) return 'Short description is required.';
        if (!form.description.trim()) return 'Description is required.';
        if (!form.category_id) return 'Category is required.';
        if (form.duration <= 0) return 'Duration must be greater than zero.';
        return '';
    };

    const handleSubmit = async (event: FormEvent) => {
        event.preventDefault();
        const validationError = validate();
        if (validationError) {
            setError(validationError);
            return;
        }

        setIsSubmitting(true);
        setError('');
        setSuccess('');
        try {
            const saved = id
                ? await courseService.updateCourse(id, form)
                : await courseService.createCourse(form);
            setSuccess(id ? 'Course updated.' : 'Course created.');
            navigate(`/teacher/courses/${saved.id}/manage`);
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSubmitting(false);
        }
    };

    if (isLoading) return <Loader />;

    return (
        <div className={styles.page}>
            <div className={styles.header}>
                <div>
                    <h1>{isEdit ? 'Edit course' : 'New course'}</h1>
                    <p>Ownership is assigned by backend from your authenticated account.</p>
                </div>
                <Link to="/teacher/courses">
                    <Button type="button" variant="secondary">Back</Button>
                </Link>
            </div>

            {error && <EmptyState title="Course was not saved" description={error} variant="error" />}
            {success && <p className={styles.success}>{success}</p>}

            <form className={styles.form} onSubmit={(event) => void handleSubmit(event)}>
                <Input label="Title" value={form.title} onChange={(event) => updateField('title', event.target.value)} />
                <Input
                    label="Short description"
                    value={form.short_description}
                    onChange={(event) => updateField('short_description', event.target.value)}
                />
                <label className={styles.field}>
                    <span>Description</span>
                    <textarea
                        value={form.description}
                        onChange={(event) => updateField('description', event.target.value)}
                        rows={6}
                    />
                </label>
                <div className={styles.row}>
                    <label className={styles.field}>
                        <span>Category</span>
                        <select
                            value={form.category_id}
                            onChange={(event) => updateField('category_id', Number(event.target.value))}
                        >
                            <option value={0}>Select category</option>
                            {categories.map((category) => (
                                <option key={category.id} value={category.id}>{category.name}</option>
                            ))}
                        </select>
                    </label>
                    <label className={styles.field}>
                        <span>Level</span>
                        <select
                            value={form.level}
                            onChange={(event) => updateField('level', event.target.value as CourseLevel)}
                        >
                            <option value="beginner">Beginner</option>
                            <option value="junior">Junior</option>
                            <option value="middle">Middle</option>
                            <option value="advanced">Advanced</option>
                        </select>
                    </label>
                    <label className={styles.field}>
                        <span>Status</span>
                        <select
                            value={form.status}
                            onChange={(event) => updateField('status', event.target.value as CourseStatus)}
                        >
                            <option value="draft">Draft</option>
                            <option value="published">Published</option>
                            <option value="archived">Archived</option>
                        </select>
                    </label>
                    <Input
                        label="Duration"
                        type="number"
                        min={1}
                        value={form.duration}
                        onChange={(event) => updateField('duration', Number(event.target.value))}
                    />
                </div>
                <Button type="submit" isLoading={isSubmitting}>{isEdit ? 'Save course' : 'Create course'}</Button>
            </form>
        </div>
    );
};

export default CourseForm;
