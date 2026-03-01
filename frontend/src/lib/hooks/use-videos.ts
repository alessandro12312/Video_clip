"use client";

import { useQuery, useInfiniteQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import { videosApi } from "@/lib/api/videos";
import { extractPageFromUrl } from "@/lib/utils";
import type { TopRatedRange } from "@/types";

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
