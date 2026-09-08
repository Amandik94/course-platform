import { type ReactNode, useCallback, useState } from 'react';
import styles from './Toast.module.css';
import { ToastContext, type ToastType } from './ToastContext';

interface ToastItem {
    id: number;
    message: string;
    type: ToastType;
}

let nextId = 1;

export const ToastProvider = ({ children }: { children: ReactNode }) => {
    const [toasts, setToasts] = useState<ToastItem[]>([]);

    const showToast = useCallback(
        (message: string, type: ToastType = 'info') => {
            const id = nextId++;

            setToasts((prev) => [
                ...prev,
                { id, message, type },
            ]);

            setTimeout(() => {
                setToasts((prev) =>
                    prev.filter((toast) => toast.id !== id),
                );
            }, 4000);
        },
        [],
    );

    return (
        <ToastContext.Provider value={{ showToast }}>
            {children}

            <div className={styles.container}>
                {toasts.map((toast) => (
                    <div
                        key={toast.id}
                        className={`${styles.toast} ${styles[toast.type]}`}
                    >
                        {toast.message}
                    </div>
                ))}
            </div>
        </ToastContext.Provider>
    );
};