"use client";

import Image from "next/image";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import type { MatchupOutput, ContestEntryNested } from "@/types/bracket";

interface MatchupNodeProps {
  matchup: MatchupOutput;
  onClick?: () => void;
  isActive: boolean;
}

function EntryRow({
  entry,
  isWinner,
  isLoser,
  avgRating,
}: {
  entry: ContestEntryNested | null;
  isWinner: boolean;
  isLoser: boolean;
  avgRating: number | null;
}) {
  if (!entry) {
    return (
      <div className="flex items-center gap-2 px-2 py-1.5 text-xs text-muted-foreground/50">
        <div className="w-6 h-6 rounded bg-muted/30" />
        <span className="italic">BYE</span>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex items-center gap-2 px-2 py-1.5 text-xs transition-colors",
        isWinner && "bg-primary/10 font-semibold",
        isLoser && "opacity-50"
      )}
    >
      {entry.video_thumbnail_url ? (
        <Image
          src={entry.video_thumbnail_url}
          alt={entry.video_title}
          width={24}
          height={24}
          className="w-6 h-6 rounded object-cover"
          unoptimized
        />
      ) : (
        <div className="w-6 h-6 rounded bg-muted" />
      )}
      <span className="truncate flex-1 max-w-[100px]">{entry.username}</span>
      {avgRating !== null && (
        <span className="text-muted-foreground ml-auto tabular-nums">
          {avgRating.toFixed(1)}
        </span>
      )}
    </div>
  );
}

export function MatchupNode({ matchup, onClick, isActive }: MatchupNodeProps) {
  const isClickable = isActive && onClick;
  const isBye =
    matchup.is_completed && (!matchup.entry_1 || !matchup.entry_2);

  return (
    <div
      role={isClickable ? "button" : undefined}
      tabIndex={isClickable ? 0 : undefined}
      onClick={isClickable ? onClick : undefined}
      onKeyDown={
        isClickable
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") onClick?.();
            }
          : undefined
      }
      className={cn(
        "rounded-lg border bg-card text-card-foreground w-[200px] overflow-hidden transition-all",
        isClickable &&
          "cursor-pointer hover:border-primary/50 hover:shadow-md hover:shadow-primary/5",
        isBye && "opacity-60"
      )}
    >
      {isActive && !matchup.is_completed && (
        <div className="px-2 py-0.5 bg-green-500/20 text-green-400 text-[10px] font-bold text-center tracking-wider">
          LIVE
        </div>
      )}
      <EntryRow
        entry={matchup.entry_1}
        isWinner={
          matchup.is_completed && matchup.winner === matchup.entry_1?.id
        }
        isLoser={
          matchup.is_completed &&
          matchup.winner !== null &&
          matchup.winner !== matchup.entry_1?.id
        }
        avgRating={matchup.avg_rating_1}
      />
      <div className="border-t border-border/50" />
      <EntryRow
        entry={matchup.entry_2}
        isWinner={
          matchup.is_completed && matchup.winner === matchup.entry_2?.id
        }
        isLoser={
          matchup.is_completed &&
          matchup.winner !== null &&
          matchup.winner !== matchup.entry_2?.id
        }
        avgRating={matchup.avg_rating_2}
      />
    </div>
  );
}
