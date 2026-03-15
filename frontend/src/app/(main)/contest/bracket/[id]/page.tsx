"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { Calendar, Users, Trophy } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { PageLoader } from "@/components/shared/page-loader";
import { ErrorMessage } from "@/components/shared/error-message";
import { BracketTree } from "@/components/brackets/bracket-tree";
import { BracketWinner } from "@/components/brackets/bracket-winner";
import { MatchupDetail } from "@/components/brackets/matchup-detail";
import { EnterBracketForm } from "@/components/brackets/enter-bracket-form";
import { useBracketDetail } from "@/lib/hooks/use-brackets";
import { bracketStatusConfig } from "@/components/brackets/bracket-status";
import { formatRelativeDate } from "@/lib/utils";
import type { MatchupOutput } from "@/types/bracket";

export default function BracketDetailPage() {
  const params = useParams();
  const id = Number(params.id);
  const { data: bracket, isLoading, isError, refetch } = useBracketDetail(id);
  const [selectedMatchup, setSelectedMatchup] = useState<MatchupOutput | null>(null);

  if (isLoading) return <PageLoader />;
  if (isError || !bracket) return <ErrorMessage onRetry={refetch} />;

  const status = bracketStatusConfig[bracket.status];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-start justify-between gap-3">
          <h1 className="text-2xl font-bold">{bracket.name}</h1>
          <Badge className={status.className}>{status.label}</Badge>
        </div>
        {bracket.description && (
          <p className="text-sm text-muted-foreground">{bracket.description}</p>
        )}
        <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
          <span className="flex items-center gap-1">
            <Users className="h-3.5 w-3.5" />
            {bracket.entries_count}/{bracket.max_participants} iscritti
          </span>
          <span className="flex items-center gap-1">
            <Trophy className="h-3.5 w-3.5" />
            Turno {bracket.current_round}
          </span>
          <span className="flex items-center gap-1">
            <Calendar className="h-3.5 w-3.5" />
            {formatRelativeDate(bracket.created_at)}
          </span>
          <span>di {bracket.created_by_username}</span>
        </div>
        {bracket.prize_description && bracket.status !== "completed" && (
          <p className="text-sm text-yellow-400 font-medium">
            Premio: {bracket.prize_description}
          </p>
        )}
      </div>

      {/* Registration form */}
      {bracket.status === "registration" && !bracket.my_entry && (
        <EnterBracketForm bracketId={bracket.id} onEntered={refetch} />
      )}
      {bracket.status === "registration" && bracket.my_entry && (
        <Badge variant="outline" className="text-green-400 border-green-400/30">
          Sei iscritto con: {bracket.my_entry.video_title}
        </Badge>
      )}

      {/* Winner */}
      {bracket.status === "completed" && <BracketWinner bracket={bracket} />}

      {/* Bracket tree */}
      {Object.keys(bracket.matchups_by_round).length > 0 && (
        <div>
          <h2 className="text-lg font-bold mb-3">Tabellone</h2>
          <BracketTree
            matchupsByRound={bracket.matchups_by_round}
            onMatchupClick={setSelectedMatchup}
            currentRound={bracket.current_round}
          />
        </div>
      )}

      {/* Matchup detail modal */}
      {selectedMatchup && (
        <MatchupDetail
          matchup={selectedMatchup}
          bracketId={bracket.id}
          onClose={() => setSelectedMatchup(null)}
          onVoted={() => {
            setSelectedMatchup(null);
            refetch();
          }}
        />
      )}
    </div>
  );
}
