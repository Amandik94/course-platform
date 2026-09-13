import styles from './RatingStars.module.css';

interface RatingStarsProps {
    value: number;
    onChange?: (value: number) => void;
    readonly?: boolean;
    label?: string;
}

const MAX_RATING = 5;

const RatingStars = ({ value, onChange, readonly = false, label }: RatingStarsProps) => {
    const stars = Array.from({ length: MAX_RATING }, (_, index) => index + 1);

    if (readonly) {
        return (
            <span className={styles.readonly} aria-label={label ?? `${value} из ${MAX_RATING}`}>
                {stars.map((star) => (
                    <span key={star} className={star <= value ? styles.activeStar : styles.star}>
                        ★
                    </span>
                ))}
            </span>
        );
    }

    return (
        <div className={styles.interactive} role="radiogroup" aria-label={label ?? 'Оценка курса'}>
            {stars.map((star) => (
                <button
                    key={star}
                    type="button"
                    className={star <= value ? styles.activeButton : styles.button}
                    aria-label={`Поставить ${star} из ${MAX_RATING}`}
                    aria-pressed={star === value}
                    onClick={() => onChange?.(star)}
                >
                    ★
                </button>
            ))}
        </div>
    );
};

export default RatingStars;
