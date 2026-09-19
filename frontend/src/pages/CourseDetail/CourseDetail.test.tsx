import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { courseService } from '../../services/courseService';
import { paymentService } from '../../services/paymentService';
import { useAuthStore } from '../../store/authStore';
import type { CourseDetail as CourseDetailType } from '../../types/course';
import CourseDetail from './CourseDetail';

const showToast = vi.fn();

vi.mock('../../services/courseService', () => ({
    courseService: {
        getCourseById: vi.fn(),
        getCourseSections: vi.fn(),
    },
}));

vi.mock('../../services/paymentService', () => ({
    paymentService: {
        createPayment: vi.fn(),
    },
}));

vi.mock('../../features/courses/useEnroll', () => ({
    useEnroll: () => ({ enroll: vi.fn(), isEnrolling: false, error: null }),
}));

vi.mock('../../features/reviews/CourseReviews', () => ({
    default: () => null,
}));

vi.mock('../../components/Toast/useToast', () => ({
    useToast: () => ({ showToast }),
}));

const paidCourse: CourseDetailType = {
    id: 1,
    title: 'Django для начинающих',
    slug: 'django-beginners',
    description: 'Описание курса',
    short_description: 'Практический курс',
    cover: null,
    category: { id: 1, name: 'Python', slug: 'python', description: '' },
    teacher: {
        id: 2,
        full_name: 'Иван Петров',
        email: 'teacher@example.com',
        avatar: null,
    },
    level: 'beginner',
    duration: 12,
    price: '12000.00',
    status: 'published',
    lessons_count: 8,
    average_rating: 0,
    reviews_count: 0,
    is_enrolled: false,
    created_at: '2026-09-01T00:00:00Z',
    updated_at: '2026-09-01T00:00:00Z',
};

function renderPage() {
    return render(
        <MemoryRouter initialEntries={['/courses/1']}>
            <Routes>
                <Route path="/courses/:id" element={<CourseDetail />} />
            </Routes>
        </MemoryRouter>,
    );
}

describe('CourseDetail PayBot flow', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        useAuthStore.setState({
            user: {
                id: 1,
                email: 'student@example.com',
                first_name: 'Студент',
                last_name: 'Тестовый',
                full_name: 'Студент Тестовый',
                avatar: null,
                role: 'student',
                created_at: '2026-01-01T00:00:00Z',
            },
            accessToken: 'access',
            refreshToken: 'refresh',
            isAuthenticated: true,
            isInitializing: false,
        });
        vi.mocked(courseService.getCourseById).mockResolvedValue(paidCourse);
        vi.mocked(courseService.getCourseSections).mockResolvedValue([]);
    });

    it('disables the buy button and prevents duplicate payment requests', async () => {
        vi.mocked(paymentService.createPayment).mockImplementation(
            () => new Promise(() => undefined),
        );
        const user = userEvent.setup();
        renderPage();

        const button = await screen.findByRole('button', { name: /Купить курс/ });
        await user.click(button);

        await waitFor(() => expect(button).toBeDisabled());
        fireEvent.click(button);
        expect(paymentService.createPayment).toHaveBeenCalledTimes(1);
        expect(paymentService.createPayment).toHaveBeenCalledWith(1);
    });

    it('shows an API error and enables retry', async () => {
        vi.mocked(paymentService.createPayment).mockRejectedValue(
            new Error('PayBot временно недоступен'),
        );
        const user = userEvent.setup();
        renderPage();

        const button = await screen.findByRole('button', { name: /Купить курс/ });
        await user.click(button);

        await waitFor(() => expect(showToast).toHaveBeenCalled());
        expect(button).toBeEnabled();
    });
});
