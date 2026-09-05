import { useState } from 'react';
import { isAxiosError } from 'axios';
import { courseService } from '../../services/courseService';
import type { ApiError } from '../../types/common';

export function useEnroll() {
    const [isEnrolling, setIsEnrolling] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const enroll = async (courseId: number, onSuccess?: () => void) => {
        setIsEnrolling(true);
        setError(null);
        try {
            await courseService.enroll(courseId);
            onSuccess?.();
        } catch (err) {
            if (isAxiosError<ApiError>(err) && typeof err.response?.data.detail === 'string') {
                setError(err.response.data.detail);
            } else {
                setError('Не удалось записаться на курс.');
            }
        } finally {
            setIsEnrolling(false);
        }
    };

    return { enroll, isEnrolling, error };
}