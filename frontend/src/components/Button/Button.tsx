import { type ButtonHTMLAttributes, type ReactNode } from 'react';
import styles from './Button.module.css';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    children: ReactNode;
    variant?: 'primary' | 'secondary' | 'danger';
    fullWidth?: boolean;
    isLoading?: boolean;
}

const Button = ({
    children,
    variant = 'primary',
    fullWidth = false,
    isLoading = false,
    disabled,
    className,
    ...rest
}: ButtonProps) => {
    const classNames = [
        styles.button,
        styles[variant],
        fullWidth ? styles.fullWidth : '',
        className,
    ]
        .filter(Boolean)
        .join(' ');

    return (
        <button className={classNames} disabled={disabled || isLoading} {...rest}>
            {isLoading ? 'Загрузка...' : children}
        </button>
    );
};

export default Button;