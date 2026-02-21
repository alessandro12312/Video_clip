import { apiClient } from "./client";
import type { PaginatedResponse, Video } from "@/types";

export const contestsApi = {
  getWinners: (page = 1) =>
    apiClient
      .get<PaginatedResponse<Video>>("/contests/winners/", { params: { page } })
      .then((r) => r.data),
};
