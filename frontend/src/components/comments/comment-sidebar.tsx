"use client";

import { useMemo } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { TimestampBadge } from "@/components/shared/timestamp-badge";
import { COMMENT_SLOT_SECONDS } from "@/lib/constants";
import type { Comment } from "@/types";

interface CommentSidebarProps {
  comments: Comment[];
  onTimestampClick?: (seconds: number) => void;
  maxVisible?: number;
}

export function CommentSidebar({ comments, onTimestampClick, maxVisible = 6 }: CommentSidebarProps) {
  const slots = useMemo(() => {
    const slotMap = new Map<number, Comment>();

    for (const comment of comments) {
      if (comment.timestamp_second <= 0) continue;
      const slot = Math.floor(comment.timestamp_second / COMMENT_SLOT_SECONDS);
      const existing = slotMap.get(slot);
      if (!existing || new Date(comment.created_at) > new Date(existing.created_at)) {
        slotMap.set(slot, comment);
      }
    }

    return [...slotMap.values()].sort(
      (a, b) => a.timestamp_second - b.timestamp_second
    );
  }, [comments]);

  if (slots.length === 0) {
    return (
      <div className="p-3 text-center text-xs text-muted-foreground">
        Ancora nessun commento temporizzato.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-1">
      <h3 className="px-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        Momenti salienti
      </h3>
      <ScrollArea style={{ maxHeight: `${maxVisible * 3.5}rem` }}>
        <div className="space-y-0.5 pr-2">
          {slots.map((comment) => (
            <button
              key={comment.id}
              onClick={() => onTimestampClick?.(comment.timestamp_second)}
              className="w-full text-left rounded-md px-2 py-1.5 hover:bg-accent transition-colors"
            >
              <div className="flex items-center gap-1.5 mb-0.5">
                <TimestampBadge seconds={comment.timestamp_second} />
                <span className="text-xs text-muted-foreground truncate">
                  {comment.user}
                </span>
              </div>
              <p className="text-xs text-foreground/80 line-clamp-1">
                {comment.content}
              </p>
            </button>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
