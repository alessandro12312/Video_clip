import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Formatta secondi in "M:SS" (es. 78 → "1:18") */
export function formatTimestamp(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

/** Formatta data ISO in formato relativo italiano */
export function formatRelativeDate(isoDate: string): string {
  const now = new Date();
  const date = new Date(isoDate);
  const diffMs = now.getTime() - date.getTime();
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSeconds < 60) return "adesso";
  if (diffMinutes < 60) return `${diffMinutes}m fa`;
  if (diffHours < 24) return `${diffHours}h fa`;
  if (diffDays < 7) return `${diffDays}g fa`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}sett fa`;
  return date.toLocaleDateString("it-IT", { day: "numeric", month: "short" });
}

/** Formatta numero con abbreviazione (es. 1200 → "1.2K") */
export function formatCount(count: number): string {
  if (count < 1000) return count.toString();
  if (count < 1_000_000)
    return `${(count / 1000).toFixed(1).replace(/\.0$/, "")}K`;
  return `${(count / 1_000_000).toFixed(1).replace(/\.0$/, "")}M`;
}

/** Formatta secondi in "MM:SS" con zero-padding (es. 78 → "01:18") */
export function formatMMSS(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
}

/** Parsa "MM:SS" o "M:SS" in secondi. Ritorna null se non valido. */
export function parseMMSS(value: string): number | null {
  const match = value.match(/^(\d{1,2}):(\d{2})$/);
  if (!match) return null;
  const minutes = parseInt(match[1], 10);
  const secs = parseInt(match[2], 10);
  if (secs >= 60) return null;
  return minutes * 60 + secs;
}

/** Estrae il numero di pagina da un URL paginato Django */
export function extractPageFromUrl(url: string | null): number | undefined {
  if (!url) return undefined;
  const match = url.match(/[?&]page=(\d+)/);
  return match ? parseInt(match[1], 10) : undefined;
}
