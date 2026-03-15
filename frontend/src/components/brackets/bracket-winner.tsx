"use client";

import { useMemo } from "react";
import { Trophy } from "lucide-react";
import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import type { BracketDetail } from "@/types/bracket";

interface BracketWinnerProps {
  bracket: BracketDetail;
}

export function BracketWinner({ bracket }: BracketWinnerProps) {
  const winner = useMemo(() => {
    if (bracket.status !== "completed") return null;
    const rounds = Object.entries(bracket.matchups_by_round).sort(
      ([a], [b]) => parseInt(b, 10) - parseInt(a, 10)
    );
    if (rounds.length === 0) return null;
    const finalMatchups = rounds[0][1];
    const finalMatchup = finalMatchups.find((m) => m.is_completed && m.winner);
    if (!finalMatchup) return null;
    if (finalMatchup.winner === finalMatchup.entry_1?.id)
      return finalMatchup.entry_1;
    if (finalMatchup.winner === finalMatchup.entry_2?.id)
      return finalMatchup.entry_2;
    return null;
  }, [bracket.status, bracket.matchups_by_round]);

  if (!winner) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      <Card className="p-6 text-center border-yellow-400/30 bg-yellow-400/5">
        <Trophy className="h-10 w-10 text-yellow-400 mx-auto mb-3" />
        <h2 className="text-xl font-bold mb-1">Vincitore del Torneo</h2>
        <p className="text-lg font-semibold text-primary">{winner.username}</p>
        <p className="text-sm text-muted-foreground">{winner.video_title}</p>
        {bracket.prize_description && (
          <p className="text-sm text-yellow-400 mt-2 font-medium">
            {bracket.prize_description}
          </p>
        )}
      </Card>
    </motion.div>
  );
}
