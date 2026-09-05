import { type FormEvent, useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import Button from '../../components/Button/Button';
import Loader from '../../components/Loader/Loader';
import EmptyState from '../../components/EmptyState/EmptyState';
import StatusBadge from '../../components/StatusBadge/StatusBadge';
import { useAssignment } from '../../features/assignments/useAssignment';
import { useToast } from '../../components/Toast/ToastProvider';
import styles from './Assignments.module.css';

const AssignmentPage = () => {
    const { id } = useParams<{ id: string }>();
    const { assignment, submission, isLoading, error, submitSolution, isSubmitting, submitError } =
        useAssignment(id);
    const { showToast } = useToast();
    const [code, setCode] = useState('');

    // при первой загрузке подставляем starter_code, либо код уже
    // отправленного решения (если студент возвращается доработать)
    useEffect(() => {
        if (submission) {
            setCode(submission.code);
        } else if (assignment) {
            setCode(assignment.starter_code);
        }
    }, [assignment, submission]);

    const handleSubmit = async (event: FormEvent) => {
        event.preventDefault();
        await submitSolution(code);
        showToast('Решение отправлено на проверку', 'success');
    };

    if (isLoading) return <Loader text="Загрузка задания..." />;
    if (error || !assignment) return <EmptyState title="Задание не найдено" description={error ?? undefined} />;

    const isEditable = !submission || submission.status === 'revision';

    return (
        <div className={`${styles.page} container`}>
            <div className={styles.header}>
                <h1>{assignment.title}</h1>
                {submission && <StatusBadge status={submission.status} />}
            </div>

            <div className={styles.meta}>
                Максимальный балл: {assignment.max_score}
                {assignment.deadline && ` · Дедлайн: ${new Date(assignment.deadline).toLocaleDateString()}`}
            </div>

            <div className={styles.description}>{assignment.description}</div>

            <form onSubmit={handleSubmit}>
                {submitError && <div className={styles.errorText}>{submitError}</div>}

                <textarea
                    className={styles.codeArea}
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    spellCheck={false}
                    disabled={!isEditable}
                />

                {isEditable && (
                    <Button type="submit" isLoading={isSubmitting}>
                        {submission ? 'Отправить исправленное решение' : 'Отправить решение'}
                    </Button>
                )}
            </form>

            {submission && submission.status !== 'pending' && (
                <div className={styles.feedback}>
                    <div className={styles.feedbackRow}>
                        <span>Оценка преподавателя</span>
                        <span className={styles.score}>
                            {submission.score !== null ? `${submission.score} / ${assignment.max_score}` : '—'}
                        </span>
                    </div>
                    {submission.teacher_comment && (
                        <p className={styles.comment}>{submission.teacher_comment}</p>
                    )}
                </div>
            )}
        </div>
    );
};

export default AssignmentPage;