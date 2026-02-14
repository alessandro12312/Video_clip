"use client";

import { useMemo } from "react";
import { useParams } from "next/navigation";
import { ProfileHeader } from "@/components/user/profile-header";
import { FeedGrid } from "@/components/feed/feed-grid";
import { InfiniteScroll } from "@/components/shared/infinite-scroll";
import { EmptyState } from "@/components/shared/empty-state";
import { PageLoader } from "@/components/shared/page-loader";
import { useUserVideos } from "@/lib/hooks/use-videos";
import { Film } from "lucide-react";

export default function ProfiloPage() {
  const params = useParams<{ username: string }>();
  const username = params.username;

  // We need user by username — use the users API list with filtering
  // For now, search by fetching all users (backend should support ?search=username)
  // The profile header requires a User object; we'll adapt
  const { data: userVideosData, isLoading: videosLoading, fetchNextPage, hasNextPage, isFetchingNextPage } =
    useUserVideos(username);

  const videos = useMemo(
    () => userVideosData?.pages.flatMap((p) => p.results) ?? [],
    [userVideosData]
  );

  // Find user ID from the first video uploader, or fall back
  // Since we know the username, construct a minimal profile display
  const { data: allUsers, isLoading: usersLoading } = useUserByUsername(username);

  if (usersLoading) return <PageLoader />;

  return (
    <div className="space-y-6">
      {/* Profile header */}
      {allUsers && <ProfileHeader profileUser={allUsers} />}

      {/* User's videos */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Le clip di {username}</h2>
        {videosLoading ? (
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

// Helper hook: get user by username (searches all users)
import { useQuery } from "@tanstack/react-query";
import { usersApi } from "@/lib/api/users";
import type { User } from "@/types";

function useUserByUsername(username: string) {
  return useQuery<User | null>({
    queryKey: ["users", "byUsername", username],
    queryFn: async () => {
      const page = await usersApi.getAll(1);
      const found = page.results.find((u) => u.username === username);
      return found ?? null;
    },
    staleTime: 60_000,
  });
}
