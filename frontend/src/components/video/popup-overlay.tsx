"use client";

import { AnimatePresence, motion } from "framer-motion";
import { TimestampBadge } from "@/components/shared/timestamp-badge";
import type { Comment } from "@/types";

interface PopupOverlayProps {
  comment: Comment | null;
}

export function PopupOverlay({ comment }: PopupOverlayProps) {
  return (
    <AnimatePresence>
      {comment && (
        <motion.div
          key={comment.id}
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.3 }}
          className="absolute top-3 right-3 z-20 max-w-xs glass rounded-lg p-3"
        >
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold text-primary">
              {comment.user}
            </span>
            <TimestampBadge seconds={comment.timestamp_second} />
          </div>
          <p className="text-sm text-foreground/90 leading-snug">
            {comment.content}
          </p>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
