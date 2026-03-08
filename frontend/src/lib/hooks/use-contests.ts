import { useQuery, useInfiniteQuery } from "@tanstack/react-query";
import { contestsApi } from "@/lib/api/contests";
import { queryKeys } from "@/lib/query-keys";
import { extractPageFromUrl } from "@/lib/utils";

export function useContests(params?: { is_closed?: boolean }) {
  return useInfiniteQuery({
    queryKey: queryKeys.contests.list(params),
    queryFn: ({ pageParam = 1 }) =>
      contestsApi.list({ ...params, page: pageParam }),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => extractPageFromUrl(lastPage.next),
  });
}

export function useContestDetail(id: number) {
  return useQuery({
    queryKey: queryKeys.contests.detail(id),
    queryFn: () => contestsApi.getDetail(id),
    enabled: !!id,
  });
}

export function useContestVideos(contestId: number) {
  return useInfiniteQuery({
    queryKey: queryKeys.contests.videos(contestId),
    queryFn: ({ pageParam = 1 }) =>
      contestsApi.getContestVideos(contestId, pageParam),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => extractPageFromUrl(lastPage.next),
    enabled: !!contestId,
  });
}
