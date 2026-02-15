export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export const PAGE_SIZE = 10;

export const TAG_COLORS = {
  clutch: { bg: "bg-clutch/20", text: "text-clutch", label: "Clutch" },
  funny: { bg: "bg-funny/20", text: "text-funny", label: "Funny" },
  fail: { bg: "bg-fail/20", text: "text-fail", label: "Fail" },
} as const;

export const TOP_RATED_RANGES = [
  { value: "day", label: "Oggi" },
  { value: "week", label: "Settimana" },
  { value: "month", label: "Mese" },
  { value: "year", label: "Anno" },
  { value: "all", label: "Sempre" },
] as const;

export const NAV_ITEMS = [
  { href: "/home", label: "Home", icon: "Home" },
  { href: "/esplora", label: "Esplora", icon: "Compass" },
  { href: "/carica", label: "Carica", icon: "Upload" },
  { href: "/profilo", label: "Profilo", icon: "User" },
  { href: "/contest", label: "Contest", icon: "Trophy" },
] as const;

export const POPUP_DISPLAY_DURATION_MS = 4000;
export const VIEW_COUNT_DELAY_MS = 5000;
export const COMMENT_MARKER_SIZE_PX = 6;
