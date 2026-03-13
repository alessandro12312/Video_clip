import { CommentItem } from "./comment-item";
import type { Comment } from "@/types";

interface CommentListProps {
  comments: Comment[];
  limit?: number;
  currentUsername?: string;
  videoId: number;
  onTimestampClick?: (seconds: number) => void;
  onDelete?: (commentId: number) => void;
}

export function CommentList({ comments, limit, currentUsername, videoId, onTimestampClick, onDelete }: CommentListProps) {
  const sorted = [...comments].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
  const displayed = limit !== undefined ? sorted.slice(0, limit) : sorted;

  if (displayed.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">
        Nessun commento.
      </p>
    );
  }

  return (
    <div className="divide-y divide-border/50">
      {displayed.map((comment) => (
        <CommentItem
          key={comment.id}
          comment={comment}
          currentUsername={currentUsername}
          videoId={videoId}
          onTimestampClick={onTimestampClick}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
