import { api } from './api';
import type { PaginatedResponse } from '../types/common';
import type { AdminUser, AdminUserFilters, AdminUserUpdatePayload } from '../types/user';


export const adminService = {
    getUsers: (filters: AdminUserFilters = {}) =>
        api
            .get<PaginatedResponse<AdminUser>>('admin/users/', { params: filters })
            .then((res) => res.data),

    getUser: (id: number | string) =>
        api.get<AdminUser>(`admin/users/${id}/`).then((res) => res.data),

    updateUser: (id: number | string, payload: AdminUserUpdatePayload) =>
        api.patch<AdminUser>(`admin/users/${id}/`, payload).then((res) => res.data),
};
