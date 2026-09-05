import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import CourseCard from '../../components/CourseCard/CourseCard';
import Skeleton from '../../components/Skeleton/Skeleton';
import EmptyState from '../../components/EmptyState/EmptyState';
import Pagination from '../../components/Pagination/Pagination';
import { useCourses } from '../../features/courses/useCourses';
import { courseService } from '../../services/courseService';
import type { Category, CourseLevel } from '../../types/course';
import styles from './Courses.module.css';

const LEVELS: { value: CourseLevel | ''; label: string }[] = [
    { value: '', label: 'Все уровни' },
    { value: 'beginner', label: 'Начинающий' },
    { value: 'junior', label: 'Junior' },
    { value: 'middle', label: 'Middle' },
    { value: 'advanced', label: 'Advanced' },
];

const Courses = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const [categories, setCategories] = useState<Category[]>([]);

    const search = searchParams.get('search') ?? '';
    const category = searchParams.get('category') ?? '';
    const level = (searchParams.get('level') as CourseLevel) ?? '';
    const ordering = searchParams.get('ordering') ?? '-created_at';
    const page = Number(searchParams.get('page') ?? 1);

    const { courses, totalPages, isLoading, error } = useCourses({
        search: search || undefined,
        category: category || undefined,
        level: level || undefined,
        ordering,
        page,
    });

    useEffect(() => {
        courseService.getCategories().then(setCategories).catch(() => setCategories([]));
    }, []);

    const updateParam = (key: string, value: string) => {
        const next = new URLSearchParams(searchParams);
        if (value) {
            next.set(key, value);
        } else {
            next.delete(key);
        }
        if (key !== 'page') {
            next.delete('page'); // сбрасываем страницу только при смене ФИЛЬТРА, не самой страницы
        }
        setSearchParams(next);
    };

    return (
        <div className={`${styles.page} container`}>
            <div className={styles.header}>
                <h1>Каталог курсов</h1>
            </div>

            <div className={styles.controls}>
                <input
                    className={styles.searchInput}
                    placeholder="Поиск по названию курса..."
                    defaultValue={search}
                    onChange={(e) => updateParam('search', e.target.value)}
                />

                <select
                    className={styles.select}
                    value={category}
                    onChange={(e) => updateParam('category', e.target.value)}
                >
                    <option value="">Все категории</option>
                    {categories.map((cat) => (
                        <option key={cat.id} value={cat.slug}>
                            {cat.name}
                        </option>
                    ))}
                </select>

                <select
                    className={styles.select}
                    value={level}
                    onChange={(e) => updateParam('level', e.target.value)}
                >
                    {LEVELS.map((lvl) => (
                        <option key={lvl.value} value={lvl.value}>
                            {lvl.label}
                        </option>
                    ))}
                </select>

                <select
                    className={styles.select}
                    value={ordering}
                    onChange={(e) => updateParam('ordering', e.target.value)}
                >
                    <option value="-created_at">Сначала новые</option>
                    <option value="title">По названию (А-Я)</option>
                    <option value="duration">По длительности</option>
                </select>
            </div>

            {isLoading && (
                <div className={styles.grid}>
                    <Skeleton count={9} />
                </div>
            )}

            {!isLoading && error && <EmptyState title="Ошибка загрузки" description={error} />}

            {!isLoading && !error && courses.length === 0 && (
                <EmptyState title="Курсы не найдены" description="Попробуйте изменить параметры поиска" />
            )}

            {!isLoading && !error && courses.length > 0 && (
                <>
                    <div className={styles.grid}>
                        {courses.map((course) => (
                            <CourseCard key={course.id} course={course} />
                        ))}
                    </div>
                    <Pagination
                        currentPage={page}
                        totalPages={totalPages}
                        onPageChange={(newPage) => updateParam('page', String(newPage))}
                    />
                </>
            )}
        </div>
    );
};

export default Courses;