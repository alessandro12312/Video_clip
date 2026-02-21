"use client";

import { Badge } from "@/components/ui/badge";
import { formatTimestamp } from "@/lib/utils";
import { cn } from "@/lib/utils";

interface TimestampBadgeProps {
  seconds: number;
  onClick?: () => void;
  removable?: boolean;
  onRemove?: () => void;
  className?: string;
}

export function TimestampBadge({
  seconds,
  onClick,
  removable,
  onRemove,
  className,
}: TimestampBadgeProps) {
  return (
    <Badge
      variant="outline"
      className={cn(
        "cursor-pointer border-primary/30 bg-primary/10 text-primary text-xs font-mono",
        onClick && "hover:bg-primary/20",
        className
      )}
      onClick={onClick}
    >
      {formatTimestamp(seconds)}
      {removable && (
        <button
          type="button"
          className="ml-1 hover:text-destructive"
          onClick={(e) => {
            e.stopPropagation();
            onRemove?.();
          }}
        >
          ✕
        </button>
      )}
    </Badge>
  );
}
