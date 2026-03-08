import type { TopRatedRange } from "@/types";

export const queryKeys = {
  videos: {
    all: ["videos"] as const,
    list: (page: number) => ["videos", "list", page] as const,
    detail: (id: number) => ["videos", "detail", id] as const,
    following: (page: number) => ["videos", "following", page] as const,
    followingAll: ["videos", "following"] as const,
    topRated: (range: TopRatedRange) =>
      ["videos", "top-rated", range] as const,
    byUser: (userId: number) => ["videos", "user", userId] as const,
    popupComments: (videoId: number) =>
      ["videos", "popup-comments", videoId] as const,
  },
  comments: {
    byVideo: (videoId: number) => ["comments", "video", videoId] as const,
  },
  ratings: {
    byVideo: (videoId: number) => ["ratings", "video", videoId] as const,
  },
  users: {
    detail: (id: number) => ["users", id] as const,
    byUsername: (username: string) => ["users", "username", username] as const,
    followers: (id: number) => ["users", id, "followers"] as const,
    following: (id: number) => ["users", id, "following"] as const,
    search: (query: string) => ["users", "search", query] as const,
  },
  contests: {
    all: ["contests"] as const,
    list: (params?: { is_closed?: boolean }) =>
      ["contests", "list", params] as const,
    detail: (id: number) => ["contests", "detail", id] as const,
    videos: (id: number) => ["contests", "videos", id] as const,
    winners: ["contests", "winners"] as const,
  },
  notifications: {
    all: ["notifications"] as const,
    list: (page?: number) => ["notifications", "list", page] as const,
    unreadCount: ["notifications", "unread-count"] as const,
  },
} as const;
