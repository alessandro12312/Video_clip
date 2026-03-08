"use client";

import { useMemo, useState, useCallback, useRef, useEffect } from "react";
import Link from "next/link";
import { Eye, ExternalLink, Heart, MessageCircle, MessageSquare, Monitor, Play } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { VideoPlayer, type VideoPlayerHandle } from "@/components/video/video-player";
import { CommentForm } from "@/components/comments/comment-form";
import { CommentSidebar } from "@/components/comments/comment-sidebar";
import { CommentSection } from "@/components/comments/comment-section";
import { StarRating } from "@/components/rating/star-rating";
import { TagBadge } from "@/components/shared/tag-badge";
import { UserAvatar } from "@/components/user/user-avatar";
import { UsernameLink } from "@/components/user/username-link";
import { useAuth } from "@/providers/auth-provider";
import { useComments, useDeleteComment } from "@/lib/hooks/use-comments";
import { useIntersection } from "@/lib/hooks/use-intersection";
import { useIsDesktop } from "@/lib/hooks/use-media-query";
import { videosApi } from "@/lib/api/videos";
import { formatCount, formatRelativeDate, formatTimestamp } from "@/lib/utils";
import { API_BASE_URL } from "@/lib/constants";
import type { Video, Comment } from "@/types";

const CARD_ACTIVATE_EVENT = "card-player-activate";
const PREVIEW_LOOP_SECONDS = 5;
const EMPTY_POPUP_MAP = new Map<number, Comment>();
const EMPTY_MARKERS: number[] = [];

type CardVideoState = "idle" | "hovering" | "playing";
type CardViewMode = "popup" | "chat";

interface CardAsPlayerProps {
  video: Video;
}

export function CardAsPlayer({ video }: CardAsPlayerProps) {
  const { isAuthenticated, user } = useAuth();
  const isDesktop = useIsDesktop();
  const playerRef = useRef<VideoPlayerHandle>(null);
  const playerContainerRef = useRef<HTMLDivElement>(null);
  const previewRef = useRef<HTMLVideoElement>(null);
  const cardIdRef = useRef(video.id);

  // Viewport detection: load comments when card is near viewport
  const { ref: intersectionRef, isIntersecting } = useIntersection("200px");
  const { data: comments = [] } = useComments(video.id, { enabled: isIntersecting });
  const { mutate: deleteComment } = useDeleteComment(video.id);

  const [videoState, setVideoState] = useState<CardVideoState>("idle");
  const [viewMode, setViewMode] = useState<CardViewMode>("popup");
  const [showComments, setShowComments] = useState(false);
  const [thumbError, setThumbError] = useState(false);
  const [pauseTimestamp, setPauseTimestamp] = useState<number | null>(null);
  const [playerTime, setPlayerTime] = useState<number | null>(null);
  const [currentSrc, setCurrentSrc] = useState(
    video.file.startsWith("http") ? video.file : `${API_BASE_URL}${video.file}`
  );

  // Deactivate player when card exits viewport
  useEffect(() => {
    if (!isIntersecting && videoState === "playing") {
      setVideoState("idle");
      setPauseTimestamp(null);
      setPlayerTime(null);
    }
  }, [isIntersecting, videoState]);

  // Single active player: listen for other cards activating
  useEffect(() => {
    function handleOtherActivate(e: Event) {
      const activatedId = (e as CustomEvent<number>).detail;
      if (activatedId !== cardIdRef.current && videoState === "playing") {
        setVideoState("idle");
        setPauseTimestamp(null);
        setPlayerTime(null);
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

  const handlePlayerTimeUpdate = useCallback((currentTime: number) => {
    setPlayerTime(currentTime);
  }, []);

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

  const toggleViewMode = useCallback(() => {
    setViewMode((m) => (m === "popup" ? "chat" : "popup"));
  }, []);

  return (
    <Card ref={intersectionRef} data-snap-target className="overflow-hidden border-border/50 flex flex-col h-[calc(100dvh-5.5rem)]">
      {/* Video area + Sidebar (YouTube/Twitch style) */}
      <div className="flex flex-col lg:flex-row flex-1 min-h-0" ref={playerContainerRef}>
        {/* Video area */}
        <div
          className="flex-1 min-w-0 min-h-0 relative"
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
          {videoState === "playing" ? (
            <VideoPlayer
              ref={playerRef}
              src={currentSrc}
              videoId={video.id}
              duration={video.duration}
              popupMap={viewMode === "popup" ? popupMap : EMPTY_POPUP_MAP}
              markerPositions={viewMode === "popup" ? markerPositions : EMPTY_MARKERS}
              onPause={handlePause}
              onTimeUpdate={handlePlayerTimeUpdate}
              onRefreshUrl={handleRefreshUrl}
            />
          ) : (
            <div
              className="relative bg-black cursor-pointer overflow-hidden h-full"
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
                  className="w-full h-full object-contain"
                />
              )}

              {/* Thumbnail (visible when idle, or as fallback) */}
              {videoState === "idle" && (
                <>
                  {showThumbnail ? (
                    <img
                      src={video.thumbnail_url!}
                      alt={video.title}
                      className="w-full h-full object-contain"
                      loading="lazy"
                      onError={() => setThumbError(true)}
                    />
                  ) : (
                    <div className="flex items-center justify-center bg-muted h-full">
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

        {/* Chat sidebar — below on mobile/tablet, lateral on lg+ (Twitch style) */}
        {viewMode === "chat" && (
          <div className="border-t lg:border-t-0 lg:border-l border-border/50 p-2 lg:p-3 lg:w-72 shrink-0 overflow-y-auto max-h-48 lg:max-h-none">
            <CommentSidebar
              comments={comments}
              onTimestampClick={handleTimestampClick}
              maxVisible={4}
              currentTime={playerTime}
            />
          </div>
        )}
      </div>

      {/* Title (YouTube style — below video) */}
      <div className="px-3 pt-2">
        <Link href={`/clip/${video.id}`} className="block">
          <h3 className="font-bold text-lg leading-snug line-clamp-2 hover:text-primary transition-colors">
            {video.title}
          </h3>
        </Link>
      </div>

      {/* Profile row */}
      <div className="px-3 pt-1.5 flex items-center gap-2 min-w-0">
        <UserAvatar username={video.uploader} size="sm" />
        <UsernameLink username={video.uploader} className="text-sm" />
        <span className="text-muted-foreground">·</span>
        <span className="flex items-center gap-1 text-xs text-muted-foreground shrink-0">
          <Eye className="h-3 w-3" />
          {formatCount(video.views)}
        </span>
        <span className="text-xs text-muted-foreground shrink-0">
          {formatRelativeDate(video.created_at)}
        </span>
      </div>

      {/* Actions row */}
      <div className="px-3 pt-1 pb-2 flex flex-wrap items-center gap-1">
        {/* View mode toggle — moved outside video */}
        <Button
          variant="ghost"
          size="sm"
          className={`h-7 px-2 ${viewMode === "chat" ? "text-primary" : "text-muted-foreground hover:text-primary"}`}
          onClick={toggleViewMode}
          title={viewMode === "popup" ? "Mostra chat laterale" : "Mostra popup sul video"}
        >
          {viewMode === "popup" ? (
            <MessageCircle className="h-3.5 w-3.5 sm:mr-1" />
          ) : (
            <Monitor className="h-3.5 w-3.5 sm:mr-1" />
          )}
          <span className="hidden sm:inline text-xs">{viewMode === "popup" ? "Chat" : "Popup"}</span>
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="text-muted-foreground hover:text-red-500 h-7 px-2 opacity-40"
          disabled
          title="Mi piace (in arrivo)"
        >
          <Heart className="h-3.5 w-3.5 sm:mr-1" />
          <span className="hidden sm:inline text-xs">Mi piace</span>
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className={`h-7 px-2 ${showComments ? "text-primary" : "text-muted-foreground hover:text-primary"}`}
          onClick={() => setShowComments((prev) => !prev)}
          title="Commenti"
        >
          <MessageSquare className="h-3.5 w-3.5 sm:mr-1" />
          <span className="hidden sm:inline text-xs">Commenti</span>
          <span className="text-xs">({comments.length})</span>
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="text-muted-foreground hover:text-primary h-7 px-2"
          asChild
        >
          <Link href={`/clip/${video.id}`} title="Vai al dettaglio">
            <ExternalLink className="h-3.5 w-3.5 sm:mr-1" />
            <span className="hidden sm:inline text-xs">Dettaglio</span>
          </Link>
        </Button>
        <div className="flex-1" />
        <StarRating value={video.average_rating} readonly size="sm" />
      </div>

      {/* Expandable comment section */}
      {showComments && (
        <div className="px-3 pb-3 border-t border-border/50 pt-2 space-y-3 overflow-y-auto max-h-48">
          {isAuthenticated && (
            <CommentForm
              videoId={video.id}
              pauseTimestamp={pauseTimestamp}
              onClearTimestamp={handleClearTimestamp}
              onSeekTo={videoState === "playing" ? (s) => playerRef.current?.seekTo(s) : undefined}
              videoDuration={video.duration}
            />
          )}
          <CommentSection
            comments={comments}
            currentUsername={user?.username}
            onTimestampClick={handleTimestampClick}
            onDelete={(commentId) => deleteComment(commentId)}
            videoId={video.id}
          />
        </div>
      )}
    </Card>
  );
}
