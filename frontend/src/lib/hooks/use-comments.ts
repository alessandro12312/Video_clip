"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import { commentsApi } from "@/lib/api/comments";
import type { CreateCommentData } from "@/types";

export function useComments(videoId: number, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: queryKeys.comments.byVideo(videoId),
    enabled: options?.enabled,
    queryFn: async () => {
      // Fetch all comments for a video (may need multiple pages)
      const firstPage = await commentsApi.getByVideo(videoId, 1);
      const allComments = [...firstPage.results];

      // If there are more pages, fetch them all (comments are pre-loaded for popup map)
      let nextPage = 2;
      while (allComments.length < firstPage.count) {
        const page = await commentsApi.getByVideo(videoId, nextPage);
        allComments.push(...page.results);
        nextPage++;
      }

      return allComments;
    },
    staleTime: 60_000,
  });
}

export function useCreateComment(videoId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateCommentData) => commentsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.comments.byVideo(videoId),
      });
    },
  });
}

export function useDeleteComment(videoId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (commentId: number) => commentsApi.delete(commentId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.comments.byVideo(videoId),
      });
    },
  });
}
