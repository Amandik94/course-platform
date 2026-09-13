import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import ReviewForm from './ReviewForm';

describe('ReviewForm', () => {
    it('submits rating and trimmed comment', async () => {
        const user = userEvent.setup();
        const onSubmit = vi.fn().mockResolvedValue(undefined);

        render(<ReviewForm isSubmitting={false} onSubmit={onSubmit} />);

        await user.click(screen.getByRole('button', { name: 'Поставить 4 из 5' }));
        await user.type(screen.getByLabelText('Комментарий'), '  Очень полезный курс.  ');
        await user.click(screen.getByRole('button', { name: 'Оставить отзыв' }));

        await waitFor(() => expect(onSubmit).toHaveBeenCalledWith({
            rating: 4,
            comment: 'Очень полезный курс.',
        }));
    });

    it('shows validation error for a short comment', async () => {
        const user = userEvent.setup();
        const onSubmit = vi.fn();

        render(<ReviewForm isSubmitting={false} onSubmit={onSubmit} />);

        await user.type(screen.getByLabelText('Комментарий'), 'мало');
        await user.click(screen.getByRole('button', { name: 'Оставить отзыв' }));

        expect(await screen.findByText('Комментарий должен быть не короче 10 символов.')).toBeInTheDocument();
        expect(onSubmit).not.toHaveBeenCalled();
    });
});
