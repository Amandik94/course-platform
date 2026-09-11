import { api } from './api';
import type {
    AnswerOption,
    AnswerUpsertPayload,
    QuestionUpsertPayload,
    QuizAnswerDraft,
    QuizAttemptResult,
    QuizDetail,
    QuizQuestion,
    QuizUpsertPayload,
} from '../types/quiz';

export const quizService = {
    getQuiz: (id: number | string) =>
        api.get<QuizDetail>(`quizzes/${id}/`).then((res) => res.data),

    createQuiz: (lessonId: number | string, payload: QuizUpsertPayload) =>
        api.post<QuizDetail>(`lessons/${lessonId}/quiz/`, payload).then((res) => res.data),

    updateQuiz: (id: number | string, payload: Partial<QuizUpsertPayload>) =>
        api.patch<QuizDetail>(`quizzes/${id}/manage/`, payload).then((res) => res.data),

    deleteQuiz: (id: number | string) =>
        api.delete(`quizzes/${id}/manage/`),

    createQuestion: (quizId: number | string, payload: QuestionUpsertPayload) =>
        api.post<QuizQuestion>(`quizzes/${quizId}/questions/`, payload).then((res) => res.data),

    updateQuestion: (questionId: number | string, payload: Partial<QuestionUpsertPayload>) =>
        api.patch<QuizQuestion>(`questions/${questionId}/`, payload).then((res) => res.data),

    deleteQuestion: (questionId: number | string) =>
        api.delete(`questions/${questionId}/`),

    createAnswer: (questionId: number | string, payload: AnswerUpsertPayload) =>
        api.post<AnswerOption>(`questions/${questionId}/answers/`, payload).then((res) => res.data),

    updateAnswer: (answerId: number | string, payload: Partial<AnswerUpsertPayload>) =>
        api.patch<AnswerOption>(`answers/${answerId}/`, payload).then((res) => res.data),

    deleteAnswer: (answerId: number | string) =>
        api.delete(`answers/${answerId}/`),

    submit: (id: number | string, answers: QuizAnswerDraft[]) =>
        api.post<QuizAttemptResult>(`quizzes/${id}/submit/`, { answers }).then((res) => res.data),
};
