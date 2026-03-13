import { apiClient } from "./client";
import type { PaginatedResponse, Notification } from "@/types";

export const notificationsApi = {
  getAll: (page = 1) =>
    apiClient
      .get<PaginatedResponse<Notification>>("/notifications/", { params: { page } })
      .then((r) => r.data),

  getUnreadCount: () =>
    apiClient
      .get<{ count: number }>("/notifications/unread-count/")
      .then((r) => r.data),

  markRead: (id: number) =>
    apiClient
      .post<{ detail: string }>(`/notifications/${id}/mark-read/`)
      .then((r) => r.data),

  markAllRead: () =>
    apiClient
      .post<{ detail: string }>("/notifications/mark-all-read/")
      .then((r) => r.data),
};
