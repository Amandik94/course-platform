import { api } from './api';
import type { PaginatedResponse } from '../types/common';
import type {
    Category,
    CourseDetail,
    CourseFilters,
    CourseListItem,
    Section,
    Lesson,
    LessonDetail,
} from '../types/course';

export const courseService = {
    getCourses: (filters: CourseFilters) =>
        api
            .get<PaginatedResponse<CourseListItem>>('courses/', {
                params: filters,
            })
            .then((res) => res.data),

    getCourseById: (id: number | string) =>
        api
            .get<CourseDetail>(`courses/${id}/`)
            .then((res) => res.data),

    getCategories: () =>
        api
            .get<PaginatedResponse<Category>>('categories/')
            .then((res) => res.data.results),

    getCourseSections: (courseId: number | string) =>
        api
            .get<PaginatedResponse<Section>>(
                `courses/${courseId}/sections/`
            )
            .then((res) => res.data.results),

    getSectionLessons: (sectionId: number) =>
        api.get<Lesson[]>(`sections/${sectionId}/lessons/`).then((res) => res.data),

    getLessonById: (lessonId: number | string) =>
        api.get<LessonDetail>(`lessons/${lessonId}/`).then((res) => res.data),

    enroll: (courseId: number | string) =>
        api.post(`courses/${courseId}/enroll/`),
};