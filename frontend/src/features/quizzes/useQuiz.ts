import { useEffect, useState } from 'react';
import { quizService } from '../../services/quizService';
import type {
    QuizAnswerDraft,
    QuizAttemptResult,
    QuizDetail,
} from '../../types/quiz';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';

export function useQuiz(id: string | undefined) {
    const [quiz, setQuiz] = useState<QuizDetail | null>(null);
    const [loadedId, setLoadedId] = useState<string | undefined>();
    const [error, setError] = useState<string | null>(null);

    const [result, setResult] = useState<QuizAttemptResult | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitError, setSubmitError] = useState<string | null>(null);

    useEffect(() => {
        if (!id) return;

        let cancelled = false;

        const loadQuiz = async () => {
            try {
                const data = await quizService.getQuiz(id);

                if (cancelled) return;

                setQuiz(data);
                setError(null);
                setLoadedId(id);
            } catch (err) {
                if (cancelled) return;

                setError(getApiErrorMessage(err));
                setLoadedId(id);
            }
        };

        loadQuiz();

        return () => {
            cancelled = true;
        };
    }, [id]);

    const isLoading = Boolean(id && loadedId !== id);

    const submitAnswers = async (answers: QuizAnswerDraft[]) => {
        if (!id) return;

        setIsSubmitting(true);
        setSubmitError(null);

        try {
            const data = await quizService.submit(id, answers);
            setResult(data);
        } catch (err) {
            setSubmitError(getApiErrorMessage(err));
        } finally {
            setIsSubmitting(false);
        }
    };

    return {
        quiz,
        isLoading,
        error,
        result,
        submitAnswers,
        isSubmitting,
        submitError,
    };
}