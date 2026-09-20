export type PaymentCurrency = 'RUB' | 'KZT';

const FORMATTERS: Record<PaymentCurrency, Intl.NumberFormat> = {
    RUB: new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        maximumFractionDigits: 0,
    }),
    KZT: new Intl.NumberFormat('ru-KZ', {
        style: 'currency',
        currency: 'KZT',
        maximumFractionDigits: 0,
    }),
};

export function formatMoney(amount: number | string, currency: PaymentCurrency = 'RUB'): string {
    const value = Number(amount);
    return Number.isFinite(value) ? FORMATTERS[currency].format(value) : '—';
}

export function formatCoursePrice(amount: number | string): string {
    return isPaidAmount(amount) ? formatMoney(amount, 'RUB') : 'Бесплатно';
}

export function isPaidAmount(amount: number | string): boolean {
    const value = Number(amount);
    return Number.isFinite(value) && value > 0;
}
