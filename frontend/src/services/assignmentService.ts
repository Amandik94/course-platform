import { api } from './api';
import type { AssignmentDetail, AssignmentSubmission } from '../types/assignment';

export const assignmentService = {
    getAssignment: (id: number | string) =>
        api.get<AssignmentDetail>(`assignments/${id}/`).then((res) => res.data),

    // возвращает null, если решения ещё нет (404 — ожидаемый штатный случай)
    getMySubmission: async (id: number | string): Promise<AssignmentSubmission | null> => {
        try {
            const res = await api.get<AssignmentSubmission>(`assignments/${id}/my-submission/`);
            return res.data;
        } catch (err) {
            return null;
        }
    },

    submit: (id: number | string, code: string) =>
        api.post<AssignmentSubmission>(`assignments/${id}/submit/`, { code }).then((res) => res.data),
};