import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";

interface UserAvatarProps {
  username: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

const SIZES = {
  sm: "h-7 w-7 text-xs",
  md: "h-9 w-9 text-sm",
  lg: "h-14 w-14 text-lg",
};

export function UserAvatar({ username, size = "md", className }: UserAvatarProps) {
  const initial = username.charAt(0).toUpperCase();

  return (
    <Avatar className={cn(SIZES[size], className)}>
      <AvatarFallback className="gradient-bg text-white font-semibold">
        {initial}
      </AvatarFallback>
    </Avatar>
  );
}
