"use client";

import { useState } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { TimestampBadge } from "@/components/shared/timestamp-badge";
import { useCreateComment } from "@/lib/hooks/use-comments";
import { toast } from "sonner";

interface CommentFormProps {
  videoId: number;
  pauseTimestamp: number | null;
  onClearTimestamp: () => void;
}

export function CommentForm({
  videoId,
  pauseTimestamp,
  onClearTimestamp,
}: CommentFormProps) {
  const [content, setContent] = useState("");
  const { mutate: createComment, isPending } = useCreateComment(videoId);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!content.trim()) return;

    createComment(
      {
        video: videoId,
        content: content.trim(),
        timestamp_second: pauseTimestamp ?? 0,
      },
      {
        onSuccess: () => {
          setContent("");
          onClearTimestamp();
          toast.success("Commento inviato!");
        },
        onError: () => {
          toast.error("Errore nell'invio del commento.");
        },
      }
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 items-end">
      <div className="flex-1 relative">
        {pauseTimestamp !== null && pauseTimestamp > 0 && (
          <div className="mb-1.5">
            <TimestampBadge
              seconds={pauseTimestamp}
              removable
              onRemove={onClearTimestamp}
            />
          </div>
        )}
        <Textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder={
            pauseTimestamp
              ? "Descrivi questo momento..."
              : "Scrivi un commento..."
          }
          className="min-h-[60px] resize-none"
          maxLength={500}
        />
      </div>
      <Button
        type="submit"
        size="icon"
        className="gradient-bg h-10 w-10 shrink-0"
        disabled={!content.trim() || isPending}
      >
        <Send className="h-4 w-4" />
      </Button>
    </form>
  );
}
