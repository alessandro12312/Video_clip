"use client";

import { Bell } from "lucide-react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { useUnreadCount } from "@/lib/hooks/use-notifications";
import { formatCount } from "@/lib/utils";

export function NotificationBell() {
  const router = useRouter();
  const { data, isError } = useUnreadCount();
  const count = data?.count ?? 0;

  return (
    <Button
      variant="ghost"
      size="icon"
      className="relative h-9 w-9"
      aria-label="Notifiche"
      onClick={() => router.push("/notifiche")}
    >
      <Bell className="h-5 w-5" />
      {count > 0 && (
        <span className="absolute -top-1 -right-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-destructive px-1 text-[10px] font-bold text-destructive-foreground">
          {formatCount(count)}
        </span>
      )}
      {isError && (
        <span className="absolute -top-1 -right-1 h-2.5 w-2.5 rounded-full bg-yellow-500" />
      )}
    </Button>
  );
}
