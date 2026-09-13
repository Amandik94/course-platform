export type NotificationType =
    | 'course'
    | 'lesson'
    | 'assignment'
    | 'submission'
    | 'quiz'
    | 'certificate'
    | 'system';

export interface Notification {
    id: number;
    type: NotificationType;
    title: string;
    message: string;
    is_read: boolean;
    link: string | null;
    created_at: string;
    read_at: string | null;
}

export interface UnreadCountResponse {
    count: number;
}
