"use client";

import { useRef, useState, useCallback, useEffect, forwardRef, useImperativeHandle } from "react";
import { PlayerControls } from "./player-controls";
import { ProgressBar } from "./progress-bar";
import { PopupOverlay } from "./popup-overlay";
import { useIncrementViews } from "@/lib/hooks/use-videos";
import { POPUP_DISPLAY_DURATION_MS, VIEW_COUNT_DELAY_MS } from "@/lib/constants";
import type { Comment } from "@/types";

const MAX_RETRIES = 2;

export interface VideoPlayerHandle {
  seekTo: (seconds: number) => void;
}

interface VideoPlayerProps {
  src: string;
  videoId: number;
  duration: number;
  popupMap: Map<number, Comment>;
  markerPositions: number[];
  onPause?: (currentTime: number) => void;
  onTimeUpdate?: (currentTime: number) => void;
  onRefreshUrl?: () => Promise<void>;
}

export const VideoPlayer = forwardRef<VideoPlayerHandle, VideoPlayerProps>(function VideoPlayer({
  src,
  videoId,
  duration,
  popupMap,
  markerPositions,
  onPause,
  onTimeUpdate,
  onRefreshUrl,
}, ref) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [buffered, setBuffered] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [activePopup, setActivePopup] = useState<Comment | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const popupTimeoutRef = useRef<NodeJS.Timeout>(null);
  const viewSentRef = useRef(false);
  const viewTimerRef = useRef<NodeJS.Timeout>(null);
  const lastPopupSecondRef = useRef(-1);
  const retryCountRef = useRef(0);
  const savedTimeRef = useRef(0);

  const { mutate: incrementViews } = useIncrementViews();

  useImperativeHandle(ref, () => ({
    seekTo: (seconds: number) => {
      const video = videoRef.current;
      if (!video) return;
      video.currentTime = seconds;
      setCurrentTime(seconds);
      lastPopupSecondRef.current = -1;
    },
  }));

  // Handle time update — check for popups
  const handleTimeUpdate = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;

    setCurrentTime(video.currentTime);
    onTimeUpdate?.(video.currentTime);

    // Update buffered
    if (video.buffered.length > 0) {
      setBuffered(video.buffered.end(video.buffered.length - 1));
    }

    // Check popup map
    const second = Math.floor(video.currentTime);
    if (second !== lastPopupSecondRef.current) {
      lastPopupSecondRef.current = second;
      const popup = popupMap.get(second);
      if (popup) {
        setActivePopup(popup);
        if (popupTimeoutRef.current) clearTimeout(popupTimeoutRef.current);
        popupTimeoutRef.current = setTimeout(() => {
          setActivePopup(null);
        }, POPUP_DISPLAY_DURATION_MS);
      }
    }
  }, [popupMap, onTimeUpdate]);

  // Play handler
  const handlePlay = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;
    video.play();
    setIsPlaying(true);

    // Start view count timer
    if (!viewSentRef.current) {
      viewTimerRef.current = setTimeout(() => {
        incrementViews(videoId);
        viewSentRef.current = true;
      }, VIEW_COUNT_DELAY_MS);
    }
  }, [incrementViews, videoId]);

  // Pause handler
  const handlePause = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;
    video.pause();
    setIsPlaying(false);
    onPause?.(video.currentTime);

    // Cancel view timer
    if (viewTimerRef.current && !viewSentRef.current) {
      clearTimeout(viewTimerRef.current);
    }
  }, [onPause]);

  const togglePlay = useCallback(() => {
    if (isPlaying) {
      handlePause();
    } else {
      handlePlay();
    }
  }, [isPlaying, handlePause, handlePlay]);

  // Seek handler
  const handleSeek = useCallback((time: number) => {
    const video = videoRef.current;
    if (!video) return;
    video.currentTime = time;
    setCurrentTime(time);
    lastPopupSecondRef.current = -1;
  }, []);

  // Volume handler
  const handleVolumeChange = useCallback((newVolume: number) => {
    const video = videoRef.current;
    if (!video) return;
    video.volume = newVolume;
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
  }, []);

  const toggleMute = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;
    if (isMuted) {
      video.muted = false;
      setIsMuted(false);
    } else {
      video.muted = true;
      setIsMuted(true);
    }
  }, [isMuted]);

  // Fullscreen
  const toggleFullscreen = useCallback(() => {
    const container = videoRef.current?.parentElement;
    if (!container) return;
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      container.requestFullscreen();
    }
  }, []);

  // Reset tutto quando cambia video (navigazione a clip diversa)
  useEffect(() => {
    retryCountRef.current = 0;
    savedTimeRef.current = 0;
    setIsRefreshing(false);
    setErrorMessage(null);
  }, [videoId]);

  // Riprendi playback dopo caricamento nuova sorgente
  const handleLoadedData = useCallback(() => {
    if (savedTimeRef.current > 0) {
      const video = videoRef.current;
      if (video) {
        video.currentTime = savedTimeRef.current;
        video.play().catch(() => {});
        savedTimeRef.current = 0;
      }
    }
    setIsRefreshing(false);
    setErrorMessage(null);
  }, []);

  // Handler errore video — retry per URL scadute
  const handleVideoError = useCallback(async () => {
    const video = videoRef.current;
    if (!video?.error) return;

    const code = video.error.code;

    // Solo MEDIA_ERR_NETWORK (2) e MEDIA_ERR_SRC_NOT_SUPPORTED (4) triggherano retry
    if (code !== 2 && code !== 4) {
      setErrorMessage("Impossibile riprodurre il video");
      return;
    }

    if (retryCountRef.current >= MAX_RETRIES) {
      setIsRefreshing(false);
      setErrorMessage("Video non disponibile, ricarica la pagina");
      return;
    }

    retryCountRef.current += 1;
    savedTimeRef.current = video.currentTime;
    setIsRefreshing(true);

    try {
      await onRefreshUrl?.();
    } catch {
      // API refetch fallita — mostra errore di fallback
      setIsRefreshing(false);
      setErrorMessage("Video non disponibile, ricarica la pagina");
    }
  }, [onRefreshUrl]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (popupTimeoutRef.current) clearTimeout(popupTimeoutRef.current);
      if (viewTimerRef.current) clearTimeout(viewTimerRef.current);
    };
  }, []);

  return (
    <div className="relative flex flex-col overflow-hidden rounded-lg bg-black max-h-[70vh]">
      {/* Video element */}
      <video
        ref={videoRef}
        src={src}
        className="w-full min-h-0 flex-1 object-contain cursor-pointer"
        onTimeUpdate={handleTimeUpdate}
        onEnded={() => setIsPlaying(false)}
        onClick={togglePlay}
        onError={handleVideoError}
        onLoadedData={handleLoadedData}
        onPlay={() => setIsPlaying(true)}
        playsInline
        autoPlay
      />

      {/* Spinner durante refresh URL */}
      {isRefreshing && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-white/30 border-t-white" />
        </div>
      )}

      {/* Messaggio di errore */}
      {errorMessage && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/70">
          <p className="text-sm text-white/80">{errorMessage}</p>
        </div>
      )}

      {/* Popup overlay */}
      <PopupOverlay comment={activePopup} />

      {/* Progress bar with comment markers */}
      <ProgressBar
        currentTime={currentTime}
        buffered={buffered}
        duration={duration}
        markers={markerPositions}
        onSeek={handleSeek}
      />

      {/* Controls */}
      <PlayerControls
        isPlaying={isPlaying}
        currentTime={currentTime}
        duration={duration}
        volume={volume}
        isMuted={isMuted}
        onTogglePlay={togglePlay}
        onVolumeChange={handleVolumeChange}
        onToggleMute={toggleMute}
        onToggleFullscreen={toggleFullscreen}
      />
    </div>
  );
});
