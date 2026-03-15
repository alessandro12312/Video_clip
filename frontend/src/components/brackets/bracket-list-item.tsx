"use client";

import Link from "next/link";
import { Users, Trophy } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatRelativeDate } from "@/lib/utils";
import { bracketStatusConfig } from "./bracket-status";
import type { BracketListItem as BracketListItemType } from "@/types/bracket";

interface BracketListItemProps {
  bracket: BracketListItemType;
}

export function BracketListItem({ bracket }: BracketListItemProps) {
  const status = bracketStatusConfig[bracket.status];

  return (
    <Link href={`/contest/bracket/${bracket.id}`}>
      <Card className="p-4 hover:border-primary/50 transition-colors cursor-pointer space-y-2">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-bold text-lg leading-snug line-clamp-1">
            {bracket.name}
          </h3>
          <Badge className={status.className}>{status.label}</Badge>
        </div>
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <span className="flex items-center gap-1">
            <Users className="h-3.5 w-3.5" />
            {bracket.entries_count}/{bracket.max_participants}
          </span>
          <span>Turno {bracket.current_round}</span>
          <span>{formatRelativeDate(bracket.created_at)}</span>
        </div>
        {bracket.prize_description && (
          <div className="flex items-center gap-1 text-sm text-yellow-400 font-medium">
            <Trophy className="h-3.5 w-3.5" />
            {bracket.prize_description}
          </div>
        )}
      </Card>
    </Link>
  );
}
