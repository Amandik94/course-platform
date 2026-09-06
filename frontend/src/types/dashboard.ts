export interface QuizResultItem {
    quiz_title: string;
    score: number;
    passed: boolean;
    created_at: string;
}

export interface StudentDashboard {
    active_courses_count: number;
    completed_courses_count: number;
    average_progress: number;
    certificates_count: number;
    recent_quiz_results: QuizResultItem[];
}

export interface TeacherDashboardCourse {
    id: number;
    title: string;
    students_count: number;
    status: string;
}

export interface TeacherDashboard {
    courses_count: number;
    students_count: number;
    pending_submissions_count: number;
    courses: TeacherDashboardCourse[];
}

export interface AdminDashboard {
    users_count: number;
    students_count: number;
    teachers_count: number;
    courses_count: number;
    active_courses_count: number;
    completed_enrollments_count: number;
    average_progress: number;
}