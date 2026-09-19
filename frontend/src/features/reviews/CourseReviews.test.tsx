import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ToastProvider } from '../../components/Toast/ToastProvider';
import { courseService } from '../../services/courseService';
import { reviewService } from '../../services/reviewService';
import { useAuthStore } from '../../store/authStore';
import type { CourseDetail } from '../../types/course';
import CourseReviews from './CourseReviews';

vi.mock('../../services/reviewService', () => ({
    reviewService: {
        getCourseReviews: vi.fn(),
        getMyReview: vi.fn(),
        createReview: vi.fn(),
        updateReview: vi.fn(),
        deleteReview: vi.fn(),
    },
}));

vi.mock('../../services/courseService', () => ({
    courseService: {
        getCourseById: vi.fn(),
    },
}));

const course: CourseDetail = {
    id: 1,
    title: 'Django Course',
    slug: 'django-course',
    description: 'Full description',
    short_description: 'Short description',
    cover: null,
    category: { id: 1, name: 'Python', slug: 'python', description: '' },
    teacher: {
        id: 2,
        email: 'teacher@test.com',
        full_name: 'Teacher User',
        avatar: null,
    },
    level: 'junior',
    duration: 10,
    price: '0.00',
    status: 'published',
    lessons_count: 5,
    average_rating: 4.5,
    reviews_count: 1,
    is_enrolled: true,
    created_at: '2026-01-01',
    updated_at: '2026-01-01',
};

const review = {
    id: 7,
    student: {
        id: 1,
        first_name: 'Student',
        last_name: 'User',
        avatar: null,
    },
    rating: 5,
    comment: 'Очень полезный курс.',
    created_at: '2026-09-12T10:00:00Z',
    updated_at: '2026-09-12T10:00:00Z',
};

const renderCourseReviews = () => render(
    <ToastProvider>
        <CourseReviews course={course} onCourseUpdated={vi.fn()} />
    </ToastProvider>,
);

describe('CourseReviews', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        useAuthStore.setState({
            user: {
                id: 1,
                email: 'student@test.com',
                first_name: 'Student',
                last_name: 'User',
                full_name: 'Student User',
                avatar: null,
                role: 'student',
                created_at: '2026-01-01',
            },
            accessToken: 'token',
            refreshToken: 'refresh',
            isAuthenticated: true,
            isInitializing: false,
        });
        vi.mocked(reviewService.getCourseReviews).mockResolvedValue({
            count: 1,
            next: null,
            previous: null,
            results: [review],
        });
        vi.mocked(reviewService.getMyReview).mockResolvedValue(review);
        vi.mocked(courseService.getCourseById).mockResolvedValue(course);
        vi.mocked(reviewService.updateReview).mockResolvedValue(review);
        vi.mocked(reviewService.deleteReview).mockResolvedValue({} as never);
    });

    it('renders paginated reviews', async () => {
        renderCourseReviews();

        expect(await screen.findByText('Очень полезный курс.')).toBeInTheDocument();
        expect(screen.getByText('Student User')).toBeInTheDocument();
    });

    it('shows edit and delete for own review', async () => {
        renderCourseReviews();

        expect(await screen.findByRole('button', { name: 'Редактировать' })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Удалить' })).toBeInTheDocument();
    });

    it('deletes review after confirmation', async () => {
        const user = userEvent.setup();
        vi.spyOn(window, 'confirm').mockReturnValue(true);
        renderCourseReviews();

        await user.click(await screen.findByRole('button', { name: 'Удалить' }));

        await waitFor(() => expect(reviewService.deleteReview).toHaveBeenCalledWith(7));
    });

    it('does not show a second create form when own review is outside the current page', async () => {
        vi.mocked(reviewService.getCourseReviews).mockResolvedValue({
            count: 10,
            next: null,
            previous: '/api/v1/courses/1/reviews/?page=1',
            results: [{ ...review, id: 8, student: { ...review.student, id: 3 } }],
        });

        renderCourseReviews();

        await waitFor(() => expect(reviewService.getMyReview).toHaveBeenCalledWith(1));
        expect(screen.queryByRole('button', { name: 'Отправить отзыв' })).not.toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Редактировать' })).toBeInTheDocument();
    });
});
