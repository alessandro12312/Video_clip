"use client";

import { useMemo, useState, useCallback, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { VideoPlayer, type VideoPlayerHandle } from "@/components/video/video-player";
import { CommentForm } from "@/components/comments/comment-form";
import { CommentSection } from "@/components/comments/comment-section";
import { CommentSidebar } from "@/components/comments/comment-sidebar";
import { DownloadButton } from "@/components/video/download-button";
import { TagBadge } from "@/components/shared/tag-badge";
import { UsernameLink } from "@/components/user/username-link";
import { UserAvatar } from "@/components/user/user-avatar";
import { PageLoader } from "@/components/shared/page-loader";
import { ErrorMessage } from "@/components/shared/error-message";
import { Button } from "@/components/ui/button";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { useAuth } from "@/providers/auth-provider";
import { useVideo, useDeleteVideo, useLikeVideo, useUnlikeVideo, usePopupComments } from "@/lib/hooks/use-videos";
import { useComments, useDeleteComment } from "@/lib/hooks/use-comments";
import { useMarkerComments } from "@/lib/hooks/use-marker-comments";
import { useIsDesktop } from "@/lib/hooks/use-media-query";
import { cn, formatRelativeDate, formatCount, formatTimestamp } from "@/lib/utils";
import { API_BASE_URL } from "@/lib/constants";
import { Eye, Heart, MessageCircle, Monitor, LogIn, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import type { Comment } from "@/types";

interface ClipContentProps {
  videoId: number;
}

export function ClipContent({ videoId }: ClipContentProps) {
  const { user, isAuthenticated, isAuthenticating: authLoading } = useAuth();
  const isDesktop = useIsDesktop();
  const router = useRouter();
  const playerRef = useRef<VideoPlayerHandle>(null);
  const playerContainerRef = useRef<HTMLDivElement>(null);

  const { data: video, isLoading: videoLoading, error: videoError, refetch: refetchVideo } = useVideo(videoId);
  const { data: comments = [], isLoading: commentsLoading } = useComments(videoId);
  const { data: popupComments = [] } = usePopupComments(videoId);
  const deleteVideo = useDeleteVideo();
  const { mutate: deleteComment } = useDeleteComment(videoId);
  const likeMutation = useLikeVideo();
  const unlikeMutation = useUnlikeVideo();

  const lastTapRef = useRef<number>(0);
  const tapTimerRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  // Cleanup tap timer on unmount
  useEffect(() => {
    return () => {
      clearTimeout(tapTimerRef.current);
    };
  }, []);

  const [pauseTimestamp, setPauseTimestamp] = useState<number | null>(null);
  const [playerTime, setPlayerTime] = useState<number | null>(null);
  const [viewMode, setViewMode] = useState<"popup" | "chat">("popup");
  const [showHeartAnimation, setShowHeartAnimation] = useState(false);

  const EMPTY_POPUP_MAP = useMemo(() => new Map<number, Comment>(), []);
  const EMPTY_MARKERS: number[] = useMemo(() => [], []);

  // Build popup map from backend-filtered popup comments (like >= 1, top per timestamp)
  const popupMap = useMemo(() => {
    const map = new Map<number, Comment>();
    for (const comment of popupComments) {
      map.set(comment.timestamp_second, comment);
    }
    return map;
  }, [popupComments]);

  const markerPositions = useMemo(() => {
    return [...new Set(comments.filter((c) => c.timestamp_second > 0).map((c) => c.timestamp_second))];
  }, [comments]);

  const markerCommentsMap = useMarkerComments(popupComments, comments);

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
    playerRef.current?.seekTo(seconds);
    playerContainerRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  }, []);

  const handleVideoTap = useCallback(() => {
    if (!video) return;
    const now = Date.now();
    if (now - lastTapRef.current < 300) {
      clearTimeout(tapTimerRef.current);
      if (!video.is_liked_by_me) {
        likeMutation.mutate(video.id);
        setShowHeartAnimation(true);
      }
    } else {
      tapTimerRef.current = setTimeout(() => {
        playerRef.current?.togglePlay();
      }, 300);
    }
    lastTapRef.current = now;
  }, [video, likeMutation]);

  const handleDeleteVideo = useCallback(() => {
    if (!video || deleteVideo.isPending) return;
    deleteVideo.mutate(video.id, {
      onSuccess: () => {
        toast.success("Clip eliminata");
        router.replace(`/profilo/${user?.username}`);
      },
      onError: () => toast.error("Errore nell'eliminazione della clip."),
    });
  }, [video, deleteVideo, router, user?.username]);

  const handleDeleteComment = useCallback(
    (commentId: number) => {
      deleteComment(commentId, {
        onSuccess: () => toast.success("Commento eliminato"),
        onError: () => toast.error("Errore nell'eliminazione del commento"),
      });
    },
    [deleteComment]
  );

  const handleRefreshUrl = useCallback(async () => {
    const result = await refetchVideo();
    if (result.isError) {
      throw new Error("Refresh URL fallito");
    }
  }, [refetchVideo]);

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
        <div ref={playerContainerRef} className="relative">
          <VideoPlayer
            ref={playerRef}
            src={videoSrc}
            videoId={video.id}
            duration={video.duration}
            popupMap={viewMode === "popup" ? popupMap : EMPTY_POPUP_MAP}
            markerPositions={viewMode === "popup" ? markerPositions : EMPTY_MARKERS}
            markerComments={viewMode === "popup" ? markerCommentsMap : undefined}
            onPause={handlePause}
            onTimeUpdate={handlePlayerTimeUpdate}
            onRefreshUrl={handleRefreshUrl}
          />
          {/* Double-tap overlay — only covers video, not controls */}
          <div
            className="absolute inset-0 bottom-20 z-10"
            onClick={handleVideoTap}
          />
          {/* Heart animation */}
          <AnimatePresence>
            {showHeartAnimation && (
              <motion.div
                className="absolute inset-0 flex items-center justify-center pointer-events-none z-50"
                initial={{ scale: 0, opacity: 1 }}
                animate={{ scale: 1.2, opacity: 1 }}
                exit={{ scale: 1.5, opacity: 0 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
                onAnimationComplete={() => setShowHeartAnimation(false)}
              >
                <Heart className="h-20 w-20 text-red-500 fill-current drop-shadow-lg" />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

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

          </div>

          <div className="flex flex-wrap items-center gap-1 text-xs text-muted-foreground">
            <Button
              variant="ghost"
              size="sm"
              className={`h-7 px-2 ${viewMode === "chat" ? "text-primary" : "text-muted-foreground hover:text-primary"}`}
              onClick={() => setViewMode((m) => (m === "popup" ? "chat" : "popup"))}
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
              className={cn(
                "h-7 px-2",
                video.is_liked_by_me
                  ? "text-red-500 hover:text-red-400"
                  : "text-muted-foreground hover:text-red-500"
              )}
              onClick={() =>
                video.is_liked_by_me
                  ? unlikeMutation.mutate(video.id)
                  : likeMutation.mutate(video.id)
              }
              disabled={likeMutation.isPending || unlikeMutation.isPending}
              title="Mi piace"
            >
              <Heart className={cn("h-3.5 w-3.5 sm:mr-1", video.is_liked_by_me && "fill-current")} />
              <span className="hidden sm:inline text-xs">{video.like_count}</span>
            </Button>
            <span className="flex items-center gap-1 ml-2">
              <Eye className="h-3.5 w-3.5" />
              {formatCount(video.views)}
            </span>
            <span>{formatRelativeDate(video.created_at)}</span>
            <DownloadButton
              videoId={video.id}
              isOwner={user?.username === video.uploader}
              allowDownload={video.allow_download}
            />
            {user?.username === video.uploader && (
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <button
                    className="text-muted-foreground/50 hover:text-destructive transition-colors"
                    aria-label="Elimina clip"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Eliminare questa clip?</AlertDialogTitle>
                    <AlertDialogDescription>
                      Sei sicuro di voler eliminare questa clip? L&apos;azione è
                      irreversibile. La clip, i commenti e i voti associati
                      verranno eliminati permanentemente.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Annulla</AlertDialogCancel>
                    <AlertDialogAction
                      onClick={handleDeleteVideo}
                      disabled={deleteVideo.isPending}
                      className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                    >
                      {deleteVideo.isPending ? "Eliminazione..." : "Elimina"}
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            )}
          </div>
        </div>

        <div className="pt-2 border-t border-border/50">
          <CommentForm
            videoId={video.id}
            pauseTimestamp={pauseTimestamp}
            onClearTimestamp={handleClearTimestamp}
            onSeekTo={(s) => playerRef.current?.seekTo(s)}
            videoDuration={video.duration}
          />
        </div>

        <CommentSection
          comments={comments}
          currentUsername={user?.username}
          videoId={videoId}
          onTimestampClick={handleTimestampClick}
          onDelete={handleDeleteComment}
        />

        {commentsLoading && (
          <p className="text-center text-sm text-muted-foreground py-4">
            Caricamento commenti...
          </p>
        )}
      </div>

      {isDesktop && viewMode === "chat" && (
        <aside className="w-72 shrink-0">
          <div className="sticky top-4">
            <CommentSidebar
              comments={comments}
              onTimestampClick={handleTimestampClick}
              maxVisible={10}
              currentTime={playerTime}
            />
          </div>
        </aside>
      )}
    </div>
  );
}
