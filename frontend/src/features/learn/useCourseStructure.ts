import { useEffect, useState } from 'react';
import { courseService } from '../../services/courseService';
import { progressService } from '../../services/progressService';
import type { Lesson, Section } from '../../types/course';

interface SectionWithLessons extends Section {
    lessons: Lesson[];
}

interface UseCourseStructureResult {
    sections: SectionWithLessons[];
    completedLessonIds: Set<number>;
    isLoading: boolean;
    error: string | null;
    markLessonCompleted: (lessonId: number) => void;
}

export function useCourseStructure(courseId: string | undefined): UseCourseStructureResult {
    const [sections, setSections] = useState<SectionWithLessons[]>([]);
    const [completedLessonIds, setCompletedLessonIds] = useState<Set<number>>(new Set());
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!courseId) return;
        let isCancelled = false;

        const load = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const rawSections = await courseService.getCourseSections(courseId);

                // Догружаем уроки для каждого раздела параллельно (Promise.all),
                // а не последовательно — иначе на курсе с 5 разделами загрузка
                // сайдбара занимала бы в 5 раз больше времени.
                const sectionsWithLessons = await Promise.all(
                    rawSections.map(async (section) => ({
                        ...section,
                        lessons: await courseService.getSectionLessons(section.id),
                    })),
                );

                const progress = await progressService.getMyProgress();
                const completedIds = new Set(
                    progress.filter((p) => p.is_completed).map((p) => p.lesson),
                );

                if (!isCancelled) {
                    setSections(sectionsWithLessons);
                    setCompletedLessonIds(completedIds);
                }
            } catch {
                if (!isCancelled) setError('Не удалось загрузить структуру курса.');
            } finally {
                if (!isCancelled) setIsLoading(false);
            }
        };

        load();
        return () => {
            isCancelled = true;
        };
    }, [courseId]);

    const markLessonCompleted = (lessonId: number) => {
        setCompletedLessonIds((prev) => new Set(prev).add(lessonId));
    };

    return { sections, completedLessonIds, isLoading, error, markLessonCompleted };
}