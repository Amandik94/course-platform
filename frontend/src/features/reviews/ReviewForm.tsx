import { type FormEvent, useState } from 'react';
import Button from '../../components/Button/Button';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';
import type { CreateReviewPayload, Review } from '../../types/review';
import RatingStars from './RatingStars';
import styles from './ReviewForm.module.css';

interface ReviewFormProps {
    initialReview?: Review | null;
    isSubmitting: boolean;
    onSubmit: (payload: CreateReviewPayload) => Promise<void>;
    onCancel?: () => void;
}

const ReviewForm = ({ initialReview, isSubmitting, onSubmit, onCancel }: ReviewFormProps) => {
    const [rating, setRating] = useState(initialReview?.rating ?? 5);
    const [comment, setComment] = useState(initialReview?.comment ?? '');
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (event: FormEvent) => {
        event.preventDefault();

        const trimmedComment = comment.trim();
        if (!rating) {
            setError('Выберите оценку.');
            return;
        }
        if (trimmedComment.length < 10) {
            setError('Комментарий должен быть не короче 10 символов.');
            return;
        }

        try {
            setError(null);
            await onSubmit({ rating, comment: trimmedComment });
            if (!initialReview) {
                setRating(5);
                setComment('');
            }
        } catch (err) {
            setError(getApiErrorMessage(err));
        }
    };

    return (
        <form className={styles.form} onSubmit={(event) => void handleSubmit(event)}>
            <div className={styles.field}>
                <span className={styles.label}>Оценка</span>
                <RatingStars value={rating} onChange={setRating} label="Выберите оценку курса" />
            </div>

            <label className={styles.field}>
                <span className={styles.label}>Комментарий</span>
                <textarea
                    className={styles.textarea}
                    value={comment}
                    rows={4}
                    maxLength={2000}
                    onChange={(event) => setComment(event.target.value)}
                    placeholder="Расскажите, что было полезно в этом курсе."
                    disabled={isSubmitting}
                />
            </label>

            {error && <p className={styles.error}>{error}</p>}

            <div className={styles.actions}>
                <Button type="submit" isLoading={isSubmitting}>
                    {initialReview ? 'Сохранить отзыв' : 'Оставить отзыв'}
                </Button>
                {onCancel && (
                    <Button type="button" variant="secondary" onClick={onCancel} disabled={isSubmitting}>
                        Отмена
                    </Button>
                )}
            </div>
        </form>
    );
};

export default ReviewForm;
