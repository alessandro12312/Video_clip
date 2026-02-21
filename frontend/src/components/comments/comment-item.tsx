import { UserAvatar } from "@/components/user/user-avatar";
import { UsernameLink } from "@/components/user/username-link";
import { TimestampBadge } from "@/components/shared/timestamp-badge";
import { formatRelativeDate } from "@/lib/utils";
import type { Comment } from "@/types";

interface CommentItemProps {
  comment: Comment;
  compact?: boolean;
  onTimestampClick?: (seconds: number) => void;
}

export function CommentItem({ comment, compact, onTimestampClick }: CommentItemProps) {
  return (
    <div className="flex gap-2.5 py-2">
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
        </div>
        <p className={`mt-0.5 text-foreground/90 ${compact ? "text-xs" : "text-sm"}`}>
          {comment.content}
        </p>
      </div>
    </div>
  );
}
