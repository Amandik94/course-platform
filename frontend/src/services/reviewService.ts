import { api } from './api';
import type { PaginatedResponse } from '../types/common';
import type { CreateReviewPayload, Review, ReviewFilters, UpdateReviewPayload } from '../types/review';

export const reviewService = {
    getCourseReviews: (courseId: number | string, params?: ReviewFilters) =>
        api
            .get<PaginatedResponse<Review>>(`courses/${courseId}/reviews/`, { params })
            .then((res) => res.data),

    getMyReview: (courseId: number | string) =>
        api
            .get<PaginatedResponse<Review>>(`courses/${courseId}/reviews/`, {
                params: { mine: true },
            })
            .then((res) => res.data.results[0] ?? null),

    createReview: (courseId: number | string, payload: CreateReviewPayload) =>
        api
            .post<Review>(`courses/${courseId}/reviews/`, payload)
            .then((res) => res.data),

    updateReview: (reviewId: number | string, payload: UpdateReviewPayload) =>
        api
            .patch<Review>(`reviews/${reviewId}/`, payload)
            .then((res) => res.data),

    deleteReview: (reviewId: number | string) =>
        api.delete(`reviews/${reviewId}/`),
};
