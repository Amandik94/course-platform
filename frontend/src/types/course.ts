export type CourseLevel = 'beginner' | 'junior' | 'middle' | 'advanced';
export type CourseStatus = 'draft' | 'published' | 'archived';

export interface Category {
    id: number;
    name: string;
    slug: string;
    description: string;
}

// Соответствует CourseListSerializer на бэкенде (Этап 4)
export interface CourseListItem {
    id: number;
    title: string;
    slug: string;
    short_description: string;
    cover: string | null;
    category: Category;
    teacher_name: string;
    level: CourseLevel;
    duration: number;
    lessons_count: number;
    status: CourseStatus;
}

export interface Teacher {
    id: number;
    full_name: string;
    email: string;
    avatar: string | null;
}

// Соответствует CourseDetailSerializer
export interface CourseDetail {
    id: number;
    title: string;
    slug: string;
    description: string;
    short_description: string;
    cover: string | null;
    category: Category;
    teacher: Teacher;
    level: CourseLevel;
    duration: number;
    status: CourseStatus;
    lessons_count: number;
    is_enrolled: boolean;
    created_at: string;
    updated_at: string;
}

export interface Section {
    id: number;
    course: number;
    title: string;
    description: string;
    order: number;
}

export interface Lesson {
    id: number;
    title: string;
    type: 'text' | 'video' | 'assignment' | 'quiz' | 'file' | 'project';
    duration: number;
    order: number;
    is_free: boolean;
}

// расширяем Lesson полным контентом для страницы Learn
export interface LessonDetail extends Lesson {
    section: number;
    description: string;
    content: string;
    video_url: string;
    assignment_id: number | null;
    quiz_id: number | null;
}

export interface CourseFilters {
    search?: string;
    category?: string;
    level?: CourseLevel | '';
    ordering?: string;
    page?: number;
}