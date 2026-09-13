import { describe, expect, it, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useCourses } from './useCourses';
import { courseService } from '../../services/courseService';

vi.mock('../../services/courseService', () => ({
    courseService: {
        getCourses: vi.fn(),
    },
}));

describe('useCourses', () => {
    it('loads courses and updates state', async () => {
        vi.mocked(courseService.getCourses).mockResolvedValue({
            count: 1, next: null, previous: null,
            results: [{
                id: 1, title: 'Django Course', slug: 'django-course',
                short_description: '...', cover: null,
                category: { id: 1, name: 'Python', slug: 'python', description: '' },
                teacher_name: 'Teacher', teacher_id: 1, level: 'junior', duration: 10,
                lessons_count: 5, average_rating: 4.5, reviews_count: 2, status: 'published',
            }],
        });

        const { result } = renderHook(() => useCourses({}));

        expect(result.current.isLoading).toBe(true);

        await waitFor(() => expect(result.current.isLoading).toBe(false));

        expect(result.current.courses).toHaveLength(1);
        expect(result.current.courses[0].title).toBe('Django Course');
        expect(result.current.error).toBeNull();
    });

    it('sets error message on request failure', async () => {
        vi.mocked(courseService.getCourses).mockRejectedValue(new Error('Network error'));

        const { result } = renderHook(() => useCourses({}));

        await waitFor(() => expect(result.current.isLoading).toBe(false));
        expect(result.current.error).not.toBeNull();
        expect(result.current.courses).toHaveLength(0);
    });
});
