import { useState } from 'react';
import { progressService } from '../../services/progressService';
import type { CompleteLessonResponse } from '../../types/progress';

export function useLessonProgress() {
    const [isCompleting, setIsCompleting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const completeLesson = async (
        lessonId: number,
        onSuccess?: (result: CompleteLessonResponse) => void,
    ) => {
        setIsCompleting(true);
        setError(null);
        try {
            const result = await progressService.completeLesson(lessonId);
            onSuccess?.(result);
        } catch {
            setError('Не удалось отметить урок пройденным. Попробуйте снова.');
        } finally {
            setIsCompleting(false);
        }
    };

    return { completeLesson, isCompleting, error };
}