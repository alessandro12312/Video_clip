import { apiClient } from "./client";
import type { PaginatedResponse, Comment, CreateCommentData } from "@/types";

export const commentsApi = {
  getByVideo: (videoId: number, page = 1) =>
    apiClient
      .get<PaginatedResponse<Comment>>("/comments/", {
        params: { video: videoId, page },
      })
      .then((r) => r.data),

  create: (data: CreateCommentData) =>
    apiClient.post<Comment>("/comments/", data).then((r) => r.data),

  delete: (id: number) => apiClient.delete(`/comments/${id}/`),
};
