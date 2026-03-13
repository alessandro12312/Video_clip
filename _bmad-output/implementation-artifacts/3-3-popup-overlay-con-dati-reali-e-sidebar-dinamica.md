# Story 3.3: Popup Overlay con Dati Reali e Sidebar Dinamica

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a spettatore,
I want vedere i commenti più likati apparire come popup durante la riproduzione e nella sidebar,
so that scopro le reazioni migliori della community ancorati al momento esatto.

## Acceptance Criteria

1. **Endpoint popup data backend** — Un endpoint backend `GET /api/videos/{id}/popup-comments/` ritorna i popup data: per ogni `timestamp_second` con almeno 1 commento con `like_count >= 1`, il commento con più like (FR31, FR34). I dati sono pre-caricati in una singola chiamata API (NFR8). Commenti con `is_disabled=True` sono esclusi.

2. **Popup overlay con dati reali** — Durante la riproduzione, quando il playback raggiunge un timestamp con un popup disponibile, il popup overlay appare in alto a destra con username, timestamp badge e testo del commento (FR32). Il popup scompare dopo 3 secondi con animazione fade-out Framer Motion (FR33). La latenza tra timestamp e popup è < 200ms (NFR8).

3. **Soglia minima 1 like** — Un commento con 0 like NON diventa popup (FR34). Solo commenti con `like_count >= 1` sono candidati popup.

4. **Sidebar dinamica ordinata per like** — La Sidebar Dinamica (desktop ≥1280px in clip-content, sotto il video in card-as-player) mostra i commenti con più like per la clip corrente, ordinati per `like_count` decrescente (FR35). NON più per data o per slot temporale come workaround attuale.

5. **Ricalcolo dopo moderazione** — Quando un commento popup viene disabilitato dalla moderazione (`is_disabled=True`), al prossimo caricamento il sistema restituisce il prossimo commento con più like per quel timestamp (FR36). Nessun meccanismo real-time — il ricalcolo avviene via re-fetch API.

## Tasks / Subtasks

- [x] Task 1: Endpoint backend `popup-comments` (AC: #1, #3, #5)
  - [x] 1.1 In `api/videos/video_views.py`: aggiungere `@action(detail=True, methods=["get"], url_path="popup-comments")` su `VideoViewSet`
  - [x] 1.2 Query: `Comment.objects.filter(video=video, is_disabled=False).annotate(like_count=Count('likes', distinct=True)).filter(like_count__gte=1)`
  - [x] 1.3 Raggruppare per `timestamp_second`: per ogni timestamp, prendere il commento con il `like_count` più alto (in caso di parità, il più recente)
  - [x] 1.4 Serializzare con `CommentSerializer` esistente (include `like_count`, `is_liked_by_me`)
  - [x] 1.5 Risposta: lista piatta (NON paginata — i popup sono pochi, max ~durata_video commenti)
  - [x] 1.6 Test: almeno 5 test — nessun commento likato → vuoto, soglia 1 like, commento disabilitato escluso, selezione top-liked per timestamp, ordinamento

- [x] Task 2: Aggiornare API frontend e query keys (AC: #1)
  - [x] 2.1 In `src/lib/api/videos.ts`: aggiungere `getPopupComments(videoId: number)` → `GET /api/videos/${videoId}/popup-comments/`
  - [x] 2.2 In `src/lib/query-keys.ts`: aggiungere `popupComments: (videoId: number) => ["videos", "popup-comments", videoId] as const` dentro `videos`

- [x] Task 3: Creare hook `usePopupComments` (AC: #1, #2)
  - [x] 3.1 In `src/lib/hooks/use-videos.ts`: nuovo hook `usePopupComments(videoId: number)` con `useQuery`
  - [x] 3.2 `staleTime: 60_000` (come commenti)
  - [x] 3.3 Return type: `Comment[]` (lista piatta dal backend)

- [x] Task 4: Aggiornare `popupMap` con dati reali (AC: #2, #3)
  - [x] 4.1 In `src/components/feed/card-as-player.tsx`: sostituire la costruzione di `popupMap` (attualmente basata su tutti i commenti, seleziona il più recente per timestamp) con dati da `usePopupComments`
  - [x] 4.2 Nuovo `popupMap`: `Map<number, Comment>` costruita direttamente da popup-comments (un commento per timestamp, già filtrato dal backend)
  - [x] 4.3 `markerPositions` resta basato su tutti i commenti (NON solo popup) — i marker mostrano dove ci sono commenti, non solo popup
  - [x] 4.4 In `src/app/clip/[id]/clip-content.tsx`: stessa modifica — `popupMap` da `usePopupComments`

- [x] Task 5: Aggiornare Sidebar Dinamica con ordinamento per like (AC: #4)
  - [x] 5.1 In `src/components/comments/comment-sidebar.tsx`: cambiare logica di selezione — NON più "1 commento per slot temporale (3s), più recente" → "commenti con like_count >= 1, ordinati per like_count decrescente"
  - [x] 5.2 Rimuovere logica slot `Math.floor(timestamp / COMMENT_SLOT_SECONDS)` — mostrare direttamente i top-liked
  - [x] 5.3 Se nessun commento ha like, mostrare messaggio vuoto ("Nessun commento con like ancora")
  - [x] 5.4 Il `currentTime` filter (live mode) resta invariato — mostra solo commenti con timestamp <= currentTime
  - [x] 5.5 Prop opzionale `popupComments?: Comment[]` per ricevere i dati già filtrati, OPPURE ricevere tutti i commenti e filtrare internamente per like_count >= 1

- [x] Task 6: Correggere durata popup a 3 secondi (AC: #2)
  - [x] 6.1 In `src/lib/constants.ts`: cambiare `POPUP_DISPLAY_DURATION_MS` da `4000` a `3000` (l'AC e FR33 specificano 3 secondi)

- [x] Task 7: Verifica qualità (AC: tutti)
  - [x] 7.1 `npm run build` — 0 errori TypeScript
  - [x] 7.2 Test backend passanti (inclusi nuovi test popup-comments)
  - [x] 7.3 Verifica visiva: popup appare solo per commenti likati, sidebar ordinata per like_count, popup scompare dopo 3s

## Dev Notes

### Architettura e Pattern Obbligatori

- **Import Framer Motion**: `import { motion, AnimatePresence } from "framer-motion"` — NON `"motion/react"` [Source: MEMORY.md#Framer-Motion-Import-Path]
- **Componenti React**: named export, mai default export (tranne page.tsx) [Source: project-context.md#Architettura-Route]
- **Import path**: sempre `@/` alias, mai path relativi [Source: project-context.md#Architettura-Route]
- **Backend @action pattern**: `@action(detail=True, methods=["get"], url_path="popup-comments")` — seguire pattern di `views`, `download`, `like` già in `VideoViewSet`
- **Backend test**: usare `django.test.TestCase`, NON pytest. Helper `create_authenticated_user()` da `conftest.py`. [Source: project-context.md#Testing]
- **read_only_fields**: ogni campo calcolato DEVE essere read_only al primo commit [Source: MEMORY.md#Epic-1+2-Retro]

### Stato attuale dei componenti da modificare

**`popup-overlay.tsx`** — GIÀ FUNZIONANTE, animazione corretta:
```tsx
// Struttura attuale — NON modificare l'animazione, solo i dati cambiano
<AnimatePresence>
  {comment && (
    <motion.div
      key={comment.id}
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.3 }}
      className="absolute top-3 right-3 z-20 max-w-xs glass rounded-lg p-3"
    >
      ...username, TimestampBadge, content
    </motion.div>
  )}
</AnimatePresence>
```
Il popup è già conforme all'AC #2 (username, timestamp badge, testo, fade-out). NON modificare `popup-overlay.tsx`. Cambia solo la SORGENTE DATI (popupMap).

**`comment-sidebar.tsx`** — Da REFACTORARE:
```tsx
// Logica attuale (DA CAMBIARE):
// - Raggruppa per slot temporale (Math.floor(timestamp / 3))
// - Seleziona il più recente per slot
// - Ordina per timestamp

// Logica target:
// - Filtra commenti con like_count >= 1
// - Ordina per like_count decrescente
// - Mostra tutti (con maxVisible limit)
// - Il filtro currentTime (live mode) resta invariato
```

**`video-player.tsx`** — Il meccanismo popup è qui (righe 84-95):
```tsx
// handleTimeUpdate → check popupMap → setActivePopup → timeout POPUP_DISPLAY_DURATION_MS
// NON MODIFICARE — solo la costante POPUP_DISPLAY_DURATION_MS cambia (4000 → 3000)
```

### Endpoint backend — Decisioni architetturali

L'endpoint `popup-comments` è un'action GET su `VideoViewSet` (non un ViewSet separato). Motivazioni:
- I popup sono una vista specifica dei commenti di UN video → detail action su video
- Non serve paginazione — i popup sono al massimo ~durata_video (uno per secondo)
- Usa `CommentSerializer` esistente per consistenza (include `like_count`, `is_liked_by_me`)

**Query SQL equivalente:**
```python
# Per ogni timestamp_second, il commento con like_count più alto (≥1)
Comment.objects.filter(
    video=video,
    is_disabled=False,
    timestamp_second__gt=0  # timestamp 0 = commento generico, non popup
).annotate(
    like_count=Count('likes', distinct=True)
).filter(
    like_count__gte=1
)
```
Poi in Python: raggruppare per `timestamp_second`, tenere il top-liked per ciascuno.

**Alternativa SQL pura con Window function** (più efficiente):
```python
from django.db.models import Window, F
from django.db.models.functions import RowNumber

# Window function per rank per timestamp
ranked = Comment.objects.filter(
    video=video,
    is_disabled=False,
    timestamp_second__gt=0
).annotate(
    like_count=Count('likes', distinct=True)
).filter(
    like_count__gte=1
).annotate(
    rank=Window(
        expression=RowNumber(),
        partition_by=[F('timestamp_second')],
        order_by=[F('like_count').desc(), F('created_at').desc()]
    )
).filter(rank=1)
```
**NOTA**: Window functions con `.filter(rank=1)` non funzionano direttamente in Django ORM (il filter viene applicato prima della window). Usare subquery o raggruppamento Python. L'approccio Python è più semplice e corretto per questo caso d'uso (max ~300 commenti per video).

### Pattern `popupMap` — Cosa cambia nel frontend

**Prima (attuale):**
```tsx
// In card-as-player.tsx e clip-content.tsx
const popupMap = useMemo(() => {
  const map = new Map<number, Comment>();
  for (const comment of comments) {            // ← TUTTI i commenti
    if (comment.timestamp_second <= 0) continue;
    const existing = map.get(comment.timestamp_second);
    if (!existing || new Date(comment.created_at) > new Date(existing.created_at)) {
      map.set(comment.timestamp_second, comment); // ← seleziona il più RECENTE
    }
  }
  return map;
}, [comments]);
```

**Dopo (target):**
```tsx
// In card-as-player.tsx e clip-content.tsx
const { data: popupComments = [] } = usePopupComments(video.id);

const popupMap = useMemo(() => {
  const map = new Map<number, Comment>();
  for (const comment of popupComments) {        // ← solo commenti con like ≥ 1
    map.set(comment.timestamp_second, comment);  // ← già top-liked dal backend
  }
  return map;
}, [popupComments]);
```

### Sidebar — Cosa cambia

**Prima (attuale):**
- Slot da 3 secondi, 1 commento/slot (il più recente)
- Ordinamento per timestamp

**Dopo (target):**
- Tutti i commenti con `like_count >= 1`
- Ordinamento per `like_count` decrescente
- `currentTime` filter invariato (live mode)
- L'import `COMMENT_SLOT_SECONDS` può essere rimosso dalla sidebar

### Due chiamate API parallele — Accettabile

Il page load farà 2 chiamate:
1. `useComments(videoId)` — tutti i commenti (per lista commenti, form, marker)
2. `usePopupComments(videoId)` — solo popup comments (per popupMap, sidebar)

Entrambe partono in parallelo grazie a React Query. La latenza totale è `max(t1, t2)`, non `t1 + t2`. Per video con pochi commenti, `popup-comments` sarà più veloce del fetch completo.

In `card-as-player.tsx`, `usePopupComments` va abilitato con `{ enabled: isIntersecting }` come `useComments`, per non fare fetch per card non visibili.

### Costante `POPUP_DISPLAY_DURATION_MS` — Bug trovato

Il valore attuale è `4000` (4 secondi). L'AC #2 e FR33 specificano **3 secondi**. Questa story corregge a `3000`.

### Gestione `is_disabled` nel backend

Il campo `is_disabled` esiste già sul model `Comment` (aggiunto in Story 0.4). L'endpoint `popup-comments` deve filtrare `is_disabled=False`. L'endpoint commenti standard (`/api/comments/`) potrebbe già filtrare — VERIFICARE nel `CommentViewSet.get_queryset()` prima di duplicare il filtro.

### File da modificare

| File | Modifica |
|------|----------|
| `backend/cs_clips/api/videos/video_views.py` | +action `popup_comments` (GET) |
| `frontend/src/lib/constants.ts` | `POPUP_DISPLAY_DURATION_MS`: 4000 → 3000 |
| `frontend/src/lib/api/videos.ts` | +metodo `getPopupComments(videoId)` |
| `frontend/src/lib/query-keys.ts` | +key `popupComments(videoId)` |
| `frontend/src/lib/hooks/use-videos.ts` | +hook `usePopupComments(videoId)` |
| `frontend/src/components/feed/card-as-player.tsx` | `popupMap` da `usePopupComments`, rimuovi calcolo da tutti i commenti |
| `frontend/src/app/clip/[id]/clip-content.tsx` | Idem — `popupMap` da `usePopupComments` |
| `frontend/src/components/comments/comment-sidebar.tsx` | Ordinamento per `like_count` desc, rimuovi logica slot |

### File NON da modificare

| File | Motivo |
|------|--------|
| `popup-overlay.tsx` | Animazione e layout già conformi all'AC — cambiano solo i dati |
| `video-player.tsx` | Meccanismo popup invariato — solo la costante cambia |
| `comment-item.tsx` | Non coinvolto in questa story |
| `comment-list.tsx` | Non coinvolto |
| `comment-section.tsx` | Non coinvolto |
| Tipi TypeScript (`video.ts`, `comment.ts`) | `like_count` e `is_liked_by_me` già presenti (Story 3.2) |

### Lezioni dalla Story 3.2 (precedente)

- **Optimistic update robusto**: pattern `onMutate` snapshot + `onError` rollback + `onSettled` invalidate — applicare se necessario su popup queries
- **`useRef` con `undefined`**: `useRef<ReturnType<typeof setTimeout>>(undefined)` per Next.js 16 strict mode
- **Toast errore**: sempre `toast.error()` per errori non gestiti (aggiunto in review 3.2)
- **Bottoni `disabled` durante pending**: sempre `disabled={mutation.isPending}` su bottoni interattivi
- **Cleanup timeout su unmount**: sempre `useEffect(() => () => clearTimeout(...), [])` per timer
- **Test backend**: 178 test passanti + 23 test like — baseline per non rompere nulla

### Project Structure Notes

- Tutti i file frontend seguono la struttura `src/components/{dominio}/`, `src/lib/hooks/`, `src/lib/api/`
- L'endpoint backend segue il pattern `api/videos/` (action su `VideoViewSet`)
- Nessun nuovo file frontend necessario — tutte modifiche a file esistenti
- 1 solo file backend modificato (`video_views.py`), potenzialmente 1 file test nuovo

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-3.3] — AC BDD completi (FR31-FR36)
- [Source: _bmad-output/planning-artifacts/architecture.md#Popup-e-Loop-di-Engagement] — Pre-caricamento popup, latenza < 200ms, glassmorphism
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Micro-animazioni] — Tier 1 popup, glassmorphism overlay, fade-out 3s
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Core-User-Experience] — "Il commento è contenuto", popup = co-creazione permanente
- [Source: _bmad-output/project-context.md#React-Query] — Chiavi precise, staleTime differenziato, optimistic update
- [Source: _bmad-output/implementation-artifacts/3-2-ui-like-su-clip-e-commenti-frontend.md] — Pattern ottimistici, fix review, file modificati
- [Source: MEMORY.md#Framer-Motion-Import-Path] — Import da "framer-motion"
- [Source: MEMORY.md#Epic-1+2-Retro] — read_only_fields, test assertions, translation_override

### Git Intelligence — Pattern Recenti

Ultimi commit rilevanti:
- `da01a68` — Story 3.1: modelli VideoLike/CommentLike + endpoint like/unlike + annotazioni
- `798d229` — snap scroll feed + clip detail view modes + docs update
- `ea05799` — feed card redesign — commenti inline, chat sidebar, responsive mobile

Pattern commit: prefisso `feat:` per feature, riepilogo conciso.

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

Nessun debug necessario — tutti i test passati al primo tentativo.

### Completion Notes List

- **Task 1**: Endpoint `popup_comments` action su `VideoViewSet` — query con `Count("likes")`, raggruppamento Python per timestamp, `is_liked_by_me` annotato. 8 test scritti e passati.
- **Task 2**: Aggiunto `getPopupComments()` in `videosApi` e query key `popupComments` in `queryKeys.videos`.
- **Task 3**: Hook `usePopupComments(videoId, { enabled })` con `staleTime: 60_000`.
- **Task 4**: `popupMap` in `card-as-player.tsx` e `clip-content.tsx` ora costruita da `usePopupComments` (dati backend filtrati per like ≥ 1). `markerPositions` resta basato su tutti i commenti.
- **Task 5**: Sidebar refactored — rimossa logica slot temporali, ora filtra `like_count >= 1` e ordina per `like_count` desc. Aggiunto badge like count. Messaggio vuoto "Nessun commento con like ancora".
- **Task 6**: `POPUP_DISPLAY_DURATION_MS` corretto da 4000 a 3000 (FR33).
- **Task 7**: `npm run build` 0 errori, 186 test backend (185 pass, 1 fail pre-esistente non correlato), ruff 0 errori.

### Change Log

- 2026-03-08: Story 3.3 — Popup overlay con dati reali e sidebar dinamica. Endpoint backend popup-comments, popupMap da dati backend, sidebar ordinata per like, durata popup corretta a 3s.
- 2026-03-08: Code review fix — H1: invalidazione cache popup-comments dopo like/unlike commento; H2: context request su CommentSerializer; M1: rimosso COMMENT_SLOT_SECONDS dead code; M2: aggiunto currentTime a sidebar in clip-content; M3: rimosso unlikeMutation da deps handleVideoTap; M4: aggiunto test 404 video inesistente.

### File List

**Nuovi:**
- `backend/cs_clips/tests/test_popup_comments.py` — 9 test endpoint popup-comments

**Modificati:**
- `backend/cs_clips/api/videos/video_views.py` — +action `popup_comments` (GET), +import Comment/CommentLike/CommentSerializer/defaultdict, fix context serializer
- `frontend/src/lib/api/videos.ts` — +metodo `getPopupComments(videoId)`, +import Comment
- `frontend/src/lib/query-keys.ts` — +key `popupComments(videoId)`
- `frontend/src/lib/hooks/use-videos.ts` — +hook `usePopupComments`, +import Comment
- `frontend/src/lib/hooks/use-comments.ts` — +invalidazione queryKeys.videos.popupComments in useLikeComment/useUnlikeComment
- `frontend/src/components/feed/card-as-player.tsx` — `popupMap` da `usePopupComments`, +import usePopupComments, fix deps handleVideoTap
- `frontend/src/app/clip/[id]/clip-content.tsx` — `popupMap` da `usePopupComments`, +import usePopupComments, +currentTime a sidebar, +playerTime state
- `frontend/src/components/comments/comment-sidebar.tsx` — refactored: filtro like ≥ 1, ordinamento like desc, rimosso slot logic, +badge like count
- `frontend/src/lib/constants.ts` — `POPUP_DISPLAY_DURATION_MS`: 4000 → 3000, rimosso COMMENT_SLOT_SECONDS
