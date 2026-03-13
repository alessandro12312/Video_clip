import Link from "next/link";
import { CommentList } from "./comment-list";
import type { Comment } from "@/types";

interface CommentSectionProps {
  comments: Comment[];
  currentUsername?: string;
  onTimestampClick?: (seconds: number) => void;
  onDelete?: (commentId: number) => void;
  limit?: number;
  videoId: number;
}

export function CommentSection({ comments, currentUsername, onTimestampClick, onDelete, limit, videoId }: CommentSectionProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-muted-foreground">
          Commenti ({comments.length})
        </h3>
        {limit !== undefined && comments.length > limit && (
          <Link
            href={`/clip/${videoId}`}
            className="text-xs text-primary hover:underline"
          >
            Visualizza tutti i commenti
          </Link>
        )}
      </div>
      <CommentList
        comments={comments}
        limit={limit}
        currentUsername={currentUsername}
        videoId={videoId}
        onTimestampClick={onTimestampClick}
        onDelete={onDelete}
      />
    </div>
  );
}
