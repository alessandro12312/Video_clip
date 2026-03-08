"use client";

import { useQuery, useInfiniteQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { queryKeys } from "@/lib/query-keys";
import { videosApi } from "@/lib/api/videos";
import { extractPageFromUrl } from "@/lib/utils";
import type { Comment } from "@/types/comment";
import type { TopRatedRange, Video, PaginatedResponse } from "@/types";

export function useVideo(id: number) {
  return useQuery({
    queryKey: queryKeys.videos.detail(id),
    queryFn: () => videosApi.getById(id),
  });
}

export function useVideoFeed() {
  return useInfiniteQuery({
    queryKey: queryKeys.videos.followingAll,
    queryFn: ({ pageParam = 1 }) => videosApi.getFollowingFeed(pageParam),
    getNextPageParam: (lastPage) => extractPageFromUrl(lastPage.next),
    initialPageParam: 1,
  });
}

export function useTopRatedVideos(range: TopRatedRange = "all") {
  return useInfiniteQuery({
    queryKey: queryKeys.videos.topRated(range),
    queryFn: ({ pageParam = 1 }) => videosApi.getTopRated(range, pageParam),
    getNextPageParam: (lastPage) => extractPageFromUrl(lastPage.next),
    initialPageParam: 1,
  });
}

export function useUserVideos(userId: number) {
  return useInfiniteQuery({
    queryKey: queryKeys.videos.byUser(userId),
    queryFn: ({ pageParam = 1 }) => videosApi.getByUploader(userId, pageParam),
    getNextPageParam: (lastPage) => extractPageFromUrl(lastPage.next),
    initialPageParam: 1,
    enabled: userId > 0,
  });
}

export function useIncrementViews() {
  return useMutation({
    mutationFn: (videoId: number) => videosApi.incrementViews(videoId),
  });
}

export function useUploadVideo() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      data,
      onProgress,
    }: {
      data: FormData;
      onProgress?: (percent: number) => void;
    }) => videosApi.upload(data, onProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.videos.all });
    },
  });
}

export function useDeleteVideo() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (videoId: number) => videosApi.delete(videoId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.videos.all });
    },
  });
}

export function useDownloadVideo() {
  return useMutation({
    mutationFn: (videoId: number) => videosApi.download(videoId),
    onSuccess: (data) => {
      const a = document.createElement("a");
      a.href = data.download_url;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    },
  });
}

function updateVideoInPages(
  pages: PaginatedResponse<Video>[],
  videoId: number,
  updater: (video: Video) => Video
): PaginatedResponse<Video>[] {
  return pages.map((page) => ({
    ...page,
    results: page.results.map((v) => (v.id === videoId ? updater(v) : v)),
  }));
}

export function useLikeVideo() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (videoId: number) => videosApi.like(videoId),
    onMutate: async (videoId) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.videos.detail(videoId) });
      await queryClient.cancelQueries({ queryKey: queryKeys.videos.all });

      const previousDetail = queryClient.getQueryData<Video>(queryKeys.videos.detail(videoId));
      const previousLists = queryClient.getQueriesData<{ pages: PaginatedResponse<Video>[]; pageParams: number[] }>({ queryKey: queryKeys.videos.all });

      queryClient.setQueryData<Video>(queryKeys.videos.detail(videoId), (old) =>
        old ? { ...old, like_count: old.like_count + 1, is_liked_by_me: true } : old
      );

      // Update all infinite query caches that contain this video
      queryClient.setQueriesData<{ pages: PaginatedResponse<Video>[]; pageParams: number[] }>(
        { queryKey: queryKeys.videos.all },
        (old) => {
          if (!old || !('pages' in old) || !Array.isArray(old.pages)) return old;
          return { ...old, pages: updateVideoInPages(old.pages, videoId, (v) => ({ ...v, like_count: v.like_count + 1, is_liked_by_me: true })) };
        }
      );

      return { previousDetail, previousLists };
    },
    onError: (err, videoId, context) => {
      // 409 = like already exists on server — don't rollback
      if ((err as { response?: { status?: number } })?.response?.status === 409) return;
      if (context?.previousDetail) {
        queryClient.setQueryData(queryKeys.videos.detail(videoId), context.previousDetail);
      }
      if (context?.previousLists) {
        for (const [key, data] of context.previousLists) {
          queryClient.setQueryData(key, data);
        }
      }
      toast.error("Errore nel like, riprova.");
    },
    onSettled: (_data, _err, videoId) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.videos.detail(videoId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.videos.all });
    },
  });
}

export function useUnlikeVideo() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (videoId: number) => videosApi.unlike(videoId),
    onMutate: async (videoId) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.videos.detail(videoId) });
      await queryClient.cancelQueries({ queryKey: queryKeys.videos.all });

      const previousDetail = queryClient.getQueryData<Video>(queryKeys.videos.detail(videoId));
      const previousLists = queryClient.getQueriesData<{ pages: PaginatedResponse<Video>[]; pageParams: number[] }>({ queryKey: queryKeys.videos.all });

      queryClient.setQueryData<Video>(queryKeys.videos.detail(videoId), (old) =>
        old ? { ...old, like_count: Math.max(0, old.like_count - 1), is_liked_by_me: false } : old
      );

      queryClient.setQueriesData<{ pages: PaginatedResponse<Video>[]; pageParams: number[] }>(
        { queryKey: queryKeys.videos.all },
        (old) => {
          if (!old || !('pages' in old) || !Array.isArray(old.pages)) return old;
          return { ...old, pages: updateVideoInPages(old.pages, videoId, (v) => ({ ...v, like_count: Math.max(0, v.like_count - 1), is_liked_by_me: false })) };
        }
      );

      return { previousDetail, previousLists };
    },
    onError: (_err, videoId, context) => {
      if (context?.previousDetail) {
        queryClient.setQueryData(queryKeys.videos.detail(videoId), context.previousDetail);
      }
      if (context?.previousLists) {
        for (const [key, data] of context.previousLists) {
          queryClient.setQueryData(key, data);
        }
      }
      toast.error("Errore nella rimozione del like, riprova.");
    },
    onSettled: (_data, _err, videoId) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.videos.detail(videoId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.videos.all });
    },
  });
}

export function usePopupComments(
  videoId: number,
  options?: { enabled?: boolean }
) {
  return useQuery<Comment[]>({
    queryKey: queryKeys.videos.popupComments(videoId),
    queryFn: () => videosApi.getPopupComments(videoId),
    staleTime: 60_000,
    enabled: options?.enabled ?? true,
  });
}
