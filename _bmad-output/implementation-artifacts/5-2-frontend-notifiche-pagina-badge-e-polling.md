# Story 5.2: Frontend Notifiche — Pagina, Badge e Polling

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utente registrato,
I want vedere un badge con le notifiche non lette e consultare la lista completa,
So that sono sempre aggiornato su cosa succede con le mie clip e i miei commenti.

## Acceptance Criteria

1. **Given** un utente autenticato
   **When** è su qualsiasi pagina dell'app
   **Then** vede un'icona campanella nella navbar (desktop) e nel header (mobile) con badge numerico delle non lette (FR52)
   **And** il conteggio è aggiornato via polling ogni 15 secondi (`refetchInterval: 15000`) (D1)

2. **Given** un utente che clicca sulla campanella
   **When** naviga a `/notifiche`
   **Then** vede la lista completa delle notifiche con: icona per tipo, testo descrittivo, timestamp relativo (FR51)
   **And** le notifiche non lette sono visivamente distinte (sfondo diverso)
   **And** la pagina ha `isError` + `<ErrorMessage onRetry={refetch} />`

3. **Given** un utente sulla pagina notifiche
   **When** clicca una notifica
   **Then** viene marcata come letta e naviga al contenuto collegato (clip, commento, contest)

4. **Given** un utente sulla pagina notifiche
   **When** clicca "Segna tutte come lette"
   **Then** tutte le notifiche vengono marcate come lette e il badge si azzera

5. **Given** i nuovi moduli frontend
   **When** vengono creati
   **Then** `src/lib/api/notifications.ts` con metodi getAll, getUnreadCount, markRead, markAllRead
   **And** `src/lib/hooks/use-notifications.ts` con `useNotifications` (polling 15s), `useUnreadCount`, `useMarkRead`, `useMarkAllRead`
   **And** `src/types/notification.ts` con tipo `Notification`
   **And** query keys in `query-keys.ts`: `notifications.all`, `notifications.list`, `notifications.unreadCount`

## Tasks / Subtasks

- [x] Task 1: Tipo TypeScript e API client (AC: #5)
  - [x] 1.1 Creare `frontend/src/types/notification.ts` con interfaccia `Notification`
  - [x] 1.2 Aggiungere barrel export in `frontend/src/types/index.ts`
  - [x] 1.3 Creare `frontend/src/lib/api/notifications.ts` con metodi: `getAll(page)`, `getUnreadCount()`, `markRead(id)`, `markAllRead()`
  - [x] 1.4 Aggiungere query keys `notifications` in `frontend/src/lib/query-keys.ts`

- [x] Task 2: Hook React Query (AC: #5)
  - [x] 2.1 Creare `frontend/src/lib/hooks/use-notifications.ts`
  - [x] 2.2 `useNotifications()` — `useInfiniteQuery` con paginazione, `staleTime: 30_000`
  - [x] 2.3 `useUnreadCount()` — `useQuery` con `refetchInterval: 15_000` per polling
  - [x] 2.4 `useMarkRead()` — `useMutation` con invalidazione cache notifiche + unread-count
  - [x] 2.5 `useMarkAllRead()` — `useMutation` con invalidazione cache notifiche + unread-count

- [x] Task 3: Componente NotificationBell — campanella con badge (AC: #1)
  - [x] 3.1 Creare `frontend/src/components/layout/notification-bell.tsx`
  - [x] 3.2 Icona `Bell` da `lucide-react`, badge numerico sovrapposto (cerchio rosso con conteggio)
  - [x] 3.3 Click → `router.push("/notifiche")`
  - [x] 3.4 Badge nascosto se count === 0, mostra `formatCount(count)` se > 0
  - [x] 3.5 Integrare in `desktop-navbar.tsx` — tra search e `DesktopUserMenu`
  - [x] 3.6 Integrare in `header.tsx` — tra search e avatar dropdown

- [x] Task 4: Pagina `/notifiche` (AC: #2, #3, #4)
  - [x] 4.1 Creare `frontend/src/app/(main)/notifiche/page.tsx`
  - [x] 4.2 Lista notifiche con `useNotifications()`, infinite scroll con `useInfiniteQuery`
  - [x] 4.3 Ogni notifica mostra: icona tipo, testo descrittivo, timestamp relativo (`formatRelativeDate`)
  - [x] 4.4 Notifiche non lette con sfondo distinto (es. `bg-accent/50` vs trasparente)
  - [x] 4.5 Click su notifica → `useMarkRead` + navigazione al contenuto collegato
  - [x] 4.6 Pulsante "Segna tutte come lette" → `useMarkAllRead`
  - [x] 4.7 `isError` + `<ErrorMessage onRetry={refetch} />` obbligatorio
  - [x] 4.8 Stato vuoto: messaggio "Nessuna notifica" se lista vuota

- [x] Task 5: Verifica qualità (AC: tutti)
  - [x] 5.1 `npm run build` — 0 errori di compilazione
  - [x] 5.2 Verifica visiva desktop: campanella visibile nella navbar, badge funzionante
  - [x] 5.3 Verifica visiva mobile: campanella visibile nel header, badge funzionante
  - [x] 5.4 Verifica polling: conteggio si aggiorna automaticamente ogni ~15s
  - [x] 5.5 Verifica navigazione: click su notifica porta al contenuto corretto

## Dev Notes

### Stato attuale — Cosa esiste già

**Backend completo (Story 5.1):**
- Modello `Notification` con 7 tipi, FK esplicite, 2 indici composti
- `GET /api/notifications/` — lista paginata, ordinata `-created_at`, `select_related("sender","video")`
- `GET /api/notifications/unread-count/` — ritorna `{"count": N}`
- `POST /api/notifications/{id}/mark-read/` — ritorna `{"detail": "Notifica marcata come letta."}`
- `POST /api/notifications/mark-all-read/` — ritorna `{"detail": "N notifiche marcate come lette."}`
- Auto-creazione: `comment_received`, `like_received` (video+commento), `contest_opened`
- **240 test backend** (1 fail pre-esistente)

**Frontend — Nessun file notifiche esiste**. Tutto da creare da zero.

### Tipo Notification — Specifiche esatte

```typescript
// frontend/src/types/notification.ts
export interface Notification {
  id: number;
  recipient: number;
  sender: number | null;
  sender_username: string | null;
  type: NotificationType;
  type_display: string;
  is_read: boolean;
  created_at: string; // ISO 8601
  video: number | null;
  video_title: string | null;
  comment: number | null;
  contest: number | null;
}

export type NotificationType =
  | "comment_received"
  | "like_received"
  | "comment_promoted"
  | "contest_opened"
  | "bracket_invite"
  | "bracket_turn"
  | "contest_results";
```

Questo tipo corrisponde ESATTAMENTE ai campi del `NotificationSerializer` backend in `backend/cs_clips/api/notifications/notification_serializers.py`.

### API Client — Pattern da seguire

```typescript
// frontend/src/lib/api/notifications.ts
import { apiClient } from "./client";
import type { PaginatedResponse, Notification } from "@/types";

export const notificationsApi = {
  getAll: (page = 1) =>
    apiClient
      .get<PaginatedResponse<Notification>>("/notifications/", { params: { page } })
      .then((r) => r.data),

  getUnreadCount: () =>
    apiClient
      .get<{ count: number }>("/notifications/unread-count/")
      .then((r) => r.data),

  markRead: (id: number) =>
    apiClient
      .post<{ detail: string }>(`/notifications/${id}/mark-read/`)
      .then((r) => r.data),

  markAllRead: () =>
    apiClient
      .post<{ detail: string }>("/notifications/mark-all-read/")
      .then((r) => r.data),
};
```

Pattern identico a `commentsApi` e `contestsApi` — oggetto con metodi, `.then((r) => r.data)`, tipi generici su `apiClient.get/post`.

### Query Keys — Esatto formato

```typescript
// Aggiungere a frontend/src/lib/query-keys.ts
notifications: {
  all: ["notifications"] as const,
  list: (page?: number) => ["notifications", "list", page] as const,
  unreadCount: ["notifications", "unread-count"] as const,
},
```

Pattern identico a `contests` — usare `as const` per type safety.

### Hook — Specifiche complete

```typescript
// frontend/src/lib/hooks/use-notifications.ts
"use client";

import { useQuery, useInfiniteQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { notificationsApi } from "@/lib/api/notifications";
import { queryKeys } from "@/lib/query-keys";
import { extractPageFromUrl } from "@/lib/utils";

// Lista notifiche paginata — per la pagina /notifiche
export function useNotifications() {
  return useInfiniteQuery({
    queryKey: queryKeys.notifications.all,
    queryFn: ({ pageParam = 1 }) => notificationsApi.getAll(pageParam),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => extractPageFromUrl(lastPage.next),
    staleTime: 30_000,
  });
}

// Conteggio non lette — polling 15s per badge campanella
export function useUnreadCount() {
  return useQuery({
    queryKey: queryKeys.notifications.unreadCount,
    queryFn: () => notificationsApi.getUnreadCount(),
    refetchInterval: 15_000,
    staleTime: 10_000,
  });
}

// Marca singola come letta
export function useMarkRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => notificationsApi.markRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.notifications.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.notifications.unreadCount });
    },
  });
}

// Marca tutte come lette
export function useMarkAllRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => notificationsApi.markAllRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.notifications.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.notifications.unreadCount });
    },
  });
}
```

**NOTA CRITICA**: `useUnreadCount` usa `refetchInterval: 15_000` (D1) — questo è il cuore del sistema di polling. Il `staleTime: 10_000` evita refetch duplicati in caso di mount/unmount rapido.

### Componente NotificationBell — Posizionamento preciso

**Desktop (`desktop-navbar.tsx`):**
Il componente va inserito tra la search bar e `DesktopUserMenu`. La struttura attuale è:
```tsx
<header className="hidden lg:flex h-14 items-center border-b ...">
  <div className="flex-1" />
  <div className="w-full max-w-md"><UserSearchBar /></div>
  <div className="flex flex-1 justify-end">
    {/* INSERIRE NotificationBell QUI, prima di DesktopUserMenu */}
    <NotificationBell />
    <DesktopUserMenu />
  </div>
</header>
```

**Mobile (`header.tsx`):**
Il componente va inserito tra la search bar e l'avatar dropdown:
```tsx
<header className="... lg:hidden">
  <Link href="/home">...</Link>
  <div className="flex-1 max-w-xs mx-2"><UserSearchBar /></div>
  {/* INSERIRE NotificationBell QUI, prima del DropdownMenu avatar */}
  <NotificationBell />
  {user ? (<DropdownMenu>...</DropdownMenu>) : <div className="w-9" />}
</header>
```

### Componente NotificationBell — Specifiche

```tsx
// frontend/src/components/layout/notification-bell.tsx
"use client";

import { Bell } from "lucide-react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { useUnreadCount } from "@/lib/hooks/use-notifications";
import { formatCount } from "@/lib/utils";

export function NotificationBell() {
  const router = useRouter();
  const { data } = useUnreadCount();
  const count = data?.count ?? 0;

  return (
    <Button
      variant="ghost"
      size="icon"
      className="relative h-9 w-9"
      onClick={() => router.push("/notifiche")}
    >
      <Bell className="h-5 w-5" />
      {count > 0 && (
        <span className="absolute -top-1 -right-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-destructive px-1 text-[10px] font-bold text-destructive-foreground">
          {formatCount(count)}
        </span>
      )}
    </Button>
  );
}
```

**Icona**: `Bell` da `lucide-react` (coerente con il resto del progetto che usa Lucide).
**Badge**: cerchio `bg-destructive` (rosso nel tema) sovrapposto con `absolute positioning`.
**Click**: navigazione a `/notifiche` via `router.push`.

### Pagina Notifiche — Specifiche UI

**Route**: `frontend/src/app/(main)/notifiche/page.tsx` — sotto `(main)` layout (richiede autenticazione).

**Icone per tipo notifica:**
| Tipo | Icona Lucide | Testo esempio |
|------|-------------|--------------|
| `comment_received` | `MessageCircle` | "**{sender}** ha commentato la tua clip «{video_title}»" |
| `like_received` | `Heart` | "**{sender}** ha messo like alla tua clip «{video_title}»" |
| `comment_promoted` | `Star` | "Il tuo commento è stato promosso a popup" |
| `contest_opened` | `Trophy` | "Nuovo contest aperto!" |
| `bracket_invite` | `Swords` | "Sei stato invitato a un bracket" |
| `bracket_turn` | `Timer` | "È il tuo turno nel bracket" |
| `contest_results` | `Award` | "Risultati contest disponibili" |

**Navigazione da notifica:**
| Tipo | Destinazione |
|------|-------------|
| `comment_received` | `/clip/{video_id}` |
| `like_received` | `/clip/{video_id}` se `video` non null, altrimenti nessuna navigazione |
| `comment_promoted` | `/clip/{video_id}` |
| `contest_opened` | `/contest/{contest_id}` |
| `bracket_invite` | nessuna navigazione (bracket non implementato) |
| `bracket_turn` | nessuna navigazione (bracket non implementato) |
| `contest_results` | `/contest/{contest_id}` |

**NOTA**: per `like_received` su commento (`video` è null, `comment` non null), il video_id non è direttamente disponibile nel serializer. In questo caso, la notifica NON deve navigare (o navigare alla pagina /notifiche stessa). **NON** fare chiamate API extra per risolvere il video del commento.

### Layout pagina notifiche

```tsx
// Pattern struttura pagina
<div className="mx-auto max-w-2xl px-4 py-6">
  <div className="flex items-center justify-between mb-6">
    <h1 className="text-2xl font-bold">Notifiche</h1>
    <Button variant="ghost" onClick={markAllRead} disabled={unreadCount === 0}>
      Segna tutte come lette
    </Button>
  </div>

  {isError && <ErrorMessage onRetry={refetch} />}

  {/* Lista notifiche */}
  {notifications.map((n) => (
    <NotificationItem key={n.id} notification={n} onClick={handleClick} />
  ))}

  {/* Infinite scroll trigger */}
  {hasNextPage && <div ref={loadMoreRef}>...</div>}

  {/* Empty state */}
  {notifications.length === 0 && !isLoading && (
    <p className="text-center text-muted-foreground py-12">Nessuna notifica</p>
  )}
</div>
```

### Anti-pattern da evitare

1. **NON usare WebSocket o SSE** — polling REST a 15s come da D1
2. **NON creare componente separato per la pagina in `/notifiche/notifiche-content.tsx`** — la pagina è sufficientemente semplice per un singolo file `page.tsx` con `"use client"`
3. **NON fare optimistic update complesso** sulle mutazioni mark-read — `invalidateQueries` è sufficiente. Il polling a 15s garantisce consistenza
4. **NON aggiungere `refetchInterval` su `useNotifications()`** — solo `useUnreadCount` ha il polling. La lista si aggiorna solo quando l'utente visita la pagina
5. **NON creare un file `notification-urls.ts`** — le route sono gestite da Next.js App Router
6. **NON usare `"motion/react"`** — se serve animazione, importare da `"framer-motion"` (vedi MEMORY.md)
7. **NON creare `notification_bell.tsx`** (underscore) — usare `notification-bell.tsx` (kebab-case, pattern stabilito)
8. **NON dimenticare `isError + ErrorMessage`** sulla pagina notifiche — è obbligatorio (pattern Epic 1+)
9. **NON fare polling se l'utente non è autenticato** — `useUnreadCount` deve avere `enabled: !!user` dove `user` viene da `useAuth()`

### Edge case e rischi

1. **Utente non autenticato**: `useUnreadCount` non deve fare polling. Aggiungere `enabled` basato su `useAuth().user`. Il componente `NotificationBell` è dentro `(main)` layout che richiede auth, ma il hook potrebbe essere montato prima del redirect
2. **Conteggio > 99**: `formatCount` gestisce già abbreviazioni (99 → "99", 150 → "150", 1200 → "1.2K")
3. **Click rapido su "Segna tutte come lette"**: la mutation `useMarkAllRead` deve avere `disabled` quando `isPending` per evitare chiamate duplicate
4. **Notifica senza video/sender**: alcuni campi sono nullable. Il testo descrittivo deve gestire `sender_username === null` (es. notifiche di sistema come `contest_opened` non hanno sender)
5. **Infinite scroll**: usare `IntersectionObserver` con un div sentinella in fondo alla lista (pattern già usato nel feed)
6. **Pagina /notifiche non in sidebar/bottom-bar**: la campanella nella navbar/header è l'unico punto di accesso. NON aggiungere voce di navigazione nella sidebar o bottom bar

### Performance Considerations

- **Polling 15s su `unread-count`**: ~240 req/hour per utente — ben sotto il rate limit di 2000/hour (D6)
- **`staleTime: 10_000` su unread-count**: evita refetch on mount se il dato è fresco (< 10s)
- **`staleTime: 30_000` su lista notifiche**: evita refetch superfluo quando l'utente naviga avanti/indietro
- **`select_related("sender","video")` lato backend**: già implementato in Story 5.1, nessun N+1

### Decisione architetturale D1 — Conferma polling

Dalla architettura: "Endpoint `GET /api/notifications/` con polling periodico dal frontend. Intervallo: 15 secondi. Zero infrastruttura aggiuntiva — nessun Redis, nessun Channels, nessun WebSocket."

Il polling è implementato SOLO su `useUnreadCount` (endpoint leggero: `COUNT` query). La lista completa NON è in polling — si aggiorna solo su navigazione.

### Project Structure Notes

**File da creare:**
- `frontend/src/types/notification.ts` — tipo Notification + NotificationType
- `frontend/src/lib/api/notifications.ts` — API client notificationsApi
- `frontend/src/lib/hooks/use-notifications.ts` — 4 hook React Query
- `frontend/src/components/layout/notification-bell.tsx` — campanella con badge
- `frontend/src/app/(main)/notifiche/page.tsx` — pagina lista notifiche

**File da modificare:**
- `frontend/src/types/index.ts` — aggiungere barrel export per Notification
- `frontend/src/lib/query-keys.ts` — aggiungere chiavi `notifications`
- `frontend/src/components/layout/desktop-navbar.tsx` — inserire NotificationBell
- `frontend/src/components/layout/header.tsx` — inserire NotificationBell

**File da NON toccare:**
- Backend — completamente implementato in Story 5.1
- `frontend/src/lib/utils.ts` — `formatRelativeDate` e `formatCount` già esistenti e sufficienti
- `frontend/src/components/layout/left-sidebar.tsx` — nessuna voce notifiche nella sidebar
- `frontend/src/components/layout/mobile-bottom-bar.tsx` — nessuna voce notifiche nel bottom bar

### Intelligence dalla Story 5.1 (precedente)

- **240 test backend** baseline, 1 fail pre-esistente (`test_registration_assigns_toconfirm_group`)
- **API confermata funzionante**: tutti gli endpoint testati e passanti
- **`select_related("sender","video")`** già applicato nel queryset — nessun N+1 lato API
- **FK nullable su video/comment/contest**: usano `SET_NULL` (fix dalla code review 5.1) — la notifica sopravvive anche se il contenuto collegato viene cancellato
- **Debug insight**: Custom User model ha `related_name="custom_user_set"` sui groups — se serve filtrare per gruppo, usare `User.objects.filter(groups=group)` NON `group.user_set`
- **Formato risposta confermato**: `{"count": N}` per unread-count, `{"detail": "..."}` per mark-read/mark-all-read, paginato standard per lista

### Git Intelligence — Pattern recenti

Ultimi commit:
- `612f66c` — Epic 3 completo: like UI, popup overlay, spareggio like, comment markers

Pattern commit: prefisso `feat:` per feature, riepilogo conciso.
Suggerito: `feat: Story 5.2 — frontend notifiche, campanella badge, polling 15s`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-5.2] — AC BDD: campanella, badge, /notifiche, polling 15s
- [Source: _bmad-output/planning-artifacts/epics.md#Epic-5] — FRs: FR50, FR51, FR52, D1
- [Source: _bmad-output/planning-artifacts/architecture.md#D1-Notifiche-Delivery] — Polling REST 15s, NO WebSocket
- [Source: _bmad-output/planning-artifacts/architecture.md#D6-Rate-Limiting] — 2000/hour user, polling compatibile
- [Source: _bmad-output/planning-artifacts/architecture.md#Frontend-Checklist] — Procedura creazione nuovo dominio frontend
- [Source: backend/cs_clips/api/notifications/notification_serializers.py] — Campi esatti del serializer
- [Source: backend/cs_clips/api/notifications/notification_views.py] — Endpoint e formati risposta
- [Source: frontend/src/lib/api/comments.ts] — Pattern API client (oggetto con metodi, .then(r => r.data))
- [Source: frontend/src/lib/hooks/use-contests.ts] — Pattern hook (useInfiniteQuery, extractPageFromUrl)
- [Source: frontend/src/lib/query-keys.ts] — Pattern query keys (as const, nested object)
- [Source: frontend/src/lib/utils.ts] — formatRelativeDate, formatCount, extractPageFromUrl già disponibili
- [Source: frontend/src/components/layout/desktop-navbar.tsx] — Punto di inserimento campanella desktop
- [Source: frontend/src/components/layout/header.tsx] — Punto di inserimento campanella mobile
- [Source: _bmad-output/implementation-artifacts/5-1-modello-notification-e-api-backend.md] — Story precedente: pattern, learnings, debug log

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- `npm run build` — 0 errori, route `/notifiche` generata come static page

### Completion Notes List

- **Task 1**: Tipo `Notification` + `NotificationType` in `types/notification.ts`, barrel export aggiunto, API client `notificationsApi` con 4 metodi (getAll, getUnreadCount, markRead, markAllRead), query keys `notifications.all`, `notifications.list`, `notifications.unreadCount`
- **Task 2**: 4 hook React Query — `useNotifications` (useInfiniteQuery, staleTime 30s), `useUnreadCount` (polling 15s, enabled: !!user), `useMarkRead`, `useMarkAllRead` (entrambi con invalidazione cache)
- **Task 3**: `NotificationBell` con icona Bell, badge `bg-destructive` con `formatCount`, click → `/notifiche`. Integrato in `desktop-navbar.tsx` (tra search e DesktopUserMenu) e `header.tsx` (tra search e avatar dropdown)
- **Task 4**: Pagina `/notifiche` con infinite scroll (IntersectionObserver), icone per tipo (7 tipi), testo descrittivo, timestamp relativo, sfondo `bg-accent/50` per non lette, click → markRead + navigazione, "Segna tutte come lette" con disabled su isPending, ErrorMessage + empty state
- **Task 5**: Build 0 errori. Verifica visiva Playwright: campanella desktop OK (navbar, tra search e avatar), campanella mobile OK (header 390x844), pagina /notifiche OK (titolo, "Segna tutte come lette" disabled, empty state "Nessuna notifica"), navigazione click campanella → /notifiche OK
- **Edge case gestiti**: sender_username nullable ("Qualcuno" come fallback), video nullable (no navigazione), `enabled: !!user` su polling, `isPending` su markAllRead

### Change Log

- 2026-03-08: Implementazione completa Story 5.2 — frontend notifiche, campanella badge, polling 15s
- 2026-03-08: Code Review — 3 MEDIUM fix: rimossa invalidazione query ridondante (useMarkRead/useMarkAllRead), aggiunto aria-label su NotificationBell, aggiunto indicatore errore polling (pallino giallo)

### File List

**Nuovi:**
- `frontend/src/types/notification.ts`
- `frontend/src/lib/api/notifications.ts`
- `frontend/src/lib/hooks/use-notifications.ts`
- `frontend/src/components/layout/notification-bell.tsx`
- `frontend/src/app/(main)/notifiche/page.tsx`

**Modificati:**
- `frontend/src/types/index.ts` — barrel export Notification + NotificationType
- `frontend/src/lib/query-keys.ts` — chiavi notifications
- `frontend/src/components/layout/desktop-navbar.tsx` — NotificationBell integrato
- `frontend/src/components/layout/header.tsx` — NotificationBell integrato
