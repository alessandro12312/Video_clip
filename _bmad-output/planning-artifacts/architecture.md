---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - _bmad-output/planning-artifacts/product-brief-Video_clip-2026-02-14.md
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/ux-design-specification.md
  - _bmad-output/project-context.md
  - docs/index.md
  - docs/project-overview.md
  - docs/architecture.md
  - docs/data-models.md
  - docs/api-contracts.md
  - docs/source-tree-analysis.md
  - docs/development-guide.md
workflowType: 'architecture'
project_name: 'Video_clip'
user_name: 'AcchippameQuisso'
date: '2026-02-14'
lastStep: 8
status: 'complete'
completedAt: '2026-02-14'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Requisiti Funzionali (52 FR in 7 categorie):**

| Categoria | FR | Implicazioni architetturali |
|---|---|---|
| **Gestione Utenti** (FR1-FR6) | 6 | Auth JWT, profilo, follow/unfollow — integrazione con backend esistente |
| **Creazione & Gestione Contenuti** (FR7-FR16) | 10 | Pipeline video (upload→validazione→conversione ffmpeg→storage Vercel Blob), **doppio canale**: upload diretto a Django (bypass Next.js 4MB limit), API normali via CORS |
| **Scoperta & Fruizione** (FR17-FR22) | 6 | Feed Home (following), card-to-detail navigation, SSR per link preview OG tags |
| **Commenti & Interazioni** (FR23-FR30) | 8 | Dual-layer commenting (normali + temporizzati), timestamp pre-compilato alla pausa, due viste commenti, like su clip e commenti. **Optimistic UI** per scrittura commenti (feedback immediato, sync in background) |
| **Popup & Engagement Loop** (FR31-FR36) | 6 | Pre-caricamento popup — **decisione architetturale**: endpoint backend dedicato per top comments per timestamp vs calcolo client-side. Overlay sincronizzato al player, soglia minima 1 like, ricalcolo popup post-moderazione |
| **Contest System** (FR37-FR44) | 8 | Bracket eliminazione diretta con albero grafico interattivo — **pattern architetturale distinto** dal resto dell'app (libreria React dedicata, struttura dati ad albero, stato complesso). Release B separata |
| **Admin & Moderazione** (FR45-FR52) | 8 | Interfaccia admin frontend, disabilita commenti, elimina video, sospendi account, notifiche in-app con badge |

**Requisiti Non-Funzionali:**

| Area | Target chiave | Implicazione architetturale |
|---|---|---|
| **Performance** | FCP <1.5s, TTI <3s, video start <2s, popup latency <200ms, API reads <500ms | SSR per pagine pubbliche, pre-caricamento dati popup, lazy loading feed, formato video ottimizzato |
| **Security** | JWT, CORS restrittivo, input validation, vote integrity, file whitelist, max 500MB | Validazione doppia (frontend + backend), constraint DB per unicità voto, sanitizzazione XSS |
| **Resilienza** | Retry ffmpeg (1 retry auto), upload diretto a Django per file grandi | Error boundary frontend, modale retry, gestione upload interrotto |
| **Scalabilità** | 50 utenti concorrenti, 100GB Vercel Blob | Architettura che permette evoluzione verso async (Celery), proxy API, WebSocket senza riscritture maggiori |
| **Accessibilità** | WCAG 2.1 AA base | Radix UI primitives (shadcn/ui), focus management, keyboard nav, alt text, label form |
| **Integrazione** | Django REST, Vercel Blob, ffmpeg, OpenGraph | 4 sistemi esterni, ciascuno con pattern di integrazione specifico |

**Scala & Complessità:**

- Dominio primario: **Full-stack web application** (social network gaming verticale)
- Livello complessità: **Medio-alto**
- Componenti architetturali stimati: **~15-20** (auth, video pipeline, player micro-system, feed system, comment system, contest system, notification system, admin system, layout system, SSR/routing, state management, API layer, storage layer, design system, error handling)

### Technical Constraints & Dependencies

**Vincoli backend esistente (brownfield):**
- Django 5.1.6 + DRF 3.15.1 con pattern consolidati (ViewSet + DefaultRouter, error handling centralizzato, permessi role-based)
- Custom User Model (`cs_clips.User` — SEMPRE `get_user_model()`)
- PostgreSQL 16 (Docker), psycopg 3.x (NON psycopg2)
- moviepy 2.x per calcolo durata (import v2 syntax)
- Contest creati implicitamente da `get_or_create_current_contest()` — nessun CRUD
- Django gira in locale, NON in Docker
- Paginazione globale PageNumberPagination (PAGE_SIZE=10)
- 87 regole documentate per agenti AI in project-context.md

**Gap backend critici (modelli/endpoint mancanti per il PRD):**

| Gap | Impatto | Priorità |
|---|---|---|
| **Modello CommentLike** | Blocca: like sui commenti, calcolo popup, sidebar dinamica — il cuore del prodotto | Critica |
| **Modello Notification** | Blocca: notifiche in-app, badge, engagement loop | Alta |
| **Campo allow_download su Video** | Blocca: download clip da altri utenti | Media |
| **Endpoint top comments per timestamp** | Blocca: popup overlay nel player | Critica |
| **Like sulle clip (modello ClipLike)** | Blocca: FR28 like su clip | Alta |
| **Disabilitazione commenti (soft delete/flag)** | Blocca: moderazione commenti (FR45) | Media |

**Disallineamento backend esistente ↔ PRD:**

| Aspetto | Backend attuale | PRD richiede | Azione |
|---|---|---|---|
| **Rating clip** | Rating 1-5 stelle su clip normali | "N/A — non previsto" nel feed. Rating solo nei contest (1-5 stelle per matchup) | Ripensare uso modello Rating |
| **Contest** | Settimanali automatici, calcolo vincitore per media voto | Bracket eliminazione diretta, votazione per matchup, albero interattivo | Evoluzione significativa modello Contest |
| **Like clip** | Non esiste | FR28: like su clip (binary, non rating) | Nuovo modello |
| **Like commenti** | Non esiste | FR27 + cuore del sistema popup | Nuovo modello CommentLike |

**Vincoli frontend (greenfield):**
- Next.js 16 (Turbopack) + React 19 + TypeScript 5
- App Router (SSR per pagine pubbliche, client components per interattività)
- Tailwind CSS v4 + shadcn/ui (Radix UI) + Framer Motion + Lucide React
- TanStack React Query + Axios + jwt-decode + next-themes
- Deploy target: Vercel (Vercel Blob per storage video)

**Vincoli di integrazione — Doppio canale:**
- **Canale 1 (API)**: CORS diretto Django ↔ Next.js per chiamate API standard (JWT in header Authorization)
- **Canale 2 (Upload)**: Upload video diretto a Django (bypass Next.js API Routes, limite body size 4MB). JWT inviato direttamente a Django
- Video processing sincrono (Celery + Redis rimandato a Fase 2)
- Nessun real-time (fetch-based, polling manuale — WebSocket/SSE rimandato a Fase 2)

**Debito tecnico consapevole MVP:**
- CORS diretto con `CORS_ALLOWED_ORIGINS` restrittivo
- Processing video sincrono
- Nessuna test suite formale
- Nessuna CI/CD
- Bug noti: `RoleBasedPermission.has_object_permission()` e `VideoSerializer.create()` senza `transaction.atomic()`

### Cross-Cutting Concerns Identified

| Concern | Componenti impattati | Priorità |
|---|---|---|
| **Autenticazione JWT cross-layer** | Ogni componente frontend, API layer, stato globale, SSR vs client, **doppio canale upload** | Critica |
| **Pipeline video (doppio canale)** | Upload component, API layer diretto Django, backend processing, storage, error handling, progress tracking | Critica |
| **Player come micro-sistema** | VideoPlayer, PopupOverlay, CommentMarkers (timeline), CommentSidebar, CommentForm (pre-rendered), controlli player — **6 sotto-componenti sincronizzati** | Critica |
| **Optimistic UI** | Scrittura commenti, like, follow — feedback immediato con sync background (React Query mutation + optimistic update) | Alta |
| **Dual-layout (auth vs public)** | Routing, layout components, middleware, SSR, conditional rendering | Alta |
| **Responsive desktop-first → mobile** | Ogni componente UI, layout system, navigation pattern | Alta |
| **Error handling unificato** | API calls, upload, video processing, form validation, toast notifications | Alta |
| **State management** | Auth state (Context), server state (React Query), UI state (local), player state (refs + local) | Alta |
| **Design system consistency** | Tutti i componenti (dark mode, gradient DNA, glassmorphism, 3-tier animations) | Media |
| **Notifiche in-app** | Backend events, frontend badge, notification page, cross-component updates | Media |
| **SEO/OG meta tags** | Pagine clip pubbliche SSR, metadata generation | Media |
| **Release A→B compatibility** | Contest system deve innestarsi senza riscritture; pattern architetturali distinti (bracket tree vs feed/player) | Media |

## Starter Template Evaluation

### Primary Technology Domain

**Full-stack web application** — Frontend Next.js (greenfield, già inizializzato) + Backend Django REST (brownfield esistente)

### Starter già applicato

Il frontend è stato inizializzato con `create-next-app` (Next.js 16, App Router, TypeScript, Tailwind CSS) e successivamente integrato con `npx shadcn init`. Il progetto è in fase di sviluppo attivo con implementazione significativa.

### Stato versioni (verificato Feb 2026)

| Tecnologia | Versione | Ultima stabile | Stato |
|---|---|---|---|
| Next.js | 16.1.6 | 16.1.6 LTS | Aggiornato |
| React | 19.2.3 | 19.2.4 | Patch security disponibile |
| TypeScript | ^5 | 5.x | Aggiornato |
| TailwindCSS | ^4 | 4.x (CSS-first) | Aggiornato |
| shadcn/ui | 3.8.4 (new-york, RSC, unified radix-ui) | 3.8.x | Aggiornato |
| TanStack React Query | ^5.90.21 | 5.90.21 | Aggiornato |
| Framer Motion | ^12.34.0 | 12.34.0 | Aggiornato |
| Axios | ^1.13.5 | 1.13.x | Aggiornato |

### Decisioni architetturali stabilite dallo starter

**Language & Runtime:** TypeScript 5 strict mode, target ES2017, module resolution bundler, path alias `@/*`

**Styling:** Tailwind CSS v4 (CSS-first config, `@tailwindcss/postcss`), CSS variables per theming, shadcn/ui base color neutral

**UI Component Strategy:** shadcn/ui (copy-paste, zero lock-in) con Radix UI unified package per accessibilità. Style new-york. Lucide React per iconografia.

**Animazioni:** Framer Motion 12 (Tier 1+2) + tw-animate-css per micro-animazioni Tailwind (Tier 3)

**State Management:** TanStack React Query per server state, React Context per auth/global state (providers/)

**HTTP Client:** Axios con API layer organizzato in `lib/api/`

**Routing:** Next.js App Router con route groups — `(auth)` per login/registrazione, `(main)` per app autenticata, `clip/` per pagine pubbliche SSR

**Organizzazione codice:** Componenti organizzati per dominio (comments, contest, feed, layout, rating, shared, ui, user, video), non per tipo

**Font:** Geist (sans-serif moderno)

**Linting:** ESLint 9 + eslint-config-next

**Nota:** Aggiornare React da 19.2.3 a 19.2.4 (patch security del 26 gennaio 2026).

## Core Architectural Decisions

### Decision Priority Analysis

**Decisioni critiche (bloccano implementazione):**
- Top comments: endpoint backend dedicato
- JWT storage: access in memory + refresh in localStorage
- Player micro-sistema: VideoPlayerProvider con ref pattern
- Vercel Blob: integrato in Fase 1, upload via Django → Blob
- Evoluzione backend: batch migration per nuovi modelli (CommentLike, ClipLike, Notification, allow_download, is_disabled)

**Decisioni importanti (modellano architettura):**
- Route protection: Middleware + AuthProvider con stato "authenticating"
- API client: Axios interceptors con refresh mutex/queue
- Optimistic UI: React Query mutation pattern
- Server/Client Components boundary con "Server fetch, Client render"
- React Query caching strategy

**Decisioni differite (Post-MVP):**
- Proxy API pattern (Next.js API Routes → Django)
- Processing video asincrono (Celery + Redis)
- Real-time (WebSocket/SSE)
- CI/CD pipeline

### Data Architecture

**Calcolo top comments per timestamp: Backend endpoint dedicato**
- Endpoint `GET /api/videos/{id}/popup-comments/` restituisce lista pre-calcolata `{timestamp, comment_id, text, author, like_count}`
- Rationale: NFR popup latency <200ms, payload minimo, query SQL ottimizzabile (`GROUP BY timestamp, ORDER BY like_count`), logica centralizzata (utile per ricalcolo post-moderazione)
- Impatta: VideoPlayer, PopupOverlay, moderazione commenti

**Evoluzione backend — Batch migration unica "PRD alignment":**

| Modello | Struttura | Pattern |
|---|---|---|
| **CommentLike** | `user` FK + `comment` FK, `unique_together`, CASCADE | Stesso pattern di Rating |
| **ClipLike** (VideoLike) | `user` FK + `video` FK, `unique_together`, CASCADE | Binary like (no valore) |
| **Notification** | `recipient` FK, `type` enum, `content` text, `related_object_id`, `read` bool, `created_at` | Generico per tutti gli eventi |
| **allow_download** | Campo booleano su Video, default True | Aggiunta campo |
| **is_disabled** | Campo booleano su Comment, default False | Soft-delete moderazione |

Tutti i nuovi modelli creati in un'unica batch migration ben pianificata per evitare conflitti. Includere data migration per eventuali nuovi gruppi utente (moderatore).

**Rating esistente: Mantenuto per contest (Release B), ClipLike aggiunto per feed (Release A)**
- Rating 1-5 rimane per votazione matchup contest (Fase B)
- ClipLike binary aggiunto per like clip nel feed (Fase A)
- Due modelli separati, due scopi distinti

**React Query caching strategy:**

| Risorsa | staleTime | Rationale |
|---|---|---|
| Popup data | `5min` | Safety net per tab multipli, invalidazione esplicita dopo like |
| Feed (home/esplora) | `30s` | Aggiornamento frequente |
| Profilo/user | `5min` | Dati stabili |
| Commenti clip | `1min` | Aggiornamento moderato |
| Notifiche | `30s` | Feedback tempestivo |

Invalidazione dopo mutation: like → popup + commenti; commento → lista commenti; upload → feed; follow → profilo

### Authentication & Security

**JWT token storage: Access in memory + Refresh in localStorage**
- Access token: conservato in React state (memory-only). Perso al refresh pagina, mai esposto a XSS persistente
- Refresh token: conservato in localStorage per persistenza sessione
- Al caricamento pagina: chiamata `/api/token/refresh/` per ottenere nuovo access token
- **Stato "authenticating"**: AuthProvider espone uno stato intermedio durante il refresh iniziale → mostra GradientSpinner (UX spec) invece di flash redirect o contenuto vuoto
- Impatta: AuthProvider, Axios interceptor, tutte le API calls, UX primo caricamento

**Route protection: Middleware + AuthProvider**
- `middleware.ts`: intercetta richieste a route `(main)/*`, verifica presenza refresh token, redirect a `/login` se assente
- `AuthProvider` (React Context): gestisce stato utente (profilo, ruolo, token in memory), espone `login()`, `logout()`, `isAuthenticated`, `isAuthenticating`
- Doppio layer: middleware per redirect server-side, AuthProvider per stato client-side

### API & Communication Patterns

**API client: Axios instance con interceptors + refresh mutex**
- `lib/api/client.ts`: Axios instance con `baseURL = NEXT_PUBLIC_API_URL` (unico URL per API e upload)
- Request interceptor: inietta `Authorization: Bearer {access_token}` da AuthProvider
- Response interceptor: su 401 → **mutex/queue pattern**: la prima 401 triggera il refresh, le chiamate successive si accodano e attendono il nuovo token. Previene race condition con refresh token rotation
- Upload: stessa istanza Axios con `Content-Type: multipart/form-data` + `onUploadProgress` callback, stesso `NEXT_PUBLIC_API_URL`

**Optimistic UI: React Query mutation standard**
- Pattern: `useMutation` con `onMutate` (update cache locale ottimistico) → `onError` (rollback snapshot) → `onSettled` (invalidate query)
- Applicato a: commenti, like (clip e commenti), follow/unfollow
- Feedback: commento appare immediatamente, cuore cambia stato al tap, toast Sonner su errore con rollback

### Frontend Architecture

**Player micro-sistema: VideoPlayerProvider con ref pattern**

```
<VideoPlayerProvider>          ← Context: isPlaying, isPaused, duration, seekTo(), popupData[]
  <VideoPlayer>                ← HTML5 <video> + controlli custom, ref al video element
    <PopupOverlay />           ← Glassmorphism popup, legge currentTimeRef via rAF interno
    <CommentMarkers />         ← Dot gradiente sulla progress bar, legge currentTimeRef via rAF interno
  </VideoPlayer>
  <CommentSidebar />           ← Sidebar destra desktop, commenti top likati (no currentTime needed)
  <CommentForm />              ← Pre-rendered (nascosto), legge currentTimeRef solo al momento della pausa (evento)
</VideoPlayerProvider>
```

- **`currentTime` come ref, NON come state** — elimina re-render a cascata (~360/sec). Solo PopupOverlay e CommentMarkers leggono il ref via `requestAnimationFrame` interno
- `popupData[]` caricati in singola API call al mount del provider
- `CommentForm` sempre nel DOM (pre-rendered), toggle visibilità con CSS/Framer Motion per zero latenza emotiva
- CommentSidebar e CommentForm non sottoscrivono currentTime — leggono il ref solo su evento (pausa, submit)

**Server Components vs Client Components — "Server fetch, Client render" pattern:**

| Componente | Tipo | Motivazione |
|---|---|---|
| Root layout | Server | Shell HTML, metadata |
| Layout `(auth)` | Server | Form statici |
| Layout `(main)` | Client (`"use client"`) | AuthProvider, React Query, interattività |
| `/clip/[id]` page | **Server** (SSR) | Fa data fetch (clip metadata + popup data), genera OG meta tags, passa props al Client player via `<Suspense>` |
| Player + commenti | **Client** | Riceve dati iniziali da Server parent, gestisce stato e interazioni |
| Feed pages | Client | React Query, infinite scroll, interazioni |
| Card clip | Client | Hover, lazy loading, like |
| Admin pages | Client | CRUD interattivo |

**Bundle optimization:**
- `dynamic()` + `ssr: false` per componenti Framer Motion pesanti (PopupOverlay, page transitions)
- Code splitting automatico per route (App Router)
- `next/image` per thumbnail con lazy loading
- `<video preload="metadata">` per video (no preload full su feed)
- Font Geist: caricamento ottimizzato via `next/font`

### Infrastructure & Deployment

**Vercel Blob integrato in Fase 1 (con story upload):**

```
Frontend                    Django (backend)                Vercel Blob
   │                            │                              │
   │── POST /api/videos/ ──────►│ (multipart, file + metadata) │
   │   (upload diretto CORS)    │                              │
   │                            │── validate (durata, formato) │
   │                            │── ffmpeg convert             │
   │                            │── PUT blob (retry x3) ──────►│ (REST API, token)
   │                            │◄── blob_url ─────────────────│
   │                            │── save Video(file_url=blob)  │
   │                            │── delete temp files          │
   │◄── 201 {video, file_url} ──│                              │
   │                            │                              │
   │── GET blob_url ────────────┼──────────────────────────────►│ (CDN streaming)
```

- **Retry con backoff esponenziale** sull'upload a Vercel Blob (3 tentativi). Se tutto fallisce: mantieni file convertito locale come fallback, logga errore per retry manuale
- **Playback**: streaming diretto da Vercel Blob CDN (performance globale)
- Singolo `NEXT_PUBLIC_API_URL` per API e upload (stesso host Django, stessa config CORS)

**Environment variables:**

| Variabile | Dove | Valore |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Frontend (.env.local) | URL Django (API + upload) |
| `BLOB_READ_WRITE_TOKEN` | Backend (.env) | Token Vercel Blob |
| `DATABASE_URL` | Backend (.env) | PostgreSQL connection |

### Testing Strategy (pianificazione architetturale)

Non è prevista una test suite completa per MVP, ma l'architettura deve garantire testabilità in queste aree critiche:

| Area | Tipo test | Cosa testare |
|---|---|---|
| Pipeline video (Django → ffmpeg → Blob) | Integration test | Upload, conversione, upload Blob, cleanup |
| Axios refresh interceptor con mutex | Unit test | Race condition 401, queue, retry |
| Optimistic UI rollback | React Testing Library | Mutation → error → rollback cache → toast |
| Endpoint popup-comments | API test | Correttezza calcolo top comment per timestamp |
| Auth flow (refresh al load) | Integration test | Stato authenticating → authenticated → redirect |

### Decision Impact Analysis

**Sequenza implementazione:**
1. Evoluzione backend (batch migration + nuovi endpoint) → sblocca tutto il frontend
2. Auth flow (JWT storage + AuthProvider + interceptors con mutex) → sblocca pagine protette
3. API client + React Query setup → sblocca data fetching
4. Upload pipeline con Vercel Blob → sblocca pagina carica
5. Player micro-sistema (VideoPlayerProvider con ref pattern) → sblocca cuore del prodotto
6. Feed + card-to-detail → sblocca navigazione
7. Commenti + like + optimistic UI → sblocca engagement
8. Notifiche + admin → completa Release A

**Dipendenze cross-componente:**
- Auth flow → necessario per ogni componente che fa API calls
- Backend evolution → necessario prima del frontend (endpoint mancanti)
- Player Provider → necessario prima di PopupOverlay, CommentMarkers, CommentForm, CommentSidebar
- Vercel Blob → necessario per upload funzionante, ma non blocca sviluppo player (mockabile)

## Implementation Patterns & Consistency Rules

### Naming Patterns

**Frontend file naming (conflitto: PascalCase vs kebab-case):**

Un agente potrebbe creare `UserCard.tsx`, un altro `user-card.tsx`. La regola:

| Tipo file | Convenzione | Esempio |
|---|---|---|
| Componenti React | `kebab-case.tsx` | `clip-card.tsx`, `popup-overlay.tsx` |
| Pagine (App Router) | `page.tsx` / `layout.tsx` | (Next.js convention) |
| Hooks custom | `use-kebab-case.ts` | `use-auth.ts`, `use-clip-like.ts` |
| Tipi/interfacce | `kebab-case.ts` | `clip.ts`, `user.ts` |
| Utility | `kebab-case.ts` | `format-date.ts`, `cn.ts` |
| Costanti | `kebab-case.ts` | `query-keys.ts`, `constants.ts` |
| API functions | `kebab-case.ts` | `clips.ts`, `comments.ts` |

Questo segue la convenzione shadcn/ui e Next.js (kebab-case per file, PascalCase per export).

**Frontend export naming (conflitto: named vs default):**

| Tipo | Export | Esempio |
|---|---|---|
| Componenti React | **Named export** | `export function ClipCard() {}` |
| Hooks | **Named export** | `export function useAuth() {}` |
| Tipi/interfacce | **Named export** | `export interface Clip {}` |
| Utility | **Named export** | `export function formatDate() {}` |
| Pagine Next.js | **Default export** | `export default function HomePage() {}` (richiesto da Next.js) |

Regola: **MAI default export** tranne dove Next.js lo richiede (page, layout, error, not-found). Named exports per tutto il resto — permette auto-import e tree shaking migliore.

**Frontend-backend field mapping (conflitto: snake_case vs camelCase):**

Il backend Django restituisce `snake_case` (`created_at`, `timestamp_second`, `like_count`). Il frontend potrebbe:
- A) Usare snake_case ovunque (nessuna trasformazione)
- B) Trasformare in camelCase all'ingresso (`createdAt`, `timestampSecond`)

Decisione: **Opzione A — snake_case ovunque** nel frontend. Nessuna trasformazione, nessun layer di mapping, nessun rischio di inconsistenza. I tipi TypeScript usano snake_case per matchare la risposta API. Più semplice per un solo developer.

```typescript
// ✅ Corretto
interface Clip {
  id: number;
  title: string;
  file_url: string;
  created_at: string;
  timestamp_second: number;
}

// ❌ Evitare
interface Clip {
  id: number;
  title: string;
  fileUrl: string;
  createdAt: string;
  timestampSecond: number;
}
```

---

### Structure Patterns

**Hook organization (conflitto: dove mettere gli hook custom):**

| Tipo hook | Posizione | Esempio |
|---|---|---|
| Hook globali (auth, theme) | `src/lib/hooks/` | `use-auth.ts`, `use-theme.ts` |
| Hook per dominio (clip, commenti) | `src/lib/hooks/` | `use-clip-like.ts`, `use-comments.ts` |
| Hook React Query (queries/mutations) | `src/lib/hooks/` | `use-clip-query.ts`, `use-like-mutation.ts` |

Regola: **tutti gli hooks in `src/lib/hooks/`**, flat (no sotto-cartelle). Un file per hook. Nome che inizia con `use-`.

**API layer organization:**

```
src/lib/api/
├── client.ts          ← Axios instance + interceptors + refresh mutex
├── clips.ts           ← getClips(), getClip(), uploadClip(), deleteClip()
├── comments.ts        ← getComments(), createComment(), deleteComment()
├── likes.ts           ← likeClip(), unlikeClip(), likeComment(), unlikeComment()
├── auth.ts            ← login(), register(), refreshToken()
├── users.ts           ← getUser(), followUser(), unfollowUser()
├── notifications.ts   ← getNotifications(), markAsRead()
└── upload.ts          ← uploadVideo() con progress callback
```

Regola: un file per dominio, funzioni pure che usano l'Axios instance da `client.ts`. Nessuna logica di stato — solo chiamate HTTP.

**Type definition organization:**

```
src/types/
├── clip.ts            ← Clip, ClipCard, ClipDetail, CreateClipPayload
├── comment.ts         ← Comment, CreateCommentPayload, PopupComment
├── user.ts            ← User, UserProfile, AuthTokens
├── notification.ts    ← Notification, NotificationType
├── contest.ts         ← Contest, Bracket, Matchup, Vote
├── api.ts             ← PaginatedResponse<T>, ApiError, ApiResponse
└── index.ts           ← re-export tutto
```

Regola: un file per dominio, `index.ts` per re-export. Usare `interface` per forme di dati (API responses), `type` per union/utility types.

---

### Format Patterns

**API response handling (conflitto: come wrappare le risposte):**

Il backend Django restituisce risposte paginate nel formato DRF:
```json
{ "count": 10, "next": "url", "previous": "url", "results": [...] }
```

E errori nel formato centralizzato:
```json
{ "code": "ValidationError", "detail": "messaggio" }
```

Frontend type:
```typescript
interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

interface ApiError {
  code: string;
  detail: string;
}
```

Regola: **nessun wrapper aggiuntivo** lato frontend. Le risposte API si usano come arrivano. L'Axios interceptor gestisce gli errori globalmente.

**Date handling (conflitto: format, libreria, timezone):**

- Backend: ISO 8601 strings (`2026-02-14T10:30:00Z`)
- Frontend: **nessuna libreria date** per MVP. `new Date(iso_string)` + `Intl.DateTimeFormat` per formattazione locale
- Formato display: relativo per recente ("2 ore fa"), assoluto per vecchio ("14 feb 2026")
- Timezone: UTC dal backend, conversione locale nel browser

---

### Communication Patterns

**React Query key convention (conflitto: stringhe libere vs strutturate):**

```typescript
// src/lib/query-keys.ts
export const queryKeys = {
  clips: {
    all: ['clips'] as const,
    lists: () => [...queryKeys.clips.all, 'list'] as const,
    list: (filters: Record<string, unknown>) => [...queryKeys.clips.lists(), filters] as const,
    details: () => [...queryKeys.clips.all, 'detail'] as const,
    detail: (id: number) => [...queryKeys.clips.details(), id] as const,
    popups: (id: number) => [...queryKeys.clips.all, 'popups', id] as const,
  },
  comments: {
    all: ['comments'] as const,
    byClip: (clipId: number) => [...queryKeys.comments.all, 'clip', clipId] as const,
  },
  users: {
    all: ['users'] as const,
    detail: (id: number) => [...queryKeys.users.all, id] as const,
    me: () => [...queryKeys.users.all, 'me'] as const,
  },
  notifications: {
    all: ['notifications'] as const,
  },
  feed: {
    home: () => ['feed', 'home'] as const,
    explore: () => ['feed', 'explore'] as const,
  },
} as const;
```

Regola: **factory pattern** per query keys. Tutte le chiavi generate da `queryKeys`. MAI stringhe hardcoded nelle query/mutations.

**Toast/notification pattern (conflitto: quando e come mostrare toast):**

| Evento | Toast | Tipo |
|---|---|---|
| Commento inviato | No (optimistic UI, già visibile) | — |
| Like/unlike | No (feedback visivo immediato) | — |
| Upload completato | "La tua clip è live!" | success |
| Upload fallito | "Upload fallito. Riprova?" con azione | error |
| Errore API generico | Messaggio dal backend (`detail`) | error |
| 401 → logout forzato | "Sessione scaduta, effettua di nuovo l'accesso" | warning |
| Follow | No (feedback visivo bottone) | — |

Regola: toast Sonner per **errori e conferme importanti**. MAI toast per azioni optimistic che hanno già feedback visivo.

---

### Process Patterns

**Error handling frontend (conflitto: dove e come gestire errori):**

```
Livello 1: Axios interceptor (globale)
  → 401: refresh + retry + logout se fallisce
  → 5xx: toast generico "Errore del server"
  → Network error: toast "Connessione persa"

Livello 2: React Query onError (per query)
  → Errori specifici business logic gestiti nel componente
  → Toast con messaggio dal backend (detail)

Livello 3: Error Boundary (per route)
  → error.tsx per errori React non gestiti
  → Mostra messaggio user-friendly + "Riprova"

Livello 4: Form validation (locale)
  → Validazione inline prima dell'invio
  → Errori API di validazione mappati ai campi
```

Regola: gli errori si gestiscono **al livello più appropriato**. L'interceptor gestisce auth e network. React Query gestisce errori business. Error boundary è l'ultimo fallback.

**Loading state pattern (conflitto: skeleton vs spinner vs nulla):**

| Contesto | Pattern | Componente |
|---|---|---|
| Primo caricamento app | GradientSpinner (stato authenticating) | `AuthProvider` |
| Feed/liste | Skeleton cards (shimmer) | `ClipCardSkeleton` |
| Pagina dettaglio clip | Skeleton player + skeleton commenti | Dedicati |
| Azioni utente (like, commento) | Nessun loading (optimistic UI) | — |
| Upload video | Progress bar con percentuale | `UploadProgress` |
| Navigazione pagine | Nessun loading visibile (App Router prefetch) | — |

Regola: **skeleton per contenuto**, **spinner solo per auth iniziale**, **nessun loading per azioni optimistic**.

---

### Enforcement Guidelines

**Tutti gli agenti AI DEVONO:**

1. Usare `snake_case` per i campi dati (match backend Django)
2. Named export per tutto tranne pagine/layout Next.js
3. File in `kebab-case.tsx` per componenti, `kebab-case.ts` per il resto
4. Query keys dal factory `queryKeys` — mai stringhe hardcoded
5. Errori gestiti al livello appropriato (interceptor → React Query → Error Boundary)
6. Commenti e messaggi utente in italiano, codice in inglese
7. Un file per hook in `src/lib/hooks/`, un file per dominio in `src/lib/api/`
8. Tipi con `interface` per forme dati, `type` per union/utility
9. Toast solo per errori e conferme importanti, mai per azioni optimistic
10. Skeleton per caricamento contenuto, optimistic UI per azioni utente

## Project Structure & Boundaries

### Complete Project Directory Structure

```
frontend/
├── .env.local                          # NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
├── .env.example                        # [NEW] Template env vars documentato
├── package.json
├── tsconfig.json
├── next.config.ts
├── components.json                     # shadcn/ui (new-york, RSC, neutral)
├── postcss.config.mjs
├── eslint.config.mjs
├── public/
│   ├── file.svg
│   ├── globe.svg
│   ├── next.svg
│   ├── vercel.svg
│   └── window.svg
│
└── src/
    ├── middleware.ts                    # [NEW] Route protection (refresh token check → redirect /login)
    │
    ├── app/
    │   ├── globals.css                 # Tailwind v4 + custom animations + design tokens
    │   ├── layout.tsx                  # Root: QueryProvider > AuthProvider > TooltipProvider
    │   ├── page.tsx                    # Landing: redirect auth→/home, anon→/login
    │   ├── error.tsx                   # Error boundary (Livello 3)
    │   ├── not-found.tsx               # 404
    │   ├── favicon.ico
    │   │
    │   ├── (auth)/                     # Route group: pagine pubbliche auth
    │   │   ├── layout.tsx              # Layout auth (Server Component)
    │   │   ├── login/
    │   │   │   └── page.tsx            # FR1: Login
    │   │   └── registrati/
    │   │       └── page.tsx            # FR2: Registrazione
    │   │
    │   ├── (main)/                     # Route group: pagine protette
    │   │   ├── layout.tsx              # Layout con sidebar + header (Client Component)
    │   │   ├── home/
    │   │   │   └── page.tsx            # FR17: Feed following
    │   │   ├── esplora/
    │   │   │   └── page.tsx            # FR18: Feed esplora/scoperta
    │   │   ├── carica/
    │   │   │   └── page.tsx            # FR7-FR10: Upload video + Vercel Blob
    │   │   ├── profilo/
    │   │   │   ├── page.tsx            # FR5: Profilo personale
    │   │   │   └── [username]/
    │   │   │       └── page.tsx        # FR6: Profilo utente (vista pubblica)
    │   │   ├── contest/
    │   │   │   └── page.tsx            # FR37-FR44: Contest (Release B)
    │   │   ├── notifiche/              # [NEW]
    │   │   │   └── page.tsx            # [NEW] FR48: Pagina notifiche
    │   │   └── admin/                  # [NEW]
    │   │       └── page.tsx            # [NEW] FR49-FR52: Dashboard admin/moderazione
    │   │
    │   └── clip/
    │       └── [id]/
    │           ├── layout.tsx          # OG meta tags (Server Component SSR)
    │           ├── page.tsx            # Server fetch → passa props a clip-content
    │           └── clip-content.tsx    # Client Component: player micro-sistema
    │
    ├── components/
    │   ├── ui/                         # shadcn/ui (18 componenti installati)
    │   │   ├── avatar.tsx
    │   │   ├── badge.tsx
    │   │   ├── button.tsx
    │   │   ├── card.tsx
    │   │   ├── dialog.tsx
    │   │   ├── dropdown-menu.tsx
    │   │   ├── input.tsx
    │   │   ├── label.tsx
    │   │   ├── popover.tsx
    │   │   ├── progress.tsx
    │   │   ├── scroll-area.tsx
    │   │   ├── separator.tsx
    │   │   ├── sheet.tsx
    │   │   ├── skeleton.tsx
    │   │   ├── sonner.tsx
    │   │   ├── tabs.tsx
    │   │   ├── textarea.tsx
    │   │   └── tooltip.tsx
    │   │
    │   ├── layout/
    │   │   ├── header.tsx              # Header responsive con nav + user menu
    │   │   ├── left-sidebar.tsx        # Sidebar desktop
    │   │   └── mobile-bottom-bar.tsx   # Bottom bar mobile
    │   │
    │   ├── shared/
    │   │   ├── empty-state.tsx         # Stato vuoto (nessun contenuto)
    │   │   ├── error-message.tsx       # Messaggio errore riusabile
    │   │   ├── gradient-spinner.tsx    # Spinner auth iniziale
    │   │   ├── infinite-scroll.tsx     # Wrapper infinite scroll
    │   │   ├── page-loader.tsx         # Loader full page
    │   │   ├── tag-badge.tsx           # Badge tag (clutch/funny/fail)
    │   │   ├── timestamp-badge.tsx     # Badge timestamp
    │   │   └── notification-bell.tsx   # [NEW] FR48: Bell icon + badge count
    │   │
    │   ├── feed/
    │   │   ├── clip-card.tsx           # FR17: Card clip nel feed
    │   │   ├── clip-card-skeleton.tsx  # Skeleton loading card
    │   │   └── feed-grid.tsx           # Griglia feed responsiva
    │   │
    │   ├── video/
    │   │   ├── video-player.tsx        # FR20: Player HTML5 + controlli custom
    │   │   ├── player-controls.tsx     # Controlli play/pause/volume/fullscreen
    │   │   ├── progress-bar.tsx        # Barra progresso + seek
    │   │   ├── comment-marker.tsx      # FR32: Dot gradiente sulla timeline
    │   │   ├── popup-overlay.tsx       # FR31: Glassmorphism popup overlay
    │   │   ├── like-button.tsx         # [NEW] FR28: Like clip (toggle cuore)
    │   │   └── upload-progress.tsx     # [NEW] Progress bar upload con percentuale
    │   │
    │   ├── comments/
    │   │   ├── comment-form.tsx        # FR23: Form commento (timestamp pre-compilato)
    │   │   ├── comment-item.tsx        # FR24: Singolo commento
    │   │   ├── comment-list.tsx        # FR25: Lista commenti
    │   │   ├── comment-section.tsx     # Container commenti
    │   │   ├── dynamic-sidebar.tsx     # Sidebar commenti desktop
    │   │   └── comment-like-button.tsx # [NEW] FR27: Like su commento
    │   │
    │   ├── user/
    │   │   ├── user-avatar.tsx         # Avatar utente
    │   │   ├── profile-header.tsx      # FR5: Header profilo
    │   │   ├── follow-button.tsx       # FR4: Bottone follow/unfollow
    │   │   └── username-link.tsx       # Link username cliccabile
    │   │
    │   ├── rating/
    │   │   └── star-rating.tsx         # Rating stelle (contest Release B)
    │   │
    │   ├── contest/                    # [VUOTO — Release B]
    │   │   ├── bracket-view.tsx        # [FUTURE] FR40: Albero bracket interattivo
    │   │   ├── matchup-card.tsx        # [FUTURE] FR41: Card matchup
    │   │   └── vote-button.tsx         # [FUTURE] FR42: Votazione matchup
    │   │
    │   └── admin/                      # [NEW]
    │       ├── user-management.tsx     # [NEW] FR49: Lista utenti + sospensione
    │       ├── content-moderation.tsx  # [NEW] FR50: Moderazione clip/commenti
    │       └── report-list.tsx         # [NEW] FR51: Lista segnalazioni
    │
    ├── lib/
    │   ├── api/
    │   │   ├── client.ts              # Axios instance + interceptors + refresh mutex
    │   │   ├── auth.ts                # login(), register(), refreshToken(), getCurrentUser()
    │   │   ├── videos.ts              # CRUD video + feed + upload
    │   │   ├── comments.ts            # CRUD commenti
    │   │   ├── users.ts               # Profilo + follow/unfollow
    │   │   ├── ratings.ts             # Create/update rating (contest)
    │   │   ├── contests.ts            # getWinners()
    │   │   ├── likes.ts               # [NEW] likeClip, unlikeClip, likeComment, unlikeComment
    │   │   ├── notifications.ts       # [NEW] getNotifications(), markAsRead()
    │   │   └── upload.ts              # [NEW] uploadVideo() dedicato con retry x3 + progress
    │   │
    │   ├── hooks/
    │   │   ├── use-videos.ts          # Hook query video
    │   │   ├── use-comments.ts        # Hook query commenti
    │   │   ├── use-ratings.ts         # Hook query rating
    │   │   ├── use-users.ts           # Hook query utenti
    │   │   ├── use-media-query.ts     # Breakpoint responsive
    │   │   ├── use-intersection.ts    # Intersection observer (infinite scroll)
    │   │   ├── use-like-mutation.ts   # [NEW] Optimistic UI like clip + commenti
    │   │   ├── use-notifications.ts   # [NEW] Query notifiche + markAsRead
    │   │   └── use-upload.ts          # [NEW] Upload con progress + retry
    │   │
    │   ├── constants.ts               # API_BASE_URL, PAGE_SIZE, TAG_COLORS, NAV_ITEMS, timing
    │   ├── query-keys.ts              # Factory pattern chiavi React Query
    │   └── utils.ts                   # cn(), utility generiche
    │
    ├── types/
    │   ├── index.ts                   # Re-export tutti i tipi
    │   ├── api.ts                     # PaginatedResponse<T>, ApiError
    │   ├── user.ts                    # User, UserRegistration, LoginCredentials, TokenPair
    │   ├── video.ts                   # Video, VideoUploadData, VideoTag
    │   ├── comment.ts                 # Comment, CreateCommentData, PopupComment [EXTEND]
    │   ├── rating.ts                  # Rating, CreateRatingData
    │   ├── contest.ts                 # Contest (Release B: Bracket, Matchup, Vote)
    │   ├── notification.ts            # [NEW] Notification, NotificationType
    │   └── like.ts                    # [NEW] ClipLike, CommentLike
    │
    └── providers/
        ├── query-provider.tsx         # QueryClient (staleTime 30s, retry 1)
        ├── auth-provider.tsx          # Auth context (user, tokens, login/logout, isAuthenticating)
        └── video-player-provider.tsx  # [NEW] Player micro-sistema (ref pattern, popupData, seekTo)
```

### Architectural Boundaries

**API Boundary (Frontend ↔ Django):**
- Singolo punto di ingresso: `lib/api/client.ts` (Axios instance)
- Singolo URL: `NEXT_PUBLIC_API_URL` per tutte le chiamate (API + upload)
- JWT iniettato automaticamente via request interceptor
- Errori gestiti via response interceptor (401 → refresh mutex → retry)
- Upload: stessa istanza, `multipart/form-data` + `onUploadProgress`

**Component Boundaries:**

| Boundary | Comunicazione | Stato condiviso |
|---|---|---|
| **Layout ↔ Pages** | Props via layout, React Context per auth | `AuthProvider` (user, isAuthenticated) |
| **Player micro-sistema** | `VideoPlayerProvider` context | currentTimeRef, isPlaying, popupData[], seekTo() |
| **Feed ↔ ClipCard** | Props (clip data) | Nessuno (React Query locale per like) |
| **Comments ↔ Player** | Evento pausa → timestamp, VideoPlayerProvider | currentTimeRef (letto solo su pausa) |
| **Header ↔ Notifications** | `notification-bell.tsx` in header | React Query (notifiche count) |

**Data Boundaries:**

| Layer | Responsabilità | Non deve fare |
|---|---|---|
| `lib/api/*.ts` | Chiamate HTTP pure, nessuna logica | Gestire stato, cache, UI |
| `lib/hooks/*.ts` | React Query wrapper, optimistic UI | Chiamate HTTP dirette, rendering |
| `providers/*.tsx` | Stato globale (auth, player) | Data fetching, rendering componenti |
| `components/*/*.tsx` | Rendering + interazione utente | Chiamate API dirette (usa hooks) |
| `types/*.ts` | Definizioni tipi | Logica, side effects |

### Requirements → Structure Mapping

**FR1-FR6 (Gestione Utenti):**
- Pagine: `(auth)/login`, `(auth)/registrati`, `(main)/profilo`
- Componenti: `user/`, `shared/gradient-spinner.tsx`
- API: `lib/api/auth.ts`, `lib/api/users.ts`
- Provider: `providers/auth-provider.tsx`
- Middleware: `src/middleware.ts`

**FR7-FR16 (Creazione & Gestione Contenuti):**
- Pagine: `(main)/carica`
- Componenti: `video/upload-progress.tsx`
- API: `lib/api/videos.ts`, `lib/api/upload.ts`
- Hooks: `lib/hooks/use-upload.ts`

**FR17-FR22 (Scoperta & Fruizione):**
- Pagine: `(main)/home`, `(main)/esplora`
- Componenti: `feed/clip-card.tsx`, `feed/feed-grid.tsx`, `feed/clip-card-skeleton.tsx`
- API: `lib/api/videos.ts`
- Hooks: `lib/hooks/use-videos.ts`

**FR23-FR36 (Commenti & Interazioni + Popup):**
- Pagine: `clip/[id]` (clip-content.tsx)
- Componenti: `comments/*`, `video/popup-overlay.tsx`, `video/comment-marker.tsx`, `video/like-button.tsx`, `comments/comment-like-button.tsx`
- API: `lib/api/comments.ts`, `lib/api/likes.ts`
- Provider: `providers/video-player-provider.tsx`
- Hooks: `lib/hooks/use-comments.ts`, `lib/hooks/use-like-mutation.ts`

**FR37-FR44 (Contest — Release B):**
- Pagine: `(main)/contest`
- Componenti: `contest/*` (bracket-view, matchup-card, vote-button)
- API: `lib/api/contests.ts`
- Tipi: `types/contest.ts`

**FR45-FR52 (Admin & Moderazione + Notifiche):**
- Pagine: `(main)/admin`, `(main)/notifiche`
- Componenti: `admin/*`, `shared/notification-bell.tsx`
- API: `lib/api/notifications.ts`
- Hooks: `lib/hooks/use-notifications.ts`

### Integration Points

**Interni (Frontend):**

```
AuthProvider ──► Axios interceptor ──► Tutte le API calls
     │
     ▼
VideoPlayerProvider ──► PopupOverlay (rAF + currentTimeRef)
     │                ──► CommentMarkers (rAF + currentTimeRef)
     │                ──► CommentForm (evento pausa → timestamp)
     │
React Query ──► Invalidation cascade:
     │           like → popup + commenti
     │           commento → lista commenti
     │           upload → feed
     │           follow → profilo
     ▼
Sonner Toast ──► Errori API (interceptor livello 1)
               ──► Upload completato/fallito
               ──► Sessione scaduta
```

**Esterni:**

| Servizio | Punto di integrazione | File |
|---|---|---|
| **Django REST API** | `lib/api/client.ts` (Axios) | Tutte le API calls |
| **Vercel Blob CDN** | URL diretta in `<video src>` | `video/video-player.tsx` |
| **Vercel Blob Upload** | Via Django (REST API) | `lib/api/upload.ts` → Django → Blob |
| **Vercel Hosting** | Deploy automatico | `next.config.ts` |

## Architecture Validation Results

### Coherence Validation ✅

**Compatibilità decisioni:**

| Verifica | Stato | Note |
|---|---|---|
| Next.js 16 + React 19 + TypeScript 5 | ✅ | Stack ufficiale, compatibilità confermata |
| Tailwind v4 + shadcn/ui 3.8 (new-york) | ✅ | CSS-first config allineato con PostCSS |
| React Query 5 + Axios interceptors | ✅ | Nessun conflitto, mutex pattern documentato |
| JWT memory + localStorage + middleware | ✅ | Doppio layer coerente (server redirect + client state) |
| Vercel Blob via Django + singolo API URL | ✅ | Pipeline unificata, nessuna config separata |
| Player ref pattern + React 19 | ✅ | useRef stabile in React 19, rAF pattern compatibile |
| snake_case frontend + Django backend | ✅ | Zero trasformazione, tipi TypeScript allineati |
| App Router SSR + "Server fetch, Client render" | ✅ | Pattern supportato nativamente da Next.js 16 |

Nessuna contraddizione identificata tra decisioni architetturali.

**Consistenza pattern:**

| Pattern | Allineamento con stack | Stato |
|---|---|---|
| File kebab-case | shadcn/ui + Next.js convention | ✅ |
| Named exports | Tree shaking + auto-import TS | ✅ |
| Query key factory | TanStack React Query best practice | ✅ |
| 4-level error handling | Axios → React Query → Error Boundary → Form | ✅ |
| Optimistic UI | React Query useMutation pattern | ✅ |
| Toast Sonner solo errori/conferme | Coerente con optimistic UI (no doppio feedback) | ✅ |

**Allineamento struttura:**

| Decisione architetturale | Supporto nella struttura | Stato |
|---|---|---|
| Player micro-sistema | `providers/video-player-provider.tsx` + 5 componenti `video/` + `comments/` | ✅ |
| Doppio canale upload | `lib/api/upload.ts` + `lib/api/client.ts` (stessa istanza) | ✅ |
| Route protection | `src/middleware.ts` + `providers/auth-provider.tsx` | ✅ |
| Notifiche | `(main)/notifiche/`, `shared/notification-bell.tsx`, `lib/api/notifications.ts` | ✅ |
| Admin/moderazione | `(main)/admin/`, `components/admin/*` | ✅ |
| Release A/B separation | Contest in directory separata, tipi estendibili | ✅ |

### Requirements Coverage Validation ✅

**Copertura FR per categoria:**

| Categoria | FR | Copertura architetturale | Stato |
|---|---|---|---|
| Gestione Utenti | FR1-FR6 | Auth flow, profilo, follow — pagine + API + provider | ✅ |
| Creazione Contenuti | FR7-FR16 | Upload pipeline Vercel Blob, video CRUD — pagine + API + hooks | ✅ |
| Scoperta & Fruizione | FR17-FR22 | Feed home/esplora, card, infinite scroll — pagine + componenti + hooks | ✅ |
| Commenti & Interazioni | FR23-FR30 | Commenti temporizzati, like clip/commenti, optimistic UI — tutti i layer | ✅ |
| Popup & Engagement | FR31-FR36 | Popup overlay, comment markers, endpoint dedicato, rAF pattern | ✅ |
| Contest System | FR37-FR44 | Struttura directory pronta, tipi estendibili — Release B | ⏳ (by design) |
| Admin & Moderazione | FR45-FR52 | Admin page, notifiche, moderazione — pagine + componenti + API | ✅ |

**Copertura NFR:**

| NFR | Decisione architetturale | Stato |
|---|---|---|
| FCP <1.5s, TTI <3s | SSR clip pages, App Router prefetch, code splitting | ✅ |
| Video start <2s | Vercel Blob CDN, `<video preload="metadata">` | ✅ |
| Popup latency <200ms | Backend endpoint dedicato, pre-caricamento al mount | ✅ |
| API reads <500ms | React Query caching (staleTime per risorsa), paginazione PAGE_SIZE=10 | ✅ |
| Security JWT/CORS | Memory token, refresh mutex, middleware, CORS restrittivo | ✅ |
| WCAG 2.1 AA | shadcn/ui (Radix UI), keyboard nav, focus management | ✅ |
| 50 utenti concorrenti | Architettura stateless frontend, CDN Vercel, caching React Query | ✅ |

### Implementation Readiness Validation ✅

**Completezza decisioni:**

| Criterio | Stato |
|---|---|
| Versioni tecnologie verificate | ✅ |
| Rationale per ogni decisione | ✅ |
| Esempi concreti per pattern | ✅ |
| Enforcement guidelines (10 regole) | ✅ |
| Sequenza implementazione ordinata | ✅ |

**Completezza struttura:**

| Criterio | Stato |
|---|---|
| Albero directory completo con ogni file | ✅ |
| File annotati con [NEW] vs esistenti | ✅ |
| FR mappati a file specifici | ✅ |
| Boundaries tra layer documentati | ✅ |
| Integration points interni ed esterni | ✅ |

### Gap Analysis Results

**Gap critici:** NESSUNO

**Gap importanti (consapevoli, non bloccanti):**

| Gap | Impatto | Stato |
|---|---|---|
| Dettagli player HTML5 (controlli custom) | UX spec copre i dettagli | Coperto da UX spec |
| Cleanup file temporanei post-upload | Responsabilità backend | Documentato nel pipeline |
| Test suite formale | Debito tecnico MVP consapevole | Aree critiche identificate |

**Gap post-MVP (by design):**
- CI/CD pipeline (GitHub Actions)
- E2E testing (Playwright)
- Monitoring/logging (Vercel Analytics)
- WebSocket per notifiche real-time
- Service worker per offline

### Architecture Completeness Checklist

**✅ Requirements Analysis**
- [x] Contesto progetto analizzato (52 FR, NFR, vincoli)
- [x] Scala e complessità valutate (medio-alta)
- [x] Vincoli tecnici identificati (backend brownfield, 87 regole)
- [x] Cross-cutting concerns mappati (12 concern)
- [x] Gap backend identificati (6 modelli/endpoint mancanti)

**✅ Architectural Decisions**
- [x] Decisioni critiche documentate con versioni
- [x] Stack tecnologico completo e verificato
- [x] Pattern di integrazione definiti
- [x] Considerazioni performance indirizzate
- [x] Party Mode insights integrati (2 sessioni)

**✅ Implementation Patterns**
- [x] Convenzioni naming stabilite
- [x] Pattern struttura definiti
- [x] Pattern comunicazione specificati
- [x] Pattern processo documentati
- [x] 10 enforcement guidelines per agenti AI

**✅ Project Structure**
- [x] Albero directory completo
- [x] Component boundaries stabiliti
- [x] Integration points mappati
- [x] Requirements → structure mapping completo

### Architecture Readiness Assessment

**Status complessivo:** PRONTO PER IMPLEMENTAZIONE

**Livello di confidenza:** ALTO

**Punti di forza:**
- Architettura basata su struttura frontend reale e esistente
- Ogni decisione ha rationale chiaro e esempi concreti
- Party Mode ha identificato e risolto 9 potenziali problemi
- Pattern di enforcement espliciti prevengono drift tra agenti AI
- Sequenza implementazione ordinata per dipendenze reali

**Aree per evoluzione futura:**
- Contest system (Release B)
- Processing video asincrono (Celery + Redis)
- Real-time notifications (WebSocket/SSE)
- CI/CD pipeline e test suite formale
- Proxy API (Next.js API Routes)

### Implementation Handoff

**Linee guida per agenti AI:**
1. Seguire le decisioni architetturali esattamente come documentate
2. Usare i pattern di implementazione in modo consistente
3. Rispettare la struttura progetto e i boundaries tra layer
4. Riferirsi a questo documento per qualsiasi dubbio architetturale
5. File marcati [NEW] vanno creati, file esistenti vanno modificati/estesi

**Prima priorità implementazione:**
1. Evoluzione backend (batch migration + nuovi endpoint)
2. Auth flow (JWT + AuthProvider + interceptors + middleware)
3. API client + React Query setup
4. Upload pipeline con Vercel Blob
5. Player micro-sistema
