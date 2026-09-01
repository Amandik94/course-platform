// Общие типы, переиспользуемые в нескольких доменах.
// Специфичные типы (Course, User и т.д.) появятся в types/course.ts,
// types/user.ts и т.д. по мере разработки соответствующих features.

export interface PaginatedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}

export interface ApiError {
    detail?: string;
    [field: string]: string[] | string | undefined;
}