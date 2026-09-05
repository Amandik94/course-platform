import { api } from './api';
import type { CompleteLessonResponse, LessonProgress } from '../types/progress';

export const progressService = {
    getMyProgress: () =>
        api.get<LessonProgress[]>('progress/').then((res) => res.data),

    completeLesson: (lessonId: number) =>
        api.post<CompleteLessonResponse>(`lessons/${lessonId}/complete/`).then((res) => res.data),
};