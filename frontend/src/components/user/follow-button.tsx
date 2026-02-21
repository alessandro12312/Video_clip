"use client";

import { Button } from "@/components/ui/button";
import { useFollow, useUnfollow } from "@/lib/hooks/use-users";
import { useAuth } from "@/providers/auth-provider";
import { cn } from "@/lib/utils";

interface FollowButtonProps {
  userId: number;
  username: string;
  isFollowing: boolean;
  size?: "sm" | "default";
  className?: string;
}

export function FollowButton({
  userId,
  username,
  isFollowing,
  size = "sm",
  className,
}: FollowButtonProps) {
  const { user } = useAuth();
  const followMutation = useFollow();
  const unfollowMutation = useUnfollow();
  const isPending = followMutation.isPending || unfollowMutation.isPending;

  if (user?.id === userId) return null;

  function handleClick() {
    if (isFollowing) {
      unfollowMutation.mutate({ userId, username });
    } else {
      followMutation.mutate({ userId, username });
    }
  }

  function getButtonText() {
    if (followMutation.isPending) return "Seguendo...";
    if (unfollowMutation.isPending) return "Rimuovendo...";
    return isFollowing ? "Smetti di seguire" : "Segui";
  }

  return (
    <Button
      variant={isFollowing ? "outline" : "default"}
      size={size}
      className={cn(
        !isFollowing && "gradient-bg text-white",
        className
      )}
      onClick={handleClick}
      disabled={isPending}
    >
      {getButtonText()}
    </Button>
  );
}
