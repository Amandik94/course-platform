import { api } from './api';
import type { QuizAnswerDraft, QuizAttemptResult, QuizDetail } from '../types/quiz';

export const quizService = {
    getQuiz: (id: number | string) =>
        api.get<QuizDetail>(`quizzes/${id}/`).then((res) => res.data),

    submit: (id: number | string, answers: QuizAnswerDraft[]) =>
        api.post<QuizAttemptResult>(`quizzes/${id}/submit/`, { answers }).then((res) => res.data),
};