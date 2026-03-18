"use client";

import { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ErrorMessage } from "@/components/shared/error-message";
import { useAuth } from "@/providers/auth-provider";
import { useUserVideos } from "@/lib/hooks/use-videos";
import { useEnterBracket } from "@/lib/hooks/use-brackets";

interface EnterBracketFormProps {
  bracketId: number;
  onEntered: () => void;
}

export function EnterBracketForm({
  bracketId,
  onEntered,
}: EnterBracketFormProps) {
  const { user } = useAuth();
  const [selectedVideoId, setSelectedVideoId] = useState<number | null>(null);
  const enterMutation = useEnterBracket();

  const {
    data: videosData,
    isLoading: videosLoading,
    isError: videosError,
    refetch: refetchVideos,
  } = useUserVideos(user?.id ?? 0);

  if (!user) {
    return (
      <Card className="p-4">
        <p className="text-sm text-muted-foreground">
          Accedi per iscriverti al torneo.
        </p>
      </Card>
    );
  }

  const videos = useMemo(
    () => videosData?.pages.flatMap((p) => p.results) ?? [],
    [videosData]
  );

  if (videosError) {
    return (
      <ErrorMessage
        message="Errore nel caricamento dei tuoi video."
        onRetry={refetchVideos}
      />
    );
  }

  const handleSubmit = () => {
    if (!selectedVideoId) return;
    enterMutation.mutate(
      { bracketId, data: { video_id: selectedVideoId } },
      { onSuccess: () => onEntered() }
    );
  };

  return (
    <Card className="p-4 space-y-3">
      <h3 className="font-semibold text-sm">Iscriviti al Torneo</h3>
      {videosLoading ? (
        <p className="text-xs text-muted-foreground">
          Caricamento video...
        </p>
      ) : videos.length === 0 ? (
        <p className="text-xs text-muted-foreground">
          Non hai video da iscrivere. Carica una clip prima di iscriverti.
        </p>
      ) : (
        <>
          <select
            value={selectedVideoId ?? ""}
            onChange={(e) =>
              setSelectedVideoId(e.target.value ? Number(e.target.value) : null)
            }
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">Seleziona un video...</option>
            {videos.map((video) => (
              <option key={video.id} value={video.id}>
                {video.title}
              </option>
            ))}
          </select>
          <Button
            onClick={handleSubmit}
            disabled={!selectedVideoId || enterMutation.isPending}
            className="w-full"
          >
            {enterMutation.isPending
              ? "Iscrizione in corso..."
              : "Iscriviti al Torneo"}
          </Button>
        </>
      )}
    </Card>
  );
}
