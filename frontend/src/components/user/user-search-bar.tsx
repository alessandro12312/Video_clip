"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { UserAvatar } from "@/components/user/user-avatar";
import { useSearchUsers } from "@/lib/hooks/use-users";
import { cn } from "@/lib/utils";

interface UserSearchBarProps {
  collapsed?: boolean;
  className?: string;
  onSelect?: () => void;
}

export function UserSearchBar({ collapsed, className, onSelect }: UserSearchBarProps) {
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  // Debounce 300ms
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  // Chiudi dropdown al click esterno
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const { data, isLoading } = useSearchUsers(debouncedQuery);
  const results = data?.results ?? [];
  const showDropdown = isOpen && debouncedQuery.length >= 2;

  function handleSelect(username: string) {
    setQuery("");
    setDebouncedQuery("");
    setIsOpen(false);
    onSelect?.();
    router.push(`/profilo/${username}`);
  }

  // In modalità collapsed mostra solo l'icona
  if (collapsed) {
    return (
      <button
        className={cn("flex items-center justify-center rounded-lg p-2.5 text-sidebar-foreground/70 hover:bg-sidebar-accent", className)}
        onClick={() => inputRef.current?.focus()}
        title="Cerca utenti"
      >
        <Search className="h-5 w-5" />
      </button>
    );
  }

  return (
    <div ref={containerRef} className={cn("relative", className)}>
      <div className="relative">
        <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          ref={inputRef}
          type="text"
          placeholder="Cerca utenti..."
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => {
            if (debouncedQuery.length >= 2) setIsOpen(true);
          }}
          className="pl-8 pr-8 h-9"
        />
        {query && (
          <button
            className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            onClick={() => {
              setQuery("");
              setDebouncedQuery("");
              setIsOpen(false);
            }}
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {showDropdown && (
        <div className="absolute top-full left-0 right-0 z-50 mt-1 max-h-64 overflow-y-auto rounded-md border border-border bg-popover shadow-md">
          {isLoading ? (
            <div className="flex flex-col gap-2 p-2">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center gap-2 px-2 py-1.5">
                  <Skeleton className="h-7 w-7 rounded-full" />
                  <Skeleton className="h-4 w-24" />
                </div>
              ))}
            </div>
          ) : results.length === 0 ? (
            <div className="px-3 py-4 text-center text-sm text-muted-foreground">
              Nessun utente trovato
            </div>
          ) : (
            <div className="flex flex-col py-1">
              {results.map((user) => (
                <button
                  key={user.id}
                  className="flex items-center gap-2 px-3 py-2 text-left text-sm hover:bg-accent transition-colors"
                  onClick={() => handleSelect(user.username)}
                >
                  <UserAvatar username={user.username} size="sm" />
                  <span className="truncate">{user.username}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
