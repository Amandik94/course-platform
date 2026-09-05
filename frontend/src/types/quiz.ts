export type QuestionType = 'single' | 'multiple' | 'text';

export interface AnswerOption {
    id: number;
    text: string;
}

export interface QuizQuestion {
    id: number;
    question: string;
    type: QuestionType;
    points: number;
    order: number;
    answers: AnswerOption[];
}

export interface QuizDetail {
    id: number;
    lesson: number;
    title: string;
    description: string;
    passing_score: number;
    questions: QuizQuestion[];
}

// то, что студент собрал перед отправкой (внутреннее состояние формы)
export interface QuizAnswerDraft {
    question_id: number;
    answer_id?: number;
    answer_ids?: number[];
    text?: string;
}

export interface QuizAttemptResult {
    id: number;
    quiz: number;
    score: number;
    passed: boolean;
    answers_snapshot: Record<string, { submitted: Partial<QuizAnswerDraft>; is_correct: boolean }>;
    created_at: string;
}
