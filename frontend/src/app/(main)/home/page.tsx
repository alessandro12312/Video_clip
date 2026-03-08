"use client";

import { Film } from "lucide-react";
import { FeedGrid } from "@/components/feed/feed-grid";
import { EmptyState } from "@/components/shared/empty-state";
import { ErrorMessage } from "@/components/shared/error-message";
import { InfiniteScroll } from "@/components/shared/infinite-scroll";
import { useVideoFeed } from "@/lib/hooks/use-videos";

export default function HomePage() {
  const {
    data,
    isLoading,
    isError,
    refetch,
    hasNextPage,
    isFetchingNextPage,
    fetchNextPage,
  } = useVideoFeed();

  const videos = data?.pages.flatMap((page) => page.results) ?? [];

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">Home</h1>

      {isError && <ErrorMessage onRetry={refetch} />}

      {!isError && videos.length === 0 && !isLoading && (
        <EmptyState
          icon={Film}
          title="Nessuna clip da mostrare"
          description="Segui altri utenti per vedere le loro clip nel tuo feed."
        />
      )}

      <FeedGrid videos={videos} isLoading={isLoading} />

      {videos.length > 0 && (
        <InfiniteScroll
          hasNextPage={hasNextPage}
          isFetchingNextPage={isFetchingNextPage}
          fetchNextPage={fetchNextPage}
        />
      )}
    </div>
  );
}
