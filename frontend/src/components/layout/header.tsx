"use client";

import Link from "next/link";
import { LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/providers/auth-provider";
import { UserAvatar } from "@/components/user/user-avatar";
import { UserSearchBar } from "@/components/user/user-search-bar";
import { NotificationBell } from "@/components/layout/notification-bell";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-40 flex h-[var(--header-height)] items-center justify-between border-b border-border bg-background/80 px-4 backdrop-blur-sm lg:hidden">
      {/* Brand logo — target mobile della transizione post-login. Vedi login-transition-overlay.tsx */}
      <Link href="/home" className="shrink-0">
        <span id="mobile-brand-logo" className="text-lg font-bold gradient-text">V</span>
      </Link>

      {/* Ricerca utenti */}
      <div className="flex-1 max-w-xs mx-2">
        <UserSearchBar />
      </div>

      {/* Campanella notifiche */}
      <NotificationBell />

      {/* User avatar + dropdown */}
      {user ? (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-9 w-9 rounded-full">
              <UserAvatar username={user.username} size="sm" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem asChild>
              <Link href="/profilo">Profilo</Link>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={logout}>
              <LogOut className="mr-2 h-4 w-4" />
              Esci
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ) : (
        <div className="w-9" />
      )}
    </header>
  );
}
