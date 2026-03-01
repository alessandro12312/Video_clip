"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Compass, Plus, User } from "lucide-react";
import { cn } from "@/lib/utils";

const ITEMS = [
  { href: "/home", label: "Home", icon: Home },
  { href: "/esplora", label: "Esplora", icon: Compass },
  { href: "/carica", label: "Carica", icon: Plus, accent: true },
  { href: "/profilo", label: "Profilo", icon: User },
];

export function MobileBottomBar() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 flex h-[var(--bottom-bar-height)] items-center justify-around border-t border-border bg-background lg:hidden">
      {ITEMS.map((item) => {
        const isActive =
          pathname === item.href || pathname.startsWith(item.href + "/");

        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex flex-col items-center gap-0.5 py-1.5 text-xs transition-colors",
              item.accent
                ? "text-primary"
                : isActive
                  ? "text-foreground"
                  : "text-muted-foreground"
            )}
          >
            {item.accent ? (
              <div className="flex h-9 w-9 items-center justify-center rounded-full gradient-bg">
                <item.icon className="h-5 w-5 text-white" />
              </div>
            ) : (
              <item.icon className="h-5 w-5" />
            )}
            {!item.accent && <span>{item.label}</span>}
          </Link>
        );
      })}
    </nav>
  );
}
