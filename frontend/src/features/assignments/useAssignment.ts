import { useEffect, useState } from 'react';
import { assignmentService } from '../../services/assignmentService';
import type { AssignmentDetail, AssignmentSubmission } from '../../types/assignment';

export function useAssignment(id: string | undefined) {
    const [assignment, setAssignment] = useState<AssignmentDetail | null>(null);
    const [submission, setSubmission] = useState<AssignmentSubmission | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitError, setSubmitError] = useState<string | null>(null);

    const loadData = () => {
        if (!id) return;
        setIsLoading(true);
        setError(null);
        Promise.all([assignmentService.getAssignment(id), assignmentService.getMySubmission(id)])
            .then(([assignmentData, submissionData]) => {
                setAssignment(assignmentData);
                setSubmission(submissionData);
            })
            .catch(() => setError('Не удалось загрузить задание.'))
            .finally(() => setIsLoading(false));
    };

    useEffect(loadData, [id]);

    const submitSolution = async (code: string) => {
        if (!id) return;
        setIsSubmitting(true);
        setSubmitError(null);
        try {
            const result = await assignmentService.submit(id, code);
            setSubmission(result);
        } catch {
            setSubmitError('Не удалось отправить решение. Попробуйте снова.');
        } finally {
            setIsSubmitting(false);
        }
    };

    return { assignment, submission, isLoading, error, submitSolution, isSubmitting, submitError };
}