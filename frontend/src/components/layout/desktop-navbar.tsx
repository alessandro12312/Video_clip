"use client";

import { UserSearchBar } from "@/components/user/user-search-bar";
import { DesktopUserMenu } from "@/components/layout/desktop-user-menu";

export function DesktopNavbar() {
  return (
    <header className="hidden lg:flex h-14 items-center border-b border-border bg-background/80 backdrop-blur-sm px-4 gap-4">
      <div className="flex-1" />

      <div className="w-full max-w-md">
        <UserSearchBar />
      </div>

      <div className="flex flex-1 justify-end">
        <DesktopUserMenu />
      </div>
    </header>
  );
}
