"use client";

import { useQuery, useInfiniteQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { notificationsApi } from "@/lib/api/notifications";
import { queryKeys } from "@/lib/query-keys";
import { extractPageFromUrl } from "@/lib/utils";
import { useAuth } from "@/providers/auth-provider";

/** Lista notifiche paginata — per la pagina /notifiche */
export function useNotifications() {
  return useInfiniteQuery({
    queryKey: queryKeys.notifications.all,
    queryFn: ({ pageParam = 1 }) => notificationsApi.getAll(pageParam),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => extractPageFromUrl(lastPage.next),
    staleTime: 30_000,
  });
}

/** Conteggio non lette — polling 15s per badge campanella */
export function useUnreadCount() {
  const { user } = useAuth();
  return useQuery({
    queryKey: queryKeys.notifications.unreadCount,
    queryFn: () => notificationsApi.getUnreadCount(),
    refetchInterval: 15_000,
    staleTime: 10_000,
    enabled: !!user,
  });
}

/** Marca singola come letta */
export function useMarkRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => notificationsApi.markRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.notifications.all });
    },
  });
}

/** Marca tutte come lette */
export function useMarkAllRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => notificationsApi.markAllRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.notifications.all });
    },
  });
}
