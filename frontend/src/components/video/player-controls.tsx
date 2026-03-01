"use client";

import { Play, Pause, Volume2, VolumeX, Maximize } from "lucide-react";
import { Button } from "@/components/ui/button";
import { formatTimestamp } from "@/lib/utils";

interface PlayerControlsProps {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  isMuted: boolean;
  onTogglePlay: () => void;
  onVolumeChange: (volume: number) => void;
  onToggleMute: () => void;
  onToggleFullscreen: () => void;
}

export function PlayerControls({
  isPlaying,
  currentTime,
  duration,
  isMuted,
  onTogglePlay,
  onToggleMute,
  onToggleFullscreen,
}: PlayerControlsProps) {
  return (
    <div className="flex items-center gap-2 bg-black/60 px-3 py-1.5">
      {/* Play/Pause */}
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8 text-white hover:bg-white/10"
        onClick={onTogglePlay}
      >
        {isPlaying ? (
          <Pause className="h-4 w-4" />
        ) : (
          <Play className="h-4 w-4" />
        )}
      </Button>

      {/* Time display */}
      <span className="min-w-[5rem] text-xs font-mono text-white/80">
        {formatTimestamp(currentTime)} / {formatTimestamp(duration)}
      </span>

      <div className="flex-1" />

      {/* Volume */}
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8 text-white hover:bg-white/10"
        onClick={onToggleMute}
      >
        {isMuted ? (
          <VolumeX className="h-4 w-4" />
        ) : (
          <Volume2 className="h-4 w-4" />
        )}
      </Button>

      {/* Fullscreen */}
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8 text-white hover:bg-white/10"
        onClick={onToggleFullscreen}
      >
        <Maximize className="h-4 w-4" />
      </Button>
    </div>
  );
}
