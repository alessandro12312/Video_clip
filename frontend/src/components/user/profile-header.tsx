"use client";

import { UserAvatar } from "./user-avatar";
import { FollowButton } from "./follow-button";
import { useAuth } from "@/providers/auth-provider";
import type { User } from "@/types";

interface ProfileHeaderProps {
  profileUser: User;
}

export function ProfileHeader({ profileUser }: ProfileHeaderProps) {
  const { user: currentUser } = useAuth();
  const isOwnProfile = currentUser?.id === profileUser.id;
  const isFollowing = currentUser
    ? profileUser.followers.includes(currentUser.id)
    : false;

  return (
    <div className="flex items-start gap-4 p-4">
      <UserAvatar username={profileUser.username} size="lg" />

      <div className="flex-1">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold">{profileUser.username}</h1>
          {!isOwnProfile && (
            <FollowButton
              userId={profileUser.id}
              isFollowing={isFollowing}
            />
          )}
        </div>

        <div className="mt-2 flex gap-4 text-sm text-muted-foreground">
          <span>
            <strong className="text-foreground">
              {profileUser.followers.length}
            </strong>{" "}
            follower
          </span>
          <span>
            <strong className="text-foreground">
              {profileUser.following.length}
            </strong>{" "}
            seguiti
          </span>
        </div>
      </div>
    </div>
  );
}
