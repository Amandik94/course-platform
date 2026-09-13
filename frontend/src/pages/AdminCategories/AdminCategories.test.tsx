import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { courseService } from '../../services/courseService';
import AdminCategories from './AdminCategories';

vi.mock('../../services/courseService', () => ({
    courseService: {
        getCategories: vi.fn(),
        createCategory: vi.fn(),
        updateCategory: vi.fn(),
        deleteCategory: vi.fn(),
    },
}));

describe('AdminCategories', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        vi.mocked(courseService.getCategories).mockResolvedValue([
            { id: 1, name: 'Backend', slug: 'backend', description: 'Django' },
        ]);
    });

    it('renders categories from API', async () => {
        render(<MemoryRouter><AdminCategories /></MemoryRouter>);

        expect(await screen.findByText('Backend')).toBeInTheDocument();
        expect(screen.getByText('Django')).toBeInTheDocument();
    });

    it('creates category and reloads list', async () => {
        const user = userEvent.setup();
        vi.mocked(courseService.createCategory).mockResolvedValue({
            id: 2,
            name: 'Frontend',
            slug: 'frontend',
            description: 'React',
        });

        render(<MemoryRouter><AdminCategories /></MemoryRouter>);
        await screen.findByText('Backend');
        await user.type(screen.getByLabelText('Название'), 'Frontend');
        await user.type(screen.getByLabelText('Описание'), 'React');
        await user.click(screen.getByRole('button', { name: 'Создать категорию' }));

        await waitFor(() => {
            expect(courseService.createCategory).toHaveBeenCalledWith({
                name: 'Frontend',
                description: 'React',
            });
        });
    });
});
