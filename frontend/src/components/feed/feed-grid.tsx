import type { Video } from "@/types";
import { CardAsPlayer } from "./card-as-player";
import { CardAsPlayerSkeleton } from "./card-as-player-skeleton";

interface FeedGridProps {
  videos: Video[];
  isLoading?: boolean;
}

export function FeedGrid({ videos, isLoading }: FeedGridProps) {
  if (isLoading) {
    return (
      <div className="flex flex-col gap-6">
        {Array.from({ length: 3 }).map((_, i) => (
          <CardAsPlayerSkeleton key={i} />
        ))}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      {videos.map((video) => (
        <CardAsPlayer key={video.id} video={video} />
      ))}
    </div>
  );
}
