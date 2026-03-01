import { apiClient } from "./client";
import type { Rating, CreateRatingData } from "@/types";

export const ratingsApi = {
  create: (data: CreateRatingData) =>
    apiClient.post<Rating>("/ratings/", data).then((r) => r.data),

  update: (id: number, value: number) =>
    apiClient.patch<Rating>(`/ratings/${id}/`, { value }).then((r) => r.data),
};
