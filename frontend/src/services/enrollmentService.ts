import { api } from './api';
import type { PaginatedResponse } from '../types/common';
import type { Enrollment } from '../types/enrollment';

export const enrollmentService = {
    getMyCourses: () =>
        api.get<PaginatedResponse<Enrollment>>('my-courses/').then((res) => res.data),
};