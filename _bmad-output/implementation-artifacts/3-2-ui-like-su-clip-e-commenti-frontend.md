# Story 3.2: UI Like su Clip e Commenti Frontend

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utente registrato,
I want mettere e togliere like a clip e commenti con feedback visivo immediato,
so that posso esprimere apprezzamento e contribuire alla promozione dei migliori commenti.

## Acceptance Criteria

1. **Like su clip (bottone)** — Click sul bottone like nella card feed e nella pagina dettaglio registra il like con optimistic update (FR28). Il contatore `like_count` si aggiorna immediatamente. In caso di errore, rollback automatico.

2. **Unlike su clip** — Click sul bottone like di una clip già likata rimuove il like (toggle). Il contatore si decrementa con optimistic update.

3. **Like su commento** — Click sul bottone like su un commento registra il like con optimistic update (FR27). Il contatore `like_count` sul commento si aggiorna immediatamente.

4. **Unlike su commento** — Click sul bottone like di un commento già likato rimuove il like (toggle). Il contatore si decrementa.

5. **Double-tap su video** — Double-tap/double-click sul video registra un like con la stessa logica del bottone (FR28). Un'animazione cuore appare brevemente al centro del video come feedback visivo. Se già likato, il double-tap non fa nulla (non toglie il like).

6. **Hook frontend** — `useLikeVideo` e `useUnlikeVideo` in `use-videos.ts` con optimistic update pattern completo (onMutate/onError rollback/onSettled invalidate). `useLikeComment` e `useUnlikeComment` in `use-comments.ts` con lo stesso pattern.

7. **Tipi e query keys** — I tipi `Video` e `Comment` in `src/types/` includono `like_count: number` e `is_liked_by_me: boolean`. Le query keys per invalidazione sono definite in `query-keys.ts`.

8. **API endpoints frontend** — `videos.like(id)` (POST), `videos.unlike(id)` (DELETE), `comments.like(id)` (POST), `comments.unlike(id)` (DELETE) in moduli API.

## Tasks / Subtasks

- [x] Task 1: Aggiornare tipi TypeScript (AC: #7)
  - [x] 1.1 Aggiungere `like_count: number` e `is_liked_by_me: boolean` a interfaccia `Video` in `src/types/video.ts`
  - [x] 1.2 Aggiungere `like_count: number` e `is_liked_by_me: boolean` a interfaccia `Comment` in `src/types/comment.ts`

- [x] Task 2: Aggiungere endpoint API frontend (AC: #8)
  - [x] 2.1 In `src/lib/api/videos.ts`: aggiungere `like(id: number)` → `POST /api/videos/${id}/like/` e `unlike(id: number)` → `DELETE /api/videos/${id}/like/`
  - [x] 2.2 In `src/lib/api/comments.ts`: aggiungere `like(id: number)` → `POST /api/comments/${id}/like/` e `unlike(id: number)` → `DELETE /api/comments/${id}/like/`

- [x] Task 3: Aggiornare query keys (AC: #7)
  - [x] 3.1 NON servono nuove query keys dedicate — i like invalidano le query keys esistenti: `videos.detail(id)`, `videos.all`, `videos.list(page)`, `comments.byVideo(videoId)`. Seguire pattern follow/unfollow.

- [x] Task 4: Creare hook useLikeVideo/useUnlikeVideo (AC: #6)
  - [x] 4.1 In `src/lib/hooks/use-videos.ts`: `useLikeVideo()` con optimistic update su detail + liste
  - [x] 4.2 In `src/lib/hooks/use-videos.ts`: `useUnlikeVideo()` con optimistic update su detail + liste
  - [x] 4.3 Pattern: `onMutate` → cancel queries, snapshot, update cache → `onError` rollback → `onSettled` invalidate

- [x] Task 5: Creare hook useLikeComment/useUnlikeComment (AC: #6)
  - [x] 5.1 In `src/lib/hooks/use-comments.ts`: `useLikeComment(videoId)` con optimistic update su `comments.byVideo(videoId)`
  - [x] 5.2 In `src/lib/hooks/use-comments.ts`: `useUnlikeComment(videoId)` con optimistic update
  - [x] 5.3 Attenzione: i commenti sono in `useInfiniteQuery` con pagine — l'optimistic update deve cercare il commento in tutte le pagine

- [x] Task 6: Attivare bottone like su clip nel feed (AC: #1, #2)
  - [x] 6.1 In `src/components/feed/card-as-player.tsx`: sostituire il bottone Heart disabilitato (righe ~306-312) con bottone funzionale
  - [x] 6.2 Stato visivo: Heart pieno rosso (`fill-current text-red-500`) se `is_liked_by_me`, outline se no
  - [x] 6.3 Mostrare `like_count` accanto all'icona
  - [x] 6.4 onClick: chiama `likeMutation.mutate(videoId)` o `unlikeMutation.mutate(videoId)` in base a `is_liked_by_me`

- [x] Task 7: Attivare bottone like su clip nella pagina dettaglio (AC: #1, #2)
  - [x] 7.1 In `src/app/clip/[id]/clip-content.tsx`: sostituire il bottone Heart disabilitato (righe ~283-292) con bottone funzionale
  - [x] 7.2 Stesso pattern visivo e logica di Task 6

- [x] Task 8: Aggiungere bottone like sui commenti (AC: #3, #4)
  - [x] 8.1 In `src/components/comments/comment-item.tsx`: aggiungere bottone Heart accanto alla data/delete
  - [x] 8.2 Stato visivo: Heart pieno rosso se `is_liked_by_me`, outline se no
  - [x] 8.3 Mostrare `like_count` se > 0
  - [x] 8.4 onClick: toggle like/unlike
  - [x] 8.5 Il componente riceve `videoId` come prop (necessario per invalidazione query comments.byVideo)

- [x] Task 9: Double-tap like su video (AC: #5)
  - [x] 9.1 Creare componente `DoubleTapLike` wrapper (o logica inline) — detect double-tap/double-click
  - [x] 9.2 Se video NON è già likato → chiama `likeMutation.mutate(videoId)`
  - [x] 9.3 Se video già likato → nessuna azione (double-tap aggiunge solo, non toglie)
  - [x] 9.4 Animazione cuore: Framer Motion `AnimatePresence` + `motion.div` con scale 0→1.2→0 e opacity 1→0, durata ~800ms
  - [x] 9.5 Applicare in `card-as-player.tsx` e `clip-content.tsx`
  - [x] 9.6 Distinguere double-tap da single-tap (play/pause) con timer 300ms

- [x] Task 10: Verifica qualità (AC: tutti)
  - [x] 10.1 `npm run build` — 0 errori TypeScript
  - [x] 10.2 Verifica visiva: like su card feed, like su pagina dettaglio, like su commento, double-tap animazione
  - [x] 10.3 Verifica optimistic update: like/unlike immediato, rollback su errore rete

## Dev Notes

### Architettura e Pattern Obbligatori

- **Import Framer Motion**: `import { motion, AnimatePresence } from "framer-motion"` — NON `"motion/react"` [Source: MEMORY.md#Framer-Motion-Import-Path]
- **Componenti React**: named export, mai default export (tranne page.tsx) [Source: project-context.md#Architettura-Route]
- **Import path**: sempre `@/` alias, mai path relativi [Source: project-context.md#Architettura-Route]
- **Icone**: `Heart` da `lucide-react` — già usata nel codebase come placeholder

### Backend già pronto (Story 3.1 completata)

Gli endpoint backend sono **già implementati e testati** (23 test):
- `POST /api/videos/{id}/like/` → 201 (like aggiunto)
- `DELETE /api/videos/{id}/like/` → 204 (like rimosso)
- `POST /api/comments/{id}/like/` → 201
- `DELETE /api/comments/{id}/like/` → 204
- Like duplicato → 409 `{code, detail}` (gestito da error handler centralizzato)
- Unlike inesistente → 404

I campi `like_count` (intero) e `is_liked_by_me` (booleano) sono **già presenti** nelle risposte API di video e commenti. Il frontend attualmente li ignora perché i tipi TypeScript non li dichiarano.

### Placeholder UI già esistenti — Sostituire, NON creare da zero

Due bottoni Heart **disabilitati** esistono già nel codebase:

**`src/components/feed/card-as-player.tsx` (~riga 306-312):**
```tsx
<Button variant="ghost" size="sm"
  className="text-muted-foreground hover:text-red-500 h-7 px-2 opacity-40"
  disabled title="Mi piace (in arrivo)">
  <Heart className="h-3.5 w-3.5 sm:mr-1" />
  <span className="hidden sm:inline text-xs">Mi piace</span>
</Button>
```

**`src/app/clip/[id]/clip-content.tsx` (~riga 283-292):**
Stesso identico pattern. Entrambi da sostituire con versione funzionale.

**`src/components/comments/comment-item.tsx`:**
Nessun bottone like — da aggiungere ex novo accanto a data/delete.

### Pattern Optimistic Update — Seguire follow/unfollow

Il pattern optimistic update è già stabilito in `use-users.ts` (follow/unfollow). Applicare lo stesso schema:

```tsx
// Pattern da seguire (da use-users.ts)
export function useLikeVideo() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (videoId: number) => videosApi.like(videoId),
    onMutate: async (videoId) => {
      // 1. Cancel queries in volo
      await queryClient.cancelQueries({ queryKey: queryKeys.videos.detail(videoId) });
      // 2. Snapshot per rollback
      const previous = queryClient.getQueryData(queryKeys.videos.detail(videoId));
      // 3. Optimistic update
      queryClient.setQueryData(queryKeys.videos.detail(videoId), (old: Video | undefined) =>
        old ? { ...old, like_count: old.like_count + 1, is_liked_by_me: true } : old
      );
      return { previous };
    },
    onError: (_err, videoId, context) => {
      // 4. Rollback su errore
      if (context?.previous) {
        queryClient.setQueryData(queryKeys.videos.detail(videoId), context.previous);
      }
    },
    onSettled: (_data, _err, videoId) => {
      // 5. Invalidate per re-sync col server
      queryClient.invalidateQueries({ queryKey: queryKeys.videos.detail(videoId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.videos.all });
    },
  });
}
```

**ATTENZIONE optimistic update su liste feed**: il feed usa `useInfiniteQuery`. Per aggiornare optimisticamente il like_count nelle card del feed, iterare `data.pages[].results[]` cercando il video per ID. Se troppo complesso, è accettabile aggiornare solo il detail e invalidare le liste in `onSettled`.

**ATTENZIONE optimistic update su commenti**: `useComments` ritorna dati paginati (infinite query). L'optimistic update deve cercare il commento in `data.pages[].results[]` per aggiornare `like_count` e `is_liked_by_me`. Il `videoId` è necessario per la query key `comments.byVideo(videoId)`.

### Pattern Double-Tap — Distinguere da Play/Pause

Il video player attualmente ha un click handler per play/pause. Il double-tap deve coesistere:

```tsx
// Pattern raccomandato
const lastTapRef = useRef<number>(0);
const tapTimerRef = useRef<ReturnType<typeof setTimeout>>();

function handleTap() {
  const now = Date.now();
  if (now - lastTapRef.current < 300) {
    // Double tap → like
    clearTimeout(tapTimerRef.current);
    if (!video.is_liked_by_me) {
      likeMutation.mutate(video.id);
    }
    setShowHeartAnimation(true);
  } else {
    // Single tap → delay per escludere double tap, poi play/pause
    tapTimerRef.current = setTimeout(() => {
      togglePlayPause();
    }, 300);
  }
  lastTapRef.current = now;
}
```

**NOTA**: il delay di 300ms sul play/pause è un trade-off UX accettato (Instagram/TikTok fanno lo stesso). Applicare SOLO sul container video, NON sui controlli player.

### Animazione Cuore — Framer Motion Tier 1

L'animazione cuore al double-tap è classificata come **Tier 1 (significato)** nel design system UX. Pattern:

```tsx
<AnimatePresence>
  {showHeartAnimation && (
    <motion.div
      className="absolute inset-0 flex items-center justify-center pointer-events-none z-50"
      initial={{ scale: 0, opacity: 1 }}
      animate={{ scale: 1.2, opacity: 1 }}
      exit={{ scale: 1.5, opacity: 0 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
      onAnimationComplete={() => setShowHeartAnimation(false)}
    >
      <Heart className="h-20 w-20 text-red-500 fill-current drop-shadow-lg" />
    </motion.div>
  )}
</AnimatePresence>
```

Posizionare all'interno del container `relative` del video player. Il cuore deve essere centrato e sovrapposto al video.

### Stato Visivo Bottone Like

```tsx
// Heart pieno rosso = likato, outline = non likato
<Button
  variant="ghost"
  size="sm"
  className={cn(
    "h-7 px-2",
    video.is_liked_by_me
      ? "text-red-500 hover:text-red-400"
      : "text-muted-foreground hover:text-red-500"
  )}
  onClick={() => video.is_liked_by_me
    ? unlikeMutation.mutate(video.id)
    : likeMutation.mutate(video.id)
  }
>
  <Heart className={cn("h-3.5 w-3.5 sm:mr-1", video.is_liked_by_me && "fill-current")} />
  <span className="hidden sm:inline text-xs">{video.like_count}</span>
</Button>
```

**Stessa logica per commenti** — ma mostrare `like_count` solo se > 0.

### Query Keys — NON creare chiavi nuove per like

I like non sono una risorsa con propria lista/dettaglio. L'azione like/unlike invalida le risorse esistenti:
- Like video → invalida `videos.detail(id)` + `videos.all` (per aggiornare like_count nelle card feed)
- Like commento → invalida `comments.byVideo(videoId)` (per aggiornare like_count nei commenti)

### File da modificare (nessun file nuovo)

| File | Modifica |
|------|----------|
| `frontend/src/types/video.ts` | +2 campi: `like_count`, `is_liked_by_me` |
| `frontend/src/types/comment.ts` | +2 campi: `like_count`, `is_liked_by_me` |
| `frontend/src/lib/api/videos.ts` | +2 metodi: `like()`, `unlike()` |
| `frontend/src/lib/api/comments.ts` | +2 metodi: `like()`, `unlike()` |
| `frontend/src/lib/hooks/use-videos.ts` | +2 hook: `useLikeVideo()`, `useUnlikeVideo()` |
| `frontend/src/lib/hooks/use-comments.ts` | +2 hook: `useLikeComment()`, `useUnlikeComment()` |
| `frontend/src/components/feed/card-as-player.tsx` | Sostituire Heart disabilitato + aggiungere double-tap |
| `frontend/src/app/clip/[id]/clip-content.tsx` | Sostituire Heart disabilitato + aggiungere double-tap |
| `frontend/src/components/comments/comment-item.tsx` | Aggiungere bottone like con contatore |

### Lezioni dalla Story 3.1 (precedente)

- Pattern `@action(methods=["post", "delete"], url_path="like")` con branching su `request.method` — gli endpoint backend sono già solidi
- `like_count` usa `Count('likes', distinct=True)` — il valore ritornato è sempre accurato
- `is_liked_by_me` usa `Exists()` — booleano preciso per utente autenticato, `false` per anonimi (SSR)
- L'error handler centralizzato mappa IntegrityError → 409 — il frontend può ricevere 409 se tenta un like duplicato (es. race condition su double-tap veloce) → gestire silenziosamente in `onError`

### Gestione errore 409 (like duplicato)

Se il backend ritorna 409 (like già presente), NON mostrare errore all'utente. Gestire silenziosamente:
```tsx
onError: (err, videoId, context) => {
  // Se 409, il like esiste già sul server — non rollbackare
  if (err?.response?.status === 409) return;
  // Altrimenti rollback
  if (context?.previous) {
    queryClient.setQueryData(queryKeys.videos.detail(videoId), context.previous);
  }
},
```

### Project Structure Notes

- Tutti i file modificati sono nel frontend — nessuna modifica backend
- Nessun file nuovo necessario — tutte modifiche a file esistenti
- Struttura conforme a `src/components/{dominio}/`, `src/lib/hooks/`, `src/lib/api/`, `src/types/`
- Nessun conflitto con struttura esistente

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-3.2] — AC BDD completi
- [Source: _bmad-output/planning-artifacts/architecture.md#Implementation-Patterns] — Optimistic update template, API module template, mutation pattern
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#UX-Pattern-Analysis] — Doppio tap like (Instagram/TikTok), micro-animazioni Tier 1, toast feedback
- [Source: _bmad-output/project-context.md#React-Query] — Chiavi precise, optimistic update, staleTime
- [Source: _bmad-output/project-context.md#Regole-Frontend] — Named export, @/ alias, "use client", Framer Motion path
- [Source: _bmad-output/implementation-artifacts/3-1-modelli-videolike-e-commentlike-backend.md] — Endpoint backend, formato risposta, pattern annotazioni
- [Source: MEMORY.md#Framer-Motion-Import-Path] — Import da "framer-motion", NON "motion/react"
- [Source: MEMORY.md#Epic-1+2-Retro] — Error handling frontend obbligatorio, test assertions complete

### Git Intelligence — Pattern Recenti

Ultimo commit rilevante:
- `da01a68` — Story 3.1: modelli VideoLike/CommentLike + endpoint like/unlike + annotazioni (backend completato)

Pattern commit: prefisso `feat:` per feature, riepilogo conciso.

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Fix `useRef` TypeScript strict mode: `useRef<ReturnType<typeof setTimeout>>()` → `useRef<ReturnType<typeof setTimeout>>(undefined)` (Next.js 16 strict)

### Completion Notes List

- Tipi `Video` e `Comment` aggiornati con `like_count` e `is_liked_by_me`
- Endpoint API `like()`/`unlike()` aggiunti a `videosApi` e `commentsApi`
- Query keys esistenti riutilizzate (nessuna nuova chiave) — invalidazione su `videos.all`, `videos.detail(id)`, `comments.byVideo(videoId)`
- Hook `useLikeVideo`/`useUnlikeVideo` con optimistic update su detail + liste infinite (iterazione `pages[].results[]`)
- Hook `useLikeComment`/`useUnlikeComment` con optimistic update su array piatto `Comment[]`
- Gestione silente errore 409 (like duplicato) — nessun rollback
- Bottone like funzionale nel feed (card-as-player) e nella pagina dettaglio (clip-content) — Heart pieno rosso se likato, outline se no
- Bottone like su commenti (`comment-item.tsx`) — `videoId` prop aggiunto nella catena `CommentSection` → `CommentList` → `CommentItem`
- Double-tap su video: overlay trasparente sopra il player, timer 300ms per distinguere single-tap (play/pause) da double-tap (like)
- Animazione cuore Framer Motion: `AnimatePresence` + `motion.div` scale 0→1.2→0, durata 800ms
- `VideoPlayerHandle` esteso con `togglePlay()` per permettere il single-tap dall'overlay
- `npm run build` — 0 errori TypeScript
- 178 test backend passanti (1 fallimento pre-esistente noto: `test_registration_assigns_toconfirm_group`)

### Change Log

- **2026-03-08**: Story 3.2 implementata — UI like su clip e commenti con optimistic update, double-tap like con animazione cuore
- **2026-03-08**: Code review fix — memory leak tapTimer, disable bottoni durante pending, snapshot liste per rollback, toast errore like, animazione cuore solo su nuovo like, dead code rimosso

### File List

- `frontend/src/types/video.ts` — +2 campi: `like_count`, `is_liked_by_me`
- `frontend/src/types/comment.ts` — +2 campi: `like_count`, `is_liked_by_me`
- `frontend/src/lib/api/videos.ts` — +2 metodi: `like()`, `unlike()`
- `frontend/src/lib/api/comments.ts` — +2 metodi: `like()`, `unlike()`
- `frontend/src/lib/hooks/use-videos.ts` — +2 hook: `useLikeVideo()`, `useUnlikeVideo()`, +helper `updateVideoInPages()`
- `frontend/src/lib/hooks/use-comments.ts` — +2 hook: `useLikeComment()`, `useUnlikeComment()`
- `frontend/src/components/feed/card-as-player.tsx` — Bottone like funzionale, double-tap overlay + animazione cuore
- `frontend/src/app/clip/[id]/clip-content.tsx` — Bottone like funzionale, double-tap overlay + animazione cuore
- `frontend/src/components/comments/comment-item.tsx` — +bottone like, +prop `videoId`, +"use client"
- `frontend/src/components/comments/comment-list.tsx` — +prop `videoId` (passthrough)
- `frontend/src/components/comments/comment-section.tsx` — `videoId` reso required (era opzionale)
- `frontend/src/components/video/video-player.tsx` — `VideoPlayerHandle` esteso con `togglePlay()`
