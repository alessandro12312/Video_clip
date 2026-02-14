import { Badge } from "@/components/ui/badge";
import { TAG_COLORS } from "@/lib/constants";
import { cn } from "@/lib/utils";
import type { VideoTag } from "@/types";

interface TagBadgeProps {
  tag: VideoTag;
  className?: string;
}

export function TagBadge({ tag, className }: TagBadgeProps) {
  const colors = TAG_COLORS[tag];
  return (
    <Badge
      variant="outline"
      className={cn(colors.bg, colors.text, "border-0 text-xs font-medium", className)}
    >
      {colors.label}
    </Badge>
  );
}
