"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import { ratingsApi } from "@/lib/api/ratings";
import type { CreateRatingData } from "@/types";

export function useCreateRating(videoId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateRatingData) => ratingsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.videos.detail(videoId),
      });
    },
  });
}
