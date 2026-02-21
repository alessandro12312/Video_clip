import type { Video } from "@/types";
import { ClipCard } from "./clip-card";
import { ClipCardSkeleton } from "./clip-card-skeleton";

interface FeedGridProps {
  videos: Video[];
  isLoading?: boolean;
}

export function FeedGrid({ videos, isLoading }: FeedGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <ClipCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {videos.map((video) => (
        <ClipCard key={video.id} video={video} />
      ))}
    </div>
  );
}
