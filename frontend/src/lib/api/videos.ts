import { apiClient } from "./client";
import type { PaginatedResponse, Video, TopRatedRange, DownloadResponse } from "@/types";

// Normalize response: backend may return a plain array instead of paginated format
function normalizePaginated<T>(data: PaginatedResponse<T> | T[]): PaginatedResponse<T> {
  if (Array.isArray(data)) {
    return { count: data.length, next: null, previous: null, results: data };
  }
  return data;
}

export const videosApi = {
  getAll: (page = 1) =>
    apiClient
      .get<PaginatedResponse<Video>>("/videos/", { params: { page } })
      .then((r) => normalizePaginated(r.data)),

  getByUploader: (uploaderId: number, page = 1) =>
    apiClient
      .get<PaginatedResponse<Video>>("/videos/", { params: { uploader: uploaderId, page } })
      .then((r) => normalizePaginated(r.data)),

  getById: (id: number) =>
    apiClient.get<Video>(`/videos/${id}/`).then((r) => r.data),

  getFollowingFeed: (page = 1) =>
    apiClient
      .get<PaginatedResponse<Video>>("/videos/following/", { params: { page } })
      .then((r) => normalizePaginated(r.data)),

  getTopRated: (range: TopRatedRange = "all", page = 1) =>
    apiClient
      .get<PaginatedResponse<Video>>("/videos/top-rated/", {
        params: { range, page },
      })
      .then((r) => normalizePaginated(r.data)),

  upload: (
    data: FormData,
    onProgress?: (percent: number) => void
  ) =>
    apiClient
      .post<Video>("/videos/", data, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (e) => {
          if (onProgress && e.total) {
            onProgress(Math.round((e.loaded / e.total) * 100));
          }
        },
      })
      .then((r) => r.data),

  incrementViews: (id: number) =>
    apiClient.post<{ views: number }>(`/videos/${id}/views/`).then((r) => r.data),

  download: (id: number) =>
    apiClient.get<DownloadResponse>(`/videos/${id}/download/`).then((r) => r.data),

  delete: (id: number) => apiClient.delete(`/videos/${id}/`),
};
