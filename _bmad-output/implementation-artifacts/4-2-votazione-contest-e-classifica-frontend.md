# Story 4.2: Votazione Contest e Classifica Frontend

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utente registrato,
I want votare le clip in un contest e vedere la classifica,
So that posso partecipare attivamente e seguire la competizione.

## Acceptance Criteria

1. **Given** un utente autenticato che visualizza un contest attivo
   **When** accede alla pagina dettaglio contest `/contest/[id]`
   **Then** vede la lista delle clip partecipanti con player embedded e sistema di voto 1-5 stelle (FR40a)

2. **Given** un utente che vota una clip nel contest
   **When** seleziona un rating da 1 a 5 stelle
   **Then** il voto viene registrato (un voto per utente per clip, `unique_together` enforced) (FR40a, NFR13)
   **And** il feedback visivo conferma il voto (toast Sonner)

3. **Given** un utente che ha gia votato una clip
   **When** visualizza la clip nel contest
   **Then** vede il proprio voto esistente con stelle pre-compilate e possibilita di modifica (NFR13)

4. **Given** un utente che visualizza un contest (attivo o chiuso)
   **When** accede alla sezione classifica
   **Then** vede le clip ordinate per media voti con posizione in classifica (FR43a)
   **And** per contest chiusi, il vincitore e evidenziato

5. **Given** la pagina contest nel frontend
   **When** viene riscritta
   **Then** mostra: lista contest attivi, lista contest chiusi con vincitori, pagina dettaglio singolo contest con clip + voto + classifica
   **And** utilizza `isError` + `<ErrorMessage onRetry={refetch} />`

6. **Given** il feed home, la pagina esplora e la pagina dettaglio clip `/clip/[id]`
   **When** un utente le visualizza
   **Then** NON vede stelle di rating ne sistema di votazione — le stelle sono presenti ESCLUSIVAMENTE nella sezione contest
   **And** il componente `<StarRating>` viene rimosso da `card-as-player.tsx` e `clip-content.tsx`

## Tasks / Subtasks

- [x] Task 0: Frontend — Rimuovere stelle rating dal feed e dalla pagina clip detail (AC: #6)
  - [x] 0.1 In `components/feed/card-as-player.tsx`: rimuovere `<StarRating>` (riga ~406) e relativo import
  - [x] 0.2 In `app/clip/[id]/clip-content.tsx`: rimuovere `<StarRating>` interattivo (righe ~311-322), label "Il tuo voto / Media" e icona stella nelle stats (righe ~228-236)
  - [x] 0.3 In `app/clip/[id]/clip-content.tsx`: rimuovere `handleRate` callback (~130-152), import/uso di `useCreateRating` e `useUpdateRating`, import `StarRating`
  - [x] 0.4 Verificare che non restino import orfani (`Star` da lucide-react se non usata altrove nel file)
  - [x] 0.5 `npm run build` — 0 errori TypeScript dopo cleanup

- [x] Task 1: Backend — Aggiungere @action contest videos (AC: #1, #4)
  - [x] 1.1 In `contest_views.py`: aggiungere `@action(detail=True, methods=["get"], url_path="videos")` a `ContestViewSet` che ritorna i video del contest con annotazioni `avg_rating`, `my_rating_id`, `my_rating_value`, ordinati per `-avg_rating` (classifica)
  - [x] 1.2 Aggiungere `@extend_schema` sull'action per documentazione OpenAPI
  - [x] 1.3 Test: `GET /api/contests/{id}/videos/` ritorna lista paginata video del contest con annotazioni rating
  - [x] 1.4 Test: utente non autenticato riceve 401
  - [x] 1.5 `ruff check backend/` — 0 errori

- [x] Task 2: Frontend — Estendere API contests e query keys (AC: #1, #5)
  - [x] 2.1 In `lib/api/contests.ts`: aggiungere `list(params?)` → `GET /api/contests/`, `getDetail(id)` → `GET /api/contests/{id}/`, `getContestVideos(contestId, page?)` → `GET /api/contests/{contestId}/videos/`
  - [x] 2.2 In `lib/query-keys.ts`: aggiungere `contests.list(params)`, `contests.detail(id)`, `contests.videos(id, page)`
  - [x] 2.3 Creare `lib/hooks/use-contests.ts`: `useContests(params)` con `useInfiniteQuery`, `useContestDetail(id)` con `useQuery`, `useContestVideos(contestId)` con `useInfiniteQuery`

- [x] Task 3: Frontend — Riscrivere pagina lista contest (AC: #5)
  - [x] 3.1 Riscrivere `app/(main)/contest/page.tsx`: due sezioni — "Contest Attivi" (is_closed=false) e "Contest Chiusi" (is_closed=true con vincitori)
  - [x] 3.2 Ogni contest card mostra: name, tag (Badge), date, video_count, stato (attivo/chiuso), vincitore se chiuso
  - [x] 3.3 Click su card → navigazione a `/contest/[id]`
  - [x] 3.4 `<ErrorMessage>` + loading skeleton + `<EmptyState>` per lista vuota

- [x] Task 4: Frontend — Creare pagina dettaglio contest con votazione (AC: #1, #2, #3, #4)
  - [x] 4.1 Creare `app/(main)/contest/[id]/page.tsx`: header contest (nome, tag, date, stato), sezione clip con votazione, sezione classifica
  - [x] 4.2 Sezione clip: griglia di video card con `<StarRating>` inline per votare — usa `useCreateRating` per primo voto, `useUpdateRating` per modifica
  - [x] 4.3 Mostrare `my_rating_value` pre-compilato se l'utente ha gia votato — stelle piene corrispondenti al voto esistente
  - [x] 4.4 Sezione classifica: lista ordinata per `average_rating` DESC con posizione (#1, #2, ...), media voti, vincitore evidenziato (icona trofeo o badge "Vincitore") per contest chiusi
  - [x] 4.5 Toast Sonner su voto creato/aggiornato con successo
  - [x] 4.6 `<ErrorMessage>` + loading state per tutte le query

- [x] Task 5: Verifica qualita (AC: tutti)
  - [x] 5.1 `ruff check backend/` — 0 errori
  - [x] 5.2 `ruff format --check backend/` — 0 errori
  - [x] 5.3 `python manage.py test` — 221 test, 220 pass, 1 fail pre-esistente noto
  - [x] 5.4 `npm run build` nel frontend — 0 errori TypeScript
  - [x] 5.5 Verifica visuale: feed SENZA stelle, clip detail SENZA stelle, contest con votazione + classifica

## Dev Notes

### Stato attuale — Cosa esiste gia

**Backend (Story 4.1 completata):**

| Componente | File | Stato |
|-----------|------|-------|
| `ContestViewSet` (read-only) | `backend/cs_clips/api/contests/contest_views.py` | Completo — list, retrieve, winners @action, end @action |
| `ContestListOutputSerializer` | `backend/cs_clips/api/contests/contest_serializers.py` | Completo — id, name, tag, dates, is_closed, winner, video_count |
| `ContestDetailOutputSerializer` | `backend/cs_clips/api/contests/contest_serializers.py` | Completo — estende list con winner_detail nested |
| Rating model | `backend/cs_clips/models/rating.py` | Completo — user, video, value (1-5), unique_together |
| Rating API | `backend/cs_clips/api/ratings/rating_views.py` | Completo — POST create, PATCH update |
| Video annotations | `backend/cs_clips/api/videos/video_views.py` | `avg_rating`, `my_rating_id`, `my_rating_value` gia annotati in get_queryset() |

**Frontend (parziale):**

| Componente | File | Stato |
|-----------|------|-------|
| `<StarRating>` | `frontend/src/components/rating/star-rating.tsx` | Completo — value, onChange, readonly, size, hover preview |
| `useCreateRating` | `frontend/src/lib/hooks/use-ratings.ts` | Completo — mutation + invalidate videos.detail |
| `useUpdateRating` | `frontend/src/lib/hooks/use-ratings.ts` | Completo — mutation + invalidate videos.detail |
| `contestsApi.getWinners()` | `frontend/src/lib/api/contests.ts` | Solo winners — manca list, detail, videos |
| Tipo `Contest` | `frontend/src/types/contest.ts` | Parziale — manca `video_count`, `closed_at` |
| Tipo `Rating` | `frontend/src/types/rating.ts` | Completo |
| Tipo `Video` | `frontend/src/types/video.ts` | Completo — include `average_rating`, `my_rating_id`, `my_rating_value`, `contest` |
| Query keys contests | `frontend/src/lib/query-keys.ts` | Solo `contests.winners` — manca list, detail, videos |
| Pagina contest | `frontend/src/app/(main)/contest/page.tsx` | Solo lista vincitori — da riscrivere |

### DECISIONE ARCHITETTURALE: Stelle rating SOLO nel contest

**Le stelle di rating (1-5) NON devono apparire nel feed ne nella pagina dettaglio clip.** Il rating e un meccanismo esclusivamente legato ai contest. Nel feed l'engagement si esprime con like e commenti; nel contest con le stelle per la votazione.

Conseguenze:
- Rimuovere `<StarRating>` da `card-as-player.tsx` (read-only nel feed)
- Rimuovere `<StarRating>` interattivo e `handleRate`/`useCreateRating`/`useUpdateRating` da `clip-content.tsx`
- Rimuovere icona stella + media rating dalle stats in `clip-content.tsx`
- Le annotazioni `avg_rating`, `my_rating_id`, `my_rating_value` restano nel backend `VideoViewSet.get_queryset()` — servono per `desempate_ponderato` e per la nuova `@action videos` del contest. Il frontend le ignora fuori dal contesto contest.
- Il componente `<StarRating>` in `components/rating/star-rating.tsx` resta — verra usato nella pagina contest.
- I hook `useCreateRating`/`useUpdateRating` in `lib/hooks/use-ratings.ts` restano — verranno usati nella pagina contest.

### Cosa manca (scope di questa story)

**Frontend — Cleanup (Task 0, da fare PRIMA):**
1. Rimuovere `<StarRating>` e rating-related code da `card-as-player.tsx` e `clip-content.tsx`

**Backend (minimo):**
1. `@action(detail=True, methods=["get"], url_path="videos")` su `ContestViewSet` — ritorna i video del contest con annotazioni rating per l'utente corrente (avg_rating, my_rating_id, my_rating_value). Questo e necessario perche `VideoFilter` NON ha filtro contest e le annotazioni my_rating richiedono il request.user.

**Frontend (lavoro principale):**
1. Estendere `contests.ts` API con list, getDetail, getContestVideos
2. Aggiungere query keys per contests list/detail/videos
3. Creare hooks React Query per contests
4. Riscrivere pagina lista contest (attivi + chiusi)
5. Creare pagina dettaglio contest `/contest/[id]` con votazione + classifica

### Approccio implementativo

**Backend — @action videos su ContestViewSet:**
```python
@action(detail=True, methods=["get"], url_path="videos")
def videos(self, request, pk=None):
    """Video del contest con annotazioni rating per classifica e votazione."""
    contest = self.get_object()
    qs = Video.objects.filter(contest=contest).annotate(
        avg_rating=Avg("ratings__value"),
    ).order_by(F("avg_rating").desc(nulls_last=True))

    if request.user.is_authenticated:
        my_rating = Rating.objects.filter(
            video=OuterRef("pk"), user=request.user
        )
        qs = qs.annotate(
            my_rating_id=Subquery(my_rating.values("id")[:1]),
            my_rating_value=Subquery(my_rating.values("value")[:1]),
        )

    page = self.paginate_queryset(qs)
    if page is not None:
        serializer = VideoOutputSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    serializer = VideoOutputSerializer(qs, many=True)
    return Response(serializer.data)
```

**ATTENZIONE:** `VideoOutputSerializer` gia gestisce `avg_rating`, `my_rating_id`, `my_rating_value` come campi annotati. Verificare che il serializer li dichiari come `read_only` e che siano coerenti con le annotation names nel queryset sopra. Controllare in `video_serializers.py` se i nomi campo sono `avg_rating` vs `average_rating` — devono corrispondere.

**Frontend — Flusso votazione:**
1. Pagina dettaglio contest → fetch contest detail + fetch contest videos
2. Per ogni video card: mostrare `<StarRating value={video.my_rating_value || 0} onChange={handleRate} />`
3. Se `my_rating_id` e null → `useCreateRating` con `{ video: videoId, value }`
4. Se `my_rating_id` esiste → `useUpdateRating` con `(my_rating_id, value)`
5. Invalidare `queryKeys.contests.videos(contestId)` dopo mutazione (oltre a videos.detail)

**Frontend — Pattern da riusare:**
- `useInfiniteQuery` con `getNextPageParam` per paginazione (vedi `app/(main)/home/page.tsx`)
- `<ErrorMessage isError={isError} onRetry={refetch} />` per error handling
- `<EmptyState>` per liste vuote
- Sonner toast per feedback voto: `toast.success("Voto registrato!")`
- Shadcn `<Card>`, `<Badge>`, `<Tabs>` per layout
- Responsive: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`

### Tipo Contest — Aggiornamento necessario

Il tipo `Contest` in `types/contest.ts` va aggiornato per includere i campi aggiunti dalla Story 4.1:
```typescript
export interface Contest {
  id: number;
  name: string;
  tag: VideoTag;
  start_date: string;
  end_date: string;
  winner: number | null;
  is_closed: boolean;
  closed_at: string | null;
  video_count: number;        // aggiunto in Story 4.1
  winner_detail?: Video;      // solo su detail endpoint
}
```

### Flusso API per votazione

```
# Lista contest attivi
GET /api/contests/?is_closed=false → {count, results: Contest[]}

# Lista contest chiusi
GET /api/contests/?is_closed=true → {count, results: Contest[]}

# Dettaglio contest
GET /api/contests/{id}/ → ContestDetail (con winner_detail nested)

# Video del contest (con rating utente)
GET /api/contests/{id}/videos/ → {count, results: Video[]}
# Ogni video include: avg_rating, my_rating_id, my_rating_value

# Creare voto
POST /api/ratings/ → {video: 42, value: 4}

# Aggiornare voto
PATCH /api/ratings/{my_rating_id}/ → {value: 5}
```

### Classifica — Logica di ordinamento

I video del contest sono ordinati server-side per `avg_rating DESC NULLS LAST`. La classifica frontend:
1. Mostra posizione (#1, #2, #3...) basata sull'ordine dei risultati
2. Video senza voti appaiono in fondo (NULLS LAST)
3. Per contest chiusi: il vincitore (`contest.winner === video.id`) ha badge "Vincitore" / icona trofeo
4. A parita di media voti, l'ordine server decide (spareggio avviene solo alla chiusura via `desempate_ponderato`)

### Invalidation strategy dopo voto

Dopo un voto creato o aggiornato:
1. Invalidare `queryKeys.contests.videos(contestId)` — ricarica classifica aggiornata
2. Invalidare `queryKeys.videos.detail(videoId)` — aggiorna avg_rating se video aperto altrove
3. NON invalidare `queryKeys.contests.detail(contestId)` — non cambia con un voto

I hook `useCreateRating` e `useUpdateRating` gia invalidano `videos.detail(videoId)`. Serve aggiungere invalidazione di `contests.videos(contestId)` — passare `contestId` come parametro aggiuntivo ai hook o gestire nel componente.

### Anti-pattern da evitare

1. **NON creare un nuovo endpoint rating per contest** — gli endpoint `POST /api/ratings/` e `PATCH /api/ratings/{id}/` esistono gia e funzionano. Usare quelli.
2. **NON duplicare logica annotazione** — `@action videos` deve riusare lo stesso pattern di annotation di `VideoViewSet.get_queryset()`, non reinventare.
3. **NON usare optimistic update per la classifica** — la posizione in classifica dipende da tutti i voti, non solo dal proprio. Invalidare e ri-fetchare.
4. **NON filtrare client-side** — i video del contest DEVONO essere fetchati dal server con annotazioni. Non fetchare tutti i video e filtrare in JS.
5. **NON importare da `"motion/react"`** — usare `"framer-motion"` (pacchetto installato).
6. **NON lasciare stelle nel feed o nella clip detail** — le stelle sono ESCLUSIVAMENTE nella sezione contest. Rimuovere da `card-as-player.tsx` e `clip-content.tsx` PRIMA di implementare la pagina contest.
7. **NON eliminare il componente `<StarRating>` ne i hook `useCreateRating`/`useUpdateRating`** — servono per la pagina contest. Rimuovere solo i PUNTI DI UTILIZZO nel feed e clip detail.

### Rischi e edge case

1. **Contest senza video**: `GET /api/contests/{id}/videos/` ritorna `{count: 0, results: []}`. La UI deve mostrare `<EmptyState message="Nessuna clip in gara" />`.
2. **Video senza voti**: `avg_rating` e `null`, `my_rating_id` e `null`. Le stelle devono essere vuote (valore 0), non 5.
3. **Paginazione classifica**: se un contest ha molti video, la classifica deve essere paginata. Usare `useInfiniteQuery` con infinite scroll.
4. **Annotation field names**: verificare corrispondenza tra annotation names in queryset (`avg_rating` vs `average_rating`) e field names nel serializer. Il `VideoOutputSerializer` potrebbe usare `average_rating` — in tal caso l'annotation nell'@action deve essere `.annotate(average_rating=Avg(...))`.
5. **Contest detail vs list serializer**: la pagina dettaglio fa 2 chiamate: `getDetail(id)` per info contest + `getContestVideos(id)` per clip con rating. Non tentare di nidificare tutto in un singolo endpoint.

### Project Structure Notes

- File backend da modificare: `backend/cs_clips/api/contests/contest_views.py` (aggiungere @action videos)
- File backend da creare: nessuno (test aggiunti in `test_contests_list.py` esistente)
- File frontend da modificare (cleanup stelle): `components/feed/card-as-player.tsx` (rimuovere StarRating), `app/clip/[id]/clip-content.tsx` (rimuovere StarRating + handleRate + hooks rating)
- File frontend da modificare (contest): `lib/api/contests.ts`, `lib/query-keys.ts`, `types/contest.ts`, `app/(main)/contest/page.tsx`
- File frontend da creare: `lib/hooks/use-contests.ts`, `app/(main)/contest/[id]/page.tsx`
- File frontend da NON eliminare: `components/rating/star-rating.tsx` (usato nella pagina contest), `lib/hooks/use-ratings.ts` (usato nella pagina contest)
- Cartella componenti contest: valutare `components/contest/` per componenti riusabili (contest-card, contest-leaderboard, contest-video-card), oppure inline nella pagina se semplici

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-4.2] — AC BDD: votazione 1-5 stelle, classifica, vincitore evidenziato, pagina contest completa
- [Source: _bmad-output/planning-artifacts/epics.md#Epic-4] — FRs: FR40a, FR43a, NFR13
- [Source: _bmad-output/planning-artifacts/architecture.md#Sistema-Contest] — Modello Contest, Rating, annotazioni
- [Source: _bmad-output/planning-artifacts/architecture.md#Frontend-Patterns] — React Query hooks, Shadcn UI, error handling
- [Source: backend/cs_clips/api/contests/contest_views.py] — ContestViewSet read-only (Story 4.1)
- [Source: backend/cs_clips/api/contests/contest_serializers.py] — ContestListOutputSerializer, ContestDetailOutputSerializer
- [Source: backend/cs_clips/api/videos/video_views.py] — VideoViewSet con annotazioni rating in get_queryset()
- [Source: backend/cs_clips/api/ratings/rating_views.py] — POST create, PATCH update rating
- [Source: frontend/src/components/rating/star-rating.tsx] — Componente stelle esistente
- [Source: frontend/src/lib/hooks/use-ratings.ts] — useCreateRating, useUpdateRating esistenti
- [Source: frontend/src/lib/api/contests.ts] — Solo getWinners, da estendere
- [Source: frontend/src/types/video.ts] — Video type con average_rating, my_rating_id, my_rating_value
- [Source: _bmad-output/implementation-artifacts/4-1-backend-contest-settimanale-endpoint-e-listing.md] — Story 4.1 completion notes

### Intelligence dalla Story 4.1 (precedente)

- **ContestViewSet consolidato**: `EndContestView` e `ContestWinnersView` migrati come `@action` — pattern da seguire per la nuova action `videos`
- **214 test backend** baseline (213 pass, 1 fail pre-esistente `test_registration_assigns_toconfirm_group`)
- **select_related('winner')** applicato in get_queryset() e winners action — pattern N+1 prevention
- **`@extend_schema`** obbligatorio su ogni action per OpenAPI
- **Dead code cleanup**: `contest_urls.py` eliminato — non creare nuovi file URL separati
- **Code review fix pattern**: H1 select_related, H2 N+1 prevention, H3 ValidationError corretto (rest_framework, non django.forms)

### Git Intelligence — Pattern recenti

Ultimi commit:
- `612f66c` — Epic 3 completo: like UI, popup overlay, spareggio like, comment markers
- Commit non pushato: Story 4.1 completata (contest listing + detail + filter + routing consolidation)

Pattern commit: prefisso `feat:` per feature, riepilogo conciso.
Suggerito: `feat: Story 4.2 — votazione contest e classifica frontend`

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

Nessun debug critico richiesto.

### Completion Notes List

- **Task 0**: Rimossi `<StarRating>`, `handleRate`, `useCreateRating`/`useUpdateRating`, import `Star` da `card-as-player.tsx` e `clip-content.tsx`. Build frontend 0 errori.
- **Task 1**: Aggiunta `@action(detail=True, url_path="videos")` su `ContestViewSet` — video con annotazioni `avg_rating`, `my_rating_id`, `my_rating_value`, `like_count`, `is_liked_by_me`, ordinati per avg_rating DESC NULLS LAST. `select_related("uploader")` per N+1 prevention. `@extend_schema` per OpenAPI. 7 nuovi test (tutti pass).
- **Task 2**: Esteso `contestsApi` con `list`, `getDetail`, `getContestVideos`. Query keys aggiunte per `contests.list`, `contests.detail`, `contests.videos`. Creato `use-contests.ts` con 3 hooks (`useContests`, `useContestDetail`, `useContestVideos`).
- **Task 3**: Riscritta pagina `/contest/` con due sezioni (Contest Attivi / Chiusi), `ContestCard` con name+tag+date+video_count, navigazione a `/contest/[id]`, `ErrorMessage`+skeleton+`EmptyState`.
- **Task 4**: Creata pagina `/contest/[id]` con header contest, griglia video card con `<StarRating>` inline, votazione create/update via `ratingsApi` diretto (no shared hooks per gestire invalidazione `contests.videos`), classifica per avg_rating DESC, trofeo vincitore, toast Sonner, `ErrorMessage`+`PageLoader`.
- **Task 5**: ruff 0 errori, build 0 errori, 221 test (220 pass, 1 fail pre-esistente noto).
- **Scelta architetturale**: Nella pagina contest detail, le mutation rating sono gestite con `useMutation` inline (non i shared hooks) per poter invalidare sia `contests.videos(contestId)` che `videos.detail(videoId)` nel `onSuccess`.

**Code Review Fix (2026-03-08):**
- **H1**: AC#5 — aggiunto `winner_title` in `ContestListOutputSerializer` + mostrato nella `ContestCard` per contest chiusi
- **H2**: `<a href>` → `<Link>` in pagina dettaglio contest per navigazione client-side
- **M1**: `select_related("uploader")` aggiunto su `winners` action (N+1 fix)
- **M2**: `@extend_schema` con parametri paginazione aggiunto su `videos` action
- **M3**: Test `test_videos_includes_rating_annotations` ora verifica anche `like_count` e `is_liked_by_me`
- **M4**: Date contest formattate con `formatShortDate()` (it-IT locale) in lista e dettaglio

### File List

**Modificati:**
- `frontend/src/components/feed/card-as-player.tsx` — rimosso StarRating import e componente
- `frontend/src/app/clip/[id]/clip-content.tsx` — rimosso StarRating, handleRate, useCreateRating, useUpdateRating, icona Star
- `backend/cs_clips/api/contests/contest_views.py` — aggiunta @action videos con annotazioni rating + select_related winners + @extend_schema videos
- `backend/cs_clips/api/contests/contest_serializers.py` — aggiunto winner_title in ContestListOutputSerializer
- `frontend/src/lib/api/contests.ts` — aggiunto list, getDetail, getContestVideos
- `frontend/src/lib/query-keys.ts` — aggiunto contests.list, detail, videos
- `frontend/src/types/contest.ts` — aggiunto video_count, winner_title, winner_detail
- `frontend/src/lib/utils.ts` — aggiunto formatShortDate()
- `frontend/src/app/(main)/contest/page.tsx` — riscritta con sezioni Attivi/Chiusi
- `backend/cs_clips/tests/test_contests_list.py` — aggiunti 7 test per @action videos

**Creati:**
- `frontend/src/lib/hooks/use-contests.ts` — useContests, useContestDetail, useContestVideos
- `frontend/src/app/(main)/contest/[id]/page.tsx` — pagina dettaglio contest con votazione e classifica

### Change Log

- 2026-03-08: Story 4.2 implementata — votazione contest 1-5 stelle, classifica per media voti, pagina lista contest (attivi+chiusi), pagina dettaglio contest con votazione e classifica, stelle rimosse dal feed e clip detail
- 2026-03-08: Code review fix — 2 HIGH + 4 MEDIUM risolti (winner_title, Link nav, N+1 winners, @extend_schema, test assertions, date formatting)
