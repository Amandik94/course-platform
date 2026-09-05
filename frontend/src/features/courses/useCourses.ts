import { useEffect, useState } from 'react';
import { courseService } from '../../services/courseService';
import type { CourseFilters, CourseListItem } from '../../types/course';

interface UseCoursesResult {
    courses: CourseListItem[];
    count: number;
    totalPages: number;
    isLoading: boolean;
    error: string | null;
}

const PAGE_SIZE = 9; // соответствует backend REST_FRAMEWORK['PAGE_SIZE']

export function useCourses(filters: CourseFilters): UseCoursesResult {
    const [courses, setCourses] = useState<CourseListItem[]>([]);
    const [count, setCount] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let isCancelled = false; // защита от "гонки" ответов при быстрой смене фильтров

        const fetchCourses = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const data = await courseService.getCourses(filters);
                if (!isCancelled) {
                    setCourses(data.results);
                    setCount(data.count);
                }
            } catch {
                if (!isCancelled) {
                    setError('Не удалось загрузить курсы. Попробуйте позже.');
                }
            } finally {
                if (!isCancelled) {
                    setIsLoading(false);
                }
            }
        };

        fetchCourses();

        return () => {
            isCancelled = true;
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [JSON.stringify(filters)]);

    return { courses, count, totalPages: Math.ceil(count / PAGE_SIZE), isLoading, error };
}