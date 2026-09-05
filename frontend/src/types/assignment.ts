export type SubmissionStatus = 'pending' | 'accepted' | 'revision';

export interface AssignmentDetail {
    id: number;
    lesson: number;
    title: string;
    description: string;
    starter_code: string;
    max_score: number;
    deadline: string | null;
}

export interface AssignmentSubmission {
    id: number;
    assignment: number;
    student: number;
    student_name: string;
    code: string;
    status: SubmissionStatus;
    score: number | null;
    teacher_comment: string;
    created_at: string;
    updated_at: string;
}