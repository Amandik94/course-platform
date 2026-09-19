import { api } from './api';
import type { PaginatedResponse } from '../types/common';
import type {
    Category,
    CourseDetail,
    CourseFilters,
    CourseListItem,
    Section,
    LessonDetail,
    CourseUpsertPayload,
    LessonUpsertPayload,
    SectionUpsertPayload,
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

    createCourse: (payload: CourseUpsertPayload) =>
        api.post<CourseDetail>('courses/', payload).then((res) => res.data),

    updateCourse: (id: number | string, payload: Partial<CourseUpsertPayload>) =>
        api.patch<CourseDetail>(`courses/${id}/`, payload).then((res) => res.data),

    deleteCourse: (id: number | string) =>
        api.delete(`courses/${id}/`),

    getCategories: () =>
        api
            .get<PaginatedResponse<Category>>('categories/')
            .then((res) => res.data.results),

    createCategory: (payload: Pick<Category, 'name' | 'description'>) =>
        api.post<Category>('categories/', payload).then((res) => res.data),

    updateCategory: (id: number | string, payload: Partial<Pick<Category, 'name' | 'description'>>) =>
        api.patch<Category>(`categories/${id}/`, payload).then((res) => res.data),

    deleteCategory: (id: number | string) =>
        api.delete(`categories/${id}/`),

    getCourseSections: (courseId: number | string) =>
        api
            .get<PaginatedResponse<Section>>(
                `courses/${courseId}/sections/`
            )
            .then((res) => res.data.results),

    createSection: (courseId: number | string, payload: SectionUpsertPayload) =>
        api.post<Section>(`courses/${courseId}/sections/`, payload).then((res) => res.data),

    updateSection: (sectionId: number, payload: Partial<SectionUpsertPayload>) =>
        api.patch<Section>(`sections/${sectionId}/`, payload).then((res) => res.data),

    deleteSection: (sectionId: number) =>
        api.delete(`sections/${sectionId}/`),

    getSectionLessons: (sectionId: number) =>
        api.get<LessonDetail[]>(`sections/${sectionId}/lessons/`).then((res) => res.data),

    getLessonById: (lessonId: number | string) =>
        api.get<LessonDetail>(`lessons/${lessonId}/`).then((res) => res.data),

    createLesson: (sectionId: number, payload: LessonUpsertPayload) =>
        api.post<LessonDetail>(`sections/${sectionId}/lessons/`, payload).then((res) => res.data),

    updateLesson: (lessonId: number, payload: Partial<LessonUpsertPayload>) =>
        api.patch<LessonDetail>(`lessons/${lessonId}/`, payload).then((res) => res.data),

    deleteLesson: (lessonId: number) =>
        api.delete(`lessons/${lessonId}/`),

    enroll: (courseId: number | string) =>
        api.post(`courses/${courseId}/enroll/`),
};
