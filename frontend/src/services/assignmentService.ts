import { api } from './api';
import type { PaginatedResponse } from '../types/common';
import type {
    AssignmentDetail,
    AssignmentSubmission,
    AssignmentUpsertPayload,
    SubmissionReviewPayload,
} from '../types/assignment';


export const assignmentService = {
    getAssignment: (id: number | string) =>
        api.get<AssignmentDetail>(`assignments/${id}/`).then((res) => res.data),

    createAssignment: (lessonId: number | string, payload: AssignmentUpsertPayload) =>
        api.post<AssignmentDetail>(`lessons/${lessonId}/assignment/`, payload).then((res) => res.data),

    updateAssignment: (id: number | string, payload: Partial<AssignmentUpsertPayload>) =>
        api.patch<AssignmentDetail>(`assignments/${id}/manage/`, payload).then((res) => res.data),

    deleteAssignment: (id: number | string) =>
        api.delete(`assignments/${id}/manage/`),

    getSubmissions: (id: number | string) =>
        api
            .get<PaginatedResponse<AssignmentSubmission>>(`assignments/${id}/submissions/`)
            .then((res) => res.data.results),

    reviewSubmission: (id: number | string, payload: SubmissionReviewPayload) =>
        api.patch<AssignmentSubmission>(`submissions/${id}/`, payload).then((res) => res.data),

    // возвращает null, если решения ещё нет (404 — ожидаемый штатный случай)
    getMySubmission: async (id: number | string): Promise<AssignmentSubmission | null> => {
        try {
            const res = await api.get<AssignmentSubmission>(`assignments/${id}/my-submission/`);
            return res.data;
        } catch {
            return null;
        }
    },

    submit: (id: number | string, code: string) =>
        api.post<AssignmentSubmission>(`assignments/${id}/submit/`, { code }).then((res) => res.data),
};
