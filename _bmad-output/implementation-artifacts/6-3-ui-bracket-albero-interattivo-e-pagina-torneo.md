# Story 6.3: UI Bracket — Albero Interattivo e Pagina Torneo

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utente registrato,
I want visualizzare il bracket come albero grafico interattivo e votare nei matchup,
So that posso seguire la competizione e partecipare alle votazioni.

## Acceptance Criteria

1. **Given** un utente che accede alla pagina di un bracket
   **When** il bracket e' visualizzato
   **Then** mostra un albero grafico interattivo stile torneo con scontri, clip passate e risultati per turno (FR41b)
   **And** usa una libreria React dedicata per bracket visualization OPPURE un componente custom SVG/CSS se le librerie esistenti non sono compatibili con React 19

2. **Given** un matchup attivo nell'albero
   **When** l'utente clicca su un matchup
   **Then** vede le due clip embedded con player e il sistema di voto 1-5 stelle (FR42b)

3. **Given** un matchup completato
   **When** visualizzato nell'albero
   **Then** mostra il vincitore evidenziato e il punteggio medio di entrambe le clip

4. **Given** un bracket completato
   **When** l'utente visualizza la pagina
   **Then** vede il vincitore finale con il premio indicato (FR44b)
   **And** l'intero albero e' navigabile per rivedere tutti i matchup passati

5. **Given** un utente non iscritto e un bracket in stato "registration"
   **When** visualizza la pagina del bracket
   **Then** vede un pulsante "Iscriviti" per entrare con una propria clip
   **And** dopo iscrizione, la pagina si aggiorna mostrando `my_entry`

6. **Given** i nuovi moduli frontend
   **When** vengono creati
   **Then** `src/lib/api/brackets.ts` con metodi list + detail + enter + vote
   **And** `src/lib/hooks/use-brackets.ts` con hook per lista, dettaglio, iscrizione, voto
   **And** `src/types/bracket.ts` con tipi Bracket, ContestEntry, Matchup, MatchupVote
   **And** componenti in `src/components/brackets/` per albero, matchup card, voto
   **And** pagina `/contest/bracket/[id]/page.tsx` per dettaglio bracket
   **And** sezione bracket nella pagina `/contest/` esistente (listing)
   **And** `isError` + `<ErrorMessage onRetry={refetch} />` su ogni pagina/componente con fetch

7. **Given** i nuovi componenti
   **When** vengono renderizzati
   **Then** seguono il design system esistente (TailwindCSS 4, Shadcn/UI, dark theme oklch)
   **And** sono responsive (desktop + mobile)
   **And** usano `framer-motion` per animazioni (import da `"framer-motion"`, NON `"motion/react"`)

## Tasks / Subtasks

- [x] Task 1: Tipi TypeScript bracket (AC: #6)
  - [x] 1.1 Creare `frontend/src/types/bracket.ts` con interfacce:
    - `ContestEntryNested` — id, user_id, username, video_id, video_title, video_thumbnail_url
    - `MatchupOutput` — id, round_number, position, entry_1 (ContestEntryNested|null), entry_2 (ContestEntryNested|null), winner (number|null), is_completed, avg_rating_1 (number|null), avg_rating_2 (number|null)
    - `BracketListItem` — id, name, description, status ("registration"|"active"|"completed"), max_participants, current_round, entries_count, created_by, created_by_username, created_at, prize_description
    - `BracketDetail` — extends BracketListItem + matchups_by_round (Record<string, MatchupOutput[]>), my_entry (ContestEntryNested|null)
    - `EnterBracketInput` — video_id: number
    - `VoteMatchupInput` — entry: number, value: number
  - [x] 1.2 Aggiungere export in `frontend/src/types/index.ts`

- [x] Task 2: API client brackets (AC: #6)
  - [x] 2.1 Creare `frontend/src/lib/api/brackets.ts` con oggetto `bracketsApi`:
    - `list(params?: { status?: string; page?: number })` — GET `/api/brackets/`
    - `getDetail(id: number)` — GET `/api/brackets/${id}/`
    - `enter(bracketId: number, data: EnterBracketInput)` — POST `/api/brackets/${bracketId}/enter/`
    - `vote(matchupId: number, data: VoteMatchupInput)` — POST `/api/matchups/${matchupId}/vote/`
  - [x] 2.2 Usare `apiClient` da `./client` (pattern identico a `contests.ts`)

- [x] Task 3: Query keys e hooks React Query (AC: #6)
  - [x] 3.1 Aggiungere chiavi in `frontend/src/lib/query-keys.ts`:
    - `brackets.all`, `brackets.list(params)`, `brackets.detail(id)`
  - [x] 3.2 Creare `frontend/src/lib/hooks/use-brackets.ts`:
    - `useBrackets(params?)` — useInfiniteQuery per lista paginata con `extractPageFromUrl`
    - `useBracketDetail(id)` — useQuery per dettaglio con matchups_by_round
    - `useEnterBracket()` — useMutation POST enter con invalidazione brackets.detail + toast successo/errore
    - `useVoteMatchup()` — useMutation POST vote con invalidazione brackets.detail + toast successo/errore

- [x] Task 4: Componente BracketTree — albero interattivo (AC: #1, #3, #4)
  - [x] 4.1 Creare `frontend/src/components/brackets/bracket-tree.tsx`:
    - Props: `matchupsByRound: Record<string, MatchupOutput[]>`, `onMatchupClick: (matchup: MatchupOutput) => void`, `currentRound: number`
    - Layout: colonne per turno (da sinistra a destra), righe per posizione, linee di connessione CSS/SVG
    - Ogni nodo mostra: username entry_1 vs entry_2, punteggio medio se completato, vincitore evidenziato (bordo/sfondo accent)
    - Matchup attivi (non completati, entrambe le entry presenti) hanno stile cliccabile (cursor-pointer, hover effect)
    - Matchup bye (entry_2 null, is_completed) mostrano "BYE" grigio
    - Responsive: scroll orizzontale su mobile, colonne piu' larghe su desktop
  - [x] 4.2 Creare `frontend/src/components/brackets/matchup-node.tsx`:
    - Props: `matchup: MatchupOutput`, `onClick?: () => void`, `isActive: boolean`
    - Card compatta con due righe (entry_1, entry_2), thumbnail mini, username, punteggio
    - Vincitore con sfondo accent/highlight, perdente con opacita' ridotta
    - Badge "LIVE" su matchup attivi del turno corrente

- [x] Task 5: Componente MatchupDetail — votazione con player (AC: #2)
  - [x] 5.1 Creare `frontend/src/components/brackets/matchup-detail.tsx`:
    - Props: `matchup: MatchupOutput`, `bracketId: number`, `onClose: () => void`, `onVoted: () => void`
    - Dialog/Sheet modale con le due clip affiancate (desktop) o impilate (mobile)
    - Ogni clip mostra: thumbnail/poster del video, username, punteggio medio corrente (se ci sono voti)
    - Sistema voto: 5 stelle cliccabili per entry, submit voto via `useVoteMatchup()`
    - Gestione errori: 409 "Hai gia' votato", 400 "Matchup completato", toast per feedback
    - Matchup completato: mostra risultato finale (vincitore evidenziato, punteggi), voto disabilitato
  - [x] 5.2 Riutilizzare componente `StarRating` esistente da `src/components/rating/star-rating.tsx` per la votazione

- [x] Task 6: Componente BracketWinner — vincitore finale (AC: #4)
  - [x] 6.1 Creare `frontend/src/components/brackets/bracket-winner.tsx`:
    - Props: `bracket: BracketDetail`
    - Visibile solo se `bracket.status === "completed"`
    - Mostra: icona trofeo, username vincitore (dall'ultimo matchup completato), video title, premio (`prize_description`)
    - Animazione framer-motion per comparsa (fade-in + scale)

- [x] Task 7: Componente EnterBracketForm — iscrizione (AC: #5)
  - [x] 7.1 Creare `frontend/src/components/brackets/enter-bracket-form.tsx`:
    - Props: `bracketId: number`, `onEntered: () => void`
    - Visibile solo se bracket in "registration" e `my_entry` e' null
    - Select/dropdown per scegliere tra i propri video (fetch da `/api/videos/?uploader=me`)
    - Pulsante "Iscriviti al torneo" con `useEnterBracket()` mutation
    - Gestione errori: 409 "Gia' iscritto", 400 "Bracket pieno", toast

- [x] Task 8: Pagina dettaglio bracket `/contest/bracket/[id]/` (AC: #1, #2, #3, #4, #5, #6, #7)
  - [x] 8.1 Creare `frontend/src/app/(main)/contest/bracket/[id]/page.tsx`:
    - `"use client"` — pagina client-side
    - Fetch dettaglio con `useBracketDetail(id)`
    - Header: nome bracket, status badge, descrizione, turno corrente, numero iscritti, creatore, data
    - Corpo: `BracketTree` con matchups_by_round
    - Se bracket "registration": mostra `EnterBracketForm` (se non iscritto) o badge "Iscritto" (se `my_entry`)
    - Se bracket "completed": mostra `BracketWinner` in evidenza sopra l'albero
    - Click su matchup attivo: apre `MatchupDetail` modale
    - States: `isLoading` → `PageLoader`, `isError` → `ErrorMessage` con `onRetry={refetch}`

- [x] Task 9: Sezione bracket nella pagina contest listing (AC: #6)
  - [x] 9.1 Modificare `frontend/src/app/(main)/contest/page.tsx`:
    - Aggiungere tab/sezione "Bracket" accanto ai contest settimanali (usare Tabs di Shadcn se non gia' presente)
    - Lista bracket con `useBrackets()` infinite query
    - Ogni item: nome, status badge (colorato), iscritti/max, turno corrente, data
    - Click su item: navigazione a `/contest/bracket/${id}`
    - `isError` + `ErrorMessage` per la sezione bracket
  - [x] 9.2 Creare `frontend/src/components/brackets/bracket-list-item.tsx`:
    - Card con info bracket compatte: nome, status, entries_count/max_participants, premio (se presente)
    - Badge colorato per status: verde "Registrazione", giallo "In corso", grigio "Completato"

- [x] Task 10: Build e verifica finale (AC: tutti)
  - [x] 10.1 `npm run build` — nessun errore TypeScript o build
  - [x] 10.2 Verifica manuale: pagina contest con tab bracket, lista bracket, dettaglio bracket, albero, votazione
  - [x] 10.3 `ruff check backend/` e `ruff format --check backend/` — 0 errori (nessuna modifica backend)
  - [x] 10.4 `python manage.py test` — nessuna regressione (nessuna modifica backend)

## Dev Notes

### Stato attuale — Cosa esiste gia'

**Backend completo (Story 6.1 + 6.2):**
- Modelli: Bracket, ContestEntry, Matchup, MatchupVote (12 modelli totali)
- API: `GET /api/brackets/` (list+filter), `GET /api/brackets/{id}/` (detail con matchups_by_round + my_entry), `POST /api/brackets/{id}/enter/`, `POST /api/matchups/{id}/vote/`, `POST /api/matchups/{id}/close/` (admin only)
- 291 test backend (tutti passano tranne 1 pre-esistente)
- Serializer: BracketListOutputSerializer, BracketDetailOutputSerializer, MatchupOutputSerializer, ContestEntryNestedSerializer, EnterBracketInputSerializer, VoteMatchupInputSerializer

**Frontend esistente (pattern di riferimento):**
- API layer: `src/lib/api/contests.ts` (pattern da seguire)
- Hooks: `src/lib/hooks/use-contests.ts` (useInfiniteQuery + useQuery pattern)
- Tipi: `src/types/contest.ts` (interface pattern)
- Query keys: `src/lib/query-keys.ts` (chiavi strutturate)
- Pagina contest: `src/app/(main)/contest/page.tsx` (listing)
- Pagina contest detail: `src/app/(main)/contest/[id]/page.tsx` (detail con griglia votazione)
- Componente StarRating: `src/components/rating/star-rating.tsx` (riutilizzabile per voto matchup)
- Notifiche: tipi `bracket_invite` e `bracket_turn` gia' gestiti nella pagina notifiche

### Forme dei dati API — Contratto backend

**GET /api/brackets/ — Response:**
```json
{
  "count": 10, "next": "...", "previous": null,
  "results": [{
    "id": 1, "name": "Torneo Clip", "description": "...",
    "status": "registration", "max_participants": 8,
    "current_round": 1, "entries_count": 3,
    "created_by": 5, "created_by_username": "admin_user",
    "created_at": "2026-03-15T10:30:00Z",
    "prize_description": "€100 premio"
  }]
}
```

**GET /api/brackets/{id}/ — Response:**
```json
{
  "id": 1, "name": "...", "status": "active", "...",
  "matchups_by_round": {
    "1": [{
      "id": 1, "round_number": 1, "position": 0,
      "entry_1": { "id": 10, "user_id": 3, "username": "player1", "video_id": 101, "video_title": "Clip 1", "video_thumbnail_url": "..." },
      "entry_2": { "id": 11, "user_id": 4, "username": "player2", "video_id": 102, "video_title": "Clip 2", "video_thumbnail_url": "..." },
      "winner": 10, "is_completed": true, "avg_rating_1": 4.5, "avg_rating_2": 3.2
    }],
    "2": [{ "...matchup turno 2..." }]
  },
  "my_entry": { "id": 10, "user_id": 3, "username": "player1", "video_id": 101, "..." }
}
```
**NOTA:** le chiavi di `matchups_by_round` sono **stringhe** (`"1"`, `"2"`), non numeri.

**POST /api/brackets/{id}/enter/ — Request:** `{ "video_id": 101 }` — Response 201: ContestEntryNested
**POST /api/matchups/{id}/vote/ — Request:** `{ "entry": 10, "value": 4 }` — Response 201: `{ "detail": "Voto registrato." }`

**Codici errore da gestire:**
- 400: bracket non in registration, bracket pieno, matchup completato, entry non del matchup, value fuori range
- 409: gia' iscritto, gia' votato
- 401: non autenticato
- 404: bracket/matchup non trovato

### Pattern di riferimento — Da seguire ESATTAMENTE

**API client — Pattern contests.ts:**
```typescript
import { apiClient } from "./client";
import type { PaginatedResponse } from "@/types/api";
import type { BracketListItem, BracketDetail, ContestEntryNested, EnterBracketInput, VoteMatchupInput } from "@/types/bracket";

export const bracketsApi = {
  list: (params?: { status?: string; page?: number }) =>
    apiClient.get<PaginatedResponse<BracketListItem>>("/api/brackets/", { params }),
  getDetail: (id: number) =>
    apiClient.get<BracketDetail>(`/api/brackets/${id}/`),
  enter: (bracketId: number, data: EnterBracketInput) =>
    apiClient.post<ContestEntryNested>(`/api/brackets/${bracketId}/enter/`, data),
  vote: (matchupId: number, data: VoteMatchupInput) =>
    apiClient.post(`/api/matchups/${matchupId}/vote/`, data),
};
```

**Hook — Pattern use-contests.ts (useInfiniteQuery + useMutation):**
```typescript
import { useInfiniteQuery, useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/query-keys";
import { bracketsApi } from "@/lib/api/brackets";
import { extractPageFromUrl } from "@/lib/utils";
import { toast } from "sonner";

export function useBrackets(params?: { status?: string }) {
  return useInfiniteQuery({
    queryKey: queryKeys.brackets.list(params),
    queryFn: ({ pageParam = 1 }) => bracketsApi.list({ ...params, page: pageParam }),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => extractPageFromUrl(lastPage.data.next),
    select: (data) => data.pages.flatMap((page) => page.data.results),
  });
}

export function useBracketDetail(id: number) {
  return useQuery({
    queryKey: queryKeys.brackets.detail(id),
    queryFn: () => bracketsApi.getDetail(id),
    select: (data) => data.data,
    enabled: !!id,
  });
}
```

**Query keys — Pattern existente:**
```typescript
brackets: {
  all: ["brackets"] as const,
  list: (params?: { status?: string }) => ["brackets", "list", params] as const,
  detail: (id: number) => ["brackets", "detail", id] as const,
},
```

**Pagina — Pattern contest/[id]/page.tsx:**
```tsx
"use client";
import { useParams } from "next/navigation";
import { PageLoader } from "@/components/shared/page-loader";
import { ErrorMessage } from "@/components/shared/error-message";

export default function BracketDetailPage() {
  const params = useParams();
  const id = Number(params.id);
  const { data: bracket, isLoading, isError, refetch } = useBracketDetail(id);

  if (isLoading) return <PageLoader />;
  if (isError || !bracket) return <ErrorMessage onRetry={refetch} />;
  // ...render
}
```

**Mutation con toast — Pattern follow/unfollow:**
```typescript
export function useEnterBracket() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ bracketId, data }: { bracketId: number; data: EnterBracketInput }) =>
      bracketsApi.enter(bracketId, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.brackets.detail(variables.bracketId) });
      toast.success("Iscrizione completata!");
    },
    onError: (error: any) => {
      const detail = error.response?.data?.detail || "Errore durante l'iscrizione.";
      toast.error(detail);
    },
  });
}
```

### Albero Bracket — Approccio implementativo

**Strategia principale: componente custom CSS Grid/Flexbox**

Le librerie React bracket esistenti (`@g-loot/react-tournament-brackets`, `react-brackets`) hanno problemi di compatibilita' con React 19 (ultima pubblicazione 2-3 anni fa). Implementare un componente custom con:

1. **Layout a colonne CSS Grid**: una colonna per turno, da sinistra (turno 1) a destra (finale)
2. **Connessioni tra nodi**: pseudo-elementi CSS (`::before`/`::after`) con bordi per le linee di collegamento
3. **Spacing automatico**: flex grow per centrare verticalmente i matchup di turni successivi
4. **Responsive**: scroll orizzontale (`overflow-x-auto`) su mobile, layout compatto

**Struttura DOM:**
```
div.bracket-tree (grid: repeat(numRounds, 1fr))
  div.round-column (round 1)
    div.matchup-node (position 0)
    div.matchup-node (position 1)
    div.matchup-node (position 2)
    div.matchup-node (position 3)
  div.round-column (round 2)
    div.matchup-node (position 0) ← connesso a pos 0+1 del turno 1
    div.matchup-node (position 1) ← connesso a pos 2+3 del turno 1
  div.round-column (round 3 — finale)
    div.matchup-node (position 0)
```

**Se si vuole provare prima una libreria:**
1. `npm install @g-loot/react-tournament-brackets` — provare con `--legacy-peer-deps` se serve
2. Se funziona con React 19, usarla per il rendering dell'albero
3. Se non funziona, passare al componente custom CSS (fallback gia' previsto)

**DECISIONE RACCOMANDATA:** Iniziare direttamente con componente custom CSS. E' piu' semplice, controllabile, e non aggiunge dipendenze potenzialmente incompatibili.

### Video player nel matchup detail

Per mostrare le clip nel matchup detail, NON serve un player video completo. Usare:
- Thumbnail come poster image (da `video_thumbnail_url` nell'entry)
- Link alla pagina clip `/clip/${videoId}` per la visione completa
- Il voto avviene sulla base della clip, non serve riprodurla inline

Se si vuole un player inline, riutilizzare il componente `VideoPlayer` esistente con `forwardRef` (pattern da Epic Intermedio).

### Vincoli e Attenzioni

1. **NON modificare il backend** — Story 6.3 e' puramente frontend
2. **NON creare nuovi endpoint API** — tutto il backend e' gia' pronto (Story 6.1 + 6.2)
3. **Import framer-motion:** da `"framer-motion"` (NON `"motion/react"`)
4. **Chiavi matchups_by_round:** sono stringhe (`"1"`, `"2"`), usare `Object.entries()` per iterare
5. **PaginatedResponse<T>:** tipo gia' in `src/types/api.ts`, riusare per lista bracket
6. **extractPageFromUrl:** utility gia' in `src/lib/utils.ts`, riusare per paginazione
7. **StarRating:** componente gia' esistente in `src/components/rating/star-rating.tsx` — verificare che accetti props per voto matchup (potrebbe servire adattamento)
8. **Error handling:** OGNI componente con fetch DEVE avere `isError` + `ErrorMessage` (pattern obbligatorio)
9. **Testi UI in italiano:** tutti i label, placeholder, messaggi in italiano
10. **Dark theme:** il progetto usa tema dark oklch — non hardcodare colori chiari
11. **Shadcn components disponibili:** Card, Badge, Dialog, Sheet, Button, Tabs, Skeleton, Tooltip — usare questi, non creare da zero
12. **`my_entry` e' null per utenti non autenticati** — gestire il caso gracefully
13. **Route `/contest/bracket/[id]/`:** sotto la route group `(main)`, richiede autenticazione per enter/vote, ma la visualizzazione dell'albero deve essere accessibile
14. **291 test backend:** non devono rompersi (nessuna modifica backend prevista)

### File da creare/modificare

**Nuovi file:**
- `frontend/src/types/bracket.ts` — tipi TypeScript
- `frontend/src/lib/api/brackets.ts` — API client
- `frontend/src/lib/hooks/use-brackets.ts` — React Query hooks
- `frontend/src/components/brackets/bracket-tree.tsx` — albero interattivo
- `frontend/src/components/brackets/matchup-node.tsx` — nodo matchup nell'albero
- `frontend/src/components/brackets/matchup-detail.tsx` — modale votazione
- `frontend/src/components/brackets/bracket-winner.tsx` — vincitore finale
- `frontend/src/components/brackets/enter-bracket-form.tsx` — form iscrizione
- `frontend/src/components/brackets/bracket-list-item.tsx` — item lista bracket
- `frontend/src/app/(main)/contest/bracket/[id]/page.tsx` — pagina dettaglio bracket

**File da modificare:**
- `frontend/src/types/index.ts` — aggiungere export bracket types
- `frontend/src/lib/query-keys.ts` — aggiungere chiavi brackets
- `frontend/src/app/(main)/contest/page.tsx` — aggiungere sezione/tab bracket

### Test helper — Fixture e pattern gia' disponibili

**React Query test pattern (non richiesti per MVP ma buona prassi):**
- Il progetto NON ha test frontend formali (0 test Vitest/RTL)
- MSW configurato con 5 handler base ma non usato in test automatici
- Per questa story: verifica manuale sufficiente (build + visual check)

### Previous Story Intelligence (Story 6.1 + 6.2)

**Learnings dalla Story 6.1:**
- Admin action test: `RequestFactory` richiede `FallbackStorage` per `MessageMiddleware`
- `ruff format` potrebbe richiedere riformattazione — eseguire proattivamente
- I modelli bracket usano `settings.AUTH_USER_MODEL` per FK
- `bracket.current_round` aggiornato automaticamente da `advance_winner`

**Learnings dalla Story 6.2:**
- Chiavi `matchups_by_round` sono int nel dict Python, ma diventano **stringhe** nel JSON serializzato
- Il campo nella Notification e' `type` (non `notification_type`) — gia' corretto nelle views
- Docker deve essere avviato per i test backend
- 32 test API bracket creati, tutti passano

**Git intelligence (ultimi 5 commit):**
- `b50ace9` feat: Story 6.1 — modelli Bracket/ContestEntry/Matchup + logica turni
- `6bef501` feat: Epic 4+5 — contest listing/voting/classifica + sistema notifiche
- `612f66c` feat: Epic 3 completo — like UI, popup overlay, spareggio like, comment markers
- Pattern commit: `feat: Story X.Y — descrizione breve delle modifiche`

### Project Structure Notes

- I componenti bracket vanno in `src/components/brackets/` (nuovo dominio, come `comments/`, `feed/`, `rating/`)
- La pagina bracket detail e' nested sotto contest: `/contest/bracket/[id]/` (coerente con la navigazione esistente)
- I tipi seguono la convenzione un-file-per-dominio in `src/types/`
- Le API seguono la convenzione un-file-per-dominio in `src/lib/api/`
- Gli hooks seguono la convenzione `use-{dominio}.ts` in `src/lib/hooks/`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 6, Story 6.3] — AC e user story
- [Source: _bmad-output/planning-artifacts/prd.md#FR41b] — Albero grafico interattivo
- [Source: _bmad-output/planning-artifacts/prd.md#FR42b] — Votazione matchup 1-5 stelle
- [Source: _bmad-output/planning-artifacts/prd.md#FR44] — Stato bracket e progressione
- [Source: _bmad-output/planning-artifacts/prd.md#FR44b] — Premio vincitore
- [Source: _bmad-output/planning-artifacts/architecture.md#D2] — Bracket separato da Contest, dominio API indipendente
- [Source: _bmad-output/implementation-artifacts/6-1-modelli-bracket-backend-e-logica-turni.md] — Story 6.1 completata
- [Source: _bmad-output/implementation-artifacts/6-2-api-bracket-e-votazione-matchup.md] — Story 6.2 completata
- [Source: frontend/src/lib/api/contests.ts] — Pattern API client
- [Source: frontend/src/lib/hooks/use-contests.ts] — Pattern hooks React Query
- [Source: frontend/src/types/contest.ts] — Pattern tipi TypeScript
- [Source: frontend/src/lib/query-keys.ts] — Pattern query keys
- [Source: frontend/src/app/(main)/contest/page.tsx] — Pagina contest listing (da modificare)
- [Source: frontend/src/components/rating/star-rating.tsx] — Componente StarRating riutilizzabile
- [Source: frontend/src/components/shared/error-message.tsx] — ErrorMessage obbligatorio
- [Source: _bmad-output/project-context.md] — Regole progetto e anti-pattern

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

Nessun debug necessario — build e test passati al primo tentativo.

### Completion Notes List

- Implementato layer tipi TypeScript completo: 6 interfacce in `bracket.ts` allineate al contratto backend
- API client `bracketsApi` con 4 metodi (list, getDetail, enter, vote) seguendo pattern `contests.ts` con `.then((r) => r.data)` unwrap
- React Query hooks: `useBrackets` (infinite query), `useBracketDetail` (query), `useEnterBracket` + `useVoteMatchup` (mutations con toast italiano)
- Componente custom `BracketTree` con layout flexbox a colonne per turno, scroll orizzontale responsive
- `MatchupNode` con thumbnail mini, username, punteggio, badge "LIVE", vincitore evidenziato (bg-primary/10), perdente opacita' ridotta, BYE grigio
- `MatchupDetail` modale con Dialog Shadcn, clip affiancate desktop/impilate mobile, StarRating riutilizzato per voto 1-5 stelle, gestione errori toast
- `BracketWinner` con animazione framer-motion fade-in+scale, trofeo, premio, vincitore estratto dall'ultimo matchup completato
- `EnterBracketForm` con select dei propri video (via `useUserVideos`), mutation `useEnterBracket`, gestione errori
- Pagina dettaglio `/contest/bracket/[id]/` con header completo, status badge colorato, form iscrizione condizionale, albero, modale votazione
- Pagina contest aggiornata con Tabs Shadcn: "Contest Settimanali" | "Bracket", sezione bracket con infinite scroll e `BracketListItem`
- Tutti i componenti hanno `isError` + `ErrorMessage onRetry` obbligatorio
- Testi UI tutti in italiano, dark theme compatibile, import framer-motion corretto
- Build frontend: 0 errori; ruff: 0 errori; test backend: 293 run, 1 fail pre-esistente (nessuna regressione)

### Change Log

- 2026-03-15: Story 6.3 implementata — UI bracket completa con albero interattivo, votazione matchup, iscrizione, vincitore, pagina dettaglio e listing
- 2026-03-15: Code review fix — 7 issue risolti: Rules of Hooks BracketWinner, voting UX con selezione entry + submit, linee connessione SVG nell'albero, auth guard EnterBracketForm, statusConfig deduplicato, label "Semifinale"

### File List

**Nuovi file:**
- `frontend/src/types/bracket.ts`
- `frontend/src/lib/api/brackets.ts`
- `frontend/src/lib/hooks/use-brackets.ts`
- `frontend/src/components/brackets/bracket-tree.tsx`
- `frontend/src/components/brackets/matchup-node.tsx`
- `frontend/src/components/brackets/matchup-detail.tsx`
- `frontend/src/components/brackets/bracket-winner.tsx`
- `frontend/src/components/brackets/enter-bracket-form.tsx`
- `frontend/src/components/brackets/bracket-list-item.tsx`
- `frontend/src/components/brackets/bracket-status.ts`
- `frontend/src/app/(main)/contest/bracket/[id]/page.tsx`

**File modificati:**
- `frontend/src/types/index.ts` — aggiunto export tipi bracket
- `frontend/src/lib/query-keys.ts` — aggiunta sezione brackets
- `frontend/src/app/(main)/contest/page.tsx` — aggiunto Tabs con sezione Bracket
