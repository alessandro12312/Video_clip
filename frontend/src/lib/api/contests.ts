import { apiClient } from "./client";
import type { PaginatedResponse, Video, Contest } from "@/types";

export const contestsApi = {
  list: (params?: { is_closed?: boolean; tag?: string; page?: number }) =>
    apiClient
      .get<PaginatedResponse<Contest>>("/contests/", { params })
      .then((r) => r.data),

  getDetail: (id: number) =>
    apiClient.get<Contest>(`/contests/${id}/`).then((r) => r.data),

  getContestVideos: (contestId: number, page = 1) =>
    apiClient
      .get<PaginatedResponse<Video>>(`/contests/${contestId}/videos/`, {
        params: { page },
      })
      .then((r) => r.data),

  getWinners: (page = 1) =>
    apiClient
      .get<PaginatedResponse<Video>>("/contests/winners/", { params: { page } })
      .then((r) => r.data),
};
