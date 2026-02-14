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
}

export function CommentMarker({ timestamp, position, size }: CommentMarkerProps) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <div
          className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 rounded-full gradient-bg opacity-80 hover:opacity-100 hover:scale-150 transition-all z-10"
          style={{
            left: `${position}%`,
            width: size,
            height: size,
          }}
        />
      </TooltipTrigger>
      <TooltipContent side="top" className="text-xs">
        Commento a {formatTimestamp(timestamp)}
      </TooltipContent>
    </Tooltip>
  );
}
