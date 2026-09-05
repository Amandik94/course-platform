import { Link } from 'react-router-dom';
import ProgressBar from '../../components/ProgressBar/ProgressBar';
import type { Lesson, Section } from '../../types/course';
import styles from './Learn.module.css';

interface SectionWithLessons extends Section {
    lessons: Lesson[];
}

interface LessonSidebarProps {
    courseId: string;
    sections: SectionWithLessons[];
    currentLessonId: number;
    completedLessonIds: Set<number>;
    progressPercent: number;
}

const LessonSidebar = ({
    courseId,
    sections,
    currentLessonId,
    completedLessonIds,
    progressPercent,
}: LessonSidebarProps) => {
    return (
        <aside className={styles.sidebar}>
            <div className={styles.sidebarHeader}>
                <div className={styles.sidebarTitle}>Программа курса</div>
                <ProgressBar value={progressPercent} />
            </div>

            {sections.map((section) => (
                <div key={section.id} className={styles.sectionBlock}>
                    <div className={styles.sectionTitle}>{section.title}</div>
                    {section.lessons.map((lesson) => {
                        const isCompleted = completedLessonIds.has(lesson.id);
                        const isActive = lesson.id === currentLessonId;
                        return (
                            <Link
                                key={lesson.id}
                                to={`/learn/${courseId}/${lesson.id}`}
                                className={`${styles.lessonLink} ${isActive ? styles.lessonActive : ''}`}
                            >
                                <span
                                    className={`${styles.checkIcon} ${isCompleted ? styles.checkCompleted : ''}`}
                                >
                                    {isCompleted && '✓'}
                                </span>
                                {lesson.title}
                            </Link>
                        );
                    })}
                </div>
            ))}
        </aside>
    );
};

export default LessonSidebar;