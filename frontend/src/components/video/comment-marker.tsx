"use client";

import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { formatTimestamp } from "@/lib/utils";

interface CommentMarkerProps {
  timestamp: number;
  position: number;
  size: number;
  commentText?: string;
  onSeek?: (timestamp: number) => void;
}

export function CommentMarker({ timestamp, position, size, commentText, onSeek }: CommentMarkerProps) {
  const displayText = commentText && commentText.length > 60
    ? commentText.slice(0, 57) + "..."
    : commentText;

  const tooltipLabel = displayText
    ? `${formatTimestamp(timestamp)} — ${displayText}`
    : `Commento a ${formatTimestamp(timestamp)}`;

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <div
          className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 rounded-full gradient-bg opacity-80 hover:opacity-100 hover:scale-150 transition-all z-10 cursor-pointer"
          style={{
            left: `${position}%`,
            width: size,
            height: size,
          }}
          role="button"
          tabIndex={0}
          aria-label={tooltipLabel}
          onClick={(e) => {
            e.stopPropagation();
            onSeek?.(timestamp);
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              e.stopPropagation();
              onSeek?.(timestamp);
            }
          }}
        />
      </TooltipTrigger>
      <TooltipContent side="top" className="text-xs max-w-[250px]">
        {tooltipLabel}
      </TooltipContent>
    </Tooltip>
  );
}
