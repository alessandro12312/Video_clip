"use client";

import Link from "next/link";
import { ChevronDown, LogOut, User, Settings } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/providers/auth-provider";
import { UserAvatar } from "@/components/user/user-avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export function DesktopUserMenu() {
  const { user, logout } = useAuth();

  if (!user) return null;

  const handleLogout = () => {
    toast("Hai effettuato il logout");
    logout();
  };

  return (
    <div className="hidden lg:flex items-center gap-1">
      <Link
        href="/profilo"
        className="opacity-100 hover:opacity-80 transition-opacity"
        aria-label="Vai al mio profilo"
      >
        <UserAvatar username={user.username} size="sm" />
      </Link>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7 text-muted-foreground"
            aria-label="Menu profilo"
          >
            <ChevronDown className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem asChild>
            <Link href="/profilo">
              <User className="mr-2 h-4 w-4" />
              Il mio profilo
            </Link>
          </DropdownMenuItem>
          <DropdownMenuItem asChild>
            <Link href="/impostazioni">
              <Settings className="mr-2 h-4 w-4" />
              Impostazioni account
            </Link>
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={handleLogout}>
            <LogOut className="mr-2 h-4 w-4" />
            Esci
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
