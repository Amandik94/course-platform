import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { adminService } from '../../services/adminService';
import { AdminUserDetail, AdminUsersList } from './AdminUsers';

vi.mock('../../services/adminService', () => ({
    adminService: {
        getUsers: vi.fn(),
        getUser: vi.fn(),
        updateUser: vi.fn(),
    },
}));

const adminUser = {
    id: 1,
    email: 'admin@test.com',
    first_name: 'Admin',
    last_name: 'User',
    full_name: 'Admin User',
    avatar: null,
    role: 'admin' as const,
    is_active: true,
    is_staff: true,
    created_at: '2026-01-01',
    updated_at: '2026-01-01',
};

describe('AdminUsers', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        vi.mocked(adminService.getUsers).mockResolvedValue({
            count: 1,
            next: null,
            previous: null,
            results: [adminUser],
        });
    });

    it('renders users from paginated API', async () => {
        render(<MemoryRouter><AdminUsersList /></MemoryRouter>);

        expect(await screen.findByText('admin@test.com')).toBeInTheDocument();
        expect(screen.getByText('Admin User')).toBeInTheDocument();
    });

    it('calls block action', async () => {
        const user = userEvent.setup();
        vi.mocked(adminService.updateUser).mockResolvedValue({ ...adminUser, is_active: false });

        render(<MemoryRouter><AdminUsersList /></MemoryRouter>);
        await screen.findByText('admin@test.com');
        await user.click(screen.getByRole('button', { name: 'Block' }));

        await waitFor(() => {
            expect(adminService.updateUser).toHaveBeenCalledWith(1, { is_active: false });
        });
    });

    it('updates user detail', async () => {
        const user = userEvent.setup();
        vi.mocked(adminService.getUser).mockResolvedValue(adminUser);
        vi.mocked(adminService.updateUser).mockResolvedValue({ ...adminUser, role: 'teacher' });

        render(
            <MemoryRouter initialEntries={['/admin/users/1']}>
                <Routes>
                    <Route path="/admin/users/:id" element={<AdminUserDetail />} />
                </Routes>
            </MemoryRouter>,
        );
        await screen.findByText('admin@test.com');
        await user.selectOptions(screen.getByLabelText('Role'), 'teacher');
        await user.click(screen.getByRole('button', { name: 'Save user' }));

        await waitFor(() => {
            expect(adminService.updateUser).toHaveBeenCalledWith('1', expect.objectContaining({ role: 'teacher' }));
        });
    });
});
