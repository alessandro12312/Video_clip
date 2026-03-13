"use client";

import { UserAvatar } from "@/components/user/user-avatar";
import { UsernameLink } from "@/components/user/username-link";
import { TimestampBadge } from "@/components/shared/timestamp-badge";
import { useLikeComment, useUnlikeComment } from "@/lib/hooks/use-comments";
import { cn, formatRelativeDate } from "@/lib/utils";
import { Heart, Trash2 } from "lucide-react";
import type { Comment } from "@/types";

interface CommentItemProps {
  comment: Comment;
  compact?: boolean;
  currentUsername?: string;
  videoId: number;
  onTimestampClick?: (seconds: number) => void;
  onDelete?: (commentId: number) => void;
}

export function CommentItem({ comment, compact, currentUsername, videoId, onTimestampClick, onDelete }: CommentItemProps) {
  const likeMutation = useLikeComment(videoId);
  const unlikeMutation = useUnlikeComment(videoId);

  return (
    <div className="flex gap-2.5 py-2 group">
      {!compact && <UserAvatar username={comment.user} size="sm" />}

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <UsernameLink
            username={comment.user}
            className={compact ? "text-xs" : "text-sm"}
          />
          {comment.timestamp_second > 0 && (
            <TimestampBadge
              seconds={comment.timestamp_second}
              onClick={() => onTimestampClick?.(comment.timestamp_second)}
            />
          )}
          <span className="text-xs text-muted-foreground">
            {formatRelativeDate(comment.created_at)}
          </span>
          <button
            onClick={() =>
              comment.is_liked_by_me
                ? unlikeMutation.mutate(comment.id)
                : likeMutation.mutate(comment.id)
            }
            disabled={likeMutation.isPending || unlikeMutation.isPending}
            className={cn(
              "flex items-center gap-0.5 transition-colors",
              comment.is_liked_by_me
                ? "text-red-500 hover:text-red-400"
                : "text-muted-foreground/50 hover:text-red-500"
            )}
            aria-label={comment.is_liked_by_me ? "Rimuovi mi piace" : "Mi piace"}
          >
            <Heart className={cn("h-3 w-3", comment.is_liked_by_me && "fill-current")} />
            {comment.like_count > 0 && (
              <span className="text-xs">{comment.like_count}</span>
            )}
          </button>
          {comment.user === currentUsername && (
            <button
              onClick={() => onDelete?.(comment.id)}
              className="text-muted-foreground/50 hover:text-destructive transition-colors opacity-100 sm:opacity-0 sm:group-hover:opacity-100"
              aria-label="Elimina commento"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
        <p className={`mt-0.5 text-foreground/90 ${compact ? "text-xs" : "text-sm"}`}>
          {comment.content}
        </p>
      </div>
    </div>
  );
}
