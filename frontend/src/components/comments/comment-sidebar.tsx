"use client";

import { useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Heart } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { TimestampBadge } from "@/components/shared/timestamp-badge";
import type { Comment } from "@/types";

interface CommentSidebarProps {
  comments: Comment[];
  onTimestampClick?: (seconds: number) => void;
  maxVisible?: number;
  /** Tempo corrente del player — se presente, i commenti appaiono in sync */
  currentTime?: number | null;
}

export function CommentSidebar({ comments, onTimestampClick, maxVisible = 6, currentTime }: CommentSidebarProps) {
  const isLive = currentTime != null;

  // Filtra commenti con like >= 1, ordinati per like_count decrescente
  const topLiked = useMemo(() => {
    return comments
      .filter((c) => c.timestamp_second > 0 && c.like_count >= 1)
      .sort((a, b) => b.like_count - a.like_count);
  }, [comments]);

  // Live: filtra per currentTime. Altrimenti mostra tutti.
  const visible = useMemo(() => {
    if (!isLive) return topLiked;
    return topLiked.filter((c) => c.timestamp_second <= currentTime!);
  }, [topLiked, isLive, currentTime]);

  if (topLiked.length === 0) {
    return (
      <div className="p-3 text-center text-xs text-muted-foreground">
        Nessun commento con like ancora.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-1">
      <h3 className="px-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        {isLive ? "Top commenti live" : "Top commenti"}
      </h3>
      <ScrollArea style={{ maxHeight: `${maxVisible * 3.5}rem` }}>
        <div className="space-y-0.5 pr-2">
          <AnimatePresence initial={false}>
            {visible.map((comment) => (
              <motion.button
                key={comment.id}
                layout
                initial={{ opacity: 0, y: -30, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 20, scale: 0.95 }}
                transition={{ type: "spring", stiffness: 500, damping: 35 }}
                onClick={() => onTimestampClick?.(comment.timestamp_second)}
                className="w-full text-left rounded-md px-2 py-1.5 hover:bg-accent transition-colors"
              >
                <div className="flex items-center gap-1.5 mb-0.5">
                  <span className="text-xs font-medium text-foreground truncate">
                    {comment.user}
                  </span>
                  <TimestampBadge seconds={comment.timestamp_second} />
                  <span className="ml-auto flex items-center gap-0.5 text-xs text-muted-foreground">
                    <Heart className="h-3 w-3" />
                    {comment.like_count}
                  </span>
                </div>
                <p className="text-xs text-foreground/80 break-words whitespace-normal">
                  {comment.content}
                </p>
              </motion.button>
            ))}
          </AnimatePresence>
        </div>
      </ScrollArea>
    </div>
  );
}
