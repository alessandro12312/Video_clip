"use client";

import { useState, useEffect, useCallback } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { useCreateComment } from "@/lib/hooks/use-comments";
import { formatMMSS, parseMMSS } from "@/lib/utils";
import { toast } from "sonner";

interface CommentFormProps {
  videoId: number;
  pauseTimestamp: number | null;
  onClearTimestamp: () => void;
  onSeekTo?: (seconds: number) => void;
  videoDuration?: number;
}

export function CommentForm({
  videoId,
  pauseTimestamp,
  onClearTimestamp,
  onSeekTo,
  videoDuration,
}: CommentFormProps) {
  const [content, setContent] = useState("");
  const [mmssValue, setMmssValue] = useState("");
  const [mmssError, setMmssError] = useState<string | null>(null);
  const { mutate: createComment, isPending } = useCreateComment(videoId);

  // Player→field: when video pauses, populate the MM:SS field
  useEffect(() => {
    if (pauseTimestamp !== null && pauseTimestamp > 0) {
      setMmssValue(formatMMSS(pauseTimestamp));
      setMmssError(null);
    }
  }, [pauseTimestamp]);

  const handleMmssChange = useCallback(
    (raw: string) => {
      setMmssValue(raw);

      if (raw === "") {
        setMmssError(null);
        onClearTimestamp();
        return;
      }

      const seconds = parseMMSS(raw);
      if (seconds === null) {
        setMmssError(null); // don't show error while typing
        return;
      }

      if (videoDuration !== undefined && seconds > videoDuration) {
        setMmssError("Timestamp oltre la durata del video");
        return;
      }

      setMmssError(null);
      // Field→player: seek video to the entered timestamp
      onSeekTo?.(seconds);
    },
    [videoDuration, onSeekTo, onClearTimestamp]
  );

  function getTimestampSeconds(): number {
    if (!mmssValue) return 0;
    const seconds = parseMMSS(mmssValue);
    if (seconds === null) return 0;
    if (videoDuration !== undefined && seconds > videoDuration) return 0;
    return seconds;
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!content.trim()) return;

    createComment(
      {
        video: videoId,
        content: content.trim(),
        timestamp_second: getTimestampSeconds(),
      },
      {
        onSuccess: () => {
          setContent("");
          setMmssValue("");
          setMmssError(null);
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
    <form onSubmit={handleSubmit} className="space-y-2">
      <div className="flex gap-2 items-end">
        <div className="flex-1">
          <Textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Scrivi un commento..."
            className="min-h-[60px] resize-none"
            maxLength={500}
          />
        </div>
        <Button
          type="submit"
          size="icon"
          className="gradient-bg h-10 w-10 shrink-0"
          disabled={!content.trim() || isPending || !!mmssError}
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
      <div className="flex items-center gap-2">
        <Input
          type="text"
          value={mmssValue}
          onChange={(e) => handleMmssChange(e.target.value)}
          placeholder="Timestamp (MM:SS)"
          className="w-40 font-mono text-xs h-8"
          maxLength={5}
        />
        {mmssError && (
          <span className="text-xs text-destructive">{mmssError}</span>
        )}
        {!mmssError && mmssValue && parseMMSS(mmssValue) !== null && (
          <span className="text-xs text-primary">Commento temporizzato</span>
        )}
      </div>
    </form>
  );
}
