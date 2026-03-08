"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { LeftSidebar } from "@/components/layout/left-sidebar";
import { MobileBottomBar } from "@/components/layout/mobile-bottom-bar";
import { Header } from "@/components/layout/header";
import { PageLoader } from "@/components/shared/page-loader";
import { DesktopNavbar } from "@/components/layout/desktop-navbar";

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, isAuthenticating } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticating && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isAuthenticating, router]);

  if (isAuthenticating) return <PageLoader />;
  if (!isAuthenticated) return null;

  return (
    <div className="flex h-screen overflow-hidden">
      <LeftSidebar />

      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <DesktopNavbar />

        <main className="flex-1 overflow-y-auto px-2 py-4 sm:px-4 pb-[var(--bottom-bar-height)] lg:pb-4 scrollbar-thin">
          {children}
        </main>
      </div>

      <MobileBottomBar />
    </div>
  );
}
