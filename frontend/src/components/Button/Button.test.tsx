import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Button from './Button';

describe('Button', () => {
    it('renders children text', () => {
        render(<Button>Нажми меня</Button>);
        expect(screen.getByText('Нажми меня')).toBeInTheDocument();
    });

    it('calls onClick when clicked', async () => {
        const handleClick = vi.fn();
        const user = userEvent.setup();

        render(<Button onClick={handleClick}>Кнопка</Button>);
        await user.click(screen.getByText('Кнопка'));

        expect(handleClick).toHaveBeenCalledOnce();
    });

    it('shows loading text and disables button when isLoading', () => {
        render(<Button isLoading>Отправить</Button>);

        const button = screen.getByRole('button');
        expect(button).toBeDisabled();
        expect(screen.getByText('Загрузка...')).toBeInTheDocument();
    });

    it('does not call onClick when disabled', async () => {
        const handleClick = vi.fn();
        const user = userEvent.setup();

        render(<Button onClick={handleClick} disabled>Кнопка</Button>);
        await user.click(screen.getByRole('button'));

        expect(handleClick).not.toHaveBeenCalled();
    });
});