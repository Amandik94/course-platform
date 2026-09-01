import { type InputHTMLAttributes, forwardRef } from 'react';
import styles from './Input.module.css';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
}

// forwardRef нужен, чтобы родительский компонент мог получить доступ
// к нативному DOM input'у напрямую (например, для .focus()), если
// понадобится в будущем — стандартная практика для reusable input.
const Input = forwardRef<HTMLInputElement, InputProps>(
    ({ label, error, id, className, ...rest }, ref) => {
        const inputId = id ?? rest.name;

        return (
            <div className={styles.wrapper}>
                {label && (
                    <label htmlFor={inputId} className={styles.label}>
                        {label}
                    </label>
                )}
                <input
                    id={inputId}
                    ref={ref}
                    className={[styles.input, error ? styles.inputError : '', className]
                        .filter(Boolean)
                        .join(' ')}
                    {...rest}
                />
                {error && <span className={styles.errorText}>{error}</span>}
            </div>
        );
    },
);

Input.displayName = 'Input';

export default Input;