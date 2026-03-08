# Inventario Componenti — Frontend Video_clip

> Aggiornato il 2026-03-08 | Deep Scan | Workflow: document-project v1.2.0

---

## 1. Panoramica

| Metrica | Valore |
|---------|--------|
| Componenti totali | **54** |
| Categorie | 8 (Layout, Feed, Video, Commenti, Rating, Utente, Condivisi, UI) |
| Primitivi UI (shadcn/ui) | 18 |
| Componenti custom | 36 |
| Provider globali | 3 (AuthProvider, QueryProvider, LoginTransitionProvider) |
| Route groups | 3 (`(auth)`, `(main)`, `clip/[id]`) |

### Distribuzione per cartella

| Cartella | File |
|----------|------|
| `components/layout/` | 5 |
| `components/feed/` | 5 |
| `components/video/` | 5 |
| `components/comments/` | 5 |
| `components/rating/` | 1 |
| `components/user/` | 7 |
| `components/shared/` | 8 |
| `components/ui/` | 18 |
| `app/` (pagine/layout) | 20 |
| `providers/` | 3 |

---

## 2. Componenti Layout

### LeftSidebar

| | |
|---|---|
| **File** | `frontend/src/components/layout/left-sidebar.tsx` |
| **Props** | Nessuna (stato interno) |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Sidebar verticale visibile solo su desktop (`hidden lg:flex`).
- Stato `collapsed` (boolean) che alterna tra `--sidebar-width` (240 px) e `--sidebar-collapsed-width` (64 px).
- 5 voci di navigazione: Home, Esplora, Carica, Profilo, Contest — con icone Lucide.
- Evidenziazione attiva basata su `usePathname()` (match esatto + prefisso).
- Logo brand "Video_clip" con struttura a 3 zone gradiente (`gradient-text` / solid cyan / `gradient-text-reverse`). In modalita' collapsed mostra solo "V".
- ID `#sidebar-brand-logo` usato come target della transizione post-login su desktop.

---

### Header

| | |
|---|---|
| **File** | `frontend/src/components/layout/header.tsx` |
| **Props** | Nessuna |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Header mobile sticky, nascosto su desktop (`lg:hidden`).
- Altezza fissa: `var(--header-height)` (56 px).
- Background con `backdrop-blur-sm` e `bg-background/80` (semi-trasparente).
- Contiene: logo "V" (`#mobile-brand-logo`), `UserSearchBar`, avatar utente con dropdown (Profilo / Esci).
- Nessun hamburger menu: la navigazione mobile e' gestita da `MobileBottomBar`.

---

### MobileBottomBar

| | |
|---|---|
| **File** | `frontend/src/components/layout/mobile-bottom-bar.tsx` |
| **Props** | Nessuna |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Barra di navigazione fixed in basso, visibile solo su mobile (`lg:hidden`).
- Altezza: `var(--bottom-bar-height)` (64 px). z-index: 50.
- 4 voci: Home, Esplora, Carica (con accent gradient cerchio), Profilo.
- Il pulsante Carica ha un cerchio `gradient-bg` con icona Plus bianca (nessuna label).
- Evidenziazione attiva basata su `usePathname()`.

---

### DesktopNavbar

| | |
|---|---|
| **File** | `frontend/src/components/layout/desktop-navbar.tsx` |
| **Props** | Nessuna |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Barra superiore visibile solo su desktop (`hidden lg:flex`), altezza 56 px.
- Background con `backdrop-blur-sm`.
- Contiene: `UserSearchBar` (max-w-md, centrata) e `DesktopUserMenu` (allineato a destra).
- Non contiene logo (quello e' nella sidebar).

---

### DesktopUserMenu

| | |
|---|---|
| **File** | `frontend/src/components/layout/desktop-user-menu.tsx` |
| **Props** | Nessuna |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Menu utente visibile solo su desktop (`hidden lg:flex`).
- Mostra `UserAvatar` (link a /profilo) + dropdown con ChevronDown.
- Voci dropdown: Il mio profilo, Impostazioni account, Separator, Esci.
- Logout mostra toast "Hai effettuato il logout".
- Restituisce `null` se l'utente non e' autenticato.

---

## 3. Componenti Feed

### CardAsPlayer

| | |
|---|---|
| **File** | `frontend/src/components/feed/card-as-player.tsx` |
| **Props** | `video: Video` |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Card feed con player video inline — riempie il viewport (`h-[calc(100dvh-5.5rem)]`).
- State machine a 3 stati: `idle | hovering | playing`.
- **Idle**: thumbnail/placeholder con icona Play; hover avvia preview (primi 5 sec in loop, muted).
- **Playing**: `VideoPlayer` completo con controlli, popup commenti, marker timeline.
- `CustomEvent("card-player-activate")` per garantire un solo player attivo nel feed.
- `IntersectionObserver` (rootMargin 200px) per lazy loading commenti.
- Layout flex colonna: video + sidebar desktop (CommentSidebar) nella riga principale, commenti inline sotto.
- Footer: avatar, username, titolo, tag, stats (views, rating, data), link al dettaglio.
- Toggle Chat/Popup per commenti, bottone Like placeholder (disabilitato).

---

### CardAsPlayerSkeleton

| | |
|---|---|
| **File** | `frontend/src/components/feed/card-as-player-skeleton.tsx` |
| **Props** | Nessuna |

**Comportamento chiave:**
- Skeleton loading della `CardAsPlayer`: area video + sidebar + info.
- Ha attributo `data-snap-target` per il sistema di snap scroll.
- Usa primitivi `Skeleton` di shadcn/ui.

---

### FeedGrid

| | |
|---|---|
| **File** | `frontend/src/components/feed/feed-grid.tsx` |
| **Props** | `videos: Video[]`, `isLoading?: boolean` |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Colonna singola (`flex flex-col gap-6`) con `CardAsPlayer` per ogni video.
- Attiva `useSnapScroll()` per navigazione card-by-card con wheel.
- Se `isLoading`, renderizza 3 `CardAsPlayerSkeleton`.

---

### ClipCard (legacy)

| | |
|---|---|
| **File** | `frontend/src/components/feed/clip-card.tsx` |
| **Props** | `video: Video` |

**Comportamento chiave:**
- Card cliccabile originale (non piu' importata, sostituita da `CardAsPlayer`).
- Conservata nel codebase ma non utilizzata.

---

### ClipCardSkeleton (legacy)

| | |
|---|---|
| **File** | `frontend/src/components/feed/clip-card-skeleton.tsx` |
| **Props** | Nessuna |

**Comportamento chiave:**
- Skeleton della `ClipCard` originale (non piu' importata).

---

## 4. Componenti Video

### VideoPlayer

| | |
|---|---|
| **File** | `frontend/src/components/video/video-player.tsx` |
| **Props** | `src: string`, `videoId: number`, `duration: number`, `popupMap: Map<number, Comment>`, `markerPositions: number[]`, `onPause?: (currentTime: number) => void` |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Player video completo con controlli custom.
- Sistema di popup commenti temporizzati: ad ogni secondo confronta `popupMap` e mostra `PopupOverlay` per `POPUP_DISPLAY_DURATION_MS` (4 sec).
- Conteggio visualizzazioni automatico dopo `VIEW_COUNT_DELAY_MS` (5 sec) di riproduzione continua (annullato se messo in pausa prima).
- Composizione interna: `<video>` nativo + `PopupOverlay` + `ProgressBar` + `PlayerControls`.
- Click sul video attiva/disattiva la riproduzione. Supporta fullscreen.
- Gestione stato: isPlaying, currentTime, buffered, volume, isMuted, activePopup.

---

### PlayerControls

| | |
|---|---|
| **File** | `frontend/src/components/video/player-controls.tsx` |
| **Props** | `isPlaying: boolean`, `currentTime: number`, `duration: number`, `volume: number`, `isMuted: boolean`, `onTogglePlay`, `onVolumeChange`, `onToggleMute`, `onToggleFullscreen` |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Barra controlli sovrapposta al video (bg `black/60`).
- Pulsanti: Play/Pause, display tempo `M:SS / M:SS` (font-mono), Volume/Mute, Fullscreen.
- Tutte le icone da Lucide. Stile: `text-white hover:bg-white/10`.

---

### ProgressBar

| | |
|---|---|
| **File** | `frontend/src/components/video/progress-bar.tsx` |
| **Props** | `currentTime: number`, `buffered: number`, `duration: number`, `markers: number[]`, `onSeek: (time: number) => void` |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Barra di avanzamento cliccabile e trascinabile (drag su mousedown + mousemove + mouseup).
- 3 strati: buffered (bianco 20%), progresso (gradient-bg), sfondo (bianco 10%).
- Seek thumb visibile solo durante il drag.
- Renderizza `CommentMarker` per ogni timestamp con commenti.
- Altezza: 8 px, hover 12 px.

---

### PopupOverlay

| | |
|---|---|
| **File** | `frontend/src/components/video/popup-overlay.tsx` |
| **Props** | `comment: Comment \| null` |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Overlay animato (framer-motion `AnimatePresence`) che mostra un commento sovrapposto al video.
- Posizionato in alto a destra del player (`absolute top-3 right-3`).
- Stile glassmorphism (`glass` class): sfondo semi-trasparente con blur.
- Mostra username, `TimestampBadge` e testo del commento.
- Animazione: fade-in + slide-down all'ingresso, fade-out + slide-up all'uscita.

---

### CommentMarker

| | |
|---|---|
| **File** | `frontend/src/components/video/comment-marker.tsx` |
| **Props** | `timestamp: number`, `position: number` (percentuale), `size: number` (px) |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Pallino `gradient-bg` posizionato sulla `ProgressBar` alla percentuale corrispondente al timestamp.
- Dimensione configurabile (default `COMMENT_MARKER_SIZE_PX` = 6).
- Tooltip (shadcn/ui) al hover con "Commento a M:SS".
- Hover: `scale-150`, opacity da 80% a 100%.

---

## 5. Componenti Commenti

### CommentForm

| | |
|---|---|
| **File** | `frontend/src/components/comments/comment-form.tsx` |
| **Props** | `videoId: number`, `pauseTimestamp: number \| null`, `onClearTimestamp: () => void` |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Form per inviare commenti, con supporto a timestamp (mostrato se `pauseTimestamp > 0`).
- `TimestampBadge` removable sopra la textarea quando e' associato un timestamp.
- Textarea con maxLength 500 e placeholder dinamico ("Descrivi questo momento..." vs "Scrivi un commento...").
- Pulsante submit con icona Send, `gradient-bg`, disabilitato se vuoto o in pending.
- Usa `useCreateComment` hook; toast success/error su risultato.

---

### CommentItem

| | |
|---|---|
| **File** | `frontend/src/components/comments/comment-item.tsx` |
| **Props** | `comment: Comment`, `compact?: boolean`, `onTimestampClick?: (seconds: number) => void` |

**Comportamento chiave:**
- Singolo commento: avatar (nascosto se `compact`), `UsernameLink`, `TimestampBadge` cliccabile (se `timestamp_second > 0`), data relativa, testo.
- Modalita' compact: font piu' piccolo (`text-xs`), senza avatar. Usata nella `CommentSidebar`.

---

### CommentList

| | |
|---|---|
| **File** | `frontend/src/components/comments/comment-list.tsx` |
| **Props** | `comments: Comment[]`, `mode: "all" \| "timestamped"`, `onTimestampClick?: (seconds: number) => void` |

**Comportamento chiave:**
- Lista di `CommentItem` con filtraggio/ordinamento:
  - `mode: "all"` — tutti i commenti, ordinati per data (piu' recenti prima).
  - `mode: "timestamped"` — solo commenti con `timestamp_second > 0`, ordinati per timestamp crescente.
- Messaggio empty state differenziato per modalita'.

---

### CommentSection

| | |
|---|---|
| **File** | `frontend/src/components/comments/comment-section.tsx` |
| **Props** | `comments: Comment[]`, `onTimestampClick?: (seconds: number) => void` |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Contenitore con tabs (shadcn/ui `Tabs`): "Tutti (N)" e "Nel video (N)".
- Ciascun tab renderizza una `CommentList` con `mode` corrispondente.
- Tabs con stile underline (border-b-2, senza sfondo).

---

### CommentSidebar

| | |
|---|---|
| **File** | `frontend/src/components/comments/comment-sidebar.tsx` |
| **Props** | `comments: Comment[]`, `onTimestampClick?: (seconds: number) => void`, `maxVisible?: number`, `currentTime?: number \| null` |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Sidebar laterale destra per commenti temporizzati.
- Slot temporali: `Math.floor(second / COMMENT_SLOT_SECONDS)` (3 sec), mostra 1 commento per slot (il piu' recente).
- Animazione con framer-motion `AnimatePresence` per ingresso/uscita commenti.
- `maxVisible` limita il numero di commenti visibili (default 10).
- `currentTime` opzionale: se presente, i commenti appaiono in sync con il player.
- Usa `ScrollArea` di shadcn/ui. `TimestampBadge` cliccabile per seek nel video.
- Usata sia in `CardAsPlayer` (feed) sia in `ClipContent` (dettaglio, modalita' chat).

---

## 6. Componenti Rating

### StarRating

| | |
|---|---|
| **File** | `frontend/src/components/rating/star-rating.tsx` |
| **Props** | `value: number`, `onChange?: (value: number) => void`, `readonly?: boolean`, `size?: "sm" \| "md"` |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- 5 stelle (icona Star di Lucide) con supporto hover preview e click per votare.
- Due dimensioni: `sm` (h-4 w-4, default) e `md` (h-5 w-5).
- Stelle attive: `fill-yellow-400 text-yellow-400`; inattive: `text-muted-foreground/30`.
- Modalita' readonly: nessun hover/click, cursor-default.
- Stato hover interno (`hoverValue`) che sovrascrive il valore visualizzato.

---

## 7. Componenti Utente

### UserAvatar

| | |
|---|---|
| **File** | `frontend/src/components/user/user-avatar.tsx` |
| **Props** | `username: string`, `size?: "sm" \| "md" \| "lg"`, `className?: string` |

**Comportamento chiave:**
- Avatar con iniziale dell'username su sfondo `gradient-bg` (viola-ciano).
- 3 dimensioni: `sm` (28 px), `md` (36 px, default), `lg` (56 px).
- Usa primitivi `Avatar` / `AvatarFallback` di shadcn/ui.
- Nessun supporto immagine profilo (solo fallback con iniziale).
- Server component (nessuna direttiva `"use client"`).

---

### FollowButton

| | |
|---|---|
| **File** | `frontend/src/components/user/follow-button.tsx` |
| **Props** | `userId: number`, `username: string`, `isFollowing: boolean`, `size?: "sm" \| "default"`, `className?: string` |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Pulsante follow/unfollow con testo dinamico: "Segui" / "Smetti di seguire" / "Seguendo..." / "Rimuovendo...".
- Restituisce `null` se l'utente corrente e' lo stesso dell'utente target.
- Stile: `gradient-bg` per "Segui", variant `outline` per "Smetti di seguire".
- Usa `useFollow` / `useUnfollow` hooks con mutazioni React Query.

---

### ProfileHeader

| | |
|---|---|
| **File** | `frontend/src/components/user/profile-header.tsx` |
| **Props** | `profileUser: User`, `videoCount?: number` |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Header del profilo utente: `UserAvatar` (lg), username, bio, stats (followers, seguiti, clip).
- Se profilo proprio: pulsante "Modifica profilo" che attiva inline `ProfileEditForm`.
- Se profilo altrui: `FollowButton`.
- Link a `/profilo/{username}/followers` e `/profilo/{username}/following` con aria-label descrittivi.
- Stats: followers_count, following_count, videoCount (con icona Film).

---

### ProfileEditForm

| | |
|---|---|
| **File** | `frontend/src/components/user/profile-edit-form.tsx` |
| **Props** | `user: User`, `onClose: () => void` |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Form inline per modificare la bio del profilo (max 500 caratteri).
- Contatore caratteri live. Label e aria-describedby per accessibilita'.
- Pulsanti: Salva (con spinner Loader2 se pending) e Annulla.
- Usa `useUpdateProfile` hook. Toast success/error.

---

### UserListItem

| | |
|---|---|
| **File** | `frontend/src/components/user/user-list-item.tsx` |
| **Props** | `user: User` |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Riga utente per liste followers/following: avatar, username (link a profilo), bio troncata, `FollowButton`.
- Hover: `bg-accent/50`. ARIA labels sui link.

**Esporta anche `UserListItemSkeleton`:**
- Props: `count?: number` (default 5).
- Skeleton loading per la lista utenti.

---

### UserSearchBar

| | |
|---|---|
| **File** | `frontend/src/components/user/user-search-bar.tsx` |
| **Props** | `collapsed?: boolean`, `className?: string`, `onSelect?: () => void` |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Barra di ricerca utenti con dropdown risultati.
- Debounce 300 ms sulla query. Minimo 2 caratteri per attivare la ricerca.
- Supporto navigazione da tastiera: ArrowDown/Up per navigare, Enter per selezionare, Escape per chiudere.
- ARIA completo: `role="combobox"`, `aria-expanded`, `aria-controls`, `aria-autocomplete`, `aria-activedescendant`; dropdown con `role="listbox"`, opzioni con `role="option"`, `aria-selected`.
- Modalita' collapsed: mostra solo icona Search; al click espande un overlay.
- Risultati: `UserAvatar` + username per ogni match; skeleton loading durante la ricerca.
- Pulsante X per cancellare la query.
- Usa `useSearchUsers` hook.

---

### UsernameLink

| | |
|---|---|
| **File** | `frontend/src/components/user/username-link.tsx` |
| **Props** | `username: string`, `className?: string` |

**Comportamento chiave:**
- Link a `/profilo/{username}` con hover `text-primary`.
- Server component (nessuna direttiva `"use client"`).

---

## 8. Componenti Condivisi

### EmptyState

| | |
|---|---|
| **File** | `frontend/src/components/shared/empty-state.tsx` |
| **Props** | `icon: LucideIcon`, `title: string`, `description?: string`, `action?: React.ReactNode`, `className?: string` |

**Comportamento chiave:**
- Stato vuoto generico centrato verticalmente con icona grande (48 px, opaca al 50%), titolo, descrizione opzionale e azione opzionale.
- Server component.

---

### ErrorMessage

| | |
|---|---|
| **File** | `frontend/src/components/shared/error-message.tsx` |
| **Props** | `message?: string` (default: "Si e' verificato un errore."), `onRetry?: () => void`, `className?: string` |

**Comportamento chiave:**
- Messaggio di errore centrato con icona `AlertCircle` (destructive), testo e pulsante "Riprova" opzionale.
- Server component.

---

### GradientSpinner

| | |
|---|---|
| **File** | `frontend/src/components/shared/gradient-spinner.tsx` |
| **Props** | `size?: number` (default: 32), `className?: string`, `variant?: "full" \| "inline"` (default: "inline"), `onAnimationReady?: () => void` |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Due varianti:
  - `inline`: solo anello spinner con gradiente conico (`conic-gradient`) che ruota.
  - `full`: schermata intera (`fixed inset-0 z-50`) con logo "Video_clip" animato (scale breathing) + spinner sotto.
- Rispetta `prefers-reduced-motion` (nessuna animazione scale se attivo).
- L'anello usa una maschera radiale per ottenere l'effetto "ring" (3 px di spessore).

---

### InfiniteScroll

| | |
|---|---|
| **File** | `frontend/src/components/shared/infinite-scroll.tsx` |
| **Props** | `hasNextPage: boolean \| undefined`, `isFetchingNextPage: boolean`, `fetchNextPage: () => void` |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Sentinel element che usa `IntersectionObserver` (tramite `useIntersection` hook) per triggerare il caricamento della pagina successiva.
- Mostra `GradientSpinner` (24 px) durante il fetching.
- Modello standard per infinite scroll con React Query (`useInfiniteQuery`).

---

### LoginTransitionOverlay

| | |
|---|---|
| **File** | `frontend/src/components/shared/login-transition-overlay.tsx` |
| **Props** | `isActive: boolean`, `sourceRect: SourceRect \| null`, `onTransitionEnd: () => void` |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Overlay cinematografico per la transizione post-login (z-50, fixed inset-0).
- Sequenza in 4 fasi orchestrata con framer-motion `useAnimate`:
  1. Logo dalla posizione auth (sourceRect) al centro dello schermo.
  2. Spinner fade-in. Attesa minima `MIN_DISPLAY_TIME` (500 ms).
  3. Logo si muove verso il target finale:
     - **Desktop**: "Video_clip" intero si scala e trasla verso `#sidebar-brand-logo`.
     - **Mobile**: dissolve "ideo_cli" (width collapse a 0), poi "V" vola verso `#mobile-brand-logo`.
  4. Overlay fade-out rivela la UI sottostante.
- Rispetta `prefers-reduced-motion`: skip animazioni, solo tempi minimi.
- Fallback robusto se sourceRect e' assente o se il DOM non e' pronto.
- Logo con struttura a 3 span: `.brand-letter-first` (V), `.brand-letters-rest` (ideo_cli + p).

---

### PageLoader

| | |
|---|---|
| **File** | `frontend/src/components/shared/page-loader.tsx` |
| **Props** | Nessuna |

**Comportamento chiave:**
- Wrapper minimale: renderizza `GradientSpinner` con `variant="full"` e `size={32}`.
- Usato come loading state globale nel layout `(main)`.

---

### TagBadge

| | |
|---|---|
| **File** | `frontend/src/components/shared/tag-badge.tsx` |
| **Props** | `tag: VideoTag`, `className?: string` |

**Comportamento chiave:**
- Badge colorato per le categorie video: Clutch (rosso), Funny (verde), Fail (blu).
- Colori definiti in `TAG_COLORS` (constants.ts) con classi Tailwind custom (`bg-clutch/20`, `text-clutch`, ecc.).
- Usa primitivo `Badge` di shadcn/ui con variant `outline`, border trasparente.

---

### TimestampBadge

| | |
|---|---|
| **File** | `frontend/src/components/shared/timestamp-badge.tsx` |
| **Props** | `seconds: number`, `onClick?: () => void`, `removable?: boolean`, `onRemove?: () => void`, `className?: string` |
| **Direttiva** | `"use client"` |

**Comportamento chiave:**
- Badge monospace che mostra un timestamp formattato (`M:SS`).
- Stile: bordo `primary/30`, sfondo `primary/10`, testo `primary`.
- Cliccabile (se `onClick`): usato per saltare al punto nel video.
- Modalita' removable: pulsante X interno (per il form commenti).

---

## 9. Primitivi UI (shadcn/ui)

Tutti i componenti in `frontend/src/components/ui/` sono primitivi shadcn/ui basati su Radix UI, configurati per il tema dark di Video_clip.

| Componente | File | Descrizione |
|-----------|------|-------------|
| **AlertDialog** | `ui/alert-dialog.tsx` | Dialog di conferma con azioni (Radix AlertDialog) |
| **Avatar** | `ui/avatar.tsx` | Avatar con AvatarImage e AvatarFallback |
| **Badge** | `ui/badge.tsx` | Badge con varianti (default, secondary, destructive, outline) |
| **Button** | `ui/button.tsx` | Pulsante con varianti e dimensioni multiple |
| **Card** | `ui/card.tsx` | Card, CardHeader, CardContent, CardFooter, CardTitle, CardDescription |
| **Dialog** | `ui/dialog.tsx` | Dialog modale (Radix Dialog) |
| **DropdownMenu** | `ui/dropdown-menu.tsx` | Menu a tendina (Radix DropdownMenu) |
| **Input** | `ui/input.tsx` | Campo input testo |
| **Label** | `ui/label.tsx` | Label per form fields |
| **Popover** | `ui/popover.tsx` | Popover posizionato (Radix Popover) |
| **Progress** | `ui/progress.tsx` | Barra di progresso |
| **ScrollArea** | `ui/scroll-area.tsx` | Area scrollabile custom (Radix ScrollArea) |
| **Separator** | `ui/separator.tsx` | Separatore orizzontale/verticale |
| **Sheet** | `ui/sheet.tsx` | Pannello laterale slide-in (Radix Dialog) |
| **Skeleton** | `ui/skeleton.tsx` | Placeholder loading animato |
| **Sonner** | `ui/sonner.tsx` | Toast notifications (wrapper Sonner) |
| **Tabs** | `ui/tabs.tsx` | Tabs navigabili (Radix Tabs) |
| **Textarea** | `ui/textarea.tsx` | Campo textarea |
| **Tooltip** | `ui/tooltip.tsx` | Tooltip al hover (Radix Tooltip) |

---

## 10. Pattern di Design

### Responsive Design (Mobile-First)

| Breakpoint | Valore | Comportamento |
|-----------|--------|---------------|
| Default (mobile) | < 640 px | 1 colonna, Header + MobileBottomBar, logo solo "V", snap scroll verticale |
| `sm:` | >= 640 px | Card feed con info espansa |
| `lg:` | >= 1024 px | Desktop layout: LeftSidebar + DesktopNavbar, Header nascosto, MobileBottomBar nascosto, CommentSidebar visibile nel feed e nella pagina clip (modalita' chat) |
| `xl:` | >= 1280 px | Layout piu' ampio |

### Tema Dark Gaming

- **Solo tema scuro** — `<html lang="it" className="dark">` hardcoded nel root layout.
- Palette: near-black con undertone blu (`oklch(0.12 0.01 260)` come background).
- Color space: OKLCH per tutti i token colore.
- Primary: viola (`oklch(0.55 0.24 290)`).

### Sistema di Gradiente

| Classe | Uso | Definizione |
|--------|-----|-------------|
| `.gradient-text` | Testo logo "V", titoli accent | `background: linear-gradient(135deg, #7c3aed, #06b6d4)` con background-clip text |
| `.gradient-text-reverse` | Testo logo "p" | `linear-gradient(135deg, #06b6d4, #7c3aed)` |
| `.gradient-bg` | Pulsanti CTA, avatar fallback, progress bar, cerchio carica | `background: var(--gradient)` |
| `.gradient-border` | Bordi accent | Pseudo-element `::before` con maschera |

### Glassmorphism

- Classe `.glass`: `rgba(12, 10, 30, 0.75)` + `backdrop-filter: blur(12px)` + bordo `rgba(124, 58, 237, 0.3)`.
- Usata in: `PopupOverlay` (commenti sovrapposti al video), CTA pubblica nella pagina clip.

### Animazioni Custom

| Keyframe | Uso |
|----------|-----|
| `popup-in` / `popup-out` | Ingresso/uscita popup commenti (translateY + opacity) |
| `spin-gradient` | Rotazione spinner gradiente (360 gradi, 1.5 s lineare) |
| `shimmer` | Effetto shimmer per skeleton loading |

### Scrollbar Personalizzata

- Classe `.scrollbar-thin`: barra sottile (6 px), thumb in `oklch(0.30 0.02 260)`, track trasparente.
- Supporta sia Firefox (`scrollbar-width: thin`) sia WebKit (`::-webkit-scrollbar`).

### Font

- Sans: **Geist Sans** (`--font-geist-sans`)
- Mono: **Geist Mono** (`--font-geist-mono`) — usato per timestamp e durate

---

## 11. Sistema di Navigazione

### Route Groups

```
app/
  (auth)/              # Gruppo autenticazione — layout centrato senza sidebar
    layout.tsx         # Logo brand + tagline, max-w-md
    login/page.tsx     # Form login
    registrati/page.tsx # Form registrazione

  (main)/              # Gruppo principale — layout con sidebar/header/bottombar
    layout.tsx         # Guard auth + LeftSidebar + DesktopNavbar + Header + MobileBottomBar
    home/page.tsx      # Feed principale
    esplora/page.tsx   # Esplorazione/ricerca clip
    carica/page.tsx    # Upload clip (wizard 4 step)
    contest/page.tsx   # Lista contest
    impostazioni/page.tsx # Impostazioni account
    profilo/page.tsx   # Redirect al proprio profilo
    profilo/[username]/page.tsx      # Profilo utente
    profilo/[username]/followers/page.tsx  # Lista follower
    profilo/[username]/following/page.tsx  # Lista seguiti

  clip/[id]/           # Gruppo clip detail — fuori da (main), supporta vista pubblica
    layout.tsx         # Layout minimale per clip
    page.tsx           # Server component che estrae l'ID
    clip-content.tsx   # Client component con tutta la logica
```

### Gerarchia Provider (Root Layout)

```
<html lang="it" className="dark">
  <QueryProvider>           # React Query (staleTime: 30s, retry: 1)
    <AuthProvider>          # Autenticazione JWT, restore session, force-logout
      <LoginTransitionProvider>  # Animazione post-login, overlay
        <TooltipProvider>        # shadcn/ui tooltips (delay: 300ms)
          {children}
          <Toaster />            # Sonner toast (bottom-right, richColors)
        </TooltipProvider>
      </LoginTransitionProvider>
    </AuthProvider>
  </QueryProvider>
</html>
```

### Middleware (Edge)

- File: `frontend/src/middleware.ts`
- Controlla il cookie `session_active`. Se assente, redirect a `/login`.
- Route protette: `/home`, `/esplora`, `/carica`, `/profilo`, `/contest`, `/notifiche`, `/admin`.
- La route `clip/[id]` **non** e' protetta: supporta la vista pubblica (non autenticata).

### Navigazione per Dispositivo

| Dispositivo | Navigazione Primaria | Navigazione Secondaria |
|------------|---------------------|----------------------|
| **Mobile** (< 1024 px) | `MobileBottomBar` (fixed bottom): Home, Esplora, Carica, Profilo | `Header` (sticky top): logo "V", ricerca utenti, avatar dropdown |
| **Desktop** (>= 1024 px) | `LeftSidebar` (collapsible): Home, Esplora, Carica, Profilo, Contest | `DesktopNavbar` (top): ricerca utenti, `DesktopUserMenu` |

### Hook Custom Rilevanti per la Navigazione

| Hook | File | Scopo |
|------|------|-------|
| `useAuth` | `providers/auth-provider.tsx` | Stato autenticazione, login, register, logout |
| `useLoginTransition` | `providers/login-transition-provider.tsx` | Avvia animazione transizione post-login |
| `useMediaQuery` | `lib/hooks/use-media-query.ts` | Media query generica |
| `useIsDesktop` | `lib/hooks/use-media-query.ts` | `>= 1024px` |
| `useIsWideDesktop` | `lib/hooks/use-media-query.ts` | `>= 1280px` |
| `useSnapScroll` | `lib/hooks/use-snap-scroll.ts` | Snap scroll card-by-card nel feed |
