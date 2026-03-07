"use client";

import { useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ScrollArea } from "@/components/ui/scroll-area";
import { TimestampBadge } from "@/components/shared/timestamp-badge";
import { COMMENT_SLOT_SECONDS } from "@/lib/constants";
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

  // Live: filtra per currentTime. Altrimenti mostra tutti.
  const visibleSlots = useMemo(() => {
    if (!isLive) return slots;
    return slots.filter((c) => c.timestamp_second <= currentTime!);
  }, [slots, isLive, currentTime]);

  // Live: i più recenti in alto (appena apparsi).
  const displaySlots = useMemo(() => {
    if (isLive) return [...visibleSlots].reverse();
    return visibleSlots;
  }, [visibleSlots, isLive]);

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
        {isLive ? "Chat live" : "Chat"}
      </h3>
      <ScrollArea style={{ maxHeight: `${maxVisible * 3.5}rem` }}>
        <div className="space-y-0.5 pr-2">
          <AnimatePresence initial={false}>
            {displaySlots.map((comment) => (
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
