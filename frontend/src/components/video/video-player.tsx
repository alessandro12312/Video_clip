"use client";

import { useRef, useState, useCallback, useEffect } from "react";
import { PlayerControls } from "./player-controls";
import { ProgressBar } from "./progress-bar";
import { PopupOverlay } from "./popup-overlay";
import { useIncrementViews } from "@/lib/hooks/use-videos";
import { POPUP_DISPLAY_DURATION_MS, VIEW_COUNT_DELAY_MS } from "@/lib/constants";
import type { Comment } from "@/types";

interface VideoPlayerProps {
  src: string;
  videoId: number;
  duration: number;
  popupMap: Map<number, Comment>;
  markerPositions: number[];
  onPause?: (currentTime: number) => void;
}

export function VideoPlayer({
  src,
  videoId,
  duration,
  popupMap,
  markerPositions,
  onPause,
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [buffered, setBuffered] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [activePopup, setActivePopup] = useState<Comment | null>(null);
  const popupTimeoutRef = useRef<NodeJS.Timeout>(null);
  const viewSentRef = useRef(false);
  const viewTimerRef = useRef<NodeJS.Timeout>(null);
  const lastPopupSecondRef = useRef(-1);

  const { mutate: incrementViews } = useIncrementViews();

  // Handle time update — check for popups
  const handleTimeUpdate = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;

    setCurrentTime(video.currentTime);

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
  }, [popupMap]);

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

  // Cleanup
  useEffect(() => {
    return () => {
      if (popupTimeoutRef.current) clearTimeout(popupTimeoutRef.current);
      if (viewTimerRef.current) clearTimeout(viewTimerRef.current);
    };
  }, []);

  return (
    <div className="relative overflow-hidden rounded-lg bg-black">
      {/* Video element */}
      <video
        ref={videoRef}
        src={src}
        className="w-full aspect-video cursor-pointer"
        onTimeUpdate={handleTimeUpdate}
        onEnded={() => setIsPlaying(false)}
        onClick={togglePlay}
        playsInline
      />

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
}
