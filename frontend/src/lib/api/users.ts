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
      .post<{ detail: string; is_followed: boolean; followers_count: number }>(
        `/users/${id}/follow/`
      )
      .then((r) => r.data),

  unfollow: (id: number) =>
    apiClient
      .post<{ detail: string; is_followed: boolean; followers_count: number }>(
        `/users/${id}/unfollow/`
      )
      .then((r) => r.data),

  getFollowers: (id: number, page = 1) =>
    apiClient
      .get<PaginatedResponse<User>>(`/users/${id}/followers/`, {
        params: { page },
      })
      .then((r) => r.data),

  getFollowing: (id: number, page = 1) =>
    apiClient
      .get<PaginatedResponse<User>>(`/users/${id}/following/`, {
        params: { page },
      })
      .then((r) => r.data),

  getByUsername: (username: string) =>
    apiClient.get<User>(`/users/by-username/${username}/`).then((r) => r.data),

  updateProfile: (id: number, data: { bio?: string }) =>
    apiClient.patch<User>(`/users/${id}/`, data).then((r) => r.data),
};
