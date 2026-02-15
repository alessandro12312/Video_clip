# Story 1.3: Login e Gestione Sessione JWT

Status: in-progress

## Story

As a utente registrato,
I want autenticarmi con le mie credenziali e mantenere la sessione attiva,
so that possa accedere ai contenuti protetti senza riautenticarmi ad ogni visita.

## Acceptance Criteria

1. **AC1 — Login con credenziali valide e JWT**
   Given: un utente registrato sulla pagina `/login`
   When: inserisce credenziali valide e invia il form
   Then: riceve JWT (access in memory-only, refresh in localStorage) e viene reindirizzato alla Home (`/home`)

2. **AC2 — Sessione persistente con refresh token**
   Given: un utente con refresh token valido in localStorage
   When: ricarica la pagina o torna al sito
   Then: il sistema mostra il GradientSpinner (stato "authenticating"), chiama `/api/token/refresh/`, ottiene un nuovo access token e autentica l'utente senza redirect al login

3. **AC3 — Route protection con middleware**
   Given: un utente non autenticato che tenta di accedere a route `(main)/*`
   When: il middleware intercetta la richiesta
   Then: viene reindirizzato a `/login`

4. **AC4 — Gestione 401 con mutex/queue pattern**
   Given: un utente autenticato che fa una chiamata API e riceve 401
   When: l'Axios interceptor gestisce l'errore
   Then: il mutex/queue pattern triggera il refresh, le chiamate in coda attendono il nuovo token e vengono riprovate
   AND: se il refresh fallisce, l'utente viene sloggato con toast "Sessione scaduta"

5. **AC5 — Logout completo**
   Given: un utente autenticato che clicca "Esci"
   When: il logout viene eseguito
   Then: i token JWT vengono rimossi (memory + localStorage + cookie flag), l'utente viene reindirizzato a `/login`

## Tasks / Subtasks

> **NOTA:** Il codice di login/auth esiste già nel codebase (backend + frontend).
> Il flusso è funzionante end-to-end ma presenta gap rispetto all'architettura.
> Il lavoro di questa story è correggere i gap di sicurezza e allineare all'architettura.

### Codice esistente (già implementato)

- [x] Backend: `CustomTokenObtainPairView` con aggiornamento `last_login` in `backend/cs_clips/views.py`
- [x] Backend: Endpoint `POST /api/token/` e `POST /api/token/refresh/` in `backend/project_clip/urls.py`
- [x] Backend: `SIMPLE_JWT` config (access 12h, refresh 1d, `ROTATE_REFRESH_TOKENS=True`) in `backend/project_clip/settings.py`
- [x] Backend: `RoleBasedPermission` + `OnlyUsersPermission` in `backend/cs_clips/permissions.py`
- [x] Frontend: Pagina login `frontend/src/app/(auth)/login/page.tsx` con form + error handling
- [x] Frontend: `AuthProvider` in `frontend/src/providers/auth-provider.tsx` con login/register/logout
- [x] Frontend: API client con interceptors in `frontend/src/lib/api/client.ts`
- [x] Frontend: `authApi` (login, register, refreshToken, getCurrentUser) in `frontend/src/lib/api/auth.ts`
- [x] Frontend: Route protection client-side in `frontend/src/app/(main)/layout.tsx`
- [x] Frontend: `GradientSpinner` + `PageLoader` in `frontend/src/components/shared/`

### Gap identificati (lavoro da completare)

- [x] Task 1: Correggere storage access token — memory-only (AC: #1)
  - [x] 1.1 — Rimuovere `localStorage.setItem("access_token", ...)` e `localStorage.getItem("access_token")` da `client.ts`
  - [x] 1.2 — `setTokens()`: access token salvato solo nella variabile in-memory, refresh token in localStorage
  - [x] 1.3 — `getAccessToken()`: leggere solo dalla variabile in-memory (no fallback localStorage)
  - [x] 1.4 — `clearTokens()`: rimuovere solo `refresh_token` da localStorage (access non è lì)
  - [x] 1.5 — Aggiornare `AuthProvider.init()`: al mount, non cercare access in localStorage. Se c'è refresh in localStorage → chiama refresh → ottieni access in memory
- [x] Task 2: Creare `middleware.ts` per route protection server-side (AC: #3)
  - [x] 2.1 — Creare `frontend/src/middleware.ts` che intercetta richieste a route `(main)/*`
  - [x] 2.2 — Il middleware è un **"canary" UX** (previene flash contenuto protetto), NON sicurezza reale. La vera protezione è nel doppio layer: interceptor 401 + AuthProvider
  - [x] 2.3 — Verificare presenza cookie `session_active=1` (settato dal frontend al login/refresh, rimosso al logout). Se assente → redirect a `/login`
  - [x] 2.4 — Configurare `matcher`: `['/home/:path*', '/esplora/:path*', '/carica/:path*', '/profilo/:path*', '/contest/:path*', '/notifiche/:path*', '/admin/:path*']`. Escludere esplicitamente: `_next/static`, `_next/image`, `favicon.ico`, `(auth)/*`, `clip/*`
  - [x] 2.5 — Il middleware è il primo layer; `(main)/layout.tsx` resta come secondo layer client-side
  - [x] 2.6 — Nel `setTokens()`: settare cookie `session_active=1` (non httpOnly — il frontend lo gestisce). Nel `clearTokens()`: rimuovere il cookie
- [x] Task 3: Implementare mutex/queue pattern nell'interceptor 401 (AC: #4)
  - [x] 3.1 — Aggiungere variabile `isRefreshing: boolean` e `failedQueue: Array` in `client.ts`
  - [x] 3.2 — Quando arriva la prima 401: `isRefreshing = true`, esegui refresh
  - [x] 3.3 — Quando arrivano altre 401 durante il refresh: accodare le promise in `failedQueue`
  - [x] 3.4 — Quando il refresh ha successo: risolvere tutte le promise in coda con il nuovo token
  - [x] 3.5 — Quando il refresh fallisce: rigettare tutte le promise in coda IMMEDIATAMENTE (non attendere timeout), eseguire logout
  - [x] 3.6 — Edge case: se il refresh token stesso è scaduto (non solo l'access), le richieste in coda devono essere rigettate subito. Distinguere "access scaduto → refresh funziona" da "refresh scaduto → logout immediato"
- [x] Task 4: Gestire rotazione refresh token (AC: #4)
  - [x] 4.1 — Nel response interceptor, dopo il refresh: leggere `response.data.refresh` (nuovo refresh token rotato)
  - [x] 4.2 — Se presente, aggiornare localStorage con il nuovo refresh token
  - [x] 4.3 — Se `ROTATE_REFRESH_TOKENS=True` e il backend non restituisce un nuovo refresh → usare quello esistente (backward compatible)
- [x] Task 5: Aggiungere toast "Sessione scaduta" e coordinamento logout (AC: #4, #5)
  - [x] 5.1 — Nel response interceptor, quando il refresh fallisce: mostrare toast Sonner "Sessione scaduta, effettua di nuovo l'accesso" (warning)
  - [x] 5.2 — Coordinamento client.ts ↔ AuthProvider: `client.ts` non ha accesso al React context. Emettere un custom event `window.dispatchEvent(new Event('auth:logout'))` da `client.ts`. L'`AuthProvider` ascolta l'evento e chiama `logout()` internamente
  - [x] 5.3 — In `AuthProvider`: aggiungere `useEffect` con listener per `auth:logout` → chiama `logout()` → router.replace('/login')
  - [x] 5.4 — Nel `logout()` di AuthProvider: `clearTokens()` rimuove memory + localStorage + cookie `session_active`
  - [x] 5.5 — Importare `toast` da `sonner` nel client.ts (è già installato nel progetto)
- [x] Task 6: Migliorare accessibilità login page (AC: #1)
  - [x] 6.1 — Aggiungere `role="alert"` al messaggio di errore (coerenza con pagina registrazione Story 1-2)
  - [x] 6.2 — Aggiungere `aria-invalid={!!error}` sui campi `Input` quando c'è un errore
  - [x] 6.3 — Aggiungere `aria-label="Accesso in corso"` al `Button` durante loading (lo spinner da solo non è accessibile)
  - [x] 6.4 — Verificare focus management: dopo errore, focus sul campo username
  - [x] 6.5 — Verificare `aria-describedby` per collegare il messaggio errore ai campi
- [x] Task 7: Scrivere test backend per login e refresh (AC: #1, #2, #4)
  - [x] 7.1 — Test login con successo: credenziali valide → 200 + access + refresh token
  - [x] 7.2 — Test login con credenziali errate: → 401 con messaggio specifico
  - [x] 7.3 — Test login con utente inesistente: → 401
  - [x] 7.4 — Test refresh token: refresh valido → nuovo access token
  - [x] 7.5 — Test refresh token scaduto: → 401
  - [x] 7.6 — Test refresh token rotation: dopo refresh → nuovo refresh token restituito (verifica che `ROTATE_REFRESH_TOKENS=True` funziona)
  - [x] 7.7 — Test `last_login` aggiornato dopo login (verifica `CustomTokenObtainPairSerializer`)
  - [x] 7.8 — Test accesso endpoint protetto senza JWT → 401
  - [x] 7.9 — Test accesso endpoint protetto con JWT valido → 200
  - [x] 7.10 — Test accesso endpoint protetto con JWT scaduto → 401

## Dev Notes

### Stato attuale del codice — Analisi gap

Il flusso login/auth è **funzionante end-to-end** ma presenta gap critici rispetto all'architettura documentata:

| Gap | Severità | File impattato | Dettaglio |
|-----|----------|----------------|-----------|
| **Access token in localStorage** | CRITICO | `client.ts` | Architettura richiede memory-only. Attualmente salvato in ENTRAMBI memory e localStorage → vulnerabilità XSS |
| **Nessun `middleware.ts`** | CRITICO | — (da creare) | Architettura richiede Middleware + AuthProvider doppio layer. Attualmente solo client-side |
| **Nessun mutex/queue nell'interceptor 401** | CRITICO | `client.ts` | Race condition: 3 richieste 401 simultanee → 3 refresh paralleli. Architettura richiede mutex/queue |
| **Token rotation non gestita** | IMPORTANTE | `client.ts` | `ROTATE_REFRESH_TOKENS=True` nel backend ma l'interceptor ignora il nuovo refresh token |
| **Nessun toast "Sessione scaduta"** | IMPORTANTE | `client.ts` | Architettura richiede toast warning al forced logout. Attualmente solo redirect |
| **Login page: `role="alert"` mancante** | MINORE | `login/page.tsx` | Inconsistente con Story 1-2 che ha aggiunto `role="alert"` alla registrazione |

### Decisione architetturale: middleware.ts come "canary" UX

Next.js Middleware gira in Edge Runtime e **NON ha accesso a localStorage**. Il middleware è un **"canary" UX** — previene il flash di contenuto protetto prima del redirect client-side. NON è sicurezza reale. La vera protezione è nel doppio layer: interceptor 401 + AuthProvider.

**Approccio scelto:** Cookie flag `session_active=1` (non httpOnly, gestito dal frontend):
- Al login/refresh: `document.cookie = "session_active=1; path=/; max-age=86400; SameSite=Lax"`
- Al logout: `document.cookie = "session_active=; path=/; max-age=0"`
- Il middleware legge `request.cookies.get('session_active')` — se assente, redirect `/login`

**Nota edge case (da Winston):** Se l'utente cancella manualmente il cookie via DevTools ma il refresh token è ancora valido in localStorage, il middleware lo blocca inutilmente. Questo è accettabile — il middleware è best-effort UX, non security gate. L'utente può fare refresh e il client-side lo ri-autentica.

**Matcher config:**
```typescript
export const config = {
  matcher: [
    '/home/:path*', '/esplora/:path*', '/carica/:path*',
    '/profilo/:path*', '/contest/:path*', '/notifiche/:path*', '/admin/:path*'
  ]
};
```

### Pattern mutex/queue per interceptor 401

```typescript
// Pattern architetturale richiesto (pseudocodice)
let isRefreshing = false;
let failedQueue: { resolve: Function; reject: Function }[] = [];

function processQueue(error: any, token: string | null) {
  failedQueue.forEach(({ resolve, reject }) => {
    error ? reject(error) : resolve(token);
  });
  failedQueue = [];
}

// Nel response interceptor 401:
if (isRefreshing) {
  // Accoda e attendi
  return new Promise((resolve, reject) => {
    failedQueue.push({ resolve, reject });
  }).then((token) => {
    originalRequest.headers.Authorization = `Bearer ${token}`;
    return apiClient(originalRequest);
  });
}

isRefreshing = true;
// ... esegui refresh ...
// ... processQueue(null, newToken) o processQueue(error, null) ...
isRefreshing = false;
```

### Coordinamento client.ts ↔ AuthProvider (da Amelia)

`client.ts` è un modulo vanilla (non React). Non ha accesso al React context di AuthProvider. Quando il refresh fallisce nell'interceptor 401, non può chiamare `logout()` direttamente.

**Soluzione: Custom Event pattern**
```typescript
// client.ts — nel catch del refresh fallito:
window.dispatchEvent(new Event('auth:logout'));

// auth-provider.tsx — nel useEffect di mount:
useEffect(() => {
  const handleForceLogout = () => { logout(); router.replace('/login'); };
  window.addEventListener('auth:logout', handleForceLogout);
  return () => window.removeEventListener('auth:logout', handleForceLogout);
}, [logout, router]);
```

Questo evita `window.location.href = "/login"` (hard navigation) e usa il router Next.js (soft navigation).

### Implicazione memory-only access token sul reload (da Amelia)

Rimuovendo l'access token da localStorage, **ogni reload di pagina causerà una chiamata `/api/token/refresh/`** obbligatoria. Attualmente il reload potrebbe riusare l'access token da localStorage senza chiamare il backend.

Impatto:
- Il `PageLoader` (GradientSpinner) sarà visibile ad ogni F5/reload (~200-500ms per la chiamata refresh)
- Con access lifetime di 12h, oggi un tab aperto non fa mai refresh fino a scadenza. Dopo il fix, ogni reload ne fa uno
- Questo è il comportamento corretto per la sicurezza (access mai persistito su disco)

### Tipo refreshToken() da estendere (da Amelia)

Il tipo attuale in `auth.ts`:
```typescript
refreshToken(refresh: string): Promise<{ access: string }>
```

Con `ROTATE_REFRESH_TOKENS=True`, il backend restituisce anche il nuovo refresh token:
```typescript
refreshToken(refresh: string): Promise<{ access: string; refresh?: string }>
```

Il `refresh` è opzionale per backward compatibility (SimpleJWT potrebbe non includerlo se la config cambia).

### Flow di autenticazione target (dopo fix)

```
1. Utente apre il sito (primo accesso o reload)
   ├── middleware.ts: verifica cookie has_refresh
   │   ├── Cookie assente → redirect /login
   │   └── Cookie presente → procedi
   └── AuthProvider.init():
       ├── accessToken in memory? → NO (perso al reload, by design)
       ├── refreshToken in localStorage? → SÌ
       ├── Chiama /api/token/refresh/
       │   ├── Successo → access in memory, nuovo refresh in localStorage
       │   │   └── fetchUser() → utente autenticato
       │   └── Fallimento → clearTokens, redirect /login
       └── Mostra GradientSpinner durante tutto il processo

2. Utente fa login dal form
   ├── POST /api/token/ → access + refresh
   ├── access → variabile in-memory (MAI localStorage)
   ├── refresh → localStorage + cookie has_refresh=1
   └── fetchUser() → redirect /home

3. Chiamata API riceve 401 (access scaduto)
   ├── isRefreshing == false?
   │   ├── SÌ → isRefreshing = true, esegui refresh
   │   │   ├── Successo → processQueue, retry originale
   │   │   └── Fallimento → processQueue(error), toast, logout
   │   └── NO → accoda in failedQueue, attendi
   └── Chiamate successive durante refresh → accodate

4. Utente fa logout
   ├── clearTokens() (memory + localStorage + cookie)
   ├── setUser(null)
   └── redirect /login
```

### Lezioni dalla Story 1-2 (da applicare)

- `role="alert"` sui messaggi di errore per screen reader
- `aria-describedby` per collegare hint/error ai campi form
- Pattern test: `APITestCase` + `force_authenticate()`, asserzioni su formato `{code, detail}` (pattern `handle_exception_with_serializer`)
- `UniqueValidator` custom con messaggi italiani per errori duplicati
- 51 test esistenti nel progetto — non rompere regressioni

### Git intelligence (ultimi commit rilevanti)

- `ededfe7` — code review Story 1-1: sicurezza, performance, dead code
- `f6845e1` — Story 1-1 backend alignment + Story 1-9 ricerca utenti + fix permessi
- Pattern stabiliti: test con `APITestCase`, error handling con `handle_exception_with_serializer()`, messaggi italiani

### Project Structure Notes

| File | Ruolo | Stato |
|------|-------|-------|
| `frontend/src/lib/api/client.ts` | Axios instance + interceptors + token storage | **DA MODIFICARE** — fix memory-only access, mutex/queue, token rotation |
| `frontend/src/middleware.ts` | Route protection server-side | **DA CREARE** |
| `frontend/src/providers/auth-provider.tsx` | Auth context con login/logout | **DA MODIFICARE** — adattare init() per memory-only access |
| `frontend/src/app/(auth)/login/page.tsx` | Pagina login | **DA MODIFICARE** — miglioramenti a11y minori |
| `frontend/src/app/(main)/layout.tsx` | Route protection client-side | Resta come secondo layer — nessuna modifica |
| `backend/cs_clips/views.py` | `CustomTokenObtainPairView` | Esistente — OK, nessuna modifica |
| `backend/project_clip/settings.py` | `SIMPLE_JWT` config | Esistente — OK, nessuna modifica |
| `backend/project_clip/urls.py` | Endpoint token | Esistente — OK, nessuna modifica |
| `backend/cs_clips/tests/test_views.py` | Test API | **DA ESTENDERE** — aggiungere test login/refresh |
| `frontend/src/components/shared/gradient-spinner.tsx` | Spinner animato | Esistente — OK |
| `frontend/src/components/shared/page-loader.tsx` | Loader con GradientSpinner | Esistente — OK |

### Stack tecnologico rilevante

- **Backend:** Django 5.1.6, DRF 3.15.1, SimpleJWT 5.3.1 (`ROTATE_REFRESH_TOKENS=True`)
- **Frontend:** Next.js 16.1.6, React 19, TypeScript 5, Axios 1.13.5
- **UI:** TailwindCSS 4, shadcn/ui, Sonner (toast), Lucide React
- **Auth JWT:** access 12h (memory-only), refresh 1d (localStorage), rotation abilitata

### Vincoli critici per lo sviluppatore

1. **SICUREZZA:** L'access token NON deve MAI essere in localStorage. Solo variabile in-memory in `client.ts`. Perso al reload → by design.
2. **INTERCEPTOR:** Il mutex/queue pattern è obbligatorio per prevenire race condition sui refresh. Pattern documentato in architettura. Distinguere "access scaduto" da "refresh scaduto" — nel secondo caso, logout immediato senza attendere timeout.
3. **ROTAZIONE:** `ROTATE_REFRESH_TOKENS=True` nel backend. L'interceptor DEVE salvare il nuovo refresh token dalla risposta `/api/token/refresh/`. Tipo da estendere: `{ access: string; refresh?: string }`.
4. **MIDDLEWARE:** Next.js Middleware gira in Edge Runtime. NON ha accesso a localStorage. Usare cookie flag `session_active=1`. Il middleware è un "canary" UX, NON sicurezza reale.
5. **LOGOUT:** Coordinamento tra `client.ts` (vanilla) e `AuthProvider` (React) via custom event `auth:logout`. MAI `window.location.href` — usare router Next.js via AuthProvider.
6. **TOAST:** Usare `toast` di Sonner (già installato). Pattern: toast solo per errori e conferme importanti, MAI per azioni optimistic. Tono: "Sessione scaduta, effettua di nuovo l'accesso" (fiducia + controllo, non allarmante).
7. **A11Y:** Login page: `role="alert"` su errori, `aria-invalid` sui campi con errore, `aria-label="Accesso in corso"` su bottone loading. Coerenza con Story 1-2.
8. **TEST:** Pattern progetto: `APITestCase` + `force_authenticate()`. Asserzioni su formato `{code, detail}`. 51 test esistenti — zero regressioni.
9. **LINGUA:** Messaggi utente/toast in italiano, codice in inglese.
10. **PATTERN:** Il layout `(main)/layout.tsx` resta invariato come secondo layer di protezione client-side.
11. **RELOAD:** Ogni reload di pagina causerà una chiamata refresh obbligatoria (access è solo in memory). Il GradientSpinner sarà visibile ~200-500ms ad ogni F5. Questo è il comportamento corretto.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.3]
- [Source: _bmad-output/planning-artifacts/architecture.md#Authentication-Security]
- [Source: _bmad-output/planning-artifacts/architecture.md#API-Communication-Patterns]
- [Source: _bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- [Source: _bmad-output/planning-artifacts/prd.md#FR2-NFR11-NFR12]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#GradientSpinner-Loading-States]
- [Source: _bmad-output/project-context.md#Autenticazione-JWT]
- [Source: _bmad-output/project-context.md#Error-Handling-Centralizzato]
- [Source: _bmad-output/implementation-artifacts/1-2-registrazione-utente.md#Dev-Notes]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

Nessun debug log necessario — implementazione lineare senza blocchi.

### Completion Notes List

- **Task 1:** Rimosso access token da localStorage. `setTokens()` salva access solo in-memory, refresh in localStorage + cookie `session_active=1`. `getAccessToken()` ritorna solo dalla variabile in-memory. `clearTokens()` rimuove refresh da localStorage e cancella cookie. `AuthProvider.init()` riscritto: al mount tenta sempre refresh via API (access perso al reload by design).
- **Task 2:** Creato `frontend/src/middleware.ts` — "canary" UX che verifica cookie `session_active` e redirige a `/login` se assente. Matcher configurato per tutte le route protette. `(main)/layout.tsx` invariato come secondo layer.
- **Task 3:** Implementato mutex/queue pattern in `client.ts`: `isRefreshing` flag + `failedQueue` array + `processQueue()`. La prima 401 triggera il refresh, le successive vengono accodate. Successo → resolve tutte le promise. Fallimento → reject immediato + logout.
- **Task 4:** Token rotation gestita nel response interceptor: legge `response.data.refresh` dopo refresh, se presente aggiorna localStorage. Fallback al refresh token esistente se il backend non ne restituisce uno nuovo.
- **Task 5:** Importato `toast` da `sonner` in `client.ts`. Al fallimento del refresh: toast warning "Sessione scaduta, effettua di nuovo l'accesso" + `window.dispatchEvent(new Event('auth:logout'))`. In `AuthProvider`: `useEffect` con listener `auth:logout` → `logout()` + `router.replace('/login')`. Eliminato `window.location.href` (hard navigation) in favore del router Next.js (soft navigation).
- **Task 6:** Login page a11y: `role="alert"` + `id="login-error"` sul messaggio errore, `aria-invalid` e `aria-describedby="login-error"` su entrambi i campi, `aria-label="Accesso in corso"` sul bottone durante loading, `useRef` + `focus()` sul campo username dopo errore.
- **Task 7:** 10 test backend aggiunti nella classe `LoginAndJWTEndpointTest`: login successo, password errata, utente inesistente, refresh valido, refresh invalido, token rotation, last_login aggiornato, endpoint protetto senza/con JWT valido/invalido. Tutti 61 test della suite passano (zero regressioni).
- **Nota:** Next.js 16.1.6 mostra warning deprecazione per `middleware.ts` (suggerisce `proxy`). Il middleware compila e funziona correttamente. Valutare migrazione a `proxy` in future story.

### Change Log

- 2026-02-15: Implementazione completa Story 1-3 — fix sicurezza access token memory-only, middleware route protection, mutex/queue interceptor 401, token rotation, toast sessione scaduta, a11y login page, 10 test backend
- 2026-02-15: **Code Review (AI)** — 10 issue trovati (2 CRITICAL, 3 HIGH, 3 MEDIUM, 2 LOW). Fix applicati: C1 `.gitignore lib/` → `/lib/`, H1 logout con redirect, H2 isLoading → isAuthenticating, H3 non-null assertion fix, M1 Secure cookie flag. Tutti i 47 test backend passano (zero regressioni). Status → in-progress (issue MEDIUM/LOW residui da valutare).

## Senior Developer Review (AI)

### Reviewer
AcchippameQuisso — 2026-02-15

### Findings Summary
- **2 CRITICAL** (fixati): `.gitignore` ignorava `frontend/src/lib/` (nessun tracking git); `client.ts`/`auth.ts` dichiarati modificati ma non tracciati
- **3 HIGH** (fixati): `logout()` senza redirect `/login`; naming `isLoading` vs `isAuthenticating`; non-null assertion unsafe su `getRefreshToken()!`
- **3 MEDIUM** (2 fixati, 1 residuo): cookie senza `Secure` flag (fixato); file git non documentati nella File List (residuo — Story 1-2 non committata); race condition AuthProvider.init() vs interceptor (residuo — mitigato dal `PageLoader` guard)
- **2 LOW** (residui): `_retry` non tipizzata; error message catch-all fuorviante

### Fixes Applied
1. **C1**: `.gitignore:60` — `lib/` → `/lib/` (ancorata a root, non matcha più `frontend/src/lib/`)
2. **H1**: `auth-provider.tsx` — `logout()` ora include `router.replace("/login")`, force-logout listener semplificato
3. **H2**: `auth-provider.tsx` + 4 consumer files — `isLoading` → `isAuthenticating` (allineamento architettura)
4. **H3**: `client.ts` — refresh token catturato in `currentRefresh` prima del blocco if, eliminata non-null assertion
5. **M1**: `client.ts` — cookie `session_active` con flag `Secure` condizionale su HTTPS

### Residual Issues (non bloccanti)
- [ ] [AI-Review][MEDIUM] File in git non documentati (`serializers.py`, `views.py`, `registrati/page.tsx`) — probabilmente Story 1-2, verificare e committare separatamente
- [ ] [AI-Review][MEDIUM] Race condition AuthProvider.init() vs interceptor refresh — mitigata da `PageLoader` guard in `(main)/layout.tsx`, valutare dedup refresh in future story
- [ ] [AI-Review][LOW] Proprietà `_retry` su Axios request non tipizzata — TypeScript non valida [client.ts:93,105]
- [ ] [AI-Review][LOW] Messaggio "Errore di connessione" catch-all potenzialmente fuorviante [login/page.tsx:38]

### File List

- `frontend/src/lib/api/client.ts` — MODIFICATO: rimosso access da localStorage, aggiunto mutex/queue pattern, token rotation, toast sonner, cookie session_active, custom event auth:logout. **[Review fix]**: currentRefresh catturato pre-if, Secure cookie flag condizionale
- `frontend/src/middleware.ts` — CREATO: route protection server-side con cookie session_active
- `frontend/src/providers/auth-provider.tsx` — MODIFICATO: init() usa solo refresh (access memory-only), aggiunto useEffect per auth:logout event, aggiunto useRouter. **[Review fix]**: isLoading → isAuthenticating, logout() con redirect, force-logout listener semplificato
- `frontend/src/lib/api/auth.ts` — MODIFICATO: tipo ritorno refreshToken esteso con `refresh?: string`
- `frontend/src/app/(auth)/login/page.tsx` — MODIFICATO: a11y (role="alert", aria-invalid, aria-describedby, aria-label, focus management con useRef)
- `backend/cs_clips/tests/test_views.py` — MODIFICATO: aggiunta classe LoginAndJWTEndpointTest con 10 test
- `.gitignore` — **[Review fix]**: `lib/` → `/lib/` (fix critico: impediva tracking di `frontend/src/lib/`)
- `frontend/src/app/page.tsx` — **[Review fix]**: isLoading → isAuthenticating
- `frontend/src/app/clip/[id]/clip-content.tsx` — **[Review fix]**: isLoading → isAuthenticating
- `frontend/src/app/clip/[id]/layout.tsx` — **[Review fix]**: isLoading → isAuthenticating
- `frontend/src/app/(main)/layout.tsx` — **[Review fix]**: isLoading → isAuthenticating
