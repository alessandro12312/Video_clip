"use client";

import { useMemo, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Trophy, Calendar, Film } from "lucide-react";
import { toast } from "sonner";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { StarRating } from "@/components/rating/star-rating";
import { TagBadge } from "@/components/shared/tag-badge";
import { EmptyState } from "@/components/shared/empty-state";
import { ErrorMessage } from "@/components/shared/error-message";
import { InfiniteScroll } from "@/components/shared/infinite-scroll";
import { PageLoader } from "@/components/shared/page-loader";
import { useContestDetail, useContestVideos } from "@/lib/hooks/use-contests";
import { ratingsApi } from "@/lib/api/ratings";
import { queryKeys } from "@/lib/query-keys";
import { formatShortDate } from "@/lib/utils";
import type { Video } from "@/types";

function ContestVideoCard({
  video,
  position,
  isWinner,
  contestId,
}: {
  video: Video;
  position: number;
  isWinner: boolean;
  contestId: number;
}) {
  const queryClient = useQueryClient();

  const invalidateContestVideos = useCallback(() => {
    queryClient.invalidateQueries({
      queryKey: queryKeys.contests.videos(contestId),
    });
    queryClient.invalidateQueries({
      queryKey: queryKeys.videos.detail(video.id),
    });
  }, [queryClient, contestId, video.id]);

  const createRating = useMutation({
    mutationFn: (data: { video: number; value: number }) =>
      ratingsApi.create(data),
    onSuccess: () => {
      toast.success("Voto registrato!");
      invalidateContestVideos();
    },
    onError: () => toast.error("Errore nel salvataggio del voto."),
  });

  const updateRating = useMutation({
    mutationFn: ({ ratingId, value }: { ratingId: number; value: number }) =>
      ratingsApi.update(ratingId, value),
    onSuccess: () => {
      toast.success("Voto aggiornato!");
      invalidateContestVideos();
    },
    onError: () => toast.error("Errore nell'aggiornamento del voto."),
  });

  const handleRate = useCallback(
    (value: number) => {
      if (createRating.isPending || updateRating.isPending) return;
      if (video.my_rating_id) {
        updateRating.mutate({ ratingId: video.my_rating_id, value });
      } else {
        createRating.mutate({ video: video.id, value });
      }
    },
    [video.my_rating_id, video.id, createRating, updateRating]
  );

  return (
    <Card className="p-4 space-y-3">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <span
            className={`shrink-0 text-lg font-bold ${
              isWinner ? "text-yellow-400" : "text-muted-foreground"
            }`}
          >
            {isWinner ? (
              <Trophy className="h-5 w-5 inline" />
            ) : (
              `#${position}`
            )}
          </span>
          <h3 className="font-semibold truncate">{video.title}</h3>
        </div>
        <TagBadge tag={video.tag} />
      </div>

      {video.thumbnail_url && (
        <Link href={`/clip/${video.id}`}>
          <img
            src={video.thumbnail_url}
            alt={video.title}
            className="w-full aspect-video object-cover rounded-md"
            loading="lazy"
          />
        </Link>
      )}

      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>di <strong className="text-foreground">{video.uploader}</strong></span>
          {video.average_rating > 0 && (
            <span>Media: {video.average_rating.toFixed(1)}</span>
          )}
        </div>
        <div className="flex flex-col items-end gap-0.5">
          <StarRating
            value={video.my_rating_value ?? 0}
            onChange={handleRate}
            size="md"
          />
          {video.my_rating_value ? (
            <span className="text-xs text-muted-foreground">
              Il tuo voto: {video.my_rating_value}
            </span>
          ) : (
            <span className="text-xs text-muted-foreground">Vota</span>
          )}
        </div>
      </div>
    </Card>
  );
}

export default function ContestDetailPage() {
  const params = useParams<{ id: string }>();
  const contestId = Number(params.id);

  const {
    data: contest,
    isLoading: contestLoading,
    isError: contestError,
    refetch: refetchContest,
  } = useContestDetail(contestId);

  const {
    data: videosData,
    isLoading: videosLoading,
    isError: videosError,
    refetch: refetchVideos,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useContestVideos(contestId);

  const videos = useMemo(
    () => videosData?.pages.flatMap((p) => p.results) ?? [],
    [videosData]
  );

  if (contestLoading) return <PageLoader />;
  if (contestError || !contest) {
    return <ErrorMessage message="Contest non trovato." onRetry={refetchContest} />;
  }

  return (
    <div className="space-y-6">
      {/* Header contest */}
      <div className="space-y-2">
        <div className="flex items-start justify-between gap-3">
          <h1 className="text-2xl font-bold">{contest.name}</h1>
          <TagBadge tag={contest.tag} />
        </div>
        <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
          <span className="flex items-center gap-1">
            <Calendar className="h-4 w-4" />
            {formatShortDate(contest.start_date)} — {formatShortDate(contest.end_date)}
          </span>
          <span className="flex items-center gap-1">
            <Film className="h-4 w-4" />
            {contest.video_count} clip
          </span>
          {contest.is_closed ? (
            <span className="flex items-center gap-1 text-yellow-400 font-medium">
              <Trophy className="h-4 w-4" />
              Chiuso
            </span>
          ) : (
            <span className="text-green-400 font-medium">Attivo</span>
          )}
        </div>
      </div>

      {/* Sezione clip con votazione + classifica */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold">
          {contest.is_closed ? "Classifica finale" : "Clip in gara — Vota!"}
        </h2>

        {videosError ? (
          <ErrorMessage onRetry={refetchVideos} />
        ) : videosLoading ? (
          <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-64 rounded-lg" />
            ))}
          </div>
        ) : videos.length === 0 ? (
          <EmptyState
            icon={Film}
            title="Nessuna clip in gara"
            description="Non ci sono ancora clip in questo contest."
          />
        ) : (
          <>
            <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
              {videos.map((video, index) => (
                <ContestVideoCard
                  key={video.id}
                  video={video}
                  position={index + 1}
                  isWinner={contest.is_closed && contest.winner === video.id}
                  contestId={contestId}
                />
              ))}
            </div>
            <InfiniteScroll
              hasNextPage={hasNextPage}
              isFetchingNextPage={isFetchingNextPage}
              fetchNextPage={fetchNextPage}
            />
          </>
        )}
      </div>
    </div>
  );
}
