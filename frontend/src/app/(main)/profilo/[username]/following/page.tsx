"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useUserByUsername, useFollowing } from "@/lib/hooks/use-users";
import { UserListItem, UserListItemSkeleton } from "@/components/user/user-list-item";
import { EmptyState } from "@/components/shared/empty-state";
import { ErrorMessage } from "@/components/shared/error-message";
import { PageLoader } from "@/components/shared/page-loader";
import { Button } from "@/components/ui/button";
import { ArrowLeft, UserPlus } from "lucide-react";
import { PAGE_SIZE } from "@/lib/constants";

export default function FollowingPage() {
  const params = useParams<{ username: string }>();
  const username = params.username;
  const [page, setPage] = useState(1);

  const {
    data: profileUser,
    isLoading: profileLoading,
    isError: profileError,
  } = useUserByUsername(username);

  const {
    data,
    isLoading: listLoading,
    isError: listError,
    refetch,
  } = useFollowing(profileUser?.id ?? 0, page);

  if (profileLoading) return <PageLoader />;
  if (profileError || !profileUser) {
    return (
      <ErrorMessage
        message="Impossibile caricare il profilo utente."
        onRetry={() => window.location.reload()}
      />
    );
  }

  const totalPages = data ? Math.ceil(data.count / PAGE_SIZE) : 0;

  return (
    <div className="space-y-4 p-4">
      <div className="flex items-center gap-3">
        <Link
          href={`/profilo/${username}`}
          className="p-2 -m-2 rounded-md hover:bg-accent transition-colors"
          aria-label={`Torna al profilo di ${username}`}
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <h1 className="text-lg font-bold">Seguiti da {username}</h1>
      </div>

      <div className="space-y-1">
        {listLoading ? (
          <UserListItemSkeleton />
        ) : listError ? (
          <ErrorMessage
            message="Errore nel caricamento della lista seguiti."
            onRetry={() => refetch()}
          />
        ) : !data || data.results.length === 0 ? (
          <EmptyState
            icon={UserPlus}
            title="Non segue ancora nessuno"
            description={`${username} non segue ancora nessun utente.`}
          />
        ) : (
          data.results.map((user) => (
            <UserListItem key={user.id} user={user} />
          ))
        )}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-4 pt-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => p - 1)}
            disabled={page === 1}
          >
            Precedente
          </Button>
          <span className="text-sm text-muted-foreground">
            Pagina {page} di {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => p + 1)}
            disabled={!data?.next}
          >
            Successivo
          </Button>
        </div>
      )}
    </div>
  );
}
