"use client";

import { Button } from "@/components/ui/button";
import { useFollow, useUnfollow } from "@/lib/hooks/use-users";
import { useAuth } from "@/providers/auth-provider";
import { cn } from "@/lib/utils";

interface FollowButtonProps {
  userId: number;
  isFollowing: boolean;
  size?: "sm" | "default";
  className?: string;
}

export function FollowButton({
  userId,
  isFollowing,
  size = "sm",
  className,
}: FollowButtonProps) {
  const { user } = useAuth();
  const followMutation = useFollow();
  const unfollowMutation = useUnfollow();
  const isPending = followMutation.isPending || unfollowMutation.isPending;

  // Don't show follow button for yourself
  if (user?.id === userId) return null;

  function handleClick() {
    if (isFollowing) {
      unfollowMutation.mutate(userId);
    } else {
      followMutation.mutate(userId);
    }
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
      {isFollowing ? "Segui già" : "Segui"}
    </Button>
  );
}
