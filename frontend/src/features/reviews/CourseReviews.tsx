import { useCallback, useEffect, useMemo, useState } from 'react';
import EmptyState from '../../components/EmptyState/EmptyState';
import Loader from '../../components/Loader/Loader';
import Pagination from '../../components/Pagination/Pagination';
import { useToast } from '../../components/Toast/useToast';
import { courseService } from '../../services/courseService';
import { reviewService } from '../../services/reviewService';
import { useAuthStore } from '../../store/authStore';
import type { PaginatedResponse } from '../../types/common';
import type { CourseDetail } from '../../types/course';
import type { CreateReviewPayload, Review } from '../../types/review';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';
import { pluralizeRu } from '../../utils/labels';
import RatingStars from './RatingStars';
import ReviewCard from './ReviewCard';
import ReviewForm from './ReviewForm';
import styles from './CourseReviews.module.css';

const PAGE_SIZE = 9;

interface CourseReviewsProps {
    course: CourseDetail;
    onCourseUpdated: (course: CourseDetail) => void;
}

const emptyPage: PaginatedResponse<Review> = {
    count: 0,
    next: null,
    previous: null,
    results: [],
};

const CourseReviews = ({ course, onCourseUpdated }: CourseReviewsProps) => {
    const { isAuthenticated, user } = useAuthStore();
    const { showToast } = useToast();
    const [reviewsPage, setReviewsPage] = useState<PaginatedResponse<Review>>(emptyPage);
    const [page, setPage] = useState(1);
    const [isLoading, setIsLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [deletingId, setDeletingId] = useState<number | null>(null);
    const [editingReview, setEditingReview] = useState<Review | null>(null);
    const [error, setError] = useState<string | null>(null);

    const myReview = useMemo(() => {
        if (!user) return null;
        return reviewsPage.results.find((review) => review.student.id === user.id) ?? null;
    }, [reviewsPage.results, user]);

    const totalPages = Math.ceil(reviewsPage.count / PAGE_SIZE);
    const canCreateReview = Boolean(
        isAuthenticated
        && user?.role === 'student'
        && course.is_enrolled
        && !myReview
        && !editingReview,
    );

    const loadReviews = useCallback(async (targetPage = page) => {
        setIsLoading(true);
        try {
            const data = await reviewService.getCourseReviews(course.id, {
                page: targetPage,
                ordering: '-created_at',
            });
            setReviewsPage(data);
            setError(null);
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsLoading(false);
        }
    }, [course.id, page]);

    const refreshCourse = useCallback(async () => {
        const updatedCourse = await courseService.getCourseById(course.id);
        onCourseUpdated(updatedCourse);
    }, [course.id, onCourseUpdated]);

    const refreshAll = useCallback(async (targetPage = page) => {
        await Promise.all([loadReviews(targetPage), refreshCourse()]);
    }, [loadReviews, page, refreshCourse]);

    useEffect(() => {
        queueMicrotask(() => {
            void loadReviews(page);
        });
    }, [loadReviews, page]);

    const submitCreate = async (payload: CreateReviewPayload) => {
        setIsSubmitting(true);
        try {
            await reviewService.createReview(course.id, payload);
            await refreshAll(1);
            setPage(1);
            showToast('Отзыв добавлен.', 'success');
        } finally {
            setIsSubmitting(false);
        }
    };

    const submitUpdate = async (payload: CreateReviewPayload) => {
        if (!editingReview) return;
        setIsSubmitting(true);
        try {
            await reviewService.updateReview(editingReview.id, payload);
            setEditingReview(null);
            await refreshAll(page);
            showToast('Отзыв обновлён.', 'success');
        } finally {
            setIsSubmitting(false);
        }
    };

    const deleteReview = async (review: Review) => {
        if (!window.confirm('Удалить отзыв?')) return;
        setDeletingId(review.id);
        try {
            await reviewService.deleteReview(review.id);
            await refreshAll(page);
            showToast('Отзыв удалён.', 'success');
        } catch (err) {
            showToast(getApiErrorMessage(err), 'error');
        } finally {
            setDeletingId(null);
        }
    };

    const renderReviewPrompt = () => {
        if (!isAuthenticated) {
            return <p className={styles.hint}>Войдите как записанный студент, чтобы оставить отзыв.</p>;
        }
        if (user?.role !== 'student') {
            return <p className={styles.hint}>Оставлять отзывы могут только студенты.</p>;
        }
        if (!course.is_enrolled) {
            return <p className={styles.hint}>Запишитесь на курс, чтобы оставить отзыв.</p>;
        }
        if (myReview && !editingReview) {
            return <p className={styles.hint}>Вы уже оставили отзыв. Используйте редактирование, чтобы обновить его.</p>;
        }
        return null;
    };

    return (
        <section className={styles.wrapper} aria-labelledby="course-reviews-title">
            <div className={styles.summary}>
                <div>
                    <h2 id="course-reviews-title">Отзывы студентов</h2>
                    <p className={styles.count}>
                        {course.reviews_count} {pluralizeRu(course.reviews_count, ['отзыв', 'отзыва', 'отзывов'])}
                    </p>
                </div>
                <div className={styles.rating}>
                    <RatingStars value={Math.round(course.average_rating)} readonly label={`${course.average_rating} из 5`} />
                    <strong>{course.average_rating.toFixed(1)}</strong>
                </div>
            </div>

            {canCreateReview && (
                <ReviewForm isSubmitting={isSubmitting} onSubmit={submitCreate} />
            )}

            {editingReview && (
                <ReviewForm
                    key={editingReview.id}
                    initialReview={editingReview}
                    isSubmitting={isSubmitting}
                    onSubmit={submitUpdate}
                    onCancel={() => setEditingReview(null)}
                />
            )}

            {renderReviewPrompt()}

            {isLoading && <Loader text="Загрузка отзывов..." />}
            {error && <EmptyState variant="error" title="Не удалось загрузить отзывы" description={error} />}

            {!isLoading && !error && reviewsPage.results.length === 0 && (
                <EmptyState title="Отзывов пока нет" description="Станьте первым студентом, который поделится впечатлением после записи на курс." />
            )}

            {!isLoading && !error && reviewsPage.results.length > 0 && (
                <div className={styles.list}>
                    {reviewsPage.results.map((review) => (
                        <ReviewCard
                            key={review.id}
                            review={review}
                            canManage={review.student.id === user?.id}
                            isDeleting={deletingId === review.id}
                            onEdit={setEditingReview}
                            onDelete={deleteReview}
                        />
                    ))}
                </div>
            )}

            <Pagination currentPage={page} totalPages={totalPages} onPageChange={setPage} />
        </section>
    );
};

export default CourseReviews;
