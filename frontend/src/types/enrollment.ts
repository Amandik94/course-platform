import type { CourseListItem } from './course';

export interface Enrollment {
    id: number;
    course: CourseListItem;
    progress: number;
    created_at: string;
    completed_at: string | null;
}