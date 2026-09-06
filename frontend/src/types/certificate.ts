export interface Certificate {
    id: number;
    course: number;
    course_title: string;
    certificate_number: string;
    issued_at: string;
    pdf: string | null;
}