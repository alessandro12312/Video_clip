"use client";

import { useMemo, useState, useCallback } from "react";
import Link from "next/link";
import { VideoPlayer } from "@/components/video/video-player";
import { CommentForm } from "@/components/comments/comment-form";
import { CommentSection } from "@/components/comments/comment-section";
import { DynamicSidebar } from "@/components/comments/dynamic-sidebar";
import { StarRating } from "@/components/rating/star-rating";
import { TagBadge } from "@/components/shared/tag-badge";
import { UsernameLink } from "@/components/user/username-link";
import { UserAvatar } from "@/components/user/user-avatar";
import { PageLoader } from "@/components/shared/page-loader";
import { ErrorMessage } from "@/components/shared/error-message";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/providers/auth-provider";
import { useVideo } from "@/lib/hooks/use-videos";
import { useComments } from "@/lib/hooks/use-comments";
import { useCreateRating } from "@/lib/hooks/use-ratings";
import { useIsWideDesktop } from "@/lib/hooks/use-media-query";
import { formatRelativeDate, formatCount, formatTimestamp } from "@/lib/utils";
import { API_BASE_URL } from "@/lib/constants";
import { Eye, Star, LogIn } from "lucide-react";
import { toast } from "sonner";
import type { Comment } from "@/types";

interface ClipContentProps {
  videoId: number;
}

export function ClipContent({ videoId }: ClipContentProps) {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const isWideDesktop = useIsWideDesktop();

  const { data: video, isLoading: videoLoading, error: videoError } = useVideo(videoId);
  const { data: comments = [], isLoading: commentsLoading } = useComments(videoId);
  const { mutate: createRating } = useCreateRating(videoId);

  const [pauseTimestamp, setPauseTimestamp] = useState<number | null>(null);

  // Build popup map: Map<second, top comment for that second>
  const popupMap = useMemo(() => {
    const map = new Map<number, Comment>();
    for (const comment of comments) {
      if (comment.timestamp_second <= 0) continue;
      const existing = map.get(comment.timestamp_second);
      if (!existing || new Date(comment.created_at) > new Date(existing.created_at)) {
        map.set(comment.timestamp_second, comment);
      }
    }
    return map;
  }, [comments]);

  const markerPositions = useMemo(() => {
    return [...new Set(comments.filter((c) => c.timestamp_second > 0).map((c) => c.timestamp_second))];
  }, [comments]);

  const handlePause = useCallback((currentTime: number) => {
    setPauseTimestamp(Math.floor(currentTime));
  }, []);

  const handleClearTimestamp = useCallback(() => {
    setPauseTimestamp(null);
  }, []);

  const handleTimestampClick = useCallback((seconds: number) => {
    const videoEl = document.querySelector("video");
    if (videoEl) {
      videoEl.currentTime = seconds;
      videoEl.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, []);

  const handleRate = useCallback(
    (value: number) => {
      createRating(
        { video: videoId, value },
        {
          onSuccess: () => toast.success("Voto registrato!"),
          onError: () => toast.error("Errore nel salvataggio del voto."),
        }
      );
    },
    [createRating, videoId]
  );

  if (authLoading || videoLoading) return <PageLoader />;
  if (videoError || !video) return <ErrorMessage message="Video non trovato." />;

  const videoSrc = video.file.startsWith("http") ? video.file : `${API_BASE_URL}${video.file}`;

  // Public (unauthenticated) view
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-background flex flex-col">
        <header className="border-b border-border/50 p-4">
          <div className="mx-auto max-w-4xl flex items-center justify-between">
            <Link href="/" className="text-xl font-bold gradient-text">
              Video_clip
            </Link>
            <Link href="/login">
              <Button size="sm" className="gradient-bg">
                <LogIn className="h-4 w-4 mr-2" />
                Accedi
              </Button>
            </Link>
          </div>
        </header>

        <main className="flex-1 mx-auto max-w-4xl w-full p-4 space-y-4">
          <div className="relative overflow-hidden rounded-lg bg-black">
            <video src={videoSrc} controls playsInline className="w-full aspect-video" />
          </div>

          <div className="space-y-3">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <h1 className="text-xl font-bold">{video.title}</h1>
                <div className="flex items-center gap-3 mt-2">
                  <span className="text-sm text-muted-foreground">
                    di <strong className="text-foreground">{video.uploader}</strong>
                  </span>
                  <TagBadge tag={video.tag} />
                </div>
              </div>
              <span className="font-mono text-sm text-muted-foreground">
                {formatTimestamp(video.duration)}
              </span>
            </div>

            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span className="flex items-center gap-1">
                <Eye className="h-4 w-4" />
                {formatCount(video.views)} visualizzazioni
              </span>
              {video.average_rating > 0 && (
                <span className="flex items-center gap-1">
                  <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  {video.average_rating.toFixed(1)}
                </span>
              )}
            </div>
          </div>

          <div className="glass rounded-xl p-6 text-center space-y-3">
            <h2 className="text-lg font-bold">Vuoi commentare e votare?</h2>
            <p className="text-sm text-muted-foreground">
              Accedi a Video_clip per lasciare commenti temporizzati, votare le
              clip e seguire i tuoi creator preferiti.
            </p>
            <div className="flex justify-center gap-3">
              <Link href="/login">
                <Button className="gradient-bg">Accedi</Button>
              </Link>
              <Link href="/registrati">
                <Button variant="outline">Registrati</Button>
              </Link>
            </div>
          </div>
        </main>
      </div>
    );
  }

  // Authenticated view
  return (
    <div className="flex gap-6">
      <div className="flex-1 min-w-0 space-y-4">
        <VideoPlayer
          src={videoSrc}
          videoId={video.id}
          duration={video.duration}
          popupMap={popupMap}
          markerPositions={markerPositions}
          onPause={handlePause}
        />

        <div className="space-y-3">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <h1 className="text-xl font-bold truncate">{video.title}</h1>
              <div className="flex items-center gap-3 mt-2">
                <UserAvatar username={video.uploader} size="sm" />
                <UsernameLink username={video.uploader} className="text-sm font-medium" />
                <TagBadge tag={video.tag} />
              </div>
            </div>

            <div className="flex flex-col items-end gap-1 shrink-0">
              <StarRating value={video.average_rating} onChange={handleRate} size="md" />
              <span className="text-xs text-muted-foreground">
                {video.average_rating > 0 ? video.average_rating.toFixed(1) : "Non votato"}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <Eye className="h-3.5 w-3.5" />
              {formatCount(video.views)} visualizzazioni
            </span>
            <span>{formatRelativeDate(video.created_at)}</span>
          </div>
        </div>

        <div className="pt-2 border-t border-border/50">
          <CommentForm
            videoId={video.id}
            pauseTimestamp={pauseTimestamp}
            onClearTimestamp={handleClearTimestamp}
          />
        </div>

        <CommentSection
          comments={comments}
          onTimestampClick={handleTimestampClick}
        />

        {commentsLoading && (
          <p className="text-center text-sm text-muted-foreground py-4">
            Caricamento commenti...
          </p>
        )}
      </div>

      {isWideDesktop && (
        <aside className="w-80 shrink-0">
          <div className="sticky top-4">
            <DynamicSidebar
              comments={comments}
              onTimestampClick={handleTimestampClick}
            />
          </div>
        </aside>
      )}
    </div>
  );
}
