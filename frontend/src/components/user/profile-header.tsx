"use client";

import { useState } from "react";
import { UserAvatar } from "./user-avatar";
import { FollowButton } from "./follow-button";
import { ProfileEditForm } from "./profile-edit-form";
import { useAuth } from "@/providers/auth-provider";
import { Button } from "@/components/ui/button";
import { Pencil, Film } from "lucide-react";
import Link from "next/link";
import type { User } from "@/types";

interface ProfileHeaderProps {
  profileUser: User;
  videoCount?: number;
}

export function ProfileHeader({ profileUser, videoCount }: ProfileHeaderProps) {
  const { user: currentUser } = useAuth();
  const isOwnProfile = currentUser?.id === profileUser.id;
  const isFollowing = profileUser.is_followed_by_me;
  const [isEditing, setIsEditing] = useState(false);

  return (
    <div className="flex items-start gap-4 p-4">
      <UserAvatar username={profileUser.username} size="lg" />

      <div className="flex-1">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold">{profileUser.username}</h1>
          {!isOwnProfile && (
            <FollowButton
              userId={profileUser.id}
              username={profileUser.username}
              isFollowing={isFollowing}
            />
          )}
          {isOwnProfile && !isEditing && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsEditing(true)}
              aria-label="Modifica profilo"
            >
              <Pencil className="h-4 w-4 mr-1" />
              Modifica profilo
            </Button>
          )}
        </div>

        {profileUser.bio && !isEditing && (
          <p className="mt-2 text-sm text-muted-foreground">{profileUser.bio}</p>
        )}

        <div className="mt-2 flex gap-4 text-sm text-muted-foreground">
          <Link
            href={`/profilo/${profileUser.username}/followers`}
            className="hover:underline cursor-pointer"
            aria-label={`${profileUser.followers_count} follower di ${profileUser.username}`}
          >
            <strong className="text-foreground">
              {profileUser.followers_count}
            </strong>{" "}
            follower
          </Link>
          <Link
            href={`/profilo/${profileUser.username}/following`}
            className="hover:underline cursor-pointer"
            aria-label={`${profileUser.following_count} utenti seguiti da ${profileUser.username}`}
          >
            <strong className="text-foreground">
              {profileUser.following_count}
            </strong>{" "}
            seguiti
          </Link>
          {videoCount !== undefined && (
            <span>
              <Film className="inline h-4 w-4 mr-1" />
              <strong className="text-foreground">{videoCount}</strong> clip
            </span>
          )}
        </div>

        {isEditing && (
          <ProfileEditForm
            user={profileUser}
            onClose={() => setIsEditing(false)}
          />
        )}
      </div>
    </div>
  );
}
