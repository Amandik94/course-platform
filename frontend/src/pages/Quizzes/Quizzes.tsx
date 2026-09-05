import { type FormEvent, useState } from 'react';
import { useParams } from 'react-router-dom';
import Button from '../../components/Button/Button';
import Loader from '../../components/Loader/Loader';
import EmptyState from '../../components/EmptyState/EmptyState';
import { useQuiz } from '../../features/quizzes/useQuiz';
import type { QuizAnswerDraft } from '../../types/quiz';
import styles from './Quizzes.module.css';

const QuizPage = () => {
    const { id } = useParams<{ id: string }>();
    const { quiz, isLoading, error, result, submitAnswers, isSubmitting, submitError } = useQuiz(id);

    // draft хранится как словарь question_id -> частичный ответ,
    // чтобы удобно обновлять по одному вопросу за раз
    const [draft, setDraft] = useState<Record<number, QuizAnswerDraft>>({});

    if (isLoading) return <Loader text="Загрузка теста..." />;
    if (error || !quiz) return <EmptyState title="Тест не найден" description={error ?? undefined} />;

    const setSingleAnswer = (questionId: number, answerId: number) => {
        setDraft((prev) => ({ ...prev, [questionId]: { question_id: questionId, answer_id: answerId } }));
    };

    const toggleMultipleAnswer = (questionId: number, answerId: number) => {
        setDraft((prev) => {
            const current = prev[questionId]?.answer_ids ?? [];
            const next = current.includes(answerId)
                ? current.filter((a) => a !== answerId)
                : [...current, answerId];
            return { ...prev, [questionId]: { question_id: questionId, answer_ids: next } };
        });
    };

    const setTextAnswer = (questionId: number, text: string) => {
        setDraft((prev) => ({ ...prev, [questionId]: { question_id: questionId, text } }));
    };

    const handleSubmit = (event: FormEvent) => {
        event.preventDefault();
        submitAnswers(Object.values(draft));
    };

    // --- Результат уже получен — показываем итог вместо формы ---
    if (result) {
        return (
            <div className={`${styles.page} container`}>
                <div className={`${styles.resultCard} ${result.passed ? styles.resultPassed : styles.resultFailed}`}>
                    <h2>{result.passed ? 'Тест пройден! 🎉' : 'Тест не пройден'}</h2>
                    <div className={styles.resultScore}>{result.score}%</div>
                    <p>Проходной балл: {quiz.passing_score}%</p>
                </div>

                <h2 style={{ marginTop: 'var(--spacing-lg)' }}>Разбор ответов</h2>
                {quiz.questions.map((question) => {
                    const entry = result.answers_snapshot[String(question.id)];
                    return (
                        <div key={question.id} className={styles.question}>
                            <div className={styles.questionText}>{question.question}</div>
                            <p className={entry?.is_correct ? styles.optionCorrect : styles.optionIncorrect}>
                                {entry?.is_correct ? '✓ Правильно' : '✗ Неправильно'}
                            </p>
                        </div>
                    );
                })}
            </div>
        );
    }

    // --- Форма прохождения теста ---
    return (
        <div className={`${styles.page} container`}>
            <h1>{quiz.title}</h1>
            {quiz.description && <p>{quiz.description}</p>}

            <form onSubmit={handleSubmit}>
                {submitError && <p className={styles.optionIncorrect}>{submitError}</p>}

                {quiz.questions.map((question) => (
                    <div key={question.id} className={styles.question}>
                        <div className={styles.questionText}>
                            {question.question} <span>({question.points} балл.)</span>
                        </div>

                        {question.type === 'single' &&
                            question.answers.map((answer) => (
                                <label key={answer.id} className={styles.optionRow}>
                                    <input
                                        type="radio"
                                        name={`question-${question.id}`}
                                        checked={draft[question.id]?.answer_id === answer.id}
                                        onChange={() => setSingleAnswer(question.id, answer.id)}
                                    />
                                    {answer.text}
                                </label>
                            ))}

                        {question.type === 'multiple' &&
                            question.answers.map((answer) => (
                                <label key={answer.id} className={styles.optionRow}>
                                    <input
                                        type="checkbox"
                                        checked={(draft[question.id]?.answer_ids ?? []).includes(answer.id)}
                                        onChange={() => toggleMultipleAnswer(question.id, answer.id)}
                                    />
                                    {answer.text}
                                </label>
                            ))}

                        {question.type === 'text' && (
                            <input
                                type="text"
                                className={styles.textAnswerInput}
                                value={draft[question.id]?.text ?? ''}
                                onChange={(e) => setTextAnswer(question.id, e.target.value)}
                            />
                        )}
                    </div>
                ))}

                <Button type="submit" isLoading={isSubmitting} fullWidth>
                    Завершить тест
                </Button>
            </form>
        </div>
    );
};

export default QuizPage;