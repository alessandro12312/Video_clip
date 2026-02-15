"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import { usersApi } from "@/lib/api/users";

export function useUser(id: number) {
  return useQuery({
    queryKey: queryKeys.users.detail(id),
    queryFn: () => usersApi.getById(id),
    staleTime: 60_000,
  });
}

export function useFollowers(userId: number) {
  return useQuery({
    queryKey: queryKeys.users.followers(userId),
    queryFn: () => usersApi.getFollowers(userId),
  });
}

export function useFollowing(userId: number) {
  return useQuery({
    queryKey: queryKeys.users.following(userId),
    queryFn: () => usersApi.getFollowing(userId),
  });
}

export function useSearchUsers(query: string) {
  return useQuery({
    queryKey: queryKeys.users.search(query),
    queryFn: () => usersApi.search(query),
    enabled: query.length >= 2,
    staleTime: 30_000,
  });
}

export function useFollow() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: number) => usersApi.follow(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      queryClient.invalidateQueries({
        queryKey: queryKeys.videos.followingAll,
      });
    },
  });
}

export function useUnfollow() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: number) => usersApi.unfollow(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      queryClient.invalidateQueries({
        queryKey: queryKeys.videos.followingAll,
      });
    },
  });
}
