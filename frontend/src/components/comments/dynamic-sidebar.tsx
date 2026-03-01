"use client";

import { useMemo } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { CommentItem } from "./comment-item";
import type { Comment } from "@/types";

interface DynamicSidebarProps {
  comments: Comment[];
  onTimestampClick?: (seconds: number) => void;
}

export function DynamicSidebar({ comments, onTimestampClick }: DynamicSidebarProps) {
  // Sort by most recent (proxy for "most liked" until likes are implemented)
  const topComments = useMemo(() => {
    return [...comments]
      .filter((c) => c.timestamp_second > 0)
      .sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )
      .slice(0, 20);
  }, [comments]);

  if (topComments.length === 0) {
    return (
      <div className="p-4 text-center text-sm text-muted-foreground">
        Ancora nessun commento temporizzato.
      </div>
    );
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-4 space-y-1">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
          Commenti in evidenza
        </h3>
        {topComments.map((comment) => (
          <CommentItem
            key={comment.id}
            comment={comment}
            compact
            onTimestampClick={onTimestampClick}
          />
        ))}
      </div>
    </ScrollArea>
  );
}
