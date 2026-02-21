"use client";

import { useAuth } from "@/providers/auth-provider";
import { LeftSidebar } from "@/components/layout/left-sidebar";
import { MobileBottomBar } from "@/components/layout/mobile-bottom-bar";
import { Header } from "@/components/layout/header";

export default function ClipLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, isAuthenticating } = useAuth();

  // Public view: no shell, just content
  if (isAuthenticating || !isAuthenticated) {
    return <>{children}</>;
  }

  // Authenticated view: wrap with main shell
  return (
    <div className="flex h-screen overflow-hidden">
      <LeftSidebar />

      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />

        <main className="flex-1 overflow-y-auto p-4 pb-[var(--bottom-bar-height)] lg:pb-4 scrollbar-thin">
          {children}
        </main>
      </div>

      <MobileBottomBar />
    </div>
  );
}
