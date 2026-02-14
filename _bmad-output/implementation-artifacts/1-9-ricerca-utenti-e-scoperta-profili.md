# Story 1.9: Ricerca Utenti e Scoperta Profili

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utente registrato,
I want cercare altri utenti per username tramite una barra di ricerca,
So that possa scoprire nuovi utenti da seguire e visitare i loro profili.

## Acceptance Criteria

1. **Barra di ricerca nella sidebar/header** — Un campo di ricerca con placeholder "Cerca utenti..." è accessibile dalla sidebar desktop e dall'header mobile su qualsiasi pagina.

2. **Ricerca con debounce** — Digitando almeno 2 caratteri (debounce 300ms), il sistema chiama `GET /api/users/?search=<query>` e mostra i risultati in un dropdown:
   - Ogni risultato mostra username
   - Cliccando su un risultato si naviga al profilo dell'utente (`/profilo/[username]`)
   - Se nessun risultato, mostra "Nessun utente trovato"

3. **Backend search filter** — `GET /api/users/?search=<query>` filtra gli utenti per username con `icontains` e restituisce la lista paginata.

4. **Navigazione al profilo** — Cliccando su un risultato, l'utente viene navigato alla pagina profilo dove è visibile il bottone "Segui" / "Smetti di seguire" (dipendenza: Story 1.5 - già funzionante).

## Tasks / Subtasks

- [x] Task 1: Backend — Aggiungere SearchFilter su UserViewSet (AC: #3)
  - [x] 1.1 Aggiungere `rest_framework.filters.SearchFilter` a `filter_backends` di UserViewSet
  - [x] 1.2 Aggiungere `search_fields = ['username']` a UserViewSet
  - [x] 1.3 Scrivere test per verifica ricerca funzionante

- [x] Task 2: Frontend — API search e hook (AC: #2)
  - [x] 2.1 Aggiungere metodo `search(query)` a `usersApi`
  - [x] 2.2 Aggiungere query key `search` a `queryKeys.users`
  - [x] 2.3 Creare hook `useSearchUsers(query)` con `enabled: query.length >= 2`

- [x] Task 3: Frontend — Componente UserSearchBar (AC: #1, #2)
  - [x] 3.1 Creare componente `UserSearchBar` con input, debounce 300ms, dropdown risultati
  - [x] 3.2 Mostrare username in ogni risultato con navigazione a `/profilo/[username]`
  - [x] 3.3 Stato vuoto: "Nessun utente trovato"
  - [x] 3.4 Stato loading durante la ricerca

- [x] Task 4: Frontend — Integrazione nel layout (AC: #1)
  - [x] 4.1 Aggiungere UserSearchBar nella LeftSidebar (desktop)
  - [x] 4.2 Aggiungere UserSearchBar nell'Header mobile

- [x] Task 5: Test e verifica (AC: #1-4)
  - [x] 5.1 Test backend: ricerca per username funzionante (4 test, tutti superati)
  - [x] 5.2 Verifica navigazione al profilo con bottone follow visibile

## Dev Notes

### Stato Backend Attuale

- `UserViewSet` (ModelViewSet) in `backend/cs_clips/views.py`
- Global filter backend: solo `DjangoFilterBackend` (da settings.py)
- Nessun `SearchFilter` configurato — va aggiunto a livello di ViewSet
- DRF `SearchFilter` supporta `?search=<query>` out-of-the-box con `search_fields`

### Stato Frontend Attuale

- `usersApi` in `frontend/src/lib/api/users.ts` — ha `getAll`, `getById`, `follow`, `unfollow`, `getFollowers`, `getFollowing`
- `use-users.ts` — hooks per user, followers, following, follow/unfollow mutations
- `query-keys.ts` — ha `users.detail`, `users.followers`, `users.following`
- Sidebar: `left-sidebar.tsx` con nav items (Home, Esplora, Carica, Profilo, Contest)
- Header mobile: `header.tsx` con hamburger + avatar dropdown
- Componenti UI disponibili: Input, Popover, Skeleton (Shadcn)
- `UserAvatar` component per mostrare avatar utente

### Pattern da Seguire

- Backend: `SearchFilter` per-ViewSet (non globale), `search_fields = ['username']`
- Frontend API: stesso pattern di `usersApi.getAll()` con parametro `search`
- Frontend hook: `useQuery` con `enabled: query.length >= 2` per evitare query inutili
- Debounce: `useState` + `useEffect` con `setTimeout` (300ms)
- Dropdown: Shadcn `Popover` o div posizionato absolute
- Navigazione: `router.push()` o `<Link>` a `/profilo/${username}`

### Regole Critiche

- Codice in inglese, messaggi in italiano
- `handle_exception()` override in ogni ViewSet (già presente su UserViewSet)
- Usare componenti Shadcn UI esistenti (Input, Popover, Skeleton)
- Non aggiungere dipendenze esterne per il debounce (basta useState/useEffect)

### Scope — Cosa NON è in Questa Story

- Ricerca video (solo utenti)
- Filtri avanzati (solo username)
- Autocompletamento complesso (semplice dropdown)

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Nessun bug riscontrato. Implementazione lineare senza blocchi.

### Completion Notes List

- **Task 1:** Aggiunto `SearchFilter` e `search_fields = ['username']` a `UserViewSet`. Aggiunto anche `order_by('username')` al queryset per eliminare warning di paginazione non ordinata. 4 test backend scritti e superati (ricerca per username, nessun risultato, case-insensitive, senza filtro).
- **Task 2:** Aggiunto metodo `search(query)` a `usersApi`, query key `users.search(query)` a `queryKeys`, hook `useSearchUsers(query)` con `enabled: query.length >= 2` e `staleTime: 30s`.
- **Task 3:** Creato componente `UserSearchBar` con: input con icona Search + clear button, debounce 300ms via useState/useEffect, dropdown con risultati (UserAvatar + username), stato "Nessun utente trovato", skeleton loading, chiusura al click esterno, navigazione a `/profilo/{username}`. Supporta modalità `collapsed` per sidebar.
- **Task 4:** Integrato `UserSearchBar` nella `LeftSidebar` (tra logo e nav, con supporto collapsed) e nell'`Header` mobile (al posto del logo, con max-width per non occupare troppo spazio).
- **Task 5:** 38/38 test backend superati (0 regressioni). TypeScript check superato senza errori.

### Change Log

- 2026-02-14: Implementazione completa Story 1.9 — SearchFilter backend, API frontend, componente UserSearchBar, integrazione layout, test suite (38 test totali, 4 nuovi)

### File List

- `backend/cs_clips/views.py` — Aggiunto import `SearchFilter`. Aggiunto `filter_backends`, `search_fields`, `order_by('username')` a `UserViewSet`.
- `backend/cs_clips/tests/test_views.py` — Aggiunta classe `UserSearchEndpointTest` con 4 test.
- `frontend/src/lib/api/users.ts` — Aggiunto metodo `search(query)`.
- `frontend/src/lib/query-keys.ts` — Aggiunto `users.search(query)`.
- `frontend/src/lib/hooks/use-users.ts` — Aggiunto hook `useSearchUsers(query)`.
- `frontend/src/components/user/user-search-bar.tsx` — **NUOVO** componente UserSearchBar.
- `frontend/src/components/layout/left-sidebar.tsx` — Aggiunto import e rendering `UserSearchBar`.
- `frontend/src/components/layout/header.tsx` — Aggiunto import e rendering `UserSearchBar` (sostituisce logo mobile).
