"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { queryKeys } from "@/lib/query-keys";
import { commentsApi } from "@/lib/api/comments";
import type { CreateCommentData, Comment } from "@/types";

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

export function useLikeComment(videoId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (commentId: number) => commentsApi.like(commentId),
    onMutate: async (commentId) => {
      const queryKey = queryKeys.comments.byVideo(videoId);
      await queryClient.cancelQueries({ queryKey });

      const previous = queryClient.getQueryData<Comment[]>(queryKey);

      queryClient.setQueryData<Comment[]>(queryKey, (old) =>
        old?.map((c) =>
          c.id === commentId
            ? { ...c, like_count: c.like_count + 1, is_liked_by_me: true }
            : c
        )
      );

      return { previous };
    },
    onError: (err, _commentId, context) => {
      if ((err as { response?: { status?: number } })?.response?.status === 409) return;
      if (context?.previous) {
        queryClient.setQueryData(queryKeys.comments.byVideo(videoId), context.previous);
      }
      toast.error("Errore nel like al commento, riprova.");
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.comments.byVideo(videoId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.videos.popupComments(videoId) });
    },
  });
}

export function useUnlikeComment(videoId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (commentId: number) => commentsApi.unlike(commentId),
    onMutate: async (commentId) => {
      const queryKey = queryKeys.comments.byVideo(videoId);
      await queryClient.cancelQueries({ queryKey });

      const previous = queryClient.getQueryData<Comment[]>(queryKey);

      queryClient.setQueryData<Comment[]>(queryKey, (old) =>
        old?.map((c) =>
          c.id === commentId
            ? { ...c, like_count: Math.max(0, c.like_count - 1), is_liked_by_me: false }
            : c
        )
      );

      return { previous };
    },
    onError: (_err, _commentId, context) => {
      if (context?.previous) {
        queryClient.setQueryData(queryKeys.comments.byVideo(videoId), context.previous);
      }
      toast.error("Errore nella rimozione del like, riprova.");
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.comments.byVideo(videoId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.videos.popupComments(videoId) });
    },
  });
}
