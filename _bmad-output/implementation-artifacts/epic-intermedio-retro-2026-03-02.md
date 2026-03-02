# Retrospettiva Epic Intermedio — Redesign Layout Card-as-Player

**Data:** 2026-03-02
**Epic:** Intermedio — Redesign Layout Card-as-Player
**Facilitatore:** Bob (Scrum Master)
**Partecipanti:** Alice (PO), Charlie (Senior Dev), Dana (QA), Elena (Junior Dev), AcchippameQuisso (Project Lead)

---

## Riepilogo Epic

| Metrica | Valore |
|---------|--------|
| Story completate | 4/4 (100%) |
| Test backend nuovi | 0 (epic frontend-only) |
| Test backend totali | 155 (invariato) |
| Build errori | 0 |
| Ruff errori | 0 |
| Bug DB trovati durante test | 1 (colonna `file_url` orfana) |
| Iterazioni feedback utente | 3 (layout, commenti nel feed, larghezza card) |
| Playwright smoke test | 1 (upload + feed verificato) |

**Story completate:**

| # | Story | Componenti toccati | Pattern chiave introdotto |
|---|-------|--------------------|--------------------------|
| I.1 | Layout Card-as-Player e Vista Commenti Unificata | 13 file (3 nuovi, 9 modificati, 1 eliminato) | forwardRef+useImperativeHandle su VideoPlayer, CommentSidebar con slot temporali 3s, feed colonna singola |
| I.2 | Input Timestamp MM:SS Bidirezionale | 4 file | formatMMSS/parseMMSS in utils, campo MM:SS sempre visibile, sync bidirezionale player↔field |
| I.3 | Hover Preview Video su Desktop | 1 file | State machine idle/hovering/playing, preview loop primi 5s, mobile skip hover |
| I.4 | Performance Multi-Player e Lazy Loading | 4 file | IntersectionObserver rootMargin 200px, useComments enabled lazy, CustomEvent single player, viewport exit reset |

---

## Successi

### 1. Redesign completato senza regressioni backend
L'intero epic e' stato frontend-only. Nessun endpoint backend modificato, nessun test backend rotto. I 155 test esistenti continuano a passare.

### 2. forwardRef su VideoPlayer — pattern critico stabilito
Il passaggio da `document.querySelector("video")` a `forwardRef + useImperativeHandle` risolve l'ambiguita' con multipli player nel feed. Il pattern `VideoPlayerHandle.seekTo(seconds)` e' pulito e riusabile.

### 3. State machine a 3 stati — robusto e testabile
La macchina `idle → hovering → playing` in CardAsPlayer gestisce correttamente tutte le transizioni:
- Desktop: idle → (hover) → hovering → (click) → playing
- Mobile: idle → (tap) → playing
- Viewport exit: playing → idle
- Altro player attivato: playing → idle

### 4. Performance multi-player — zero overhead fuori viewport
- `useComments(videoId, { enabled: isIntersecting })` evita fetch per card non visibili
- `IntersectionObserver` con `rootMargin: "200px"` pre-carica 200px prima dell'ingresso nel viewport
- CustomEvent `card-player-activate` garantisce un solo player attivo alla volta
- Viewport exit resetta il player a idle (unmount del `<video>`)

### 5. Feedback utente integrato rapidamente (3 iterazioni)
- **Iterazione 1:** Rimossi commenti normali dal feed (solo sidebar temporizzati + "Visualizza tutti")
- **Iterazione 2:** Allargato max-width card da 3xl a 5xl
- **Iterazione 3:** Bottone "Visualizza tutti i commenti" sempre visibile (non condizionale)

### 6. Bug DB critico trovato e fixato
Colonna `file_url` orfana nel database (non presente nel modello Django, non creata da nessuna migrazione) causava `NOT NULL constraint violation` durante upload. Fix: `ALTER TABLE DROP COLUMN`.

---

## Sfide

### 1. Colonna database orfana — nessuna migrazione corrispondente
La colonna `file_url` esisteva nel DB ma non nel modello Django e in nessuna migrazione. Probabilmente aggiunta manualmente o da una migrazione poi cancellata. Ha bloccato l'upload fino alla rimozione.

**Lezione:** Dopo ogni reset/modifica schema manuale, verificare allineamento `showmigrations` + colonne reali con `information_schema`.

### 2. Playwright MCP — file chooser fragile
Il file chooser di Playwright ha generato modal stale che bloccavano le interazioni successive. Serviti multipli tentativi e cancel espliciti per pulire lo stato.

**Lezione:** Per upload file via Playwright, usare `page.waitForEvent('filechooser')` + `Promise.all` con il click, non click separato.

### 3. N+1 commenti nel feed — accettato come debito consapevole
Ogni CardAsPlayer chiama `useComments(videoId)`. Con 20 card visibili, sono 20 richieste API. Il lazy loading (Story I.4) mitiga il problema caricando solo card nel viewport, ma resta un'ottimizzazione possibile (batch endpoint o prefetch nella risposta feed).

**Decisione:** Accettato per v1. Se necessario, Epic futuro aggiungera' endpoint `/api/videos/?include_comments=true` per prefetch.

### 4. Nessun test automatizzato per il nuovo layout
Epic interamente frontend senza test Jest/Vitest per i nuovi componenti. La verifica e' stata manuale (Playwright smoke test).

**Lezione:** Considerare test di rendering base per componenti critici come CardAsPlayer in epic futuri.

---

## Pattern Identificati

### Pattern positivi (da ripetere)
1. **forwardRef + useImperativeHandle** — per componenti che espongono API imperative (seekTo, pause, etc.)
2. **State machine esplicita** — `type CardVideoState = "idle" | "hovering" | "playing"` — chiara, debuggabile, estensibile
3. **CustomEvent per coordinamento cross-component** — `card-player-activate` — leggero, no context/store necessario
4. **IntersectionObserver con rootMargin** — pre-caricamento dati prima che la card entri nel viewport
5. **useQuery enabled** — lazy loading condizionale integrato con React Query
6. **Slot temporali per sidebar** — `Math.floor(second / 3)` con 1 commento/slot (piu' recente) — scalabile e prevedibile

### Pattern da migliorare
1. **Test frontend** — zero test per componenti nuovi (CardAsPlayer, CommentSidebar, CommentForm rivisitato)
2. **Playwright file upload** — workflow da stabilizzare
3. **N+1 commenti** — da risolvere se feed performance diventa problema
4. **useIntersection hook** — semplificato a solo `rootMargin` string, ma potrebbe servire `threshold` in futuro

---

## Follow-Through dalla Retro Epic 2

| # | Action Item Epic 2 | Status | Evidenza Epic Intermedio |
|---|---------------------|--------|--------------------------|
| P1 | Regola paginazione `page is not None` | N/A | Nessun backend toccato |
| P2 | UpdateSerializer per PATCH | N/A | Nessun backend toccato |
| P3 | Playwright nel workflow di review | ⏳ Parziale | Usato per smoke test upload+feed, non per ogni story |
| P4 | Target review < 5 H+M | N/A | Nessuna review formale (epic frontend-only, iterazioni rapide) |
| T1 | CI pipeline end-to-end | ❌ Non fatto | Debito da 4 epic |
| T2 | MinIO in CI | ❌ Non fatto | Debito da 4 epic |
| T3 | Smoke test Playwright Epic 2 | ✅ Fatto | Upload + feed verificato con Playwright MCP |
| PL1 | Aggiornare PRD con vision card-as-player | ⏳ Pending | PRD non ancora aggiornato |
| PL2 | Creare Epic intermedio | ✅ Fatto | Epic Intermedio creato e completato |
| PL3 | Riallineare Epic 3 | ⏳ Pending | Story 3.3 (popup) costruira' sul nuovo layout |
| PL4 | Review architetturale performance multi-player | ✅ Fatto | Story I.4 implementa IntersectionObserver + single player |

---

## Debito Tecnico

| # | Item | Priorita | Epic di origine | Note |
|---|------|----------|-----------------|------|
| 1 | CI pipeline mai testata end-to-end | ALTA | Epic 0 | 4 epic senza verifica |
| 2 | MinIO non in CI | ALTA | Epic 0 | 155 test tutti con mock |
| 3 | N+1 commenti nel feed | MEDIA | Epic Intermedio | Mitigato da lazy loading, ma resta overhead |
| 4 | Zero test frontend per componenti nuovi | MEDIA | Epic Intermedio | CardAsPlayer, CommentSidebar, CommentForm |
| 5 | PRD non aggiornato con vision card-as-player | MEDIA | Epic 2 retro | Da aggiornare prima di Epic 3 |
| 6 | ClipCard.tsx non eliminato | LOW | Epic Intermedio | Non piu' importato ma presente nel codebase |

---

## File Toccati — Riepilogo Completo

### Nuovi (3)
- `components/comments/comment-sidebar.tsx` — sidebar slot temporali
- `components/feed/card-as-player.tsx` — componente principale card con player inline
- `components/feed/card-as-player-skeleton.tsx` — skeleton loading

### Modificati (9)
- `components/video/video-player.tsx` — forwardRef + useImperativeHandle
- `components/comments/comment-list.tsx` — rimosso mode, aggiunto limit
- `components/comments/comment-section.tsx` — rimossi Tabs, aggiunto limit/videoId
- `components/comments/comment-form.tsx` — input MM:SS bidirezionale, onSeekTo, videoDuration
- `components/feed/feed-grid.tsx` — colonna singola, CardAsPlayer
- `components/shared/infinite-scroll.tsx` — aggiornato per nuova API useIntersection
- `app/clip/[id]/clip-content.tsx` — CommentSidebar, useIsDesktop, playerRef
- `lib/hooks/use-comments.ts` — aggiunto enabled option
- `lib/hooks/use-intersection.ts` — refactored a rootMargin string
- `lib/utils.ts` — formatMMSS, parseMMSS
- `lib/constants.ts` — COMMENT_SLOT_SECONDS

### Eliminati (1)
- `components/comments/dynamic-sidebar.tsx` — sostituito da comment-sidebar.tsx

### Database fix (1)
- `ALTER TABLE cs_clips_video DROP COLUMN file_url` — colonna orfana rimossa

---

## Preview Epic 3: Like, Popup e Engagement Loop

### Dipendenze da Epic Intermedio (tutte soddisfatte)
- [x] Layout card-as-player con player inline (Story I.1)
- [x] CommentSidebar con slot temporali (Story I.1) — base per popup overlay (Story 3.3)
- [x] forwardRef su VideoPlayer (Story I.1) — necessario per seek da popup click
- [x] Single active player (Story I.4) — un solo player attivo per popup
- [x] State machine idle/hovering/playing (Story I.3) — popup solo in stato playing

### Impatto sul layout
- Story 3.2 (UI Like): bottone like nella card metadata + doppio tap su player
- Story 3.3 (Popup Overlay): popup usa dati reali da CommentSidebar slot, fade-out 3s
- Story 3.5 (Comment Markers): dot sulla progress bar di VideoPlayer (gia' supporta markerPositions)

---

## Action Items

### Process

| # | Action | Owner | Deadline | Criterio di Successo |
|---|--------|-------|----------|----------------------|
| P1 | Test rendering base per CardAsPlayer e CommentSidebar | Dev Agent | Epic 3 | Almeno 1 test per componente critico |
| P2 | Stabilizzare workflow Playwright per file upload | Dev Agent | Prossimo smoke test | Upload via Playwright senza modal stale |
| P3 | Aggiornare PRD con layout card-as-player implementato | PM + PO | Pre-Epic 3 | PRD riflette UX attuale |

### Technical

| # | Action | Owner | Priorita | Note |
|---|--------|-------|----------|------|
| T1 | CI pipeline — verificare end-to-end | Dev Agent | ALTA | Debito da 4 epic |
| T2 | MinIO in CI | Dev Agent | ALTA | Debito da 4 epic |
| T3 | Eliminare ClipCard.tsx se confermato non necessario | Dev Agent | LOW | Non importato da nessun file |

---

## Team Agreements (confermati + nuovi)

1. **forwardRef + useImperativeHandle** per componenti con API imperativa — pattern standard
2. **State machine esplicita** per componenti con stati multipli — no booleani multipli
3. **CustomEvent per coordinamento** — leggero, preferito a Context per side-effect cross-component
4. **IntersectionObserver + useQuery enabled** — pattern standard per lazy loading nel feed
5. **Lezioni Epic 1+2 confermate** — read_only_fields, error handling, paginazione `page is not None`, UpdateSerializer per PATCH, ruff gate, target review < 5 H+M

---

## Key Takeaways

1. **Il redesign layout era il blocco critico** — la vision del Project Lead divergeva significativamente dall'implementazione. Scoprirlo nella retro Epic 2 e agire immediatamente ha evitato rework dopo Epic 3.
2. **forwardRef su VideoPlayer e' il regalo dell'Epic Intermedio** — come Subquery annotation lo e' stato per Epic 2. Senza forwardRef, il multi-player nel feed non funzionerebbe.
3. **Le iterazioni rapide con feedback utente funzionano** — 3 cicli di feedback hanno prodotto un layout che corrisponde alla vision. La review formale puo' essere meno critica per epic di puro frontend.
4. **Il debito infrastrutturale cresce** — 4 epic senza CI end-to-end. Da affrontare prima del rilascio.

---

*Retrospettiva generata il 2026-03-02 — Workflow BMAD v6.0.0-Beta.8*
