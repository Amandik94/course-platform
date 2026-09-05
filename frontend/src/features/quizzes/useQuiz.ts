import { useEffect, useState } from 'react';
import { quizService } from '../../services/quizService';
import type { QuizAnswerDraft, QuizAttemptResult, QuizDetail } from '../../types/quiz';

export function useQuiz(id: string | undefined) {
    const [quiz, setQuiz] = useState<QuizDetail | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<QuizAttemptResult | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitError, setSubmitError] = useState<string | null>(null);

    useEffect(() => {
        if (!id) return;
        setIsLoading(true);
        quizService
            .getQuiz(id)
            .then(setQuiz)
            .catch(() => setError('Не удалось загрузить тест.'))
            .finally(() => setIsLoading(false));
    }, [id]);

    const submitAnswers = async (answers: QuizAnswerDraft[]) => {
        if (!id) return;
        setIsSubmitting(true);
        setSubmitError(null);
        try {
            const data = await quizService.submit(id, answers);
            setResult(data);
        } catch {
            setSubmitError('Не удалось отправить ответы. Попробуйте снова.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return { quiz, isLoading, error, result, submitAnswers, isSubmitting, submitError };
}