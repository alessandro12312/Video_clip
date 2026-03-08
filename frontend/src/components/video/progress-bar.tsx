"use client";

import { useRef, useCallback, useState } from "react";
import { CommentMarker } from "./comment-marker";
import { COMMENT_MARKER_SIZE_PX } from "@/lib/constants";

interface ProgressBarProps {
  currentTime: number;
  buffered: number;
  duration: number;
  markers: number[];
  markerComments?: Map<number, { text: string }>;
  onMarkerSeek?: (timestamp: number) => void;
  onSeek: (time: number) => void;
}

export function ProgressBar({
  currentTime,
  buffered,
  duration,
  markers,
  markerComments,
  onMarkerSeek,
  onSeek,
}: ProgressBarProps) {
  const barRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const getTimeFromPosition = useCallback(
    (clientX: number) => {
      const bar = barRef.current;
      if (!bar || duration === 0) return 0;
      const rect = bar.getBoundingClientRect();
      const percent = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
      return percent * duration;
    },
    [duration]
  );

  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      setIsDragging(true);
      onSeek(getTimeFromPosition(e.clientX));

      const handleMouseMove = (moveEvent: MouseEvent) => {
        onSeek(getTimeFromPosition(moveEvent.clientX));
      };
      const handleMouseUp = () => {
        setIsDragging(false);
        window.removeEventListener("mousemove", handleMouseMove);
        window.removeEventListener("mouseup", handleMouseUp);
      };

      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
    },
    [getTimeFromPosition, onSeek]
  );

  const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0;
  const bufferedPercent = duration > 0 ? (buffered / duration) * 100 : 0;

  return (
    <div
      ref={barRef}
      className="group relative h-2 cursor-pointer bg-white/10 transition-all hover:h-3"
      onMouseDown={handleMouseDown}
    >
      {/* Buffered */}
      <div
        className="absolute inset-y-0 left-0 bg-white/20"
        style={{ width: `${bufferedPercent}%` }}
      />

      {/* Progress (gradient) */}
      <div
        className="absolute inset-y-0 left-0 gradient-bg"
        style={{ width: `${progressPercent}%` }}
      />

      {/* Seek thumb */}
      {isDragging && (
        <div
          className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 h-4 w-4 rounded-full gradient-bg shadow-lg"
          style={{ left: `${progressPercent}%` }}
        />
      )}

      {/* Comment markers */}
      {markers.map((timestamp) => {
        const position = duration > 0 ? (timestamp / duration) * 100 : 0;
        return (
          <CommentMarker
            key={timestamp}
            timestamp={timestamp}
            position={position}
            size={COMMENT_MARKER_SIZE_PX}
            commentText={markerComments?.get(timestamp)?.text}
            onSeek={onMarkerSeek}
          />
        );
      })}
    </div>
  );
}
