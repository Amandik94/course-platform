const KZT_FORMATTER = new Intl.NumberFormat('ru-KZ', {
    style: 'currency',
    currency: 'KZT',
    maximumFractionDigits: 0,
});

export function formatKzt(amount: number | string): string {
    const value = Number(amount);
    if (!Number.isFinite(value) || value <= 0) {
        return 'Бесплатно';
    }
    return KZT_FORMATTER.format(value);
}

export function isPaidAmount(amount: number | string): boolean {
    const value = Number(amount);
    return Number.isFinite(value) && value > 0;
}

