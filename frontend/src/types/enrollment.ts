import type { CourseListItem } from './course';

export interface Enrollment {
    id: number;
    course: CourseListItem;
    progress: number;
    next_lesson_id: number | null;
    created_at: string;
    completed_at: string | null;
}