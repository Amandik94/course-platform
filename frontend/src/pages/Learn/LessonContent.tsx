import { Link } from 'react-router-dom';
import Button from '../../components/Button/Button';
import type { LessonDetail } from '../../types/course';
import styles from './Learn.module.css';

interface LessonContentProps {
    lesson: LessonDetail;
    isCompleted: boolean;
    isCompleting: boolean;
    hasPrevious: boolean;
    hasNext: boolean;
    onComplete: () => void;
    onPrevious: () => void;
    onNext: () => void;
}

const LessonContent = ({
    lesson,
    isCompleted,
    isCompleting,
    hasPrevious,
    hasNext,
    onComplete,
    onPrevious,
    onNext,
}: LessonContentProps) => {
    return (
        <div className={styles.content}>
            <h1 className={styles.lessonTitle}>{lesson.title}</h1>

            {lesson.type === 'video' && lesson.video_url && (
                <div className={styles.videoWrapper}>
                    <iframe
                        src={lesson.video_url}
                        width="100%"
                        height="100%"
                        style={{ border: 'none', borderRadius: 'var(--radius-md)' }}
                        allow="autoplay; fullscreen"
                        title={lesson.title}
                    />
                </div>
            )}

            {lesson.content && <div className={styles.textContent}>{lesson.content}</div>}

            {lesson.type === 'assignment' && lesson.assignment_id && (
                <Link to={`/assignment/${lesson.assignment_id}`}>
                    <Button variant="secondary">Перейти к заданию →</Button>
                </Link>
            )}

            {lesson.type === 'quiz' && lesson.quiz_id && (
                <Link to={`/quiz/${lesson.quiz_id}`}>
                    <Button variant="secondary">Перейти к тесту →</Button>
                </Link>
            )}

            <div className={styles.footer}>
                <div className={styles.navButtons}>
                    <Button variant="secondary" onClick={onPrevious} disabled={!hasPrevious}>
                        ← Предыдущий
                    </Button>
                    <Button variant="secondary" onClick={onNext} disabled={!hasNext}>
                        Следующий →
                    </Button>
                </div>

                <Button onClick={onComplete} isLoading={isCompleting} disabled={isCompleted}>
                    {isCompleted ? '✓ Урок пройден' : 'Завершить урок'}
                </Button>
            </div>
        </div>
    );
};

export default LessonContent;