import { create } from 'zustand';

interface NotificationState {
    unreadCount: number;
    setUnreadCount: (count: number) => void;
    decrementUnreadCount: () => void;
    resetNotifications: () => void;
}

export const useNotificationStore = create<NotificationState>((set) => ({
    unreadCount: 0,
    setUnreadCount: (count) => set({ unreadCount: Math.max(0, count) }),
    decrementUnreadCount: () => set((state) => ({ unreadCount: Math.max(0, state.unreadCount - 1) })),
    resetNotifications: () => set({ unreadCount: 0 }),
}));
