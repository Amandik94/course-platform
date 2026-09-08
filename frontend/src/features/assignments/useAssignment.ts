import { useEffect, useState } from 'react';
import { assignmentService } from '../../services/assignmentService';
import type {
    AssignmentDetail,
    AssignmentSubmission,
} from '../../types/assignment';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';

export function useAssignment(id: string | undefined) {
    const [assignment, setAssignment] =
        useState<AssignmentDetail | null>(null);

    const [submission, setSubmission] =
        useState<AssignmentSubmission | null>(null);

    const [loadedId, setLoadedId] = useState<string | undefined>();

    const [error, setError] = useState<string | null>(null);

    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitError, setSubmitError] = useState<string | null>(null);

    useEffect(() => {
        if (!id) return;

        let cancelled = false;

        const loadData = async () => {
            try {
                const [assignmentData, submissionData] = await Promise.all([
                    assignmentService.getAssignment(id),
                    assignmentService.getMySubmission(id),
                ]);

                if (cancelled) return;

                setAssignment(assignmentData);
                setSubmission(submissionData);
                setError(null);
                setLoadedId(id);
            } catch (err) {
                if (cancelled) return;

                setError(getApiErrorMessage(err));
                setLoadedId(id);
            }
        };

        loadData();

        return () => {
            cancelled = true;
        };
    }, [id]);

    const isLoading = Boolean(id && loadedId !== id);

    const submitSolution = async (code: string) => {
        if (!id) return;

        setIsSubmitting(true);
        setSubmitError(null);

        try {
            const result = await assignmentService.submit(id, code);
            setSubmission(result);
        } catch (err) {
            setSubmitError(getApiErrorMessage(err));
        } finally {
            setIsSubmitting(false);
        }
    };

    return {
        assignment,
        submission,
        isLoading,
        error,
        submitSolution,
        isSubmitting,
        submitError,
    };
}