"use client";

import { useMemo } from "react";
import { useParams } from "next/navigation";
import { ProfileHeader } from "@/components/user/profile-header";
import { FeedGrid } from "@/components/feed/feed-grid";
import { InfiniteScroll } from "@/components/shared/infinite-scroll";
import { EmptyState } from "@/components/shared/empty-state";
import { PageLoader } from "@/components/shared/page-loader";
import { useUserVideos } from "@/lib/hooks/use-videos";
import { useUserByUsername } from "@/lib/hooks/use-users";
import { AlertTriangle, Film, UserX } from "lucide-react";

export default function ProfiloPage() {
  const params = useParams<{ username: string }>();
  const username = params.username;

  const { data: profileUser, isLoading: usersLoading, isError } = useUserByUsername(username);

  const { data: userVideosData, isLoading: videosLoading, isError: videosError, fetchNextPage, hasNextPage, isFetchingNextPage } =
    useUserVideos(profileUser?.id ?? 0);

  const videos = useMemo(
    () => userVideosData?.pages.flatMap((p) => p.results) ?? [],
    [userVideosData]
  );

  const totalVideoCount = userVideosData?.pages[0]?.count ?? 0;

  if (usersLoading) return <PageLoader />;

  if (isError || !profileUser) {
    return (
      <EmptyState
        icon={UserX}
        title="Utente non trovato"
        description={`L'utente "${username}" non esiste o non è disponibile.`}
      />
    );
  }

  return (
    <div className="space-y-6">
      <ProfileHeader profileUser={profileUser} videoCount={totalVideoCount} />

      <div>
        <h2 className="text-lg font-semibold mb-4">Le clip di {username}</h2>
        {videosError ? (
          <EmptyState
            icon={AlertTriangle}
            title="Errore nel caricamento"
            description="Impossibile caricare le clip. Riprova più tardi."
          />
        ) : videosLoading ? (
          <FeedGrid videos={[]} isLoading />
        ) : videos.length === 0 ? (
          <EmptyState
            icon={Film}
            title="Nessuna clip"
            description={`${username} non ha ancora caricato clip.`}
          />
        ) : (
          <>
            <FeedGrid videos={videos} />
            <InfiniteScroll
              hasNextPage={hasNextPage}
              isFetchingNextPage={isFetchingNextPage}
              fetchNextPage={fetchNextPage}
            />
          </>
        )}
      </div>
    </div>
  );
}
