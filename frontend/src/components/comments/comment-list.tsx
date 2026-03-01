import { CommentItem } from "./comment-item";
import type { Comment } from "@/types";

interface CommentListProps {
  comments: Comment[];
  mode: "all" | "timestamped";
  onTimestampClick?: (seconds: number) => void;
}

export function CommentList({ comments, mode, onTimestampClick }: CommentListProps) {
  const filtered =
    mode === "timestamped"
      ? [...comments]
          .filter((c) => c.timestamp_second > 0)
          .sort((a, b) => a.timestamp_second - b.timestamp_second)
      : [...comments].sort(
          (a, b) =>
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );

  if (filtered.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">
        {mode === "timestamped"
          ? "Nessun commento temporizzato."
          : "Nessun commento."}
      </p>
    );
  }

  return (
    <div className="divide-y divide-border/50">
      {filtered.map((comment) => (
        <CommentItem
          key={comment.id}
          comment={comment}
          onTimestampClick={onTimestampClick}
        />
      ))}
    </div>
  );
}
