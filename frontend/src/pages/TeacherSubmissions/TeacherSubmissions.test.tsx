import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { assignmentService } from '../../services/assignmentService';
import TeacherSubmissions from './TeacherSubmissions';

vi.mock('../../services/assignmentService', () => ({
    assignmentService: {
        getAssignment: vi.fn(),
        getSubmissions: vi.fn(),
        reviewSubmission: vi.fn(),
    },
}));

const assignment = {
    id: 10,
    lesson: 5,
    title: 'Build API',
    description: 'Task',
    starter_code: '',
    max_score: 100,
    deadline: null,
};

const submission = {
    id: 20,
    assignment: 10,
    student: 3,
    student_name: 'Student One',
    code: 'print("hello")',
    status: 'pending' as const,
    score: null,
    teacher_comment: '',
    created_at: '2026-01-01',
    updated_at: '2026-01-01',
};

describe('TeacherSubmissions', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        vi.mocked(assignmentService.getAssignment).mockResolvedValue(assignment);
        vi.mocked(assignmentService.getSubmissions).mockResolvedValue([submission]);
    });

    it('renders submissions and sends review payload', async () => {
        const user = userEvent.setup();
        vi.mocked(assignmentService.reviewSubmission).mockResolvedValue({
            ...submission,
            status: 'accepted',
            score: 95,
            teacher_comment: 'Good',
        });

        render(
            <MemoryRouter initialEntries={['/teacher/assignments/10/submissions']}>
                <Routes>
                    <Route path="/teacher/assignments/:id/submissions" element={<TeacherSubmissions />} />
                </Routes>
            </MemoryRouter>,
        );

        expect(await screen.findByText('Student One')).toBeInTheDocument();
        await user.selectOptions(screen.getByLabelText('Статус'), 'accepted');
        await user.type(screen.getByLabelText('Оценка / 100'), '95');
        await user.type(screen.getByLabelText('Комментарий'), 'Good');
        await user.click(screen.getByRole('button', { name: 'Сохранить' }));

        await waitFor(() => {
            expect(assignmentService.reviewSubmission).toHaveBeenCalledWith(20, {
                status: 'accepted',
                score: 95,
                teacher_comment: 'Good',
            });
        });
    });
});
