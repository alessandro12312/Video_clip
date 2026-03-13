"use client";

import { useMemo } from "react";
import Link from "next/link";
import { Trophy, Calendar, Film } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { TagBadge } from "@/components/shared/tag-badge";
import { EmptyState } from "@/components/shared/empty-state";
import { ErrorMessage } from "@/components/shared/error-message";
import { InfiniteScroll } from "@/components/shared/infinite-scroll";
import { useContests } from "@/lib/hooks/use-contests";
import { formatShortDate } from "@/lib/utils";
import type { Contest } from "@/types";

function ContestCard({ contest }: { contest: Contest }) {
  return (
    <Link href={`/contest/${contest.id}`}>
      <Card className="p-4 hover:border-primary/50 transition-colors cursor-pointer space-y-2">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-bold text-lg leading-snug line-clamp-1">
            {contest.name}
          </h3>
          <TagBadge tag={contest.tag} />
        </div>
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <span className="flex items-center gap-1">
            <Calendar className="h-3.5 w-3.5" />
            {formatShortDate(contest.start_date)} — {formatShortDate(contest.end_date)}
          </span>
          <span className="flex items-center gap-1">
            <Film className="h-3.5 w-3.5" />
            {contest.video_count} clip
          </span>
        </div>
        {contest.is_closed && (
          <div className="flex items-center gap-1 text-sm text-yellow-400 font-medium">
            <Trophy className="h-3.5 w-3.5" />
            {contest.winner_title
              ? `Vincitore: ${contest.winner_title}`
              : "Chiuso"}
          </div>
        )}
      </Card>
    </Link>
  );
}

function ContestListSkeleton() {
  return (
    <div className="grid gap-3">
      {Array.from({ length: 3 }).map((_, i) => (
        <Skeleton key={i} className="h-28 rounded-lg" />
      ))}
    </div>
  );
}

function ContestSection({
  title,
  isClosed,
}: {
  title: string;
  isClosed: boolean;
}) {
  const {
    data,
    isLoading,
    isError,
    refetch,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useContests({ is_closed: isClosed });

  const contests = useMemo(
    () => data?.pages.flatMap((p) => p.results) ?? [],
    [data]
  );

  if (isError) return <ErrorMessage onRetry={refetch} />;

  return (
    <section className="space-y-3">
      <h2 className="text-xl font-bold">{title}</h2>
      {isLoading ? (
        <ContestListSkeleton />
      ) : contests.length === 0 ? (
        <EmptyState
          icon={Trophy}
          title={isClosed ? "Nessun contest chiuso" : "Nessun contest attivo"}
          description={
            isClosed
              ? "I contest chiusi appariranno qui."
              : "Non ci sono contest attivi al momento."
          }
        />
      ) : (
        <>
          <div className="grid gap-3">
            {contests.map((contest) => (
              <ContestCard key={contest.id} contest={contest} />
            ))}
          </div>
          <InfiniteScroll
            hasNextPage={hasNextPage}
            isFetchingNextPage={isFetchingNextPage}
            fetchNextPage={fetchNextPage}
          />
        </>
      )}
    </section>
  );
}

export default function ContestPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Trophy className="h-6 w-6 text-yellow-400" />
          Contest
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Contest settimanali di Video_clip
        </p>
      </div>

      <ContestSection title="Contest Attivi" isClosed={false} />
      <ContestSection title="Contest Chiusi" isClosed={true} />
    </div>
  );
}
