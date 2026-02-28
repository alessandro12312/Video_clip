# State Management e API Layer — Frontend Video_clip

> Generato automaticamente il 2026-02-28 | Deep Scan | Workflow: document-project v1.2.0

---

## Panoramica Architetturale

- **HTTP Client**: Axios con istanza pre-configurata `apiClient`
- **Server State**: TanStack React Query v5 (caching, invalidation, optimistic updates)
- **Auth State**: React Context (JWT access in memoria, refresh in localStorage)
- **Transizione Login**: React Context (overlay animato cross-route)

---

## 1. Client HTTP — `apiClient`

**File**: `src/lib/api/client.ts`

- **Base URL**: `${API_BASE_URL}/api` (default `http://127.0.0.1:8000`)
- **Token Strategy**: access token in memoria (MAI in localStorage), refresh in localStorage

### Interceptor Request
- Aggiunge `Authorization: Bearer {accessToken}` se token presente

### Interceptor Response (401 con mutex/queue)
1. Se 401 + refresh token + non retry: enqueue o refresh
2. Se refresh in corso: accoda richiesta in `failedQueue`
3. Altrimenti: `POST /api/token/refresh/` → aggiorna token → rilancia coda
4. Se fallisce: `clearTokens()`, toast "Sessione scaduta", `window.auth:logout`

### API esportate
| Funzione | Descrizione |
|---|---|
| `setTokens(access, refresh)` | Salva in memoria + localStorage + cookie `session_active` |
| `getAccessToken()` | Ritorna access token dalla memoria |
| `getRefreshToken()` | Ritorna refresh (memoria o localStorage) |
| `clearTokens()` | Reset tutto |

---

## 2. Moduli API

### Auth (`src/lib/api/auth.ts`)

| Funzione | Metodo | URL | Auth? |
|---|---|---|---|
| `login` | POST | `/api/token/` | No (usa axios diretto) |
| `register` | POST | `/api/users/` | No |
| `refreshToken` | POST | `/api/token/refresh/` | No |
| `getCurrentUser` | GET | `/api/users/{userId}/` | Sì |

### Comments (`src/lib/api/comments.ts`)

| Funzione | Metodo | URL | Auth? |
|---|---|---|---|
| `getByVideo` | GET | `/api/comments/?video={id}&page={p}` | Sì |
| `create` | POST | `/api/comments/` | Sì |
| `delete` | DELETE | `/api/comments/{id}/` | Sì |

### Contests (`src/lib/api/contests.ts`)

| Funzione | Metodo | URL | Auth? |
|---|---|---|---|
| `getWinners` | GET | `/api/contests/winners/?page={p}` | Sì |

### Ratings (`src/lib/api/ratings.ts`)

| Funzione | Metodo | URL | Auth? |
|---|---|---|---|
| `create` | POST | `/api/ratings/` | Sì |
| `update` | PATCH | `/api/ratings/{id}/` | Sì |

### Users (`src/lib/api/users.ts`)

| Funzione | Metodo | URL | Auth? |
|---|---|---|---|
| `getAll` | GET | `/api/users/?page={p}` | Sì |
| `search` | GET | `/api/users/?search={q}` | Sì |
| `getById` | GET | `/api/users/{id}/` | Sì |
| `follow` | POST | `/api/users/{id}/follow/` | Sì |
| `unfollow` | POST | `/api/users/{id}/unfollow/` | Sì |
| `getFollowers` | GET | `/api/users/{id}/followers/` | Sì |
| `getFollowing` | GET | `/api/users/{id}/following/` | Sì |
| `getByUsername` | GET | `/api/users/by-username/{username}/` | Sì |
| `updateProfile` | PATCH | `/api/users/{id}/` | Sì |

### Videos (`src/lib/api/videos.ts`)

| Funzione | Metodo | URL | Auth? |
|---|---|---|---|
| `getAll` | GET | `/api/videos/?page={p}` | Sì |
| `getById` | GET | `/api/videos/{id}/` | Sì |
| `getFollowingFeed` | GET | `/api/videos/following/?page={p}` | Sì |
| `getTopRated` | GET | `/api/videos/top-rated/?range={r}&page={p}` | Sì |
| `upload` | POST | `/api/videos/` (FormData) | Sì |
| `incrementViews` | POST | `/api/videos/{id}/views/` | Sì |
| `delete` | DELETE | `/api/videos/{id}/` | Sì |

**Helper**: `normalizePaginated<T>()` — normalizza risposte array → formato paginato

---

## 3. Query Keys Factory

**File**: `src/lib/query-keys.ts`

```typescript
queryKeys = {
  videos: {
    all:              ["videos"]
    list(page):       ["videos", "list", page]
    detail(id):       ["videos", "detail", id]
    following(page):  ["videos", "following", page]
    followingAll:     ["videos", "following"]
    topRated(range):  ["videos", "top-rated", range]
    byUser(username): ["videos", "user", username]
  },
  comments: {
    byVideo(videoId): ["comments", "video", videoId]
  },
  ratings: {
    byVideo(videoId): ["ratings", "video", videoId]
  },
  users: {
    detail(id):          ["users", id]
    byUsername(username): ["users", "username", username]
    followers(id):       ["users", id, "followers"]
    following(id):       ["users", id, "following"]
    search(query):       ["users", "search", query]
  },
  contests: {
    winners: ["contests", "winners"]
  }
}
```

**Nota**: `videos.followingAll` è prefisso di `videos.following(page)` → invalidazione fuzzy intenzionale.

---

## 4. React Query Hooks

### Commenti (`src/lib/hooks/use-comments.ts`)

| Hook | Tipo | Query Key | Opzioni |
|---|---|---|---|
| `useComments(videoId)` | useQuery | `comments.byVideo(videoId)` | staleTime: 60s, loop multi-pagina |
| `useCreateComment(videoId)` | useMutation | — | Invalida `comments.byVideo(videoId)` |

### Ratings (`src/lib/hooks/use-ratings.ts`)

| Hook | Tipo | Query Key | Opzioni |
|---|---|---|---|
| `useCreateRating(videoId)` | useMutation | — | Invalida `videos.detail(videoId)` |

### Utenti (`src/lib/hooks/use-users.ts`)

| Hook | Tipo | Query Key | Opzioni |
|---|---|---|---|
| `useUser(id)` | useQuery | `users.detail(id)` | staleTime: 5min |
| `useFollowers(userId, page)` | useQuery | `users.followers(userId)` | staleTime: 5min, placeholderData |
| `useFollowing(userId, page)` | useQuery | `users.following(userId)` | staleTime: 5min, placeholderData |
| `useSearchUsers(query)` | useQuery | `users.search(query)` | enabled: query.length >= 2, staleTime: 30s |
| `useUserByUsername(username)` | useQuery | `users.byUsername(username)` | staleTime: 5min |
| `useFollow()` | useMutation | — | **Optimistic update** + invalidazione ampia |
| `useUnfollow()` | useMutation | — | **Optimistic update** + invalidazione ampia |
| `useUpdateProfile()` | useMutation | — | Invalida detail + byUsername |

**Optimistic updates (follow/unfollow)**: aggiornano `is_followed_by_me` e `followers_count` su `byUsername` e `detail` in `onMutate`, rollback in `onError`.

### Video (`src/lib/hooks/use-videos.ts`)

| Hook | Tipo | Query Key | Opzioni |
|---|---|---|---|
| `useVideo(id)` | useQuery | `videos.detail(id)` | staleTime default (30s) |
| `useVideoFeed()` | useInfiniteQuery | `videos.followingAll` | getNextPageParam via extractPageFromUrl |
| `useTopRatedVideos(range)` | useInfiniteQuery | `videos.topRated(range)` | getNextPageParam via extractPageFromUrl |
| `useUserVideos(username)` | useInfiniteQuery | `videos.byUser(username)` | **Filtraggio client-side** (problema performance) |
| `useIncrementViews()` | useMutation | — | Nessuna invalidazione |
| `useUploadVideo()` | useMutation | — | Invalida `videos.all` |

### Utility (non React Query)

| Hook | File | Descrizione |
|---|---|---|
| `useIntersection(options?)` | `use-intersection.ts` | IntersectionObserver per infinite scroll |
| `useMediaQuery(query)` | `use-media-query.ts` | CSS media query listener |
| `useIsDesktop()` | `use-media-query.ts` | `(min-width: 1024px)` |
| `useIsWideDesktop()` | `use-media-query.ts` | `(min-width: 1280px)` |

---

## 5. Providers

### AuthProvider (`src/providers/auth-provider.tsx`)

**Contesto**:
```typescript
{
  user: User | null
  isAuthenticated: boolean     // !!user
  isAuthenticating: boolean    // true durante restore sessione
  login(username, password): Promise<void>
  register(username, email, password): Promise<void>
  logout(): void
}
```

**Inizializzazione**: refresh token da localStorage → refresh → getCurrentUser(decodifica JWT) → `isAuthenticating = false`

**Side effects**: ascolta `window.auth:logout` dall'interceptor 401

### QueryProvider (`src/providers/query-provider.tsx`)

```typescript
{ staleTime: 30_000, retry: 1, refetchOnWindowFocus: false }
```

### LoginTransitionProvider (`src/providers/login-transition-provider.tsx`)

**Contesto**: `{ startLoginTransition(sourceRect?): void }`

Overlay animato che sopravvive al cambio route auth → main. Usa framer-motion con `getBoundingClientRect`.

### Gerarchia Provider (root layout)

```
QueryProvider → AuthProvider → LoginTransitionProvider → {children}
```

---

## 6. Tipi TypeScript

**File**: `src/types/`

### Generici (`api.ts`)
- `PaginatedResponse<T>`: count, next, previous, results
- `ApiError`: code, detail

### User (`user.ts`)
- `User`: id, username, email?, bio, created_at, updated_at, followers[], following[], followers_count, following_count, is_followed_by_me
- `UserRegistration`: username, email, password
- `LoginCredentials`: username, password
- `TokenPair`: access, refresh

### Video (`video.ts`)
- `VideoTag`: "clutch" | "funny" | "fail"
- `Video`: id, title, file, uploader (username), average_rating, like_count, views, tag, duration, allow_download, contest, created_at, updated_at
- `VideoUploadData`: title, file (File), tag, allow_download?
- `TopRatedRange`: "day" | "week" | "month" | "year" | "all"

### Comment (`comment.ts`)
- `Comment`: id, user (username), video (ID), content, timestamp_second, created_at, updated_at
- `CreateCommentData`: video, content, timestamp_second

### Rating (`rating.ts`)
- `Rating`: id, user (username), video (ID), value, created_at, updated_at
- `CreateRatingData`: video, value

### Contest (`contest.ts`)
- `Contest`: id, name, tag, start_date, end_date, winner (ID|null), is_closed, closed_at

---

## 7. Costanti (`src/lib/constants.ts`)

| Costante | Valore | Uso |
|---|---|---|
| `API_BASE_URL` | `NEXT_PUBLIC_API_URL \|\| "http://127.0.0.1:8000"` | Base URL API |
| `PAGE_SIZE` | 10 | Non usata (paginazione backend) |
| `TAG_COLORS` | `{clutch, funny, fail}` | Classi CSS per tag |
| `TOP_RATED_RANGES` | `[day, week, month, year, all]` | Filtri classifica |
| `NAV_ITEMS` | `[Home, Esplora, Carica, Profilo, Contest]` | Voci navigazione |
| `POPUP_DISPLAY_DURATION_MS` | 4000 | Popup commenti |
| `VIEW_COUNT_DELAY_MS` | 5000 | Delay conteggio views |
| `COMMENT_MARKER_SIZE_PX` | 6 | Marker timeline |

---

## 8. Utility (`src/lib/utils.ts`)

| Funzione | Descrizione |
|---|---|
| `cn(...inputs)` | Merge classi Tailwind (clsx + twMerge) |
| `formatTimestamp(seconds)` | Secondi → "M:SS" |
| `formatRelativeDate(isoDate)` | Data relativa in italiano |
| `formatCount(count)` | 1200 → "1.2K" |
| `extractPageFromUrl(url)` | Estrae `?page=N` per infinite queries |

---

## 9. Mappa Invalidazione Cache

```
useCreateComment(videoId)   → comments.byVideo(videoId)
useCreateRating(videoId)    → videos.detail(videoId)
useFollow()                 → users.detail, users.byUsername, users.followers,
                              users.following(currentUser), videos.followingAll
useUnfollow()               → (stessa mappa di useFollow)
useUpdateProfile()          → users.detail(id), users.byUsername(username)
useUploadVideo()            → videos.all
useIncrementViews()         → (nessuna invalidazione)
```

---

## 10. Gap Noti

1. **`useUserVideos` filtra client-side** — scarica tutti i video e filtra per username (manca endpoint backend `?uploader=`)
2. **`ApiError` tipo mai usato** — definito ma non importato da nessun hook
3. **`PAGE_SIZE` mai usata** — paginazione gestita dal backend
4. **`queryKeys.ratings.byVideo` mai usata** — nessun hook la utilizza
5. **`queryKeys.videos.list(page)` mai usata** — nessun hook corrispondente
6. **Nessun hook per `commentsApi.delete()`** — API esiste, hook mancante
7. **Nessun hook per `ratingsApi.update()`** — API esiste, hook mancante
8. **Nessun hook per `videosApi.delete()`** — API esiste, hook mancante
9. **Tipo `Contest` non usato dagli API modules** — `getWinners()` ritorna `PaginatedResponse<Video>`
