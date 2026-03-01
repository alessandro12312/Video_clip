import Link from "next/link";
import { cn } from "@/lib/utils";

interface UsernameLinkProps {
  username: string;
  className?: string;
}

export function UsernameLink({ username, className }: UsernameLinkProps) {
  return (
    <Link
      href={`/profilo/${username}`}
      className={cn(
        "text-sm font-medium text-foreground hover:text-primary transition-colors",
        className
      )}
    >
      {username}
    </Link>
  );
}
