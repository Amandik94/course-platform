export interface LessonProgress {
    id: number;
    lesson: number;
    lesson_title: string;
    is_completed: boolean;
    completed_at: string | null;
}

export interface CompleteLessonResponse {
    lesson_progress: LessonProgress;
    enrollment_progress: number;
    course_completed: boolean;
}