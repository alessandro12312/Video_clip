"use client";

import { useState } from "react";
import Link from "next/link";
import { Eye, Star } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { TagBadge } from "@/components/shared/tag-badge";
import { UserAvatar } from "@/components/user/user-avatar";
import { formatRelativeDate, formatCount, formatTimestamp } from "@/lib/utils";
import type { Video } from "@/types";

interface ClipCardProps {
  video: Video;
}

export function ClipCard({ video }: ClipCardProps) {
  const [thumbError, setThumbError] = useState(false);
  const showThumbnail = video.thumbnail_url && !thumbError;

  return (
    <Link href={`/clip/${video.id}`}>
      <Card className="group overflow-hidden border-border/50 transition-all duration-200 hover:border-border hover:shadow-lg hover:shadow-primary/5 hover:scale-[1.02]">
        {/* Thumbnail */}
        <div className="relative aspect-video bg-muted">
          {showThumbnail ? (
            <img
              src={video.thumbnail_url!}
              alt={video.title}
              className="absolute inset-0 h-full w-full object-cover"
              loading="lazy"
              onError={() => setThumbError(true)}
            />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-4xl font-bold text-muted-foreground/20">
                ▶
              </div>
            </div>
          )}
          {/* Duration badge */}
          <span className="absolute bottom-2 right-2 rounded bg-black/70 px-1.5 py-0.5 text-xs font-mono text-white">
            {formatTimestamp(video.duration)}
          </span>
          {/* Tag */}
          <div className="absolute top-2 left-2">
            <TagBadge tag={video.tag} />
          </div>
        </div>

        <CardContent className="p-3">
          {/* Title */}
          <h3 className="mb-2 line-clamp-1 text-sm font-semibold leading-tight group-hover:text-primary transition-colors">
            {video.title}
          </h3>

          {/* Uploader */}
          <div className="mb-2 flex items-center gap-1.5">
            <UserAvatar username={video.uploader} size="sm" />
            <span className="text-xs text-muted-foreground truncate">
              {video.uploader}
            </span>
          </div>

          {/* Stats row */}
          <div className="flex items-center gap-3 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <Eye className="h-3.5 w-3.5" />
              {formatCount(video.views)}
            </span>
            {video.average_rating > 0 && (
              <span className="flex items-center gap-1">
                <Star className="h-3.5 w-3.5" />
                {video.average_rating.toFixed(1)}
              </span>
            )}
            <span className="ml-auto">{formatRelativeDate(video.created_at)}</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
