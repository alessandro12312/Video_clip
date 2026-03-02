"use client";

import { useMemo, useState, useCallback, useRef, useEffect } from "react";
import Link from "next/link";
import { Eye, MessageSquare, Play } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { VideoPlayer, type VideoPlayerHandle } from "@/components/video/video-player";
import { CommentForm } from "@/components/comments/comment-form";
import { CommentSidebar } from "@/components/comments/comment-sidebar";
import { StarRating } from "@/components/rating/star-rating";
import { TagBadge } from "@/components/shared/tag-badge";
import { UserAvatar } from "@/components/user/user-avatar";
import { UsernameLink } from "@/components/user/username-link";
import { useAuth } from "@/providers/auth-provider";
import { useComments } from "@/lib/hooks/use-comments";
import { useIntersection } from "@/lib/hooks/use-intersection";
import { useIsDesktop } from "@/lib/hooks/use-media-query";
import { videosApi } from "@/lib/api/videos";
import { formatCount, formatRelativeDate, formatTimestamp } from "@/lib/utils";
import { API_BASE_URL } from "@/lib/constants";
import type { Video, Comment } from "@/types";

const CARD_ACTIVATE_EVENT = "card-player-activate";

const PREVIEW_LOOP_SECONDS = 5;

type CardVideoState = "idle" | "hovering" | "playing";

interface CardAsPlayerProps {
  video: Video;
}

export function CardAsPlayer({ video }: CardAsPlayerProps) {
  const { isAuthenticated } = useAuth();
  const isDesktop = useIsDesktop();
  const playerRef = useRef<VideoPlayerHandle>(null);
  const playerContainerRef = useRef<HTMLDivElement>(null);
  const previewRef = useRef<HTMLVideoElement>(null);
  const cardIdRef = useRef(video.id);

  // Viewport detection: load comments when card is near viewport
  const { ref: intersectionRef, isIntersecting } = useIntersection("200px");
  const { data: comments = [] } = useComments(video.id, { enabled: isIntersecting });

  const [videoState, setVideoState] = useState<CardVideoState>("idle");
  const [thumbError, setThumbError] = useState(false);
  const [pauseTimestamp, setPauseTimestamp] = useState<number | null>(null);
  const [currentSrc, setCurrentSrc] = useState(
    video.file.startsWith("http") ? video.file : `${API_BASE_URL}${video.file}`
  );

  // Deactivate player when card exits viewport
  useEffect(() => {
    if (!isIntersecting && videoState === "playing") {
      setVideoState("idle");
      setPauseTimestamp(null);
    }
  }, [isIntersecting, videoState]);

  // Single active player: listen for other cards activating
  useEffect(() => {
    function handleOtherActivate(e: Event) {
      const activatedId = (e as CustomEvent<number>).detail;
      if (activatedId !== cardIdRef.current && videoState === "playing") {
        setVideoState("idle");
        setPauseTimestamp(null);
      }
    }
    window.addEventListener(CARD_ACTIVATE_EVENT, handleOtherActivate);
    return () => window.removeEventListener(CARD_ACTIVATE_EVENT, handleOtherActivate);
  }, [videoState]);

  const showThumbnail = video.thumbnail_url && !thumbError;

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
    if (videoState !== "playing") {
      window.dispatchEvent(new CustomEvent(CARD_ACTIVATE_EVENT, { detail: video.id }));
      setVideoState("playing");
    }
    // Small delay to let VideoPlayer mount before seeking
    setTimeout(() => {
      playerRef.current?.seekTo(seconds);
      playerContainerRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
    }, 100);
  }, [videoState, video.id]);

  const handleRefreshUrl = useCallback(async () => {
    const fresh = await videosApi.getById(video.id);
    const newSrc = fresh.file.startsWith("http")
      ? fresh.file
      : `${API_BASE_URL}${fresh.file}`;
    setCurrentSrc(newSrc);
  }, [video.id]);

  // Hover preview handlers (desktop only)
  const handleMouseEnter = useCallback(() => {
    if (!isDesktop || videoState === "playing") return;
    setVideoState("hovering");
  }, [isDesktop, videoState]);

  const handleMouseLeave = useCallback(() => {
    if (videoState !== "hovering") return;
    setVideoState("idle");
    const preview = previewRef.current;
    if (preview) {
      preview.pause();
      preview.currentTime = 0;
    }
  }, [videoState]);

  // Loop first N seconds during hover preview
  const handlePreviewTimeUpdate = useCallback(() => {
    const preview = previewRef.current;
    if (!preview) return;
    if (preview.currentTime >= PREVIEW_LOOP_SECONDS) {
      preview.currentTime = 0;
    }
  }, []);

  // Click to activate full player (single-player enforcement)
  const handleActivatePlayer = useCallback(() => {
    window.dispatchEvent(new CustomEvent(CARD_ACTIVATE_EVENT, { detail: video.id }));
    setVideoState("playing");
  }, [video.id]);

  return (
    <Card ref={intersectionRef} className="overflow-hidden border-border/50">
      {/* Video area + Sidebar */}
      <div className="flex flex-col lg:flex-row" ref={playerContainerRef}>
        {/* Video area */}
        <div
          className="lg:flex-1 min-w-0 relative"
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
          {videoState === "playing" ? (
            <VideoPlayer
              ref={playerRef}
              src={currentSrc}
              videoId={video.id}
              duration={video.duration}
              popupMap={popupMap}
              markerPositions={markerPositions}
              onPause={handlePause}
              onRefreshUrl={handleRefreshUrl}
            />
          ) : (
            <div
              className="relative aspect-video bg-black cursor-pointer"
              onClick={handleActivatePlayer}
            >
              {/* Hover preview video */}
              {videoState === "hovering" && (
                <video
                  ref={previewRef}
                  src={currentSrc}
                  muted
                  autoPlay
                  playsInline
                  preload="metadata"
                  onTimeUpdate={handlePreviewTimeUpdate}
                  className="absolute inset-0 h-full w-full object-cover"
                />
              )}

              {/* Thumbnail (visible when idle, or as fallback) */}
              {videoState === "idle" && (
                <>
                  {showThumbnail ? (
                    <img
                      src={video.thumbnail_url!}
                      alt={video.title}
                      className="absolute inset-0 h-full w-full object-cover"
                      loading="lazy"
                      onError={() => setThumbError(true)}
                    />
                  ) : (
                    <div className="absolute inset-0 flex items-center justify-center bg-muted">
                      <Play className="h-12 w-12 text-muted-foreground/30" />
                    </div>
                  )}
                </>
              )}

              {/* Play button overlay (idle only) */}
              {videoState === "idle" && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/20 transition-opacity hover:bg-black/30">
                  <div className="rounded-full bg-black/60 p-3">
                    <Play className="h-8 w-8 text-white fill-white" />
                  </div>
                </div>
              )}

              {/* Duration badge */}
              <span className="absolute bottom-2 right-2 rounded bg-black/70 px-1.5 py-0.5 text-xs font-mono text-white">
                {formatTimestamp(video.duration)}
              </span>

              {/* Tag badge */}
              <div className="absolute top-2 left-2">
                <TagBadge tag={video.tag} />
              </div>
            </div>
          )}
        </div>

        {/* Sidebar — desktop */}
        <div className="hidden lg:block w-72 shrink-0 border-l border-border/50 p-3">
          <CommentSidebar
            comments={comments}
            onTimestampClick={handleTimestampClick}
            maxVisible={6}
          />
        </div>
      </div>

      {/* Sidebar — mobile */}
      <div className="lg:hidden px-3 pt-2 pb-1 border-t border-border/50">
        <CommentSidebar
          comments={comments}
          onTimestampClick={handleTimestampClick}
          maxVisible={3}
        />
      </div>

      {/* Metadata */}
      <div className="px-3 py-2 flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <Link href={`/clip/${video.id}`}>
            <h3 className="font-semibold text-base truncate hover:text-primary transition-colors">
              {video.title}
            </h3>
          </Link>
          <div className="flex items-center gap-2 mt-1">
            <UserAvatar username={video.uploader} size="sm" />
            <UsernameLink username={video.uploader} className="text-sm" />
            {videoState === "playing" || <TagBadge tag={video.tag} />}
          </div>
        </div>
        <div className="flex flex-col items-end gap-0.5 shrink-0">
          <StarRating value={video.average_rating} readonly size="sm" />
          <div className="flex items-center gap-3 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <Eye className="h-3 w-3" />
              {formatCount(video.views)}
            </span>
            <span>{formatRelativeDate(video.created_at)}</span>
          </div>
        </div>
      </div>

      {/* Comment form (only when playing) */}
      {isAuthenticated && videoState === "playing" && (
        <div className="px-3 pb-2 border-t border-border/50 pt-2">
          <CommentForm
            videoId={video.id}
            pauseTimestamp={pauseTimestamp}
            onClearTimestamp={handleClearTimestamp}
            onSeekTo={(s) => playerRef.current?.seekTo(s)}
            videoDuration={video.duration}
          />
        </div>
      )}

      {/* Link to detail */}
      <div className="px-3 pb-3 border-t border-border/50 pt-2">
        <Link href={`/clip/${video.id}`}>
          <Button variant="ghost" size="sm" className="w-full text-muted-foreground hover:text-primary">
            <MessageSquare className="h-4 w-4 mr-2" />
            Visualizza tutti i commenti ({comments.length})
          </Button>
        </Link>
      </div>
    </Card>
  );
}
