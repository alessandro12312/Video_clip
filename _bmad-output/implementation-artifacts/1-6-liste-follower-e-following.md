# Story 1.6: Liste Follower e Following

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utente registrato,
I want visualizzare le liste follower e following mie e di altri utenti,
so that possa vedere chi mi segue e chi seguo, e gestire le relazioni direttamente dalle liste.

## Acceptance Criteria

1. **AC1 — Visualizzazione lista follower/following dal proprio profilo**
   Given: un utente autenticato sulla propria pagina profilo
   When: clicca su "Follower" o "Following" (contatori nel ProfileHeader)
   Then: viene mostrata la lista degli utenti con username, avatar e bottone follow/unfollow
   And: la lista è paginata (PAGE_SIZE=10) con navigazione tra pagine

2. **AC2 — Visualizzazione lista follower/following di un altro utente**
   Given: un utente che visualizza il profilo di un altro utente
   When: clicca su "Follower" o "Following"
   Then: viene mostrata la lista follower/following di quell'utente
   And: ogni utente nella lista mostra il bottone follow/unfollow corretto (basato su `is_followed_by_me`)

3. **AC3 — Interazione follow/unfollow dalle liste**
   Given: un utente autenticato che visualizza una lista follower o following
   When: clicca il bottone "Segui" o "Smetti di seguire" su un utente nella lista
   Then: l'azione avviene con optimistic UI (feedback immediato)
   And: il conteggio nel ProfileHeader si aggiorna
   And: in caso di errore, rollback + toast Sonner

4. **AC4 — Navigazione al profilo dalla lista**
   Given: un utente che visualizza una lista follower o following
   When: clicca sul username o avatar di un utente nella lista
   Then: viene navigato al profilo di quell'utente (`/profilo/[username]`)

5. **AC5 — Stato vuoto e loading**
   Given: un utente che visualizza una lista follower o following vuota
   When: la lista non contiene utenti
   Then: viene mostrato un messaggio appropriato ("Nessun follower" / "Non segui ancora nessuno")
   And: durante il caricamento vengono mostrate skeleton card animate

## Tasks / Subtasks

> **NOTA:** Il backend è 100% COMPLETO. Gli endpoint `GET /api/users/{id}/followers/` e `GET /api/users/{id}/following/` sono paginati, usano queryset annotato (N+1 fix), e hanno test in `FollowUnfollowTest`. Il lavoro è TUTTO frontend.

### Codice esistente (già implementato)

- [x] Backend: `get_followers()` action — `GET /api/users/{id}/followers/` paginato con queryset annotato in `backend/cs_clips/views.py:201-214`
- [x] Backend: `get_following()` action — `GET /api/users/{id}/following/` paginato con queryset annotato in `backend/cs_clips/views.py:216-229`
- [x] Backend: `UserSerializer` con `followers_count`, `following_count`, `is_followed_by_me` in `backend/cs_clips/serializers.py`
- [x] Backend: Test `test_get_followers_list` e `test_get_following_list` in `backend/cs_clips/tests/test_views.py:749-765`
- [x] Frontend: `usersApi.getFollowers(id)` e `usersApi.getFollowing(id)` in `frontend/src/lib/api/users.ts:32-36` (MA con tipo errato — vedi Task 1)
- [x] Frontend: `useFollowers(userId)` e `useFollowing(userId)` hooks in `frontend/src/lib/hooks/use-users.ts:18-30` (MA senza paginazione — vedi Task 2)
- [x] Frontend: `queryKeys.users.followers(id)` e `queryKeys.users.following(id)` in `frontend/src/lib/query-keys.ts:23-24`
- [x] Frontend: `FollowButton` con optimistic UI, rollback e toast in `frontend/src/components/user/follow-button.tsx`
- [x] Frontend: `UserAvatar` con size sm/md/lg in `frontend/src/components/user/user-avatar.tsx`
- [x] Frontend: `EmptyState`, `PageLoader` componenti shared in `frontend/src/components/shared/`
- [x] Frontend: `PaginatedResponse<T>` tipo in `frontend/src/types/api.ts`
- [x] Frontend: `useFollow()` e `useUnfollow()` con cache invalidation che include `followers(id)` e `following(id)` in `frontend/src/lib/hooks/use-users.ts:41-187`

### Gap identificati (lavoro da completare)

- [x] Task 1: Fix tipo API — `getFollowers`/`getFollowing` con paginazione (AC: #1, #2)
  - [x] 1.1 — Modificare `usersApi.getFollowers` in `frontend/src/lib/api/users.ts`: cambiare tipo ritorno da `User[]` a `PaginatedResponse<User>`, aggiungere parametro `page = 1`, passare `{ params: { page } }` alla request
  - [x] 1.2 — Modificare `usersApi.getFollowing` in `frontend/src/lib/api/users.ts`: stesso pattern di 1.1

- [x] Task 2: Aggiornare hooks con paginazione e staleTime (AC: #1, #2)
  - [x] 2.1 — Modificare `useFollowers` in `frontend/src/lib/hooks/use-users.ts`: aggiungere parametro `page = 1`, aggiornare queryKey a `queryKeys.users.followers(userId)` con page incluso nella key (es. `[...queryKeys.users.followers(userId), page]`), aggiungere `staleTime: 5 * 60_000`, aggiungere `keepPreviousData: true` per transizioni fluide tra pagine
  - [x] 2.2 — Modificare `useFollowing` in `frontend/src/lib/hooks/use-users.ts`: stesso pattern di 2.1

- [x] Task 3: Rendere contatori cliccabili nel ProfileHeader (AC: #1, #2, #4)
  - [x] 3.1 — Modificare `ProfileHeader` in `frontend/src/components/user/profile-header.tsx`: wrappare il contatore follower in `<Link href={/profilo/${profileUser.username}/followers}>`. Il `<span>` con `{profileUser.followers_count} follower` (riga 55-60) diventa un `<Link>` con stile `hover:underline cursor-pointer`
  - [x] 3.2 — Stessa modifica per il contatore following (riga 61-66): wrappare in `<Link href={/profilo/${profileUser.username}/following}>` con testo "seguiti"
  - [x] 3.3 — Aggiungere import di `Link` da `next/link` in profile-header.tsx

- [x] Task 4: Creare componente `UserListItem` (AC: #1, #2, #3, #4)
  - [x] 4.1 — Creare `frontend/src/components/user/user-list-item.tsx`: componente che mostra una riga con `UserAvatar` (size="md") + username bold (Link a `/profilo/[username]`) + bio troncata (max 1 riga, `truncate`) + `FollowButton` a destra
  - [x] 4.2 — Props: `user: User` (il tipo User già ha `id`, `username`, `bio`, `is_followed_by_me`)
  - [x] 4.3 — Layout: `flex items-center gap-3 p-3 rounded-lg hover:bg-accent/50 transition-colors`. Avatar e username cliccabili, FollowButton allineato a destra con `ml-auto`
  - [x] 4.4 — Il componente deve usare `FollowButton` esistente passando `userId={user.id}` `username={user.username}` `isFollowing={user.is_followed_by_me}` `size="sm"`
  - [x] 4.5 — Creare anche `UserListItemSkeleton` nello stesso file: versione skeleton con `Skeleton` di shadcn/ui per avatar (cerchio h-9 w-9) + riga testo (h-4 w-24) + riga bio (h-3 w-40) + riga bottone (h-8 w-20). Usare 5 skeleton items come default

- [x] Task 5: Creare pagina followers (AC: #1, #2, #5)
  - [x] 5.1 — Creare `frontend/src/app/(main)/profilo/[username]/followers/page.tsx` come Client Component (`"use client"`)
  - [x] 5.2 — La pagina deve: usare `useParams` per estrarre `username`, usare `useUserByUsername(username)` per ottenere l'userId, poi usare `useFollowers(userId, page)` per la lista
  - [x] 5.3 — Layout: titolo `Follower di {username}` con link "indietro" (ArrowLeft di Lucide + Link a `/profilo/[username]`), poi lista di `UserListItem`, poi paginazione (bottoni "Precedente"/"Successivo" con stato `page`)
  - [x] 5.4 — Stati: `PageLoader` se il profilo sta caricando, `EmptyState` con icon `Users` e titolo "Nessun follower" se la lista è vuota, `UserListItemSkeleton` durante il caricamento della lista follower
  - [x] 5.5 — La paginazione mostra "Pagina X di Y" calcolato da `Math.ceil(data.count / 10)`. Bottone "Precedente" disabilitato se `page === 1`, bottone "Successivo" disabilitato se `data.next === null`

- [x] Task 6: Creare pagina following (AC: #1, #2, #5)
  - [x] 6.1 — Creare `frontend/src/app/(main)/profilo/[username]/following/page.tsx` come Client Component
  - [x] 6.2 — Identico pattern di Task 5 ma con: titolo "Seguiti da {username}", hook `useFollowing(userId, page)`, empty state "Non segue ancora nessuno" con icon `UserPlus`

- [x] Task 7: Verifica finale (AC: #1, #2, #3, #4, #5)
  - [x] 7.1 — Eseguire `npm run build` da `frontend/` → TypeScript strict, 0 errori
  - [x] 7.2 — Eseguire `python manage.py test` da `backend/` → tutti i test passano (nessuna modifica backend, ma verifica regressioni)

## Dev Notes

### Stato attuale del codice — Analisi gap

Il sistema follower/following è **backend-complete, frontend-partial**. Gli endpoint API sono paginati, testati e performanti (queryset annotato, N+1 fix). Il frontend ha le funzioni API e gli hooks base ma con **tipo errato** (aspettano `User[]` ma il backend ritorna `PaginatedResponse<User>`), e mancano le pagine UI per visualizzare le liste.

| Gap | Severità | File impattato | Dettaglio |
|-----|----------|----------------|-----------|
| **Type mismatch API getFollowers/getFollowing** | CRITICO | `lib/api/users.ts:32-36` | Tipizzato `User[]` ma backend ritorna `PaginatedResponse<User>` con `{count, next, previous, results}` |
| **Hook non paginato** | CRITICO | `lib/hooks/use-users.ts:18-30` | `useFollowers`/`useFollowing` non accettano parametro `page`, no `staleTime`, no `keepPreviousData` |
| **Contatori non cliccabili** | CRITICO | `components/user/profile-header.tsx:54-66` | I contatori follower/following sono `<span>` statici, servono `<Link>` alle pagine dedicate |
| **Pagine mancanti** | CRITICO | `app/(main)/profilo/[username]/` | Non esistono `followers/page.tsx` e `following/page.tsx` |
| **Componente lista mancante** | CRITICO | `components/user/` | Nessun componente per visualizzare un utente in lista con avatar + username + follow button |

### Decisione architetturale: Pagine dedicate (non Dialog)

Dopo discussione con il team, si è scelto il pattern **pagine dedicate** anziché Dialog modale:
- Route: `/profilo/[username]/followers` e `/profilo/[username]/following`
- Motivazioni: desktop-first (più spazio), URL condivisibile, deep-linkable, routing gratis con App Router, meno complessità stato modale
- I contatori nel `ProfileHeader` diventano `<Link>` cliccabili

### Pattern paginazione da implementare

Il pattern usa `useQuery` con `keepPreviousData: true` e stato `page` locale nel componente:

```typescript
export function useFollowers(userId: number, page = 1) {
  return useQuery({
    queryKey: [...queryKeys.users.followers(userId), page],
    queryFn: () => usersApi.getFollowers(userId, page),
    staleTime: 5 * 60_000,
    keepPreviousData: true,
  });
}
```

**NON** usare infinite scroll — la navigazione a pagine è più prevedibile per desktop-first e coerente con la paginazione DRF (PAGE_SIZE=10).

### Componenti da RIUTILIZZARE (NON ricreare)

| Componente | File | Riuso |
|-----------|------|-------|
| `FollowButton` | `components/user/follow-button.tsx` | Usare direttamente nelle righe lista. Props: `userId`, `username`, `isFollowing`, `size="sm"`. Già ha optimistic UI + rollback + toast |
| `UserAvatar` | `components/user/user-avatar.tsx` | Usare con `size="md"` nelle righe lista. Mostra iniziale con gradient background |
| `EmptyState` | `components/shared/empty-state.tsx` | Usare per stati vuoti. Props: `icon`, `title`, `description` |
| `PageLoader` | `components/shared/page-loader.tsx` | Usare per loading iniziale profilo (prima di avere userId) |
| `PaginatedResponse<T>` | `types/api.ts` | Tipo per risposta paginata DRF. Già importato in `types/index.ts` |

### Lezioni dalla Story 1-5 (da applicare)

- **Cache invalidation:** `useFollow`/`useUnfollow` già invalidano `queryKeys.users.followers(targetId)` e `queryKeys.users.following(currentUserId)` nel `onSettled`. Dopo follow/unfollow dalla lista, i dati si refreshano automaticamente. NESSUN lavoro aggiuntivo necessario.
- **Optimistic UI:** Il `FollowButton` ha già optimistic update su `byUsername` e `detail` cache keys. I cambi contatore nel ProfileHeader sono automatici via invalidazione.
- **N+1 fix:** `get_followers()`/`get_following()` nel backend usano `self.get_queryset().filter(pk__in=...)` che passa per il queryset annotato. Nessun N+1.
- **Test count:** 85 test backend. Zero regressioni obbligatorio (nessuna modifica backend in questa story).
- **Naming:** kebab-case per file (`user-list-item.tsx`), named exports, snake_case per campi dati.
- **Toast:** Solo su errore, MAI su successo. Il `FollowButton` lo gestisce già.
- **Query keys con page:** La key `queryKeys.users.followers(userId)` è `["users", userId, "followers"]`. Aggiungere `page` come ultimo elemento: `["users", userId, "followers", page]`. L'invalidazione in `useFollow`/`useUnfollow` usa `queryKeys.users.followers(userId)` come prefisso — invalida TUTTE le pagine. Perfetto.

### Git intelligence

Ultimi commit rilevanti:
- `d6b0b79` — Story 1-2 registrazione + Story 1-3 login JWT + code review fix
- `ededfe7` — code review Story 1-1: sicurezza, performance, dead code
- `f6845e1` — Story 1-1 backend alignment + Story 1-9 ricerca utenti + fix permessi

Pattern stabiliti nei commit precedenti:
- File pagina: `"use client"` + `useParams` + hooks + conditional rendering (loading/error/data)
- Componenti user: named exports, props tipizzate con interface, Tailwind utility classes
- Pattern profilo: `useUserByUsername(username)` → userId → altre query

### Project Structure Notes

| File | Ruolo | Azione |
|------|-------|--------|
| `frontend/src/lib/api/users.ts:32-36` | API client followers/following | **DA MODIFICARE** — fix tipo `User[]` → `PaginatedResponse<User>`, aggiungere param `page` |
| `frontend/src/lib/hooks/use-users.ts:18-30` | Hooks useFollowers/useFollowing | **DA MODIFICARE** — aggiungere `page`, `staleTime`, `keepPreviousData` |
| `frontend/src/components/user/profile-header.tsx:54-66` | Contatori follower/following | **DA MODIFICARE** — wrappare in `<Link>` cliccabili |
| `frontend/src/components/user/user-list-item.tsx` | Componente riga lista utente | **DA CREARE** — avatar + username + bio + follow button + skeleton |
| `frontend/src/app/(main)/profilo/[username]/followers/page.tsx` | Pagina lista follower | **DA CREARE** — pagina con lista paginata |
| `frontend/src/app/(main)/profilo/[username]/following/page.tsx` | Pagina lista following | **DA CREARE** — pagina con lista paginata |

**File NON da toccare:**
- `backend/cs_clips/views.py` — endpoint followers/following già completi
- `backend/cs_clips/serializers.py` — UserSerializer già include tutti i campi necessari
- `backend/cs_clips/tests/test_views.py` — test followers/following già presenti
- `frontend/src/components/user/follow-button.tsx` — FollowButton già completo con optimistic UI
- `frontend/src/components/user/user-avatar.tsx` — UserAvatar già completo
- `frontend/src/lib/query-keys.ts` — query keys followers/following già presenti
- `frontend/src/types/user.ts` — tipo User già ha tutti i campi necessari

### Stack tecnologico rilevante

- **Backend:** Django 5.1.6, DRF 3.15.1 (endpoint già completi — zero lavoro backend)
- **Frontend:** Next.js 16.1.6, React 19, TypeScript 5, Axios 1.13.5
- **UI:** TailwindCSS 4, shadcn/ui (Button, Avatar, Skeleton), Lucide React (ArrowLeft, Users, UserPlus)
- **State:** TanStack React Query 5 (`useQuery` con `keepPreviousData`), Axios
- **Routing:** Next.js App Router (`app/(main)/profilo/[username]/followers/page.tsx`)
- **Pattern:** snake_case per campi dati, kebab-case per file, named exports

### Vincoli critici per lo sviluppatore

1. **TIPO API:** `usersApi.getFollowers` e `getFollowing` DEVONO ritornare `PaginatedResponse<User>`, NON `User[]`. Il backend ritorna `{count, next, previous, results}` tramite `self.get_paginated_response()`.
2. **CACHE KEY CON PAGE:** La query key per paginazione è `[...queryKeys.users.followers(userId), page]`. L'invalidazione in `useFollow`/`useUnfollow` usa `queryKeys.users.followers(userId)` come prefisso — invalida correttamente TUTTE le pagine cached.
3. **NESSUN INFINITE SCROLL:** Usare paginazione classica con bottoni "Precedente"/"Successivo" e stato `page` locale. `keepPreviousData: true` per transizioni fluide.
4. **LINK NEL PROFILO:** I contatori follower/following nel `ProfileHeader` DEVONO diventare `<Link>` da `next/link`, NON `<button>` o `onClick` con router.push. Sono navigazione, non azione.
5. **RIUTILIZZARE FollowButton:** Il componente `FollowButton` esistente gestisce già TUTTO: optimistic UI, rollback, toast, loading state, hide su profilo proprio. NON ricreare nessuna di queste funzionalità.
6. **SKELETON:** Usare `Skeleton` di shadcn/ui per il loading state. Layout skeleton identico al `UserListItem` ma con placeholder grigio animato. Mostrare 5 skeleton items durante il caricamento.
7. **EMPTY STATE:** Usare `EmptyState` esistente con icon `Users` (Lucide) per "Nessun follower" e `UserPlus` per "Non segue ancora nessuno".
8. **MODELLO USER:** Usare SEMPRE `get_user_model()`. MAI `from django.contrib.auth.models import User`. Il Custom User Model è `cs_clips.User` (AbstractUser).
9. **LINGUA:** Messaggi utente in italiano. Codice in inglese. Titoli pagina: "Follower di {username}", "Seguiti da {username}".
10. **LINK PROFILO:** Cliccando su avatar o username nella lista si naviga a `/profilo/[username]`. Usare `<Link>` da `next/link`.
11. **DARK MODE:** Tutti i componenti usano Tailwind utility classes con semantic tokens (`text-foreground`, `text-muted-foreground`, `bg-accent`). NON hardcodare colori.
12. **ACCESSIBILITY:** Usare `aria-label` sui link di navigazione. `FollowButton` ha già accessibilità via shadcn Button. I link username devono avere testo significativo.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.6]
- [Source: _bmad-output/planning-artifacts/architecture.md#React-Query-Cache-Invalidation]
- [Source: _bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- [Source: _bmad-output/planning-artifacts/architecture.md#Pagination]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Dark-Mode]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Skeleton-Loading]
- [Source: _bmad-output/planning-artifacts/prd.md#FR6]
- [Source: _bmad-output/project-context.md#Custom-User-Model]
- [Source: _bmad-output/project-context.md#Paginazione]
- [Source: _bmad-output/implementation-artifacts/1-5-follow-e-unfollow.md#Dev-Notes]
- [Source: _bmad-output/implementation-artifacts/1-5-follow-e-unfollow.md#Senior-Developer-Review]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

Nessun issue di debug riscontrato. Implementazione liscia.

### Completion Notes List

- **Task 1:** Fix tipo API `getFollowers`/`getFollowing` — cambiato tipo ritorno da `User[]` a `PaginatedResponse<User>`, aggiunto parametro `page` con default 1, passato `{ params: { page } }` alla request Axios.
- **Task 2:** Aggiornati hooks `useFollowers`/`useFollowing` — aggiunto parametro `page`, query key con page (`[...base, page]`), `staleTime: 5 * 60_000`, `placeholderData: (prev) => prev` (equivalente React Query v5 di `keepPreviousData`).
- **Task 3:** Contatori follower/following nel `ProfileHeader` trasformati da `<span>` statici a `<Link>` cliccabili con `hover:underline` e `aria-label` per accessibilità. Navigano a `/profilo/[username]/followers` e `/profilo/[username]/following`.
- **Task 4:** Creato componente `UserListItem` con `UserAvatar` (md), username linkato, bio troncata, `FollowButton` (sm) allineato a destra. Creato `UserListItemSkeleton` con 5 skeleton items animati di default.
- **Task 5:** Creata pagina `/profilo/[username]/followers` — Client Component con `useParams`, `useUserByUsername` per userId, `useFollowers(userId, page)` per lista paginata. Include `PageLoader`, `EmptyState` (icon Users), `UserListItemSkeleton`, paginazione con "Precedente"/"Successivo" e "Pagina X di Y".
- **Task 6:** Creata pagina `/profilo/[username]/following` — stesso pattern di Task 5 con titolo "Seguiti da {username}", `useFollowing`, empty state "Non segue ancora nessuno" (icon UserPlus).
- **Task 7:** Build frontend OK (0 errori TypeScript, route followers/following generate). 85 test backend OK (zero regressioni, nessuna modifica backend).

### Change Log

- **2026-02-15:** Implementazione completa Story 1-6 — 7 task completati. Fix tipo API paginato, hooks con staleTime/placeholderData, contatori cliccabili, componente UserListItem + skeleton, pagine dedicate followers/following con paginazione classica. Build OK, 85 test OK.
- **2026-02-15 (Code Review):** Review avversariale — 8 issue trovati (3 HIGH, 3 MEDIUM, 2 LOW). Tutti HIGH e MEDIUM fixati automaticamente:
  - H1: Aggiunto `enabled: userId > 0` a `useFollowers`/`useFollowing` (previene 404 con userId=0 durante loading)
  - H2: Aggiunto error handling con `ErrorMessage` + `onRetry` per fallimento API lista su entrambe le pagine
  - H3: Aggiunto error handling per fallimento fetch profilo (era blank screen)
  - M1: Sostituito magic number `10` con `PAGE_SIZE` importato da `@/lib/constants`
  - M2: Allargato click target del link "indietro" con `p-2 -m-2` per accessibilità WCAG
  - M3: Rimosso wrapper `<div>` vuoto su `FollowButton`, spostato `ml-auto` come `className` prop
  - Build OK post-fix. 2 issue LOW lasciati come miglioramenti futuri (duplicazione codice, doppia aria-label).

### File List

- `frontend/src/lib/api/users.ts` — MODIFICATO: fix tipo `getFollowers`/`getFollowing` da `User[]` a `PaginatedResponse<User>`, aggiunto parametro `page`
- `frontend/src/lib/hooks/use-users.ts` — MODIFICATO: `useFollowers`/`useFollowing` con paginazione, staleTime, placeholderData
- `frontend/src/components/user/profile-header.tsx` — MODIFICATO: contatori follower/following wrappati in `<Link>`, aggiunto import `Link`
- `frontend/src/components/user/user-list-item.tsx` — CREATO: componente `UserListItem` + `UserListItemSkeleton`
- `frontend/src/app/(main)/profilo/[username]/followers/page.tsx` — CREATO: pagina lista follower paginata
- `frontend/src/app/(main)/profilo/[username]/following/page.tsx` — CREATO: pagina lista following paginata
