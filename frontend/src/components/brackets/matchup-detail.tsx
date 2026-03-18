"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { StarRating } from "@/components/rating/star-rating";
import { useVoteMatchup } from "@/lib/hooks/use-brackets";
import { cn } from "@/lib/utils";
import type { MatchupOutput, ContestEntryNested } from "@/types/bracket";

interface MatchupDetailProps {
  matchup: MatchupOutput;
  bracketId: number;
  onClose: () => void;
  onVoted: () => void;
}

function EntryCard({
  entry,
  avgRating,
  isWinner,
  isSelected,
  selectedRating,
  onSelect,
  onRate,
  canVote,
}: {
  entry: ContestEntryNested;
  avgRating: number | null;
  isWinner: boolean;
  isSelected: boolean;
  selectedRating: number;
  onSelect: () => void;
  onRate: (value: number) => void;
  canVote: boolean;
}) {
  return (
    <div
      role={canVote ? "button" : undefined}
      tabIndex={canVote ? 0 : undefined}
      onClick={canVote ? onSelect : undefined}
      onKeyDown={
        canVote
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") onSelect();
            }
          : undefined
      }
      className={cn(
        "flex flex-col items-center gap-3 rounded-lg border p-4 flex-1 min-w-0 transition-all",
        isWinner && "border-primary bg-primary/5",
        canVote && "cursor-pointer hover:border-primary/30",
        canVote && isSelected && "border-primary bg-primary/5 ring-1 ring-primary/30"
      )}
    >
      <Link
        href={`/clip/${entry.video_id}`}
        className="w-full"
        onClick={(e) => e.stopPropagation()}
      >
        {entry.video_thumbnail_url ? (
          <Image
            src={entry.video_thumbnail_url}
            alt={entry.video_title}
            width={320}
            height={180}
            className="w-full aspect-video rounded object-cover"
            unoptimized
          />
        ) : (
          <div className="w-full aspect-video rounded bg-muted flex items-center justify-center text-xs text-muted-foreground">
            Nessuna anteprima
          </div>
        )}
      </Link>
      <div className="text-center space-y-1">
        <p className="font-semibold text-sm truncate max-w-[180px]">
          {entry.username}
        </p>
        <p className="text-xs text-muted-foreground truncate max-w-[180px]">
          {entry.video_title}
        </p>
        {avgRating !== null && (
          <p className="text-xs text-muted-foreground">
            Media: {avgRating.toFixed(1)} / 5
          </p>
        )}
      </div>
      {canVote && isSelected && (
        <div
          className="flex flex-col items-center gap-1"
          onClick={(e) => e.stopPropagation()}
        >
          <p className="text-xs text-muted-foreground">Il tuo voto:</p>
          <StarRating value={selectedRating} onChange={onRate} size="md" />
        </div>
      )}
      {isWinner && (
        <span className="text-xs font-bold text-primary uppercase">
          Vincitore
        </span>
      )}
    </div>
  );
}

export function MatchupDetail({
  matchup,
  bracketId,
  onClose,
  onVoted,
}: MatchupDetailProps) {
  const [selectedEntryId, setSelectedEntryId] = useState<number | null>(null);
  const [rating, setRating] = useState(0);
  const voteMutation = useVoteMatchup(bracketId);

  const canVote =
    !matchup.is_completed && !!matchup.entry_1 && !!matchup.entry_2;

  const handleSelectEntry = (entryId: number) => {
    if (selectedEntryId !== entryId) {
      setSelectedEntryId(entryId);
      setRating(0);
    }
  };

  const handleSubmitVote = () => {
    if (!selectedEntryId || rating === 0) return;
    voteMutation.mutate(
      { matchupId: matchup.id, data: { entry: selectedEntryId, value: rating } },
      { onSuccess: () => onVoted() }
    );
  };

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>
            {matchup.is_completed ? "Risultato Matchup" : "Vota il Matchup"}
          </DialogTitle>
          <DialogDescription>
            {matchup.is_completed
              ? "Il matchup e' completato. Ecco il risultato finale."
              : "Seleziona una clip, assegna da 1 a 5 stelle, e conferma il voto."}
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col sm:flex-row gap-4">
          {matchup.entry_1 && (
            <EntryCard
              entry={matchup.entry_1}
              avgRating={matchup.avg_rating_1}
              isWinner={matchup.winner === matchup.entry_1.id}
              isSelected={selectedEntryId === matchup.entry_1.id}
              selectedRating={
                selectedEntryId === matchup.entry_1.id ? rating : 0
              }
              onSelect={() => handleSelectEntry(matchup.entry_1!.id)}
              onRate={setRating}
              canVote={canVote}
            />
          )}

          <div className="flex items-center justify-center text-lg font-bold text-muted-foreground">
            VS
          </div>

          {matchup.entry_2 && (
            <EntryCard
              entry={matchup.entry_2}
              avgRating={matchup.avg_rating_2}
              isWinner={matchup.winner === matchup.entry_2.id}
              isSelected={selectedEntryId === matchup.entry_2.id}
              selectedRating={
                selectedEntryId === matchup.entry_2.id ? rating : 0
              }
              onSelect={() => handleSelectEntry(matchup.entry_2!.id)}
              onRate={setRating}
              canVote={canVote}
            />
          )}
        </div>

        {canVote && (
          <Button
            onClick={handleSubmitVote}
            disabled={!selectedEntryId || rating === 0 || voteMutation.isPending}
            className="w-full"
          >
            {voteMutation.isPending
              ? "Invio voto in corso..."
              : "Invia voto"}
          </Button>
        )}
      </DialogContent>
    </Dialog>
  );
}
