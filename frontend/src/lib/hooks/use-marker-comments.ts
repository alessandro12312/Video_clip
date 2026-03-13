import { useMemo } from "react";
import type { Comment } from "@/types";

/**
 * Builds a map of timestamp → comment text for marker tooltips.
 * Priority: popupComments (top-liked, like >= 1) first, then fallback to first comment per timestamp.
 */
export function useMarkerComments(
  popupComments: Comment[],
  comments: Comment[]
): Map<number, { text: string }> {
  return useMemo(() => {
    const map = new Map<number, { text: string }>();
    for (const c of popupComments) {
      if (c.timestamp_second > 0) {
        map.set(c.timestamp_second, { text: c.content });
      }
    }
    for (const c of comments) {
      if (c.timestamp_second > 0 && !map.has(c.timestamp_second)) {
        map.set(c.timestamp_second, { text: c.content });
      }
    }
    return map;
  }, [popupComments, comments]);
}
