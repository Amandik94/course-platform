import { Link } from 'react-router-dom';
import type { CourseListItem } from '../../types/course';
import styles from './CourseCard.module.css';

const LEVEL_LABELS: Record<string, string> = {
    beginner: 'Начинающий',
    junior: 'Junior',
    middle: 'Middle',
    advanced: 'Advanced',
};

const LEVEL_COLOR_VAR: Record<string, string> = {
    beginner: 'var(--color-level-beginner)',
    junior: 'var(--color-level-junior)',
    middle: 'var(--color-level-middle)',
    advanced: 'var(--color-level-advanced)',
};

interface CourseCardProps {
    course: CourseListItem;
}

const CourseCard = ({ course }: CourseCardProps) => {
    return (
        <Link to={`/courses/${course.id}`} className={styles.card}>
            {course.cover ? (
                <img src={course.cover} alt={course.title} className={styles.cover} />
            ) : (
                <div className={styles.coverPlaceholder}>Нет обложки</div>
            )}

            <div className={styles.body}>
                <span
                    className={styles.levelBadge}
                    style={{ backgroundColor: LEVEL_COLOR_VAR[course.level] }}
                >
                    {LEVEL_LABELS[course.level]}
                </span>

                <h3 className={styles.title}>{course.title}</h3>
                <p className={styles.description}>{course.short_description}</p>

                <div className={styles.meta}>
                    <span>{course.teacher_name}</span>
                    <span>{course.lessons_count} уроков · {course.duration} ч</span>
                </div>
            </div>
        </Link>
    );
};

export default CourseCard;