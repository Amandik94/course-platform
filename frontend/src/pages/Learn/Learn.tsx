import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Loader from '../../components/Loader/Loader';
import EmptyState from '../../components/EmptyState/EmptyState';
import { useCourseStructure } from '../../features/learn/useCourseStructure';
import { useLessonProgress } from '../../features/learn/useLessonProgress';
import { courseService } from '../../services/courseService';
import { enrollmentService } from '../../services/enrollmentService';
import { useToast } from '../../components/Toast/ToastProvider';
import type { LessonDetail } from '../../types/course';
import LessonSidebar from './LessonSidebar';
import LessonContent from './LessonContent';
import styles from './Learn.module.css';

const Learn = () => {
    const { courseId, lessonId } = useParams<{ courseId: string; lessonId: string }>();
    const navigate = useNavigate();
    const { showToast } = useToast();

    const { sections, completedLessonIds, isLoading, error, markLessonCompleted } =
        useCourseStructure(courseId);
    const { completeLesson, isCompleting } = useLessonProgress();

    const [currentLesson, setCurrentLesson] = useState<LessonDetail | null>(null);
    const [isLessonLoading, setIsLessonLoading] = useState(true);
    const [progressPercent, setProgressPercent] = useState(0);

    // Плоский список всех уроков курса в правильном порядке —
    // нужен для навигации "Предыдущий/Следующий" через все разделы.
    const flatLessons = useMemo(
        () => sections.flatMap((section) => section.lessons),
        [sections],
    );

    const currentIndex = flatLessons.findIndex((l) => String(l.id) === lessonId);
    const previousLesson = currentIndex > 0 ? flatLessons[currentIndex - 1] : null;
    const nextLesson =
        currentIndex >= 0 && currentIndex < flatLessons.length - 1
            ? flatLessons[currentIndex + 1]
            : null;
    
    useEffect(() => {
        if (!courseId) return;
        enrollmentService.getMyCourses().then((data) => {
            const enrollment = data.results.find((e) => String(e.course.id) === courseId);
            if (enrollment) {
                setProgressPercent(enrollment.progress);
            }
        });
    }, [courseId]);


    useEffect(() => {
        if (!lessonId) return;
        setIsLessonLoading(true);
        courseService
            .getLessonById(lessonId)
            .then(setCurrentLesson)
            .catch(() => setCurrentLesson(null))
            .finally(() => setIsLessonLoading(false));
    }, [lessonId]);

    const handleComplete = () => {
        if (!currentLesson) return;
        completeLesson(currentLesson.id, (result) => {
            markLessonCompleted(currentLesson.id);
            setProgressPercent(result.enrollment_progress);

            if (result.course_completed) {
                showToast('🎉 Курс завершён! Сертификат выдан.', 'success');
            } else {
                showToast('Урок отмечен пройденным', 'success');
            }
        });
    };

    const goToLesson = (id: number | undefined) => {
        if (!id || !courseId) return;
        navigate(`/learn/${courseId}/${id}`);
    };

    if (isLoading || isLessonLoading) return <Loader text="Загрузка курса..." />;
    if (error) return <EmptyState title="Ошибка" description={error} />;
    if (!currentLesson) return <EmptyState title="Урок не найден" />;
    if (!courseId) return null;

    return (
        <div className={styles.page}>
            <LessonSidebar
                courseId={courseId}
                sections={sections}
                currentLessonId={currentLesson.id}
                completedLessonIds={completedLessonIds}
                progressPercent={progressPercent}
            />
            <LessonContent
                lesson={currentLesson}
                isCompleted={completedLessonIds.has(currentLesson.id)}
                isCompleting={isCompleting}
                hasPrevious={!!previousLesson}
                hasNext={!!nextLesson}
                onComplete={handleComplete}
                onPrevious={() => goToLesson(previousLesson?.id)}
                onNext={() => goToLesson(nextLesson?.id)}
            />
        </div>
    );
};

export default Learn;