import { type FormEvent, useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import Button from '../../components/Button/Button';
import EmptyState from '../../components/EmptyState/EmptyState';
import Input from '../../components/Input/Input';
import Loader from '../../components/Loader/Loader';
import { assignmentService } from '../../services/assignmentService';
import { courseService } from '../../services/courseService';
import { quizService } from '../../services/quizService';
import type { AssignmentDetail, AssignmentUpsertPayload } from '../../types/assignment';
import type {
    CourseDetail,
    Lesson,
    LessonDetail,
    LessonUpsertPayload,
    Section,
    SectionUpsertPayload,
} from '../../types/course';
import type {
    AnswerOption,
    AnswerUpsertPayload,
    QuestionType,
    QuestionUpsertPayload,
    QuizDetail,
    QuizQuestion,
    QuizUpsertPayload,
} from '../../types/quiz';
import { getApiErrorMessage } from '../../utils/apiErrorMessage';
import styles from './CourseManage.module.css';

const EMPTY_SECTION: SectionUpsertPayload = { title: '', description: '', order: 1 };
const EMPTY_LESSON: LessonUpsertPayload = {
    title: '',
    description: '',
    type: 'text',
    content: '',
    video_url: '',
    duration: 10,
    order: 1,
    is_free: false,
};
const EMPTY_ASSIGNMENT: AssignmentUpsertPayload = {
    title: '',
    description: '',
    starter_code: '',
    max_score: 100,
    deadline: null,
};
const EMPTY_QUIZ: QuizUpsertPayload = { title: '', description: '', passing_score: 70 };
const EMPTY_QUESTION: QuestionUpsertPayload = {
    question: '',
    type: 'single',
    points: 1,
    order: 1,
    text_answer: '',
};
const EMPTY_ANSWER: AnswerUpsertPayload = { text: '', is_correct: false };

const CourseManage = () => {
    const { id } = useParams();
    const [course, setCourse] = useState<CourseDetail | null>(null);
    const [sections, setSections] = useState<Section[]>([]);
    const [lessonsBySection, setLessonsBySection] = useState<Record<number, LessonDetail[]>>({});
    const [selectedSectionId, setSelectedSectionId] = useState<number | null>(null);
    const [selectedLessonId, setSelectedLessonId] = useState<number | null>(null);
    const [sectionForm, setSectionForm] = useState<SectionUpsertPayload>(EMPTY_SECTION);
    const [editingSectionId, setEditingSectionId] = useState<number | null>(null);
    const [lessonForm, setLessonForm] = useState<LessonUpsertPayload>(EMPTY_LESSON);
    const [editingLessonId, setEditingLessonId] = useState<number | null>(null);
    const [assignment, setAssignment] = useState<AssignmentDetail | null>(null);
    const [assignmentForm, setAssignmentForm] = useState<AssignmentUpsertPayload>(EMPTY_ASSIGNMENT);
    const [quiz, setQuiz] = useState<QuizDetail | null>(null);
    const [quizForm, setQuizForm] = useState<QuizUpsertPayload>(EMPTY_QUIZ);
    const [questionForm, setQuestionForm] = useState<QuestionUpsertPayload>(EMPTY_QUESTION);
    const [editingQuestionId, setEditingQuestionId] = useState<number | null>(null);
    const [answerForms, setAnswerForms] = useState<Record<number, AnswerUpsertPayload>>({});
    const [editingAnswerId, setEditingAnswerId] = useState<number | null>(null);
    const [editingAnswerQuestionId, setEditingAnswerQuestionId] = useState<number | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const allLessons = Object.values(lessonsBySection).flat();
    const selectedLesson = allLessons.find((lesson) => lesson.id === selectedLessonId) ?? null;

    const resetMessages = () => {
        setError('');
        setSuccess('');
    };

    const syncAnswerForms = (questions: QuizQuestion[]) => {
        setAnswerForms(Object.fromEntries(questions.map((question) => [question.id, EMPTY_ANSWER])));
        setEditingAnswerId(null);
        setEditingAnswerQuestionId(null);
    };

    const loadLinkedContent = useCallback(async (lesson: LessonDetail | null) => {
        setAssignment(null);
        setQuiz(null);
        setAssignmentForm(EMPTY_ASSIGNMENT);
        setQuizForm(EMPTY_QUIZ);
        setQuestionForm(EMPTY_QUESTION);
        setEditingQuestionId(null);
        syncAnswerForms([]);

        if (!lesson) return;

        if (lesson.assignment_id) {
            const data = await assignmentService.getAssignment(lesson.assignment_id);
            setAssignment(data);
            setAssignmentForm({
                title: data.title,
                description: data.description,
                starter_code: data.starter_code,
                max_score: data.max_score,
                deadline: data.deadline,
            });
        }
        if (lesson.quiz_id) {
            const data = await quizService.getQuiz(lesson.quiz_id);
            setQuiz(data);
            setQuizForm({
                title: data.title,
                description: data.description,
                passing_score: data.passing_score,
            });
            syncAnswerForms(data.questions);
        }
    }, []);

    const loadStructure = useCallback(async () => {
        if (!id) return;

        setIsLoading(true);
        setError('');
        try {
            const [courseData, sectionItems] = await Promise.all([
                courseService.getCourseById(id),
                courseService.getCourseSections(id),
            ]);
            const lessonPairs = await Promise.all(
                sectionItems.map(async (section) => {
                    const lessons = await courseService.getSectionLessons(section.id);
                    const lessonDetails = await Promise.all(
                        lessons.map((lesson: Lesson) => courseService.getLessonById(lesson.id)),
                    );
                    return [section.id, lessonDetails] as const;
                }),
            );
            const nextLessonsBySection = Object.fromEntries(lessonPairs);
            const nextAllLessons = Object.values(nextLessonsBySection).flat();

            setCourse(courseData);
            setSections(sectionItems);
            setLessonsBySection(nextLessonsBySection);
            setSelectedSectionId((current) => current ?? sectionItems[0]?.id ?? null);
            setSelectedLessonId((current) => current ?? nextAllLessons[0]?.id ?? null);
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsLoading(false);
        }
    }, [id]);

    useEffect(() => {
        queueMicrotask(() => {
            void loadStructure();
        });
    }, [loadStructure]);

    useEffect(() => {
        const loadSelectedLinkedContent = async () => {
            try {
                await loadLinkedContent(selectedLesson);
            } catch (err) {
                setError(getApiErrorMessage(err));
            }
        };

        void loadSelectedLinkedContent();
    }, [loadLinkedContent, selectedLesson]);

    const reloadSelectedLinkedContent = async () => {
        await loadLinkedContent(selectedLesson);
    };

    const saveSection = async (event: FormEvent) => {
        event.preventDefault();
        if (!id || !sectionForm.title.trim()) {
            setError('Section title is required.');
            return;
        }

        setIsSaving(true);
        resetMessages();
        try {
            if (editingSectionId) {
                await courseService.updateSection(editingSectionId, sectionForm);
                setSuccess('Section updated.');
            } else {
                await courseService.createSection(id, sectionForm);
                setSuccess('Section created.');
            }
            setSectionForm(EMPTY_SECTION);
            setEditingSectionId(null);
            await loadStructure();
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    const editSection = (section: Section) => {
        setEditingSectionId(section.id);
        setSectionForm({ title: section.title, description: section.description, order: section.order });
    };

    const deleteSection = async (section: Section) => {
        if (!window.confirm(`Delete section "${section.title}"?`)) return;
        setIsSaving(true);
        resetMessages();
        try {
            await courseService.deleteSection(section.id);
            setSuccess('Section deleted.');
            await loadStructure();
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    const saveLesson = async (event: FormEvent) => {
        event.preventDefault();
        const targetSectionId = selectedSectionId;
        if (!targetSectionId || !lessonForm.title.trim()) {
            setError('Select section and enter lesson title.');
            return;
        }
        if (lessonForm.type === 'video' && !lessonForm.video_url.trim()) {
            setError('Video URL is required for video lessons.');
            return;
        }

        setIsSaving(true);
        resetMessages();
        try {
            if (editingLessonId) {
                await courseService.updateLesson(editingLessonId, lessonForm);
                setSuccess('Lesson updated.');
            } else {
                await courseService.createLesson(targetSectionId, lessonForm);
                setSuccess('Lesson created.');
            }
            setLessonForm(EMPTY_LESSON);
            setEditingLessonId(null);
            await loadStructure();
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    const editLesson = (lesson: LessonDetail) => {
        setEditingLessonId(lesson.id);
        setSelectedSectionId(lesson.section);
        setSelectedLessonId(lesson.id);
        setLessonForm({
            title: lesson.title,
            description: lesson.description,
            type: lesson.type,
            content: lesson.content,
            video_url: lesson.video_url,
            duration: lesson.duration,
            order: lesson.order,
            is_free: lesson.is_free,
        });
    };

    const deleteLesson = async (lesson: LessonDetail) => {
        if (!window.confirm(`Delete lesson "${lesson.title}"?`)) return;
        setIsSaving(true);
        resetMessages();
        try {
            await courseService.deleteLesson(lesson.id);
            setSuccess('Lesson deleted.');
            await loadStructure();
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    const saveAssignment = async (event: FormEvent) => {
        event.preventDefault();
        if (!selectedLesson || selectedLesson.type !== 'assignment') {
            setError('Select an assignment lesson first.');
            return;
        }

        setIsSaving(true);
        resetMessages();
        try {
            if (assignment) {
                await assignmentService.updateAssignment(assignment.id, assignmentForm);
                setSuccess('Assignment updated.');
            } else {
                setAssignment(await assignmentService.createAssignment(selectedLesson.id, assignmentForm));
                setSuccess('Assignment created.');
            }
            await loadStructure();
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    const deleteAssignment = async () => {
        if (!assignment || !window.confirm(`Delete assignment "${assignment.title}"?`)) return;
        setIsSaving(true);
        resetMessages();
        try {
            await assignmentService.deleteAssignment(assignment.id);
            setAssignment(null);
            setAssignmentForm(EMPTY_ASSIGNMENT);
            setSuccess('Assignment deleted.');
            await loadStructure();
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    const saveQuiz = async (event: FormEvent) => {
        event.preventDefault();
        if (!selectedLesson || selectedLesson.type !== 'quiz') {
            setError('Select a quiz lesson first.');
            return;
        }

        setIsSaving(true);
        resetMessages();
        try {
            const savedQuiz = quiz
                ? await quizService.updateQuiz(quiz.id, quizForm)
                : await quizService.createQuiz(selectedLesson.id, quizForm);
            setQuiz(savedQuiz);
            syncAnswerForms(savedQuiz.questions);
            setSuccess(quiz ? 'Quiz updated.' : 'Quiz created.');
            await loadStructure();
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    const deleteQuiz = async () => {
        if (!quiz || !window.confirm(`Delete quiz "${quiz.title}"?`)) return;
        setIsSaving(true);
        resetMessages();
        try {
            await quizService.deleteQuiz(quiz.id);
            setQuiz(null);
            setQuizForm(EMPTY_QUIZ);
            setSuccess('Quiz deleted.');
            await loadStructure();
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    const saveQuestion = async (event: FormEvent) => {
        event.preventDefault();
        if (!quiz || !questionForm.question.trim()) {
            setError('Create a quiz and enter a question first.');
            return;
        }

        setIsSaving(true);
        resetMessages();
        try {
            if (editingQuestionId) {
                await quizService.updateQuestion(editingQuestionId, questionForm);
                setSuccess('Question updated.');
            } else {
                await quizService.createQuestion(quiz.id, questionForm);
                setSuccess('Question created.');
            }
            setQuestionForm(EMPTY_QUESTION);
            setEditingQuestionId(null);
            await reloadSelectedLinkedContent();
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    const editQuestion = (question: QuizQuestion) => {
        setEditingQuestionId(question.id);
        setQuestionForm({
            question: question.question,
            type: question.type,
            points: question.points,
            order: question.order,
            text_answer: question.text_answer ?? '',
        });
    };

    const deleteQuestion = async (question: QuizQuestion) => {
        if (!window.confirm(`Delete question "${question.question}"?`)) return;
        setIsSaving(true);
        resetMessages();
        try {
            await quizService.deleteQuestion(question.id);
            setSuccess('Question deleted.');
            await reloadSelectedLinkedContent();
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    const updateAnswerForm = (questionId: number, patch: Partial<AnswerUpsertPayload>) => {
        setAnswerForms((current) => ({
            ...current,
            [questionId]: { ...(current[questionId] ?? EMPTY_ANSWER), ...patch },
        }));
    };

    const saveAnswer = async (event: FormEvent, questionId: number) => {
        event.preventDefault();
        const form = answerForms[questionId] ?? EMPTY_ANSWER;
        if (!form.text.trim()) {
            setError('Answer text is required.');
            return;
        }

        setIsSaving(true);
        resetMessages();
        try {
            if (editingAnswerId && editingAnswerQuestionId === questionId) {
                await quizService.updateAnswer(editingAnswerId, form);
                setSuccess('Answer updated.');
            } else {
                await quizService.createAnswer(questionId, form);
                setSuccess('Answer created.');
            }
            updateAnswerForm(questionId, EMPTY_ANSWER);
            setEditingAnswerId(null);
            setEditingAnswerQuestionId(null);
            await reloadSelectedLinkedContent();
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    const editAnswer = (questionId: number, answer: AnswerOption) => {
        setEditingAnswerId(answer.id);
        setEditingAnswerQuestionId(questionId);
        updateAnswerForm(questionId, { text: answer.text, is_correct: Boolean(answer.is_correct) });
    };

    const deleteAnswer = async (answer: AnswerOption) => {
        if (!window.confirm(`Delete answer "${answer.text}"?`)) return;
        setIsSaving(true);
        resetMessages();
        try {
            await quizService.deleteAnswer(answer.id);
            setSuccess('Answer deleted.');
            await reloadSelectedLinkedContent();
        } catch (err) {
            setError(getApiErrorMessage(err));
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) return <Loader />;
    if (!course) return <EmptyState title="Course not found" variant="error" />;

    return (
        <div className={styles.page}>
            <div className={styles.header}>
                <div>
                    <h1>{course.title}</h1>
                    <p>Manage sections, lessons, assignments and quizzes.</p>
                </div>
                <Link to="/teacher/courses">
                    <Button type="button" variant="secondary">Back</Button>
                </Link>
            </div>

            {error && <EmptyState title="Action failed" description={error} variant="error" />}
            {success && <p className={styles.success}>{success}</p>}

            <div className={styles.columns}>
                <section className={styles.panel}>
                    <h2>Sections</h2>
                    <form className={styles.form} onSubmit={(event) => void saveSection(event)}>
                        <Input label="Title" value={sectionForm.title} onChange={(event) => setSectionForm({ ...sectionForm, title: event.target.value })} />
                        <Input label="Description" value={sectionForm.description} onChange={(event) => setSectionForm({ ...sectionForm, description: event.target.value })} />
                        <Input label="Order" type="number" min={1} value={sectionForm.order} onChange={(event) => setSectionForm({ ...sectionForm, order: Number(event.target.value) })} />
                        <Button type="submit" isLoading={isSaving}>{editingSectionId ? 'Save section' : 'Add section'}</Button>
                    </form>

                    <div className={styles.list}>
                        {sections.map((section) => (
                            <div key={section.id} className={styles.row}>
                                <button type="button" className={styles.rowButton} onClick={() => setSelectedSectionId(section.id)}>
                                    {section.order}. {section.title}
                                </button>
                                <div className={styles.actions}>
                                    <Button type="button" variant="secondary" onClick={() => editSection(section)}>Edit</Button>
                                    <Button type="button" variant="danger" onClick={() => void deleteSection(section)}>Delete</Button>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                <section className={styles.panel}>
                    <h2>Lessons</h2>
                    <form className={styles.form} onSubmit={(event) => void saveLesson(event)}>
                        <label className={styles.field}>
                            <span>Section</span>
                            <select value={selectedSectionId ?? 0} onChange={(event) => setSelectedSectionId(Number(event.target.value) || null)}>
                                <option value={0}>Select section</option>
                                {sections.map((section) => (
                                    <option key={section.id} value={section.id}>{section.title}</option>
                                ))}
                            </select>
                        </label>
                        <Input label="Title" value={lessonForm.title} onChange={(event) => setLessonForm({ ...lessonForm, title: event.target.value })} />
                        <label className={styles.field}>
                            <span>Type</span>
                            <select value={lessonForm.type} onChange={(event) => setLessonForm({ ...lessonForm, type: event.target.value as LessonUpsertPayload['type'] })}>
                                <option value="text">Text</option>
                                <option value="video">Video</option>
                                <option value="assignment">Assignment</option>
                                <option value="quiz">Quiz</option>
                                <option value="file">File</option>
                                <option value="project">Project</option>
                            </select>
                        </label>
                        <label className={styles.field}>
                            <span>Content</span>
                            <textarea value={lessonForm.content} rows={4} onChange={(event) => setLessonForm({ ...lessonForm, content: event.target.value })} />
                        </label>
                        <Input label="Video URL" value={lessonForm.video_url} onChange={(event) => setLessonForm({ ...lessonForm, video_url: event.target.value })} />
                        <div className={styles.inline}>
                            <Input label="Duration" type="number" min={1} value={lessonForm.duration} onChange={(event) => setLessonForm({ ...lessonForm, duration: Number(event.target.value) })} />
                            <Input label="Order" type="number" min={1} value={lessonForm.order} onChange={(event) => setLessonForm({ ...lessonForm, order: Number(event.target.value) })} />
                            <label className={styles.checkbox}>
                                <input type="checkbox" checked={lessonForm.is_free} onChange={(event) => setLessonForm({ ...lessonForm, is_free: event.target.checked })} />
                                Free
                            </label>
                        </div>
                        <Button type="submit" isLoading={isSaving}>{editingLessonId ? 'Save lesson' : 'Add lesson'}</Button>
                    </form>

                    <div className={styles.list}>
                        {allLessons.map((lesson) => (
                            <div key={lesson.id} className={styles.row}>
                                <button type="button" className={styles.rowButton} onClick={() => setSelectedLessonId(lesson.id)}>
                                    {lesson.order}. {lesson.title} - {lesson.type}
                                </button>
                                <div className={styles.actions}>
                                    <Button type="button" variant="secondary" onClick={() => editLesson(lesson)}>Edit</Button>
                                    <Button type="button" variant="danger" onClick={() => void deleteLesson(lesson)}>Delete</Button>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            </div>

            <section className={styles.panel}>
                <h2>Assignment / Quiz</h2>
                {!selectedLesson ? (
                    <EmptyState title="Select a lesson" description="Assignment and quiz tools are shown for the selected lesson." />
                ) : selectedLesson.type === 'assignment' ? (
                    <form className={styles.form} onSubmit={(event) => void saveAssignment(event)}>
                        <Input label="Title" value={assignmentForm.title} onChange={(event) => setAssignmentForm({ ...assignmentForm, title: event.target.value })} />
                        <label className={styles.field}>
                            <span>Description</span>
                            <textarea value={assignmentForm.description} rows={4} onChange={(event) => setAssignmentForm({ ...assignmentForm, description: event.target.value })} />
                        </label>
                        <label className={styles.field}>
                            <span>Starter code</span>
                            <textarea value={assignmentForm.starter_code} rows={4} onChange={(event) => setAssignmentForm({ ...assignmentForm, starter_code: event.target.value })} />
                        </label>
                        <Input label="Max score" type="number" min={1} value={assignmentForm.max_score} onChange={(event) => setAssignmentForm({ ...assignmentForm, max_score: Number(event.target.value) })} />
                        <div className={styles.actions}>
                            <Button type="submit" isLoading={isSaving}>{assignment ? 'Save assignment' : 'Create assignment'}</Button>
                            {assignment && (
                                <Link to={`/teacher/assignments/${assignment.id}/submissions`}>
                                    <Button type="button" variant="secondary">Review submissions</Button>
                                </Link>
                            )}
                            {assignment && <Button type="button" variant="danger" onClick={() => void deleteAssignment()}>Delete assignment</Button>}
                        </div>
                    </form>
                ) : selectedLesson.type === 'quiz' ? (
                    <div className={styles.quizGrid}>
                        <form className={styles.form} onSubmit={(event) => void saveQuiz(event)}>
                            <Input label="Title" value={quizForm.title} onChange={(event) => setQuizForm({ ...quizForm, title: event.target.value })} />
                            <Input label="Description" value={quizForm.description} onChange={(event) => setQuizForm({ ...quizForm, description: event.target.value })} />
                            <Input label="Passing score" type="number" min={0} max={100} value={quizForm.passing_score} onChange={(event) => setQuizForm({ ...quizForm, passing_score: Number(event.target.value) })} />
                            <div className={styles.actions}>
                                <Button type="submit" isLoading={isSaving}>{quiz ? 'Save quiz' : 'Create quiz'}</Button>
                                {quiz && <Button type="button" variant="danger" onClick={() => void deleteQuiz()}>Delete quiz</Button>}
                            </div>
                        </form>

                        {quiz ? (
                            <div className={styles.quizEditor}>
                                <form className={styles.form} onSubmit={(event) => void saveQuestion(event)}>
                                    <h3>{editingQuestionId ? 'Edit question' : 'Add question'}</h3>
                                    <Input label="Question" value={questionForm.question} onChange={(event) => setQuestionForm({ ...questionForm, question: event.target.value })} />
                                    <label className={styles.field}>
                                        <span>Type</span>
                                        <select value={questionForm.type} onChange={(event) => setQuestionForm({ ...questionForm, type: event.target.value as QuestionType })}>
                                            <option value="single">Single choice</option>
                                            <option value="multiple">Multiple choice</option>
                                            <option value="text">Text</option>
                                        </select>
                                    </label>
                                    <div className={styles.inline}>
                                        <Input label="Points" type="number" min={1} value={questionForm.points} onChange={(event) => setQuestionForm({ ...questionForm, points: Number(event.target.value) })} />
                                        <Input label="Order" type="number" min={1} value={questionForm.order} onChange={(event) => setQuestionForm({ ...questionForm, order: Number(event.target.value) })} />
                                    </div>
                                    {questionForm.type === 'text' && (
                                        <Input label="Expected answer" value={questionForm.text_answer} onChange={(event) => setQuestionForm({ ...questionForm, text_answer: event.target.value })} />
                                    )}
                                    <div className={styles.actions}>
                                        <Button type="submit" isLoading={isSaving}>{editingQuestionId ? 'Save question' : 'Add question'}</Button>
                                        {editingQuestionId && (
                                            <Button type="button" variant="secondary" onClick={() => { setEditingQuestionId(null); setQuestionForm(EMPTY_QUESTION); }}>
                                                Cancel
                                            </Button>
                                        )}
                                    </div>
                                </form>

                                {quiz.questions.length === 0 ? (
                                    <EmptyState title="No questions" />
                                ) : quiz.questions.map((question) => {
                                    const answerForm = answerForms[question.id] ?? EMPTY_ANSWER;
                                    const isEditingThisAnswer = editingAnswerQuestionId === question.id;
                                    return (
                                        <article key={question.id} className={styles.questionBlock}>
                                            <div className={styles.questionHeader}>
                                                <div>
                                                    <h3>{question.order}. {question.question}</h3>
                                                    <p>{question.type} | {question.points} points</p>
                                                </div>
                                                <div className={styles.actions}>
                                                    <Button type="button" variant="secondary" onClick={() => editQuestion(question)}>Edit</Button>
                                                    <Button type="button" variant="danger" onClick={() => void deleteQuestion(question)}>Delete</Button>
                                                </div>
                                            </div>

                                            {question.type !== 'text' && (
                                                <>
                                                    <div className={styles.answerList}>
                                                        {question.answers.map((answer) => (
                                                            <div key={answer.id} className={styles.answerRow}>
                                                                <span>{answer.text}</span>
                                                                <span>{answer.is_correct ? 'Correct' : 'Incorrect'}</span>
                                                                <div className={styles.actions}>
                                                                    <Button type="button" variant="secondary" onClick={() => editAnswer(question.id, answer)}>Edit</Button>
                                                                    <Button type="button" variant="danger" onClick={() => void deleteAnswer(answer)}>Delete</Button>
                                                                </div>
                                                            </div>
                                                        ))}
                                                    </div>
                                                    <form className={styles.answerForm} onSubmit={(event) => void saveAnswer(event, question.id)}>
                                                        <Input label={isEditingThisAnswer ? 'Edit answer' : 'New answer'} value={answerForm.text} onChange={(event) => updateAnswerForm(question.id, { text: event.target.value })} />
                                                        <label className={styles.checkbox}>
                                                            <input type="checkbox" checked={answerForm.is_correct} onChange={(event) => updateAnswerForm(question.id, { is_correct: event.target.checked })} />
                                                            Correct
                                                        </label>
                                                        <Button type="submit" isLoading={isSaving}>{isEditingThisAnswer ? 'Save answer' : 'Add answer'}</Button>
                                                    </form>
                                                </>
                                            )}
                                        </article>
                                    );
                                })}
                            </div>
                        ) : (
                            <EmptyState title="Create quiz first" />
                        )}
                    </div>
                ) : (
                    <EmptyState title="No linked CRUD for this lesson type" description="Choose an assignment or quiz lesson." />
                )}
            </section>
        </div>
    );
};

export default CourseManage;
