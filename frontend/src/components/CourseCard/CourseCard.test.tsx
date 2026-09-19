import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import type { CourseListItem } from '../../types/course';
import CourseCard from './CourseCard';

const baseCourse: CourseListItem = {
    id: 1,
    title: 'Django Course',
    slug: 'django-course',
    short_description: 'Практический курс',
    cover: null,
    category: { id: 1, name: 'Python', slug: 'python', description: '' },
    teacher_name: 'Teacher',
    teacher_id: 2,
    level: 'junior',
    duration: 10,
    price: '0.00',
    lessons_count: 5,
    average_rating: 4.8,
    reviews_count: 3,
    status: 'published',
};

function renderCard(course: CourseListItem) {
    render(
        <MemoryRouter>
            <CourseCard course={course} />
        </MemoryRouter>,
    );
}

describe('CourseCard', () => {
    it('shows free label for free courses', () => {
        renderCard(baseCourse);

        expect(screen.getByText('Бесплатно')).toBeInTheDocument();
    });

    it('shows KZT price for paid courses', () => {
        renderCard({ ...baseCourse, price: '12000.00' });

        expect(screen.getByText(/12\s?000/)).toBeInTheDocument();
    });
});

