export type QuestionType = 'single' | 'multiple' | 'text';

export interface AnswerOption {
    id: number;
    text: string;
    is_correct?: boolean;
}

export interface QuizQuestion {
    id: number;
    question: string;
    type: QuestionType;
    points: number;
    order: number;
    answers: AnswerOption[];
    text_answer?: string;
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

export interface QuizUpsertPayload {
    title: string;
    description: string;
    passing_score: number;
}

export interface QuestionUpsertPayload {
    question: string;
    type: QuestionType;
    points: number;
    order: number;
    text_answer: string;
}

export interface AnswerUpsertPayload {
    text: string;
    is_correct: boolean;
}
