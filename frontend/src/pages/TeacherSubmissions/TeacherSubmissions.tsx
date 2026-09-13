import { type FormEvent, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import Button from '../../components/Button/Button';
import EmptyState from '../../components/EmptyState/EmptyState';
import Input from '../../components/Input/Input';
import Loader from '../../components/Loader/Loader';
import { assignmentService } from '../../services/assignmentService';
import type { AssignmentDetail, AssignmentSubmission, SubmissionReviewPayload, SubmissionStatus } from '../../types/assignment';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';
import { SUBMISSION_STATUS_LABELS } from '../../utils/labels';
import styles from './TeacherSubmissions.module.css';

const TeacherSubmissions = () => {
    const { id } = useParams();
    const [assignment, setAssignment] = useState<AssignmentDetail | null>(null);
    const [submissions, setSubmissions] = useState<AssignmentSubmission[]>([]);
    const [forms, setForms] = useState<Record<number, SubmissionReviewPayload>>({});
    const [isLoading, setIsLoading] = useState(true);
    const [savingId, setSavingId] = useState<number | null>(null);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        const loadData = async () => {
            if (!id) return;
            setIsLoading(true);
            setError('');
            try {
                const [assignmentData, submissionItems] = await Promise.all([
                    assignmentService.getAssignment(id),
                    assignmentService.getSubmissions(id),
                ]);
                setAssignment(assignmentData);
                setSubmissions(submissionItems);
                setForms(Object.fromEntries(submissionItems.map((submission) => [
                    submission.id,
                    {
                        status: submission.status,
                        score: submission.score,
                        teacher_comment: submission.teacher_comment,
                    },
                ])));
            } catch (err) {
                setError(getApiErrorMessage(err));
            } finally {
                setIsLoading(false);
            }
        };

        void loadData();
    }, [id]);

    const updateForm = (submissionId: number, patch: Partial<SubmissionReviewPayload>) => {
        setForms((current) => ({
            ...current,
            [submissionId]: { ...current[submissionId], ...patch },
        }));
    };

    const submitReview = async (event: FormEvent, submission: AssignmentSubmission) => {
        event.preventDefault();
        const payload = forms[submission.id];
        if (!payload) return;
        if (assignment && payload.score !== null && payload.score > assignment.max_score) {
            setError(`Оценка не может быть больше ${assignment.max_score}.`);
            return;
        }

        setSavingId(submission.id);
        setError('');
        setSuccess('');
        try {
            const updated = await assignmentService.reviewSubmission(submission.id, payload);
            setSubmissions((items) => items.map((item) => (item.id === updated.id ? updated : item)));
            setSuccess('Решение проверено.');
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setSavingId(null);
        }
    };

    if (isLoading) return <Loader />;
    if (!assignment) return <EmptyState title="Задание не найдено" variant="error" />;

    return (
        <div className={styles.page}>
            <div className={styles.header}>
                <div>
                    <h1>{assignment.title}</h1>
                    <p>Проверяйте решения студентов и выставляйте оценки.</p>
                </div>
                <Link to="/teacher/courses">
                    <Button type="button" variant="secondary">Курсы преподавателя</Button>
                </Link>
            </div>

            {error && <EmptyState title="Не удалось проверить решение" description={error} variant="error" />}
            {success && <p className={styles.success}>{success}</p>}

            {submissions.length === 0 ? (
                <EmptyState title="Решений пока нет" />
            ) : (
                <div className={styles.list}>
                    {submissions.map((submission) => {
                        const form = forms[submission.id];
                        return (
                            <article key={submission.id} className={styles.submission}>
                                <h2>{submission.student_name}</h2>
                                <p className={styles.meta}>
                                    Отправлено: {new Date(submission.updated_at).toLocaleString('ru-RU')} | Статус: {SUBMISSION_STATUS_LABELS[submission.status]}
                                </p>
                                <pre className={styles.code}>{submission.code}</pre>
                                {form && (
                                    <form className={styles.form} onSubmit={(event) => void submitReview(event, submission)}>
                                        <label className={styles.field}>
                                            <span>Статус</span>
                                            <select value={form.status} onChange={(event) => updateForm(submission.id, { status: event.target.value as SubmissionStatus })}>
                                                <option value="pending">{SUBMISSION_STATUS_LABELS.pending}</option>
                                                <option value="accepted">{SUBMISSION_STATUS_LABELS.accepted}</option>
                                                <option value="revision">{SUBMISSION_STATUS_LABELS.revision}</option>
                                            </select>
                                        </label>
                                        <Input
                                            label={`Оценка / ${assignment.max_score}`}
                                            type="number"
                                            min={0}
                                            max={assignment.max_score}
                                            value={form.score ?? ''}
                                            onChange={(event) => updateForm(submission.id, { score: event.target.value === '' ? null : Number(event.target.value) })}
                                        />
                                        <label className={styles.field}>
                                            <span>Комментарий</span>
                                            <textarea rows={3} value={form.teacher_comment} onChange={(event) => updateForm(submission.id, { teacher_comment: event.target.value })} />
                                        </label>
                                        <Button type="submit" isLoading={savingId === submission.id}>Сохранить</Button>
                                    </form>
                                )}
                            </article>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default TeacherSubmissions;
