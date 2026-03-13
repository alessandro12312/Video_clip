# Architettura — Frontend Video_clip

> Aggiornato il 2026-03-08 | Deep Scan | Workflow: document-project v1.2.0

---

## Executive Summary

Il frontend è una **Single Page Application con SSR** costruita con Next.js 16.1.6 (App Router) + React 19. Usa un design system dark gaming-themed con TailwindCSS v4, shadcn/ui (Radix UI), e framer-motion. Lo stato server è gestito con TanStack React Query, l'autenticazione con JWT in-memory + localStorage refresh.

---

## Stack Tecnologico

| Categoria | Tecnologia | Versione |
|---|---|---|
| Framework | Next.js (App Router) | 16.1.6 |
| UI | React + Radix UI + shadcn/ui | 19.2.3 / 1.4.3 / 3.8.4 |
| Styling | TailwindCSS v4 + tw-animate-css | ^4 / 1.4.0 |
| State | TanStack React Query | 5.90.21 |
| HTTP | axios | 1.13.5 |
| Animation | framer-motion | 12.34.0 |
| Auth | jwt-decode | 4.0.0 |
| Theme | next-themes | 0.4.6 |
| Icons | lucide-react | 0.564.0 |
| Toast | sonner | 2.0.7 |
| Font | Geist (sans + mono) | 1.7.0 |

---

## Pattern Architetturale

### App Router con Route Groups

```
src/app/
├── layout.tsx              ← Root: Providers + Font + Dark mode
├── (auth)/                 ← Pubblico: login, register
│   └── layout.tsx          ← Centrato, max-w-500px
├── (main)/                 ← Protetto: sidebar + header
│   └── layout.tsx          ← Desktop: LeftSidebar + DesktopNavbar
│                              Mobile: Header + MobileBottomBar
└── clip/[id]/              ← Semi-pubblico: video detail
```

### Provider Hierarchy

```
QueryProvider (staleTime: 30s, retry: 1)
  └─ AuthProvider (JWT context, window.auth:logout)
       └─ LoginTransitionProvider (overlay animato)
            └─ TooltipProvider (delay: 300ms)
                 └─ {children}
```

### Flusso Dati

```
Pagina/Componente
  → React Query Hook (useVideos, useUser, etc.)
    → API Module (videosApi.getAll, etc.)
      → apiClient (axios + JWT interceptors)
        → Backend REST API
```

---

## Design System

### Tema Dark Gaming

| Elemento | Valore |
|---|---|
| **Gradiente brand** | Viola (#7c3aed) → Ciano (#06b6d4) |
| **Background** | oklch(0.12 0.01 260) (near-black blue) |
| **Primary** | oklch(0.55 0.24 290) (vibrant purple) |
| **Glassmorphism** | rgba(12,10,30,0.75) + blur 12px |
| **Font** | Geist Sans + Geist Mono |

### Utility CSS Custom

| Classe | Scopo |
|---|---|
| `.gradient-text` | Testo viola → ciano |
| `.gradient-text-reverse` | Testo ciano → viola |
| `.gradient-bg` | Background gradiente |
| `.gradient-border` | Bordo gradiente via mask |
| `.glass` | Glassmorphism (blur + border + bg) |
| `.scrollbar-thin` | Scrollbar dark personalizzata |

### Animazioni Custom

| Animazione | Durata | Uso |
|---|---|---|
| `popup-in/out` | 300ms | Toast notifications |
| `spin-gradient` | 1.5s infinite | Loading spinner |
| `shimmer` | 2s infinite | Skeleton loading |

---

## Architettura Componenti

### 54 Componenti in 8 Categorie

| Categoria | Count | Componenti chiave |
|---|---|---|
| **Layout** | 5 | LeftSidebar, Header, MobileBottomBar, DesktopNavbar, UserMenu |
| **Feed** | 5 | CardAsPlayer, CardAsPlayerSkeleton, FeedGrid, ClipCard (legacy), ClipCardSkeleton (legacy) |
| **Video** | 5 | VideoPlayer, PlayerControls, ProgressBar, PopupOverlay, CommentMarker |
| **Comments** | 5 | CommentSection, CommentForm, CommentList, CommentItem, CommentSidebar |
| **Rating** | 1 | StarRating (interactive + readonly) |
| **User** | 7 | UserAvatar, FollowButton, ProfileHeader, ProfileEditForm, UserSearchBar |
| **Shared** | 8 | EmptyState, ErrorMessage, GradientSpinner, InfiniteScroll, LoginTransitionOverlay |
| **UI (shadcn)** | 17 | Button, Card, Dialog, Input, Tabs, Tooltip, etc. |
| **Alert** | 1 | AlertDialog (shadcn/ui) |

### Feed UX — Snap Scroll

Il feed (Home, Esplora) usa un sistema di **snap scroll card-by-card**:

- Ogni card riempie il viewport (`h-[calc(100dvh-5.5rem)]`) con layout flex colonna
- Hook `useSnapScroll()` intercetta wheel events su `<main>` e anima lo scroll con `requestAnimationFrame` + easing `easeOutCubic`
- Posizionamento centrato con `getBoundingClientRect` (non `offsetTop`) rispetto al container di scroll
- Anti-bounce: cooldown 600ms post-snap che blocca wheel nella direzione opposta
- Soglia accumulazione delta: 80px per prevenire micro-scroll da trackpad
- Attributo `data-snap-target` sulle card per il targeting JS

### Clip Detail — View Modes

La pagina dettaglio clip (`clip/[id]`) supporta due modalità di visualizzazione commenti:

- **Popup** (default): commenti sovrapposti al video come overlay temporizzati
- **Chat**: sidebar laterale con commenti in tempo reale (solo desktop)
- Toggle via bottone Chat/Popup nella barra azioni
- Bottone Like placeholder (disabilitato, in arrivo)

### Responsive Strategy

| Breakpoint | Layout |
|---|---|
| Mobile (<1024px) | Header (logo V + search + avatar) + MobileBottomBar |
| Desktop (≥1024px) | LeftSidebar (240px, collapsible 64px) + DesktopNavbar |
| Wide (≥1024px) | + CommentSidebar (commenti laterali in modalità chat, pagina clip) |

---

## State Management

### React Query (Server State)

- **22 hooks** in `src/lib/hooks/` (incluso `useSnapScroll`)
- **Infinite Queries**: feed, top-rated, user videos
- **Optimistic Updates**: follow/unfollow con rollback
- **staleTime**: 30s default, 60s commenti, 5min utenti

### Auth Context (Client State)

- Access token: **in-memory only** (security by design)
- Refresh token: localStorage
- Interceptor 401: mutex/queue pattern per concurrent requests

### Login Transition (UI State)

- Overlay animato che sopravvive al cambio route
- Desktop: logo "Video_clip" scala e si sposta verso sidebar
- Mobile: "ideo_clip" dissolve, "V" vola verso header

---

## API Layer

- **7 moduli API** in `src/lib/api/`
- **Query Key Factory** in `src/lib/query-keys.ts`
- **Helper**: `normalizePaginated<T>()` per risposte backend inconsistenti
- **Utility**: `extractPageFromUrl()` per infinite query pagination

---

## Gap e Limitazioni

| Gap | Severità | Note |
|---|---|---|
| `useUserVideos` filtra client-side | Alta | Manca endpoint `?uploader=` backend |
| `ApiError` tipo definito ma mai usato | Bassa | Error handling via toast inline |
| Costanti inutilizzate (PAGE_SIZE, query keys) | Bassa | Dead code |
| Dark mode hardcoded | Bassa | Nessun toggle, design intenzionale |
| Nessun test frontend | Media | Da implementare (Vitest + RTL) |
| SSR non sfruttato | Bassa | Tutti i dati fetch client-side via React Query |
| VideoLike non implementato | Media | Bottone Like presente ma disabilitato |
| ClipCard/ClipCardSkeleton legacy | Bassa | Non importati, sostituiti da CardAsPlayer |
