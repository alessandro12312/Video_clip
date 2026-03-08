# Story 3.5: Comment Markers sulla Timeline del Player

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a spettatore,
I want vedere marcatori luminosi sulla barra di progresso del player ai punti dove ci sono commenti temporizzati,
So that scopro a colpo d'occhio dove si concentra la conversazione e posso saltare ai momenti più commentati.

## Acceptance Criteria

1. **Given** una clip con commenti temporizzati
   **When** il player viene renderizzato
   **Then** sulla barra di progresso appaiono dot luminosi (gradiente viola→ciano) alle posizioni corrispondenti ai timestamp dei commenti
   **And** i dot usano posizionamento percentuale (`left: (timestamp / duration) * 100%`)

2. **Given** un utente che fa hover su un dot marker
   **When** il tooltip appare
   **Then** mostra il testo del commento con più like per quel timestamp (o il primo se nessun like)
   **And** mostra il timestamp formattato (es. "0:18")

3. **Given** un utente che clicca su un dot marker
   **When** il click viene registrato
   **Then** il video salta al timestamp corrispondente e inizia la riproduzione

4. **Given** una clip senza commenti temporizzati
   **When** il player viene renderizzato
   **Then** nessun marker appare sulla barra di progresso

## Tasks / Subtasks

- [x] Task 1: Aggiornare `CommentMarker` con tooltip arricchito e click-to-seek (AC: #1, #2, #3)
  - [x] 1.1 Aggiungere prop `commentText?: string` al componente `CommentMarker` — testo del commento da mostrare nel tooltip
  - [x] 1.2 Aggiornare tooltip: se `commentText` presente, mostrare timestamp + testo troncato (~60 char); altrimenti fallback a "Commento a {timestamp}"
  - [x] 1.3 Aggiungere prop `onSeek?: (timestamp: number) => void` per click-to-seek
  - [x] 1.4 Aggiungere `onClick` handler sul dot che chiama `onSeek(timestamp)` con `e.stopPropagation()` (per non attivare il seek della progress bar sottostante)
  - [x] 1.5 Aggiungere `cursor-pointer` al dot e `role="button"` + `aria-label` per accessibilita

- [x] Task 2: Aggiornare `ProgressBar` per passare dati commento ai marker (AC: #1, #2, #3)
  - [x] 2.1 Aggiungere prop `markerComments?: Map<number, { text: string }>` — mappa timestamp → testo commento
  - [x] 2.2 Aggiungere prop `onMarkerSeek?: (timestamp: number) => void` — callback per click-to-seek sui marker
  - [x] 2.3 Per ogni marker, estrarre `commentText` dalla mappa e passarlo a `CommentMarker`
  - [x] 2.4 Passare `onSeek` (rinominato a `onMarkerSeek`) a ogni `CommentMarker`

- [x] Task 3: Costruire la mappa commenti per i marker in `card-as-player.tsx` e `clip-content.tsx` (AC: #2)
  - [x] 3.1 Creare `markerCommentsMap: Map<number, { text: string }>` usando: per ogni timestamp in `markerPositions`, cercare prima in `popupComments` (commento con piu like), poi fallback al primo commento in `comments` per quel timestamp
  - [x] 3.2 Passare `markerCommentsMap` come prop `markerComments` a `VideoPlayer`
  - [x] 3.3 In `VideoPlayer`, propagare `markerComments` e `onMarkerSeek` (che chiama `handleSeek`) a `ProgressBar`

- [x] Task 4: Collegare click-to-seek dei marker (AC: #3)
  - [x] 4.1 In `VideoPlayer`: creare handler `handleMarkerSeek(timestamp)` che chiama `handleSeek(timestamp)` esistente
  - [x] 4.2 Passare `handleMarkerSeek` come `onMarkerSeek` a `ProgressBar`
  - [x] 4.3 In `card-as-player.tsx`: nessuna modifica aggiuntiva — il seek avviene internamente al player

- [x] Task 5: Verifica qualita (AC: tutti)
  - [x] 5.1 `npm run build` — 0 errori TypeScript
  - [ ] 5.2 Verifica visiva: marker gradient visibili, tooltip con testo commento, click salta al timestamp
  - [ ] 5.3 Verifica: clip senza commenti temporizzati non mostra marker
  - [ ] 5.4 Verifica: tooltip mostra commento piu likato se disponibile, altrimenti primo commento

## Dev Notes

### Stato attuale — Base gia implementata

La pipeline dei comment markers e **gia funzionante** in forma base:

| Componente | File | Stato |
|-----------|------|-------|
| `CommentMarker` | `frontend/src/components/video/comment-marker.tsx` | Dot gradient + tooltip basico ("Commento a 0:18") |
| `ProgressBar` | `frontend/src/components/video/progress-bar.tsx` | Renderizza `CommentMarker` per ogni timestamp in `markers[]` |
| `VideoPlayer` | `frontend/src/components/video/video-player.tsx` | Riceve `markerPositions: number[]`, li passa a `ProgressBar` |
| `card-as-player.tsx` | `frontend/src/components/feed/card-as-player.tsx` | Calcola `markerPositions` da commenti con `timestamp_second > 0` |
| `clip-content.tsx` | `frontend/src/app/clip/[id]/clip-content.tsx` | Stessa logica di `markerPositions` |

**Cosa manca (scope di questa story):**
1. **Tooltip arricchito**: mostrare il testo del commento, non solo "Commento a 0:18"
2. **Click-to-seek**: cliccando sul dot, saltare al timestamp
3. **Dati commento per marker**: propagare il testo del commento top-liked fino al `CommentMarker`

### Approccio implementativo

**NON serve nuovo endpoint backend** — i dati sono gia disponibili:
- `popupComments` (da `usePopupComments`, Story 3.3) contiene il commento con piu like per ogni timestamp (like >= 1)
- `comments` (da `useComments`) contiene tutti i commenti — fallback per timestamp senza like

**Flusso dati:**
```
popupComments + comments
    ↓ (useMemo in card-as-player / clip-content)
markerCommentsMap: Map<number, { text: string }>
    ↓ (prop a VideoPlayer)
    ↓ (prop a ProgressBar)
    ↓ (prop commentText a CommentMarker)
Tooltip arricchito
```

### `CommentMarker` — Modifica target

**Attuale:**
```tsx
interface CommentMarkerProps {
  timestamp: number;
  position: number;
  size: number;
}
// Tooltip: "Commento a {formatTimestamp(timestamp)}"
// Nessun click handler
```

**Target:**
```tsx
interface CommentMarkerProps {
  timestamp: number;
  position: number;
  size: number;
  commentText?: string;           // ← NUOVO: testo commento top-liked
  onSeek?: (timestamp: number) => void;  // ← NUOVO: click-to-seek
}
// Tooltip: "{formatTimestamp(timestamp)} — {commentText}" (troncato ~60 char)
// Fallback: "Commento a {formatTimestamp(timestamp)}" (se no commentText)
// Click: e.stopPropagation() + onSeek(timestamp)
```

### `ProgressBar` — Modifica target

**Attuale:**
```tsx
interface ProgressBarProps {
  currentTime: number;
  buffered: number;
  duration: number;
  markers: number[];
  onSeek: (time: number) => void;
}
```

**Target:**
```tsx
interface ProgressBarProps {
  currentTime: number;
  buffered: number;
  duration: number;
  markers: number[];
  markerComments?: Map<number, { text: string }>;  // ← NUOVO
  onMarkerSeek?: (timestamp: number) => void;       // ← NUOVO
  onSeek: (time: number) => void;
}
```

### `VideoPlayer` — Modifica target

Propagare nuove props da `VideoPlayerProps` a `ProgressBar`:
- Aggiungere `markerComments?: Map<number, { text: string }>` alle props
- Creare `handleMarkerSeek(timestamp)` che chiama `handleSeek(timestamp)` (gia esistente, riga ~137)
- Passare entrambi a `<ProgressBar>`

### `markerCommentsMap` — Costruzione in card-as-player e clip-content

```tsx
const markerCommentsMap = useMemo(() => {
  const map = new Map<number, { text: string }>();
  // Priorita 1: popup comments (like >= 1, top-liked per timestamp)
  for (const c of popupComments) {
    map.set(c.timestamp_second, { text: c.content });
  }
  // Priorita 2: primo commento per timestamp (se non gia coperto da popup)
  for (const c of comments) {
    if (c.timestamp_second > 0 && !map.has(c.timestamp_second)) {
      map.set(c.timestamp_second, { text: c.content });
    }
  }
  return map;
}, [popupComments, comments]);
```

### Troncamento testo tooltip

Il tooltip deve essere leggibile senza essere enorme. Pattern suggerito:
```tsx
const displayText = commentText && commentText.length > 60
  ? commentText.slice(0, 57) + "..."
  : commentText;
```

### `e.stopPropagation()` — Critico

Il `CommentMarker` e un child di `ProgressBar`. Il click sulla progress bar chiama `handleMouseDown` che esegue seek. Se non si ferma la propagazione, il click sul marker causera ANCHE un seek dalla progress bar (basato sulla posizione del mouse), duplicando l'azione. `e.stopPropagation()` previene questo.

### File da modificare

| File | Modifica |
|------|----------|
| `frontend/src/components/video/comment-marker.tsx` | +props `commentText`, `onSeek`; tooltip arricchito; click handler |
| `frontend/src/components/video/progress-bar.tsx` | +props `markerComments`, `onMarkerSeek`; passa dati a `CommentMarker` |
| `frontend/src/components/video/video-player.tsx` | +prop `markerComments`; crea `handleMarkerSeek`; propaga a `ProgressBar` |
| `frontend/src/components/feed/card-as-player.tsx` | +`markerCommentsMap` useMemo; passa a `VideoPlayer` |
| `frontend/src/app/clip/[id]/clip-content.tsx` | +`markerCommentsMap` useMemo; passa a `VideoPlayer` |

### File NON da modificare

| File | Motivo |
|------|--------|
| Backend (qualsiasi) | Nessun endpoint nuovo — dati gia disponibili |
| `comment-sidebar.tsx` | Non coinvolto |
| `popup-overlay.tsx` | Non coinvolto |
| `use-comments.ts` | Nessun hook nuovo |
| `use-videos.ts` | `usePopupComments` gia esistente (Story 3.3) |
| `constants.ts` | `COMMENT_MARKER_SIZE_PX` gia presente (6px) |
| Tipi TypeScript | Nessuna modifica ai tipi |

### Pattern e vincoli architetturali

- **Import Framer Motion**: `import from "framer-motion"` (NON `"motion/react"`) [Source: MEMORY.md#Framer-Motion-Import-Path]
- **Componenti React**: named export, mai default export [Source: project-context.md]
- **Import path**: sempre `@/` alias [Source: project-context.md]
- **`"use client"`**: obbligatorio su componenti con hooks/eventi [Source: architecture.md]
- **a11y**: `role="button"`, `aria-label` su elementi interattivi [Source: Definition of Done]
- **shadcn/ui Tooltip**: gia importato in `CommentMarker` — nessuna nuova dipendenza
- **`gradient-bg`**: classe CSS gia usata per i dot — mantenerla

### Intelligence dalle Story precedenti (3.2, 3.3, 3.4)

- **193 test backend** baseline (192 pass, 1 fail pre-esistente `test_registration_assigns_toconfirm_group`)
- **Ruff 0 errori** baseline
- **`npm run build` 0 errori** baseline
- **Timeout cleanup**: sempre `useEffect(() => () => clearTimeout(...), [])` per timer
- **Optimistic update**: pattern robusto snapshot + rollback gia stabilito (non necessario per questa story)
- **`popupComments`**: gia fetched con `usePopupComments(videoId)` in entrambi i contesti (card + clip detail)
- **`markerPositions`**: gia calcolato da `[...new Set(comments.filter(c => c.timestamp_second > 0).map(c => c.timestamp_second))]`

### Rischi e edge case

1. **Marker sovrapposti**: se 2 commenti sono a timestamp vicini (es. 5s e 6s), i dot potrebbero sovrapporsi visivamente. Per ora accettabile — i dot sono 6px e il video e tipicamente > 600px wide (quindi 1% = ~6px per 600px). Sovrappongono solo se i timestamp sono identici (gia deduplicati con `Set`).
2. **Tooltip su mobile**: su mobile touch, il tooltip potrebbe non funzionare bene (no hover). shadcn/ui Tooltip usa Radix che supporta touch (long press). Il click-to-seek funziona su touch.
3. **Molti marker**: un video con 50+ commenti a timestamp diversi potrebbe avere molti dot. Accettabile — sono elementi DOM leggeri (div + tooltip lazy).

### Project Structure Notes

- Tutti i file sono gia esistenti — nessun file nuovo necessario
- Le modifiche sono **solo frontend**, nessuna modifica backend
- Segue la struttura `src/components/video/` per componenti player
- Nessun conflitto con project structure

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-3.5] — AC BDD completi, nota "opzionale"
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#SoundCloud-DNA] — Pattern "dot luminosi (gradiente) sulla timeline con hover preview"
- [Source: _bmad-output/planning-artifacts/architecture.md#Performance] — Pre-caricamento dati popup
- [Source: _bmad-output/implementation-artifacts/3-3-popup-overlay-con-dati-reali-e-sidebar-dinamica.md] — `usePopupComments`, `popupMap`, `markerPositions`
- [Source: frontend/src/components/video/comment-marker.tsx] — Componente base esistente
- [Source: frontend/src/components/video/progress-bar.tsx] — Rendering marker esistente
- [Source: frontend/src/components/video/video-player.tsx] — Props `markerPositions`, `handleSeek`
- [Source: MEMORY.md#Framer-Motion-Import-Path] — Import da "framer-motion"
- [Source: MEMORY.md#Epic-1+2-Retro] — Pattern stabiliti, a11y, test assertions

### Git Intelligence — Pattern Recenti

Ultimi commit rilevanti:
- `da01a68` — Story 3.1: modelli VideoLike/CommentLike + endpoint like/unlike + annotazioni

Pattern commit: prefisso `feat:` per feature, riepilogo conciso.
Suggerito: `feat: Story 3.5 — comment markers arricchiti con tooltip e click-to-seek`

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

Nessun bug riscontrato. Build passata al primo tentativo.

### Completion Notes List

- **Task 1**: `CommentMarker` aggiornato con props `commentText` e `onSeek`, tooltip arricchito con testo troncato ~60 char, `e.stopPropagation()` sul click, `cursor-pointer` + `role="button"` + `aria-label` per a11y, `max-w-[250px]` sul tooltip content
- **Task 2**: `ProgressBar` aggiornato con props `markerComments` e `onMarkerSeek`, dati estratti dalla mappa e passati ai singoli `CommentMarker`
- **Task 3**: `markerCommentsMap` creata con `useMemo` in entrambi i contesti (card-as-player + clip-content), priorita popupComments (top-liked) poi fallback a primo commento per timestamp
- **Task 4**: `handleMarkerSeek` creato in `VideoPlayer` che delega a `handleSeek`, propagato tramite `ProgressBar` → `CommentMarker`
- **Task 5**: `npm run build` passato con 0 errori. Subtask 5.2-5.4 sono verifiche visive manuali (lasciate non spuntate per verifica utente)

### Implementation Plan

Approccio bottom-up: CommentMarker → ProgressBar → VideoPlayer → consumer components. Nessun nuovo endpoint backend. Dati gia disponibili da `usePopupComments` e `useComments`.

### File List

- `frontend/src/components/video/comment-marker.tsx` — modificato (props commentText, onSeek, tooltip arricchito, click handler, a11y + tabIndex/onKeyDown)
- `frontend/src/components/video/progress-bar.tsx` — modificato (props markerComments, onMarkerSeek, propagazione a CommentMarker)
- `frontend/src/components/video/video-player.tsx` — modificato (prop markerComments, handleMarkerSeek con auto-play, propagazione a ProgressBar)
- `frontend/src/components/feed/card-as-player.tsx` — modificato (useMarkerComments hook, passaggio a VideoPlayer)
- `frontend/src/app/clip/[id]/clip-content.tsx` — modificato (useMarkerComments hook, passaggio a VideoPlayer)
- `frontend/src/lib/hooks/use-marker-comments.ts` — nuovo (hook condiviso per markerCommentsMap con filtro timestamp > 0)

## Senior Developer Review (AI)

**Review Date:** 2026-03-08
**Reviewer:** Claude Opus 4.6
**Review Outcome:** Changes Requested → Fixed

### Findings (6 total: 0 High, 3 Medium, 3 Low)

### Action Items

- [x] [M1] AC #3 parziale: handleMarkerSeek fa seek ma non auto-play — fixato con video.play() dopo seek
- [x] [M2] role="button" senza tabIndex={0} e onKeyDown — fixato con tabIndex={0} + onKeyDown Enter/Space
- [x] [M3] markerCommentsMap duplicata in 2 file — estratta in useMarkerComments hook condiviso
- [x] [L1] handleMarkerSeek wrapper ridondante — ora necessario perche contiene logica auto-play
- [x] [L2] popupComments non filtrato per timestamp > 0 — fixato nel nuovo hook
- [ ] [L3] Nessun test frontend per logica markerCommentsMap — accettabile data la semplicita

## Change Log

- **2026-03-08**: Story 3.5 implementata — comment markers arricchiti con tooltip e click-to-seek. Nessuna modifica backend.
- **2026-03-08**: Code review fix — auto-play su marker click (AC #3), keyboard a11y (tabIndex + onKeyDown), hook condiviso useMarkerComments (DRY), filtro timestamp > 0 per popupComments.
