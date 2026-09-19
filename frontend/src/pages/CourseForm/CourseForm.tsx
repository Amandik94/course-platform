import { type FormEvent, useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import Button from '../../components/Button/Button';
import EmptyState from '../../components/EmptyState/EmptyState';
import Input from '../../components/Input/Input';
import Loader from '../../components/Loader/Loader';
import { courseService } from '../../services/courseService';
import type { Category, CourseLevel, CourseStatus, CourseUpsertPayload } from '../../types/course';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';
import { COURSE_LEVEL_LABELS, COURSE_STATUS_LABELS } from '../../utils/labels';
import styles from './CourseForm.module.css';

const EMPTY_FORM: CourseUpsertPayload = {
    title: '',
    description: '',
    short_description: '',
    category_id: 0,
    level: 'beginner',
    duration: 1,
    price: '0.00',
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
                        price: course.price,
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
        if (!form.title.trim()) return 'Название обязательно.';
        if (!form.short_description.trim()) return 'Краткое описание обязательно.';
        if (!form.description.trim()) return 'Описание обязательно.';
        if (!form.category_id) return 'Категория обязательна.';
        if (form.duration <= 0) return 'Продолжительность должна быть больше нуля.';
        if (Number(form.price) < 0) return 'Цена не может быть отрицательной.';
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
            setSuccess(id ? 'Курс обновлён.' : 'Курс создан.');
            navigate(`/teacher/courses/${saved.id}/manage`);
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSubmitting(false);
        }
    };

    if (isLoading) return <Loader />;

    return (
        <div className={`${styles.page} container`}>
            <div className={styles.header}>
                <div>
                    <h1>{isEdit ? 'Редактировать курс' : 'Новый курс'}</h1>
                    <p>Преподаватель назначается backend по вашему аккаунту.</p>
                </div>
                <Link to="/teacher/courses">
                    <Button type="button" variant="secondary">Назад</Button>
                </Link>
            </div>

            {error && <EmptyState title="Курс не сохранён" description={error} variant="error" />}
            {success && <p className={styles.success}>{success}</p>}

            <form className={styles.form} onSubmit={(event) => void handleSubmit(event)}>
                <Input label="Название" value={form.title} onChange={(event) => updateField('title', event.target.value)} />
                <Input
                    label="Краткое описание"
                    value={form.short_description}
                    onChange={(event) => updateField('short_description', event.target.value)}
                />
                <label className={styles.field}>
                    <span>Описание</span>
                    <textarea
                        value={form.description}
                        onChange={(event) => updateField('description', event.target.value)}
                        rows={6}
                    />
                </label>
                <div className={styles.row}>
                    <label className={styles.field}>
                        <span>Категория</span>
                        <select
                            value={form.category_id}
                            onChange={(event) => updateField('category_id', Number(event.target.value))}
                        >
                            <option value={0}>Выберите категорию</option>
                            {categories.map((category) => (
                                <option key={category.id} value={category.id}>{category.name}</option>
                            ))}
                        </select>
                    </label>
                    <label className={styles.field}>
                        <span>Уровень</span>
                        <select
                            value={form.level}
                            onChange={(event) => updateField('level', event.target.value as CourseLevel)}
                        >
                            <option value="beginner">{COURSE_LEVEL_LABELS.beginner}</option>
                            <option value="junior">{COURSE_LEVEL_LABELS.junior}</option>
                            <option value="middle">{COURSE_LEVEL_LABELS.middle}</option>
                            <option value="advanced">{COURSE_LEVEL_LABELS.advanced}</option>
                        </select>
                    </label>
                    <label className={styles.field}>
                        <span>Статус</span>
                        <select
                            value={form.status}
                            onChange={(event) => updateField('status', event.target.value as CourseStatus)}
                        >
                            <option value="draft">{COURSE_STATUS_LABELS.draft}</option>
                            <option value="published">{COURSE_STATUS_LABELS.published}</option>
                            <option value="archived">{COURSE_STATUS_LABELS.archived}</option>
                        </select>
                    </label>
                    <Input
                        label="Продолжительность"
                        type="number"
                        min={1}
                        value={form.duration}
                        onChange={(event) => updateField('duration', Number(event.target.value))}
                    />
                    <Input
                        label="Цена, ₸"
                        type="number"
                        min={0}
                        step="100"
                        value={form.price}
                        onChange={(event) => updateField('price', event.target.value)}
                    />
                </div>
                <Button type="submit" isLoading={isSubmitting}>{isEdit ? 'Сохранить курс' : 'Создать курс'}</Button>
            </form>
        </div>
    );
};

export default CourseForm;
