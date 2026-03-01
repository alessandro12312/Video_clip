"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import { usersApi } from "@/lib/api/users";
import { useAuth } from "@/providers/auth-provider";
import { toast } from "sonner";
import type { User } from "@/types";

export function useUser(id: number) {
  return useQuery({
    queryKey: queryKeys.users.detail(id),
    queryFn: () => usersApi.getById(id),
    staleTime: 5 * 60_000,
  });
}

export function useFollowers(userId: number, page = 1) {
  return useQuery({
    queryKey: [...queryKeys.users.followers(userId), page],
    queryFn: () => usersApi.getFollowers(userId, page),
    enabled: userId > 0,
    staleTime: 5 * 60_000,
    placeholderData: (prev) => prev,
  });
}

export function useFollowing(userId: number, page = 1) {
  return useQuery({
    queryKey: [...queryKeys.users.following(userId), page],
    queryFn: () => usersApi.getFollowing(userId, page),
    enabled: userId > 0,
    staleTime: 5 * 60_000,
    placeholderData: (prev) => prev,
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
  const { user: currentUser } = useAuth();
  return useMutation({
    mutationFn: ({ userId }: { userId: number; username: string }) =>
      usersApi.follow(userId),
    onMutate: async ({ userId, username }) => {
      await queryClient.cancelQueries({
        queryKey: queryKeys.users.byUsername(username),
      });
      await queryClient.cancelQueries({
        queryKey: queryKeys.users.detail(userId),
      });
      const previousByUsername = queryClient.getQueryData<User>(
        queryKeys.users.byUsername(username)
      );
      const previousByDetail = queryClient.getQueryData<User>(
        queryKeys.users.detail(userId)
      );
      const optimisticUpdate = (old: User | undefined) =>
        old
          ? {
              ...old,
              is_followed_by_me: true,
              followers_count: old.followers_count + 1,
            }
          : old;
      queryClient.setQueryData<User>(
        queryKeys.users.byUsername(username),
        optimisticUpdate
      );
      queryClient.setQueryData<User>(
        queryKeys.users.detail(userId),
        optimisticUpdate
      );
      return { previousByUsername, previousByDetail, username, userId };
    },
    onError: (_err, _vars, context) => {
      if (context?.previousByUsername) {
        queryClient.setQueryData(
          queryKeys.users.byUsername(context.username),
          context.previousByUsername
        );
      }
      if (context?.previousByDetail) {
        queryClient.setQueryData(
          queryKeys.users.detail(context.userId),
          context.previousByDetail
        );
      }
      toast.error("Errore nel seguire l'utente");
    },
    onSettled: (_data, _err, { userId, username }) => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.users.detail(userId),
      });
      queryClient.invalidateQueries({
        queryKey: queryKeys.users.byUsername(username),
      });
      queryClient.invalidateQueries({
        queryKey: queryKeys.users.followers(userId),
      });
      if (currentUser?.id) {
        queryClient.invalidateQueries({
          queryKey: queryKeys.users.following(currentUser.id),
        });
      }
      queryClient.invalidateQueries({
        queryKey: queryKeys.videos.followingAll,
      });
    },
  });
}

export function useUnfollow() {
  const queryClient = useQueryClient();
  const { user: currentUser } = useAuth();
  return useMutation({
    mutationFn: ({ userId }: { userId: number; username: string }) =>
      usersApi.unfollow(userId),
    onMutate: async ({ userId, username }) => {
      await queryClient.cancelQueries({
        queryKey: queryKeys.users.byUsername(username),
      });
      await queryClient.cancelQueries({
        queryKey: queryKeys.users.detail(userId),
      });
      const previousByUsername = queryClient.getQueryData<User>(
        queryKeys.users.byUsername(username)
      );
      const previousByDetail = queryClient.getQueryData<User>(
        queryKeys.users.detail(userId)
      );
      const optimisticUpdate = (old: User | undefined) =>
        old
          ? {
              ...old,
              is_followed_by_me: false,
              followers_count: Math.max(0, old.followers_count - 1),
            }
          : old;
      queryClient.setQueryData<User>(
        queryKeys.users.byUsername(username),
        optimisticUpdate
      );
      queryClient.setQueryData<User>(
        queryKeys.users.detail(userId),
        optimisticUpdate
      );
      return { previousByUsername, previousByDetail, username, userId };
    },
    onError: (_err, _vars, context) => {
      if (context?.previousByUsername) {
        queryClient.setQueryData(
          queryKeys.users.byUsername(context.username),
          context.previousByUsername
        );
      }
      if (context?.previousByDetail) {
        queryClient.setQueryData(
          queryKeys.users.detail(context.userId),
          context.previousByDetail
        );
      }
      toast.error("Errore nello smettere di seguire l'utente");
    },
    onSettled: (_data, _err, { userId, username }) => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.users.detail(userId),
      });
      queryClient.invalidateQueries({
        queryKey: queryKeys.users.byUsername(username),
      });
      queryClient.invalidateQueries({
        queryKey: queryKeys.users.followers(userId),
      });
      if (currentUser?.id) {
        queryClient.invalidateQueries({
          queryKey: queryKeys.users.following(currentUser.id),
        });
      }
      queryClient.invalidateQueries({
        queryKey: queryKeys.videos.followingAll,
      });
    },
  });
}

export function useUserByUsername(username: string) {
  return useQuery({
    queryKey: queryKeys.users.byUsername(username),
    queryFn: () => usersApi.getByUsername(username),
    enabled: !!username,
    staleTime: 5 * 60_000,
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  const { user: currentUser } = useAuth();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: { bio?: string } }) =>
      usersApi.updateProfile(id, data),
    onSuccess: (_data, { id }) => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.users.detail(id),
      });
      if (currentUser?.username) {
        queryClient.invalidateQueries({
          queryKey: queryKeys.users.byUsername(currentUser.username),
        });
      }
    },
  });
}
