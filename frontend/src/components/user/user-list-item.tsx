"use client";

import Link from "next/link";
import { UserAvatar } from "./user-avatar";
import { FollowButton } from "./follow-button";
import { Skeleton } from "@/components/ui/skeleton";
import type { User } from "@/types";

interface UserListItemProps {
  user: User;
}

export function UserListItem({ user }: UserListItemProps) {
  return (
    <div className="flex items-center gap-3 p-3 rounded-lg hover:bg-accent/50 transition-colors">
      <Link
        href={`/profilo/${user.username}`}
        aria-label={`Profilo di ${user.username}`}
      >
        <UserAvatar username={user.username} size="md" />
      </Link>

      <div className="flex-1 min-w-0">
        <Link
          href={`/profilo/${user.username}`}
          className="font-bold text-sm hover:underline"
          aria-label={`Vai al profilo di ${user.username}`}
        >
          {user.username}
        </Link>
        {user.bio && (
          <p className="text-xs text-muted-foreground truncate">{user.bio}</p>
        )}
      </div>

      <FollowButton
        userId={user.id}
        username={user.username}
        isFollowing={user.is_followed_by_me}
        size="sm"
        className="ml-auto"
      />
    </div>
  );
}

export function UserListItemSkeleton({ count = 5 }: { count?: number }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="flex items-center gap-3 p-3 rounded-lg"
        >
          <Skeleton className="h-9 w-9 rounded-full" />
          <div className="flex-1 min-w-0 space-y-1.5">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-3 w-40" />
          </div>
          <Skeleton className="h-8 w-20 ml-auto" />
        </div>
      ))}
    </>
  );
}
