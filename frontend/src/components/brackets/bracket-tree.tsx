"use client";

import { useMemo } from "react";
import { MatchupNode } from "./matchup-node";
import type { MatchupOutput } from "@/types/bracket";

interface BracketTreeProps {
  matchupsByRound: Record<string, MatchupOutput[]>;
  onMatchupClick: (matchup: MatchupOutput) => void;
  currentRound: number;
}

/** SVG connector lines between two consecutive round columns */
function RoundConnectors({
  matchupCount,
  nodeHeight,
  gap,
}: {
  matchupCount: number;
  nodeHeight: number;
  gap: number;
}) {
  // Each pair of matchups in the current round feeds into one matchup in the next round
  const pairs = Math.floor(matchupCount / 2);
  if (pairs === 0) return null;

  const columnHeight = matchupCount * nodeHeight + (matchupCount - 1) * gap;
  const nextCount = pairs;
  const nextColumnHeight = nextCount * nodeHeight + (nextCount - 1) * gap;
  const height = Math.max(columnHeight, nextColumnHeight);
  const width = 32;

  const lines: { x1: number; y1: number; x2: number; y2: number }[] = [];

  for (let i = 0; i < pairs; i++) {
    // Source: center-right of matchup i*2 and i*2+1
    const srcTopY =
      (columnHeight - height) / 2 +
      (i * 2) * (nodeHeight + gap) +
      nodeHeight / 2;
    const srcBotY =
      (columnHeight - height) / 2 +
      (i * 2 + 1) * (nodeHeight + gap) +
      nodeHeight / 2;
    // Dest: center-left of matchup i in next round
    const nextOffsetY = (height - nextColumnHeight) / 2;
    const dstY = nextOffsetY + i * (nodeHeight + gap) + nodeHeight / 2;

    // Horizontal from source to midpoint, then vertical, then horizontal to dest
    const midX = width / 2;
    lines.push(
      { x1: 0, y1: srcTopY, x2: midX, y2: srcTopY },
      { x1: midX, y1: srcTopY, x2: midX, y2: srcBotY },
      { x1: midX, y1: dstY, x2: width, y2: dstY },
      // vertical from midpoint srcTop to dstY (which is between srcTop and srcBot)
    );
  }

  // Use path for cleaner rendering
  let pathD = "";
  for (let i = 0; i < pairs; i++) {
    const srcTopY =
      (columnHeight - height) / 2 +
      (i * 2) * (nodeHeight + gap) +
      nodeHeight / 2;
    const srcBotY =
      (columnHeight - height) / 2 +
      (i * 2 + 1) * (nodeHeight + gap) +
      nodeHeight / 2;
    const nextOffsetY = (height - nextColumnHeight) / 2;
    const dstY = nextOffsetY + i * (nodeHeight + gap) + nodeHeight / 2;
    const midX = width / 2;

    // Top source → midpoint
    pathD += `M 0 ${srcTopY} H ${midX} `;
    // Bottom source → midpoint
    pathD += `M 0 ${srcBotY} H ${midX} `;
    // Vertical connector
    pathD += `M ${midX} ${srcTopY} V ${srcBotY} `;
    // Midpoint → dest
    pathD += `M ${midX} ${dstY} H ${width} `;
  }

  return (
    <svg
      width={width}
      height={height}
      className="shrink-0"
      style={{ minHeight: height }}
    >
      <path
        d={pathD}
        fill="none"
        stroke="currentColor"
        className="text-border"
        strokeWidth={1.5}
      />
    </svg>
  );
}

export function BracketTree({
  matchupsByRound,
  onMatchupClick,
  currentRound,
}: BracketTreeProps) {
  const rounds = useMemo(() => {
    return Object.entries(matchupsByRound)
      .map(([roundStr, matchups]) => ({
        round: parseInt(roundStr, 10),
        matchups: [...matchups].sort((a, b) => a.position - b.position),
      }))
      .sort((a, b) => a.round - b.round);
  }, [matchupsByRound]);

  if (rounds.length === 0) {
    return (
      <p className="text-sm text-muted-foreground text-center py-8">
        Nessun matchup disponibile.
      </p>
    );
  }

  // Approximate node height and gap for SVG connector calculations
  const nodeHeight = 72;
  const gap = 16;

  return (
    <div className="overflow-x-auto pb-4">
      <div
        className="flex items-stretch min-w-max"
        style={{ minHeight: "200px" }}
      >
        {rounds.map(({ round, matchups }, roundIndex) => {
          const roundLabel =
            rounds.length > 1 && round === rounds[rounds.length - 1].round
              ? "Finale"
              : rounds.length > 2 &&
                  round === rounds[rounds.length - 2].round
                ? "Semifinale"
                : `Turno ${round}`;

          return (
            <div key={round} className="flex items-stretch">
              <div className="flex flex-col items-center gap-2">
                <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
                  {roundLabel}
                </h3>
                <div className="flex flex-col justify-around flex-1 gap-4">
                  {matchups.map((matchup) => {
                    const isActive =
                      round === currentRound &&
                      !matchup.is_completed &&
                      matchup.entry_1 !== null &&
                      matchup.entry_2 !== null;

                    return (
                      <MatchupNode
                        key={matchup.id}
                        matchup={matchup}
                        isActive={isActive}
                        onClick={
                          isActive
                            ? () => onMatchupClick(matchup)
                            : undefined
                        }
                      />
                    );
                  })}
                </div>
              </div>
              {/* Connector lines to next round */}
              {roundIndex < rounds.length - 1 && matchups.length > 1 && (
                <div className="flex items-center">
                  <RoundConnectors
                    matchupCount={matchups.length}
                    nodeHeight={nodeHeight}
                    gap={gap}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
