import { apiClient } from "./client";
import type { PaginatedResponse, User } from "@/types";

export const usersApi = {
  getAll: (page = 1) =>
    apiClient
      .get<PaginatedResponse<User>>("/users/", { params: { page } })
      .then((r) => r.data),

  search: (query: string) =>
    apiClient
      .get<PaginatedResponse<User>>("/users/", { params: { search: query } })
      .then((r) => r.data),

  getById: (id: number) =>
    apiClient.get<User>(`/users/${id}/`).then((r) => r.data),

  follow: (id: number) =>
    apiClient
      .post<{ detail: string }>(`/users/${id}/follow/`)
      .then((r) => r.data),

  unfollow: (id: number) =>
    apiClient
      .post<{ detail: string }>(`/users/${id}/unfollow/`)
      .then((r) => r.data),

  getFollowers: (id: number) =>
    apiClient.get<User[]>(`/users/${id}/followers/`).then((r) => r.data),

  getFollowing: (id: number) =>
    apiClient.get<User[]>(`/users/${id}/following/`).then((r) => r.data),
};
