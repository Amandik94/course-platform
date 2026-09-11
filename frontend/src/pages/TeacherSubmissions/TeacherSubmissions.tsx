import { type FormEvent, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import Button from '../../components/Button/Button';
import EmptyState from '../../components/EmptyState/EmptyState';
import Input from '../../components/Input/Input';
import Loader from '../../components/Loader/Loader';
import { assignmentService } from '../../services/assignmentService';
import type { AssignmentDetail, AssignmentSubmission, SubmissionReviewPayload, SubmissionStatus } from '../../types/assignment';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';
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
            setError(`Score cannot exceed ${assignment.max_score}.`);
            return;
        }

        setSavingId(submission.id);
        setError('');
        setSuccess('');
        try {
            const updated = await assignmentService.reviewSubmission(submission.id, payload);
            setSubmissions((items) => items.map((item) => (item.id === updated.id ? updated : item)));
            setSuccess('Submission reviewed.');
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setSavingId(null);
        }
    };

    if (isLoading) return <Loader />;
    if (!assignment) return <EmptyState title="Assignment not found" variant="error" />;

    return (
        <div className={styles.page}>
            <div className={styles.header}>
                <div>
                    <h1>{assignment.title}</h1>
                    <p>Review submissions and return grades.</p>
                </div>
                <Link to="/teacher/courses">
                    <Button type="button" variant="secondary">Teacher courses</Button>
                </Link>
            </div>

            {error && <EmptyState title="Review failed" description={error} variant="error" />}
            {success && <p className={styles.success}>{success}</p>}

            {submissions.length === 0 ? (
                <EmptyState title="No submissions yet" />
            ) : (
                <div className={styles.list}>
                    {submissions.map((submission) => {
                        const form = forms[submission.id];
                        return (
                            <article key={submission.id} className={styles.submission}>
                                <h2>{submission.student_name}</h2>
                                <p className={styles.meta}>
                                    Submitted: {new Date(submission.updated_at).toLocaleString()} | Status: {submission.status}
                                </p>
                                <pre className={styles.code}>{submission.code}</pre>
                                {form && (
                                    <form className={styles.form} onSubmit={(event) => void submitReview(event, submission)}>
                                        <label className={styles.field}>
                                            <span>Status</span>
                                            <select value={form.status} onChange={(event) => updateForm(submission.id, { status: event.target.value as SubmissionStatus })}>
                                                <option value="pending">Pending</option>
                                                <option value="accepted">Accepted</option>
                                                <option value="revision">Revision</option>
                                            </select>
                                        </label>
                                        <Input
                                            label={`Score / ${assignment.max_score}`}
                                            type="number"
                                            min={0}
                                            max={assignment.max_score}
                                            value={form.score ?? ''}
                                            onChange={(event) => updateForm(submission.id, { score: event.target.value === '' ? null : Number(event.target.value) })}
                                        />
                                        <label className={styles.field}>
                                            <span>Comment</span>
                                            <textarea rows={3} value={form.teacher_comment} onChange={(event) => updateForm(submission.id, { teacher_comment: event.target.value })} />
                                        </label>
                                        <Button type="submit" isLoading={savingId === submission.id}>Save</Button>
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
