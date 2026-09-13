import Button from '../../components/Button/Button';
import { formatDateTime } from '../../utils/formatDate';
import type { Review } from '../../types/review';
import RatingStars from './RatingStars';
import styles from './ReviewCard.module.css';

interface ReviewCardProps {
    review: Review;
    canManage: boolean;
    isDeleting: boolean;
    onEdit: (review: Review) => void;
    onDelete: (review: Review) => void;
}

const ReviewCard = ({ review, canManage, isDeleting, onEdit, onDelete }: ReviewCardProps) => {
    const authorName = `${review.student.first_name} ${review.student.last_name}`.trim() || 'Студент';
    const isEdited = review.updated_at !== review.created_at;

    return (
        <article className={styles.card}>
            <div className={styles.header}>
                {review.student.avatar ? (
                    <img src={review.student.avatar} alt="" className={styles.avatar} />
                ) : (
                    <span className={styles.avatarPlaceholder}>{authorName.slice(0, 1).toUpperCase()}</span>
                )}
                <div>
                    <h3 className={styles.author}>{authorName}</h3>
                    <div className={styles.meta}>
                        <RatingStars value={review.rating} readonly label={`${review.rating} из 5`} />
                        <span>{formatDateTime(review.created_at)}</span>
                        {isEdited && <span>изменено</span>}
                    </div>
                </div>
            </div>

            <p className={styles.comment}>{review.comment}</p>

            {canManage && (
                <div className={styles.actions}>
                    <Button type="button" variant="secondary" onClick={() => onEdit(review)}>
                        Редактировать
                    </Button>
                    <Button
                        type="button"
                        variant="danger"
                        isLoading={isDeleting}
                        onClick={() => onDelete(review)}
                    >
                        Удалить
                    </Button>
                </div>
            )}
        </article>
    );
};

export default ReviewCard;
