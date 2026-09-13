import type { CourseLevel, CourseStatus, Lesson } from '../types/course';
import type { UserRole } from '../types/user';
import type { SubmissionStatus } from '../types/assignment';
import type { QuestionType } from '../types/quiz';
import type { NotificationType } from '../types/notification';

export const ROLE_LABELS: Record<UserRole, string> = {
    student: 'Студент',
    teacher: 'Преподаватель',
    admin: 'Администратор',
};

export const COURSE_STATUS_LABELS: Record<CourseStatus, string> = {
    draft: 'Черновик',
    published: 'Опубликован',
    archived: 'В архиве',
};

export const COURSE_LEVEL_LABELS: Record<CourseLevel, string> = {
    beginner: 'Начальный',
    junior: 'Junior',
    middle: 'Middle',
    advanced: 'Продвинутый',
};

export const LESSON_TYPE_LABELS: Record<Lesson['type'], string> = {
    text: 'Текст',
    video: 'Видео',
    assignment: 'Задание',
    quiz: 'Тест',
    file: 'Файл',
    project: 'Проект',
};

export const SUBMISSION_STATUS_LABELS: Record<SubmissionStatus, string> = {
    pending: 'На проверке',
    accepted: 'Принято',
    revision: 'На доработку',
};

export const QUESTION_TYPE_LABELS: Record<QuestionType, string> = {
    single: 'Один вариант',
    multiple: 'Несколько вариантов',
    text: 'Текстовый ответ',
};

export const NOTIFICATION_TYPE_LABELS: Record<NotificationType, string> = {
    course: 'Курс',
    lesson: 'Урок',
    assignment: 'Задание',
    submission: 'Решение',
    quiz: 'Тест',
    certificate: 'Сертификат',
    system: 'Система',
};

export function pluralizeRu(value: number, forms: [string, string, string]) {
    const abs = Math.abs(value) % 100;
    const last = abs % 10;
    if (abs > 10 && abs < 20) return forms[2];
    if (last > 1 && last < 5) return forms[1];
    if (last === 1) return forms[0];
    return forms[2];
}
