"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  Compass,
  Upload,
  User,
  Trophy,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

const ICONS = {
  Home,
  Compass,
  Upload,
  User,
  Trophy,
} as const;

const NAV_ITEMS = [
  { href: "/home", label: "Home", icon: "Home" as const },
  { href: "/esplora", label: "Esplora", icon: "Compass" as const },
  { href: "/carica", label: "Carica", icon: "Upload" as const },
  { href: "/profilo", label: "Profilo", icon: "User" as const },
  { href: "/contest", label: "Contest", icon: "Trophy" as const },
];

export function LeftSidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "hidden lg:flex flex-col border-r border-border bg-sidebar transition-all duration-200",
        collapsed ? "w-[var(--sidebar-collapsed-width)]" : "w-[var(--sidebar-width)]"
      )}
    >
      {/* Logo + Collapse toggle */}
      <div className={cn(
        "flex h-14 items-center justify-between",
        collapsed ? "px-2" : "px-4"
      )}>
        <Link href="/home" className="flex items-center gap-2">
          <span id="sidebar-brand-logo" className="text-xl font-bold">{collapsed ? <span className="gradient-text">V</span> : <><span className="gradient-text">V</span><span style={{ color: 'var(--gradient-end)' }}>ideo_cli</span><span className="gradient-text-reverse">p</span></>}</span>
        </Link>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 shrink-0 text-sidebar-foreground/50"
          onClick={() => setCollapsed(!collapsed)}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      <Separator />

      {/* Navigation */}
      <nav className="flex flex-1 flex-col gap-1 p-2">
        {NAV_ITEMS.map((item) => {
          const Icon = ICONS[item.icon];
          const isActive =
            pathname === item.href || pathname.startsWith(item.href + "/");

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-sidebar-accent text-sidebar-primary"
                  : "text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-foreground"
              )}
            >
              <Icon className="h-5 w-5 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
