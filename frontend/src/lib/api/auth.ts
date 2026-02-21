import axios from "axios";
import { API_BASE_URL } from "@/lib/constants";
import type { TokenPair, User, UserRegistration } from "@/types";
import { apiClient } from "./client";

export const authApi = {
  login: (username: string, password: string) =>
    axios
      .post<TokenPair>(`${API_BASE_URL}/api/token/`, { username, password })
      .then((r) => r.data),

  register: (data: UserRegistration) =>
    axios
      .post<User>(`${API_BASE_URL}/api/users/`, data)
      .then((r) => r.data),

  refreshToken: (refresh: string) =>
    axios
      .post<{ access: string; refresh?: string }>(`${API_BASE_URL}/api/token/refresh/`, { refresh })
      .then((r) => r.data),

  getCurrentUser: (userId: number) =>
    apiClient.get<User>(`/users/${userId}/`).then((r) => r.data),
};
