"use client";

import { useMemo } from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import { Trophy } from "lucide-react";
import { FeedGrid } from "@/components/feed/feed-grid";
import { InfiniteScroll } from "@/components/shared/infinite-scroll";
import { EmptyState } from "@/components/shared/empty-state";
import { queryKeys } from "@/lib/query-keys";
import { contestsApi } from "@/lib/api/contests";
import { extractPageFromUrl } from "@/lib/utils";

export default function ContestPage() {
  const {
    data,
    isLoading,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: queryKeys.contests.winners,
    queryFn: ({ pageParam = 1 }) => contestsApi.getWinners(pageParam),
    getNextPageParam: (lastPage) => extractPageFromUrl(lastPage.next),
    initialPageParam: 1,
  });

  const videos = useMemo(
    () => data?.pages.flatMap((p) => p.results) ?? [],
    [data]
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Trophy className="h-6 w-6 text-yellow-400" />
          Contest
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Le clip vincitrici dei contest settimanali
        </p>
      </div>

      {isLoading ? (
        <FeedGrid videos={[]} isLoading />
      ) : videos.length === 0 ? (
        <EmptyState
          icon={Trophy}
          title="Nessun vincitore"
          description="I contest non sono ancora stati assegnati. Torna presto!"
        />
      ) : (
        <>
          <FeedGrid videos={videos} />
          <InfiniteScroll
            hasNextPage={hasNextPage}
            isFetchingNextPage={isFetchingNextPage}
            fetchNextPage={fetchNextPage}
          />
        </>
      )}
    </div>
  );
}
