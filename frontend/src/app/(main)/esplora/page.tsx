"use client";

import { useState } from "react";
import { Compass } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FeedGrid } from "@/components/feed/feed-grid";
import { EmptyState } from "@/components/shared/empty-state";
import { ErrorMessage } from "@/components/shared/error-message";
import { InfiniteScroll } from "@/components/shared/infinite-scroll";
import { useTopRatedVideos } from "@/lib/hooks/use-videos";
import { TOP_RATED_RANGES } from "@/lib/constants";
import { cn } from "@/lib/utils";
import type { TopRatedRange } from "@/types";

export default function EsploraPage() {
  const [range, setRange] = useState<TopRatedRange>("all");
  const {
    data,
    isLoading,
    isError,
    refetch,
    hasNextPage,
    isFetchingNextPage,
    fetchNextPage,
  } = useTopRatedVideos(range);

  const videos = data?.pages.flatMap((page) => page.results) ?? [];

  return (
    <div>
      <h1 className="mb-4 text-2xl font-bold">Esplora</h1>

      {/* Range filters */}
      <div className="mb-6 flex gap-2 overflow-x-auto pb-1">
        {TOP_RATED_RANGES.map((r) => (
          <Button
            key={r.value}
            variant={range === r.value ? "default" : "outline"}
            size="sm"
            className={cn(range === r.value && "gradient-bg")}
            onClick={() => setRange(r.value as TopRatedRange)}
          >
            {r.label}
          </Button>
        ))}
      </div>

      {isError && <ErrorMessage onRetry={refetch} />}

      {!isError && videos.length === 0 && !isLoading && (
        <EmptyState
          icon={Compass}
          title="Nessuna clip trovata"
          description="Non ci sono ancora clip per questo periodo."
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
