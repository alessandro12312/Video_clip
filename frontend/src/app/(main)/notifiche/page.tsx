"use client";

import { useCallback, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  MessageCircle,
  Heart,
  Star,
  Trophy,
  Swords,
  Timer,
  Award,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ErrorMessage } from "@/components/shared/error-message";
import { useNotifications, useMarkRead, useMarkAllRead, useUnreadCount } from "@/lib/hooks/use-notifications";
import { formatRelativeDate } from "@/lib/utils";
import type { Notification, NotificationType } from "@/types";

const ICON_MAP: Record<NotificationType, React.ElementType> = {
  comment_received: MessageCircle,
  like_received: Heart,
  comment_promoted: Star,
  contest_opened: Trophy,
  bracket_invite: Swords,
  bracket_turn: Timer,
  contest_results: Award,
};

function getNotificationText(n: Notification): string {
  const sender = n.sender_username ? `${n.sender_username}` : "Qualcuno";
  const title = n.video_title ? ` «${n.video_title}»` : "";

  switch (n.type) {
    case "comment_received":
      return `${sender} ha commentato la tua clip${title}`;
    case "like_received":
      return `${sender} ha messo like alla tua clip${title}`;
    case "comment_promoted":
      return "Il tuo commento è stato promosso a popup";
    case "contest_opened":
      return "Nuovo contest aperto!";
    case "bracket_invite":
      return "Sei stato invitato a un bracket";
    case "bracket_turn":
      return "È il tuo turno nel bracket";
    case "contest_results":
      return "Risultati contest disponibili";
  }
}

function getNotificationHref(n: Notification): string | null {
  switch (n.type) {
    case "comment_received":
    case "comment_promoted":
      return n.video ? `/clip/${n.video}` : null;
    case "like_received":
      return n.video ? `/clip/${n.video}` : null;
    case "contest_opened":
    case "contest_results":
      return n.contest ? `/contest/${n.contest}` : null;
    case "bracket_invite":
    case "bracket_turn":
      return null;
  }
}

export default function NotifichePage() {
  const router = useRouter();
  const { data, isLoading, isError, refetch, fetchNextPage, hasNextPage, isFetchingNextPage } = useNotifications();
  const { data: unreadData } = useUnreadCount();
  const markRead = useMarkRead();
  const markAllRead = useMarkAllRead();
  const sentinelRef = useRef<HTMLDivElement>(null);

  const notifications = data?.pages.flatMap((p) => p.results) ?? [];
  const unreadCount = unreadData?.count ?? 0;

  // Infinite scroll via IntersectionObserver
  const handleObserver = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [entry] = entries;
      if (entry.isIntersecting && hasNextPage && !isFetchingNextPage) {
        fetchNextPage();
      }
    },
    [fetchNextPage, hasNextPage, isFetchingNextPage],
  );

  useEffect(() => {
    const el = sentinelRef.current;
    if (!el) return;
    const observer = new IntersectionObserver(handleObserver, { rootMargin: "200px" });
    observer.observe(el);
    return () => observer.disconnect();
  }, [handleObserver]);

  function handleClick(n: Notification) {
    if (!n.is_read) {
      markRead.mutate(n.id);
    }
    const href = getNotificationHref(n);
    if (href) {
      router.push(href);
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Notifiche</h1>
        <Button
          variant="ghost"
          onClick={() => markAllRead.mutate()}
          disabled={unreadCount === 0 || markAllRead.isPending}
        >
          Segna tutte come lette
        </Button>
      </div>

      {isError && <ErrorMessage onRetry={refetch} />}

      {notifications.map((n) => {
        const Icon = ICON_MAP[n.type];
        return (
          <button
            key={n.id}
            className={`flex w-full items-start gap-3 rounded-lg px-3 py-3 text-left transition-colors hover:bg-accent ${
              !n.is_read ? "bg-accent/50" : ""
            }`}
            onClick={() => handleClick(n)}
          >
            <div className="mt-0.5 shrink-0">
              <Icon className="h-5 w-5 text-muted-foreground" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm">{getNotificationText(n)}</p>
              <p className="text-xs text-muted-foreground mt-0.5">
                {formatRelativeDate(n.created_at)}
              </p>
            </div>
            {!n.is_read && (
              <div className="mt-2 h-2 w-2 shrink-0 rounded-full bg-primary" />
            )}
          </button>
        );
      })}

      {/* Infinite scroll sentinel */}
      {hasNextPage && (
        <div ref={sentinelRef} className="flex justify-center py-4">
          {isFetchingNextPage && (
            <p className="text-sm text-muted-foreground">Caricamento...</p>
          )}
        </div>
      )}

      {/* Empty state */}
      {notifications.length === 0 && !isLoading && !isError && (
        <p className="text-center text-muted-foreground py-12">Nessuna notifica</p>
      )}

      {/* Loading state */}
      {isLoading && (
        <p className="text-center text-muted-foreground py-12">Caricamento...</p>
      )}
    </div>
  );
}
