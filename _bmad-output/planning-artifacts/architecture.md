---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/product-brief-Video_clip-2026-02-14.md
  - _bmad-output/planning-artifacts/ux-design-specification.md
  - _bmad-output/implementation-artifacts/1-1-evoluzione-backend-migration-prd-alignment.md
  - _bmad-output/project-context.md
  - docs/index.md
  - docs/project-overview.md
  - docs/architecture-backend.md
  - docs/architecture-frontend.md
  - docs/integration-architecture.md
  - docs/api-contracts-backend.md
  - docs/data-models-backend.md
  - docs/component-inventory-frontend.md
  - docs/state-management-frontend.md
  - docs/source-tree-analysis.md
  - docs/development-guide.md
workflowType: 'architecture'
project_name: 'Video_clip'
user_name: 'AcchippameQuisso'
date: '2026-02-28'
lastStep: 8
status: 'complete'
completedAt: '2026-02-28'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Panoramica Requisiti

**Requisiti Funzionali (55 FR):**

Il PRD definisce 55 requisiti funzionali organizzati in 7 categorie. Per ciascuna categoria si riportano i FR con il relativo impatto architetturale.

**Gestione Utenti (6 FR):**
- FR1: Registrazione con username, email, password — richiede Custom User Model (`cs_clips/models/user.py`, estende `AbstractUser`), gruppo `toconfirm` assegnato automaticamente in `perform_create()`
- FR2: Autenticazione con credenziali — JWT stateless via SimpleJWT (`/api/token/`, `/api/token/refresh/`), access token 12h, refresh 1d, rotation attiva
- FR3: Visualizzazione e modifica profilo pubblico — `UserViewSet` con serializer multipli (`UserSerializer`, `UserRegistrationSerializer`), campo `bio` mancante
- FR4: Follow utente — `@action` su `UserViewSet`, relazione M2M asimmetrica `User.following` con `related_name='followers'`
- FR5: Unfollow utente — `@action` su `UserViewSet`, optimistic updates lato frontend con rollback in React Query
- FR6: Visualizzazione liste follower/following — endpoint `GET /api/users/{id}/followers/` e `/following/` esistono ma paginazione non implementata (array piatto)

**Creazione e Gestione Contenuti (10 FR):**
- FR7: Upload clip 10s-1min — `VideoViewSet` con `MultiPartParser`/`FormParser`, salvataggio su MinIO, estrazione durata via MoviePy
- FR8: Validazione durata clip — attualmente solo estrazione durata senza reject automatico (pianificato FR54)
- FR9: Validazione formato clip — whitelist: MP4, MOV, AVI, MKV, WebM, limite 500MB
- FR10: Conversione H.264/MP4 — pianificato, non implementato; file originale su MinIO
- FR11: Titolo e tag per clip — `VideoInputSerializer` con campi `title` (max 100 char), `tag` (clutch/funny/fail)
- FR12: Impostazione allow_download — campo `allow_download` mancante nel modello `Video`
- FR13-FR14: Download clip proprie e altrui — dipende da FR12
- FR15: Storage con URL autenticati — presigned URL MinIO con scadenza 1h, generazione via `minio` client Python con `@lru_cache(maxsize=1)` in `VideoOutputSerializer`
- FR16: Modale errore upload con retry — implementata lato frontend

**Scoperta e Fruizione Contenuti (6 FR):**
- FR17: Feed Home (following) — `GET /api/videos/following/`, paginato, ordinato per `-created_at`, frontend usa `useInfiniteQuery`
- FR18: Pagina dettaglio clip — `/clip/[id]/page.tsx` e' l'unica RSC (SSR), fetch server-side + `generateMetadata` per SEO
- FR19: URL diretto per condivisione — route pubblica `/clip/[id]`
- FR20: Link preview SSR (OG tags) — `generateMetadata` in `/clip/[id]/page.tsx`
- FR21-FR22: Card nel feed con navigazione a dettaglio — componenti `ClipCard` (`clip-card.tsx`), `FeedGrid` (`feed-grid.tsx`), pattern card-to-detail

**Sistema Commenti e Interazioni (8 FR):**
- FR23-FR24: Commenti normali e temporizzati — `CommentViewSet`, campo `timestamp_second` (default=0), validazione `0 <= timestamp_second <= video.duration`
- FR25-FR26: Timestamp pre-compilato alla pausa — logica frontend nel `CommentForm` (`comment-form.tsx`)
- FR27: Like su commenti — modello `CommentLike` mancante, bloccante per il sistema popup
- FR28: Like su clip — modello `VideoLike` mancante
- FR29-FR30: Vista commenti gerarchica e dual-view ("Tutti"/"Nel video") — componenti `CommentSection` (`comment-section.tsx`), `CommentList` (`comment-list.tsx`) con tab via shadcn/ui `Tabs`

**Popup e Loop di Engagement (6 FR):**
- FR31-FR32: Popup overlay durante riproduzione — `PopupOverlay` (`popup-overlay.tsx`), dati pre-caricati in singola chiamata API; `useComments` fa fetch eager di tutte le pagine per costruire `popupMap` (by design)
- FR33: Popup con fade-out dopo 3s — animazione Framer Motion
- FR34: Soglia minima 1 like per promozione — richiede `CommentLike` (mancante)
- FR35: Sidebar Dinamica — `DynamicSidebar` (`dynamic-sidebar.tsx`), commenti piu likati della clip
- FR36: Ricalcolo popup dopo moderazione — richiede campo `is_disabled` su Comment (mancante)

**Sistema Contest (11 FR):**
- FR37: Backoffice admin per creazione contest — da implementare nel frontend
- FR38: Visualizzazione contest disponibili — pagina `/contest/page.tsx` esistente
- FR39a-FR43a (Settimanale auto-gestito): modello `Contest` (`cs_clips/models/contest.py`) con tag, `get_or_create_current_contest()`, APScheduler per chiusura automatica (giovedi 11:33), algoritmo spareggio in `cs_clips/utils/desempate.py` con numpy
- FR39c-FR44b (Bracket Champions League): nessuna infrastruttura esistente — modelli `Bracket`, `Matchup`, `ContestEntry` da progettare da zero

**Amministrazione e Moderazione (8 FR):**
- FR45: Disabilita commenti — richiede campo `is_disabled` (mancante)
- FR46: Elimina video — `DELETE /api/videos/{id}/`, `django-cleanup` gestisce file su MinIO
- FR47: Sospensione account — via campo `is_active` di AbstractUser
- FR48: Promozione ruoli — modifica gruppi Django (`toconfirm` -> `user` -> `admin`)
- FR49: Lista video per utente nell'admin — `VideoAdmin` con filtri, ma manca endpoint `?uploader=` per il frontend
- FR50-FR52: Notifiche in-app — modello `Notification` mancante, nessuna infrastruttura delivery
- FR53: Profilo per username — endpoint `by-username` mancante nel backend, frontend lo chiama gia
- FR54: Validazione durata al reject — da implementare
- FR55: Gestione contest da backoffice frontend — da implementare

---

**Gerarchizzazione per Impatto Architetturale:**

**Tier 1 — Core Loop (fondamenta, senza questi niente app):**
- Auth JWT — funzionante (SimpleJWT, `CustomTokenObtainPairView`, interceptor Axios con mutex/queue per refresh concorrenti)
- Upload video + storage MinIO — funzionante (pipeline upload -> MoviePy durata -> MinIO storage -> presigned URL 1h)
- Feed + visualizzazione — funzionante (`/api/videos/following/`, `/api/videos/top-rated/`, infinite queries React Query)
- Rating/Commenti — parziale (modelli `Rating` e `Comment` esistono e funzionano, ma `CommentLike` e `VideoLike` mancanti rendono il sistema popup non operativo)

**Tier 2 — Social Layer (senza questi, niente engagement):**
- Follow/unfollow — funzionante con bug noti (`Response` import mancante in `user_views.py`), manca endpoint `by-username` (il frontend in `profilo/[username]/page.tsx` lo chiama e riceve 404)
- Notifiche — nulla implementato, DECISIONE ARCHITETTURALE PENDENTE: real-time WebSocket vs polling vs SSE. Il modello `Notification` e' da creare da zero. La scelta tra WebSocket e polling impatta l'intera infrastruttura (Channels/Redis vs endpoint REST periodico)
- VideoLike/CommentLike — modelli mancanti, bloccano FR27, FR28, FR31, FR34, FR35

**Tier 3 — Differenziatori (senza questi, app generica):**
- Contest settimanali — parziale (modello `Contest`, `close_contests`, APScheduler funzionano; mancano backoffice frontend, validazione durata con reject)
- Champions League bracket — da zero, componente architetturale distinto con modelli, logica di progressione turni e UI bracket visualization
- Classifica top-rated — funzionante (`GET /api/videos/top-rated/` con annotazione `Avg`, query param `range`)

---

**Requisiti Non-Funzionali:**

**Performance:**
- First Contentful Paint < 1.5s su pagine pubbliche SSR (`/clip/[id]`)
- Time to Interactive < 3s con priorita al player video
- Video Start Playback < 2s via presigned URL MinIO
- Risposta API lettura < 500ms, scrittura < 1s
- Upload video < 30s per 500MB su connessione stabile
- Latenza popup overlay vs timestamp < 200ms (dati popup pre-caricati al page load)
- Strategia pre-caricamento popup: `useComments` fa fetch eager di tutte le pagine per costruire `popupMap` e `markerPositions` — nessuna chiamata API on-demand durante la riproduzione

**Sicurezza:**
- JWT stateless con refresh token rotation (SimpleJWT 5.3.1), migrazione pianificata a Keycloak
- CORS: `CORS_ALLOW_ALL_ORIGINS = True` — da restringere a origini specifiche prima del deploy
- Validazione input su tutti gli endpoint (DRF serializers + validators)
- Vincolo integrita voto contest: un voto per utente per clip/matchup, enforced backend (`unique_together`) e frontend (UI disabilitata)
- Upload limitato a formati whitelist (MP4, MOV, AVI, MKV, WebM), max 500MB
- Limiti lunghezza input: commenti max 500 char, titolo max 100 char
- Password con requisiti minimi via `create_user()`
- `SECRET_KEY` in `.env` (attualmente presente ma credenziali MinIO hardcoded in `settings.py` — TODO da risolvere)
- `CorsMiddleware` posizionato dopo `CommonMiddleware` — bug noto, dovrebbe essere prima secondo la documentazione `django-cors-headers`

**Resilienza:**
- Error handler centralizzato (`cs_clips/exceptions/error_handler.py`) con formato standard `{code, detail}` via `ErrorResponseSerializer`
- Mapping errori: ValidationError->400, NotAuthenticated->401, PermissionDenied->403, NotFound->404, IntegrityError->409
- Frontend: ogni pagina deve avere `isError` + `<ErrorMessage onRetry={refetch} />` (lezione Epic 1)
- Upload: modale errore con retry e messaggi specifici (durata, formato, connessione)
- Nessun target di uptime rigido per la fase amici

**Scalabilita:**
- MVP: fino a 50 utenti concorrenti con risposta API < 1s
- Storage MinIO self-hosted, file originali senza transcoding — monitorare utilizzo
- Architettura predisposta per Celery + Redis (pacchetti installati, non configurati) e proxy API pattern (Fase 2)
- **Vincolo presigned URL MinIO (scadenza 1h)**: rischio operativo per sessioni di navigazione lunghe. Se un utente tiene aperta una pagina per oltre 1 ora senza ricaricare, le URL dei video scadono e il playback fallisce silenziosamente. Richiede strategia di refresh URL lato frontend (re-fetch periodico o lazy re-fetch al play) — non implementata
- **Vincolo APScheduler single-instance**: APScheduler gira in-process dentro `CsClipsConfig.ready()`. Con scaling orizzontale (multiple istanze Django), lo scheduler eseguirebbe job duplicati. Mitigation richiede lock distribuito (Redis lock, database advisory lock) o migrazione a Celery Beat con Redis broker

**Accessibilita:**
- WCAG 2.1 livello AA base per MVP
- Contrasti colore su dark theme gaming (oklch palette)
- Navigazione keyboard completa (tab, enter, escape)
- Radix UI Primitives (sotto shadcn/ui) garantiscono focus management, ARIA attributes
- Lezione Epic 1: ARIA/a11y deve essere inclusa al primo commit, non retrofittata

**Integrazione:**
- Frontend <-> Backend: REST API JSON, CORS diretto (Fase 2: proxy API pattern)
- Backend <-> PostgreSQL: psycopg 3.2.4, Django ORM
- Backend <-> MinIO: `django-minio-storage` + client `minio` Python
- Backend scheduler: APScheduler in-process
- Frontend <-> MinIO: indiretto via presigned URL nel payload JSON delle risposte backend

---

**Scala e Complessita:**
- Dominio primario: full-stack (Django REST Framework + Next.js React)
- Livello complessita: medio-alto
- Componenti architetturali stimati: ~15-18 (5 modelli backend + 7 moduli API + scheduler + storage + auth + error handling + frontend SPA + SSR layer)
- Frontend: 52 componenti (in 8 categorie: layout 5, feed 3, video 5, comments 5, rating 1, user 7, shared 8, ui/shadcn 18), 6 hook files (in `src/lib/hooks/`), 13 pagine (in `src/app/`), 7 moduli API
- Backend: 5 modelli (in `cs_clips/models/`), 35 endpoint (in 5 domini: users, videos, comments, ratings, contests), struttura modulare `api/{dominio}/` (brownfield)

### Vincoli Tecnici e Dipendenze

1. **Backend brownfield con struttura modulare esistente** — Il backend proviene dal repo Skikky/Video_clip (reset del 2026-02-28), con convenzioni gia stabilite: package `cs_clips/models/` (1 file per modello), `cs_clips/api/{dominio}/` (views + serializers + urls per dominio), `cs_clips/exceptions/` per error handling centralizzato. Ogni modifica deve rispettare questi pattern.

2. **Frontend greenfield GIA SVILUPPATO (asimmetria frontend-avanti)** — Il frontend e' stato sviluppato durante l'Epic 1 e compila correttamente, ma le chiamate API falliranno a runtime per endpoint mancanti (`by-username`, `followers_count`, `is_followed_by_me`, etc.). Questa asimmetria e' strutturale: **il frontend funge da specifica vivente** — ogni hook che chiama un'API inesistente e' un requisito implicito documentato nel codice. I tipi TypeScript in `src/types/` definiscono la shape attesa delle risposte backend. La priorita delle story backend deve essere guidata da cio che il frontend gia chiama.

3. **MinIO S3-compatible per storage** — Self-hosted via Docker Compose, bucket `video` e `video-backup`. Presigned URL con scadenza 1h generate in `VideoOutputSerializer`. Init automatico via `scripts/minio_init.sh` nel container `minio-init`. `django-cleanup 9.0.0` gestisce auto-delete file su model delete.

4. **PostgreSQL 16** — Driver `psycopg 3.2.4` (non psycopg2). Configurazione via `dj-database-url` in settings. 5 tabelle + 3 tabelle M2M. Indici automatici su FK + indici compositi `unique_together` su `Rating(user, video)` e `Contest(start_date, end_date, tag)`.

5. **JWT stateless (SimpleJWT)** — Access token 12h, refresh 1d, rotation attiva. `CustomTokenObtainPairView` aggiorna `last_login`. Frontend: access token in-memory (variabile modulo), refresh in localStorage, cookie `session_active=1` per awareness SSR/middleware. Interceptor Axios con pattern mutex/queue per gestione 401 concorrenti.

6. **APScheduler in-process (single-instance)** — Avvio automatico in `CsClipsConfig.ready()`, cron job `close_contests` ogni giovedi 11:33 UTC. Vincolo: non scalabile orizzontalmente senza lock distribuito. Celery 5.5.3 + Redis 5.2.1 installati ma **non configurati** — non usare.

7. **118 regole AI agent in `project-context.md`** — File di governance per agenti AI con regole critiche su: Custom User Model (`get_user_model()` obbligatorio), struttura modulare, error handling centralizzato, anti-pattern (no `obj.campo += 1`, no import `User` diretto, no Celery), linguaggio (codice in inglese, messaggi UI in italiano, commenti in italiano), testing (Django TestCase, PostgreSQL richiesto, MinIO per test con file).

8. **Monorepo con orchestrazione NPM** — `package.json` root con `concurrently` + `wait-on`, comando `npm run dev` avvia Docker + backend + frontend. Django gira in locale (non in container), PostgreSQL e MinIO in Docker.

9. **Nessun linter/formatter configurato** — No flake8, black, isort, ruff per Python. No Prettier per frontend. ESLint 9 FlatConfig presente ma solo `core-web-vitals`. Nessuna CI/CD.

10. **Framework frontend vincolante** — Framer Motion 12.34.0 (import da `"framer-motion"`, NON `"motion/react"`), TailwindCSS v4 con config-in-CSS (`@theme inline` in `globals.css`), Next.js 16.1.6 App Router con route groups `(auth)/` e `(main)/`.

### Gap Backend — Categorizzazione per Impatto

**Critico (blocca Tier 2):**

- **Modello `Notification` + infrastruttura delivery** — Nessun modello, nessun endpoint, nessuna infrastruttura. La PRD definisce 7 tipi di notifica (commento ricevuto, like ricevuto, commento promosso a popup, contest aperto, invito bracket, turno disponibile, risultati contest). DECISIONE ARCHITETTURALE PENDENTE: WebSocket (Django Channels + Redis — infrastruttura pesante ma real-time vero), polling REST (endpoint `GET /api/notifications/` chiamato periodicamente dal frontend — semplice ma carico su server), oppure SSE (Server-Sent Events — compromesso). Per l'MVP la PRD indica esplicitamente "nessun real-time, fetch-based", suggerendo polling come scelta iniziale.

- **Endpoint `by-username` mancante** — Il frontend in `profilo/[username]/page.tsx` chiama un endpoint per risolvere utenti per username. L'endpoint non esiste nel backend. Risultato: 404 a runtime su ogni navigazione a profilo utente. Impatto diretto sulla funzionalita core di navigazione social.

**Alto (funzionalita core incompleta):**

- **Modelli `VideoLike` e `CommentLike` mancanti** — Bloccano: like su clip (FR28), like su commenti (FR27), sistema popup (FR31, FR34 — il commento con piu like per timestamp non e' calcolabile senza `CommentLike`), Sidebar Dinamica (FR35), algoritmo spareggio (attualmente usa commenti come fallback per il peso 20% che dovrebbe essere "like"). Richiedono: 2 nuovi modelli con `unique_together(user, target)`, endpoint CRUD, migrazione, aggiornamento serializer e views.

- **Endpoint `followers_count`, `following_count`, `is_followed_by_me` mancanti** — Il `UserSerializer` attuale serializza `followers` e `following` come liste complete di utenti. Il frontend si aspetta campi calcolati `followers_count` (intero), `following_count` (intero), `is_followed_by_me` (booleano rispetto all'utente autenticato). Richiede `SerializerMethodField` nel `UserSerializer` con annotazioni `Count()` (con `distinct=True` — lezione Epic 1 su N+1 queries).

- **Sistema Champions League bracket (da zero)** — Modelli necessari: `Bracket` (o estensione di `Contest`), `Matchup` (coppia di video + risultati), `ContestEntry` (iscrizione partecipante con clip). Logica di progressione turni, calcolo vincitore per matchup (per media voti interni), generazione albero bracket. UI: libreria React per bracket visualization. Nessuna infrastruttura esistente.

**Medio (funzionalita presente ma con limitazioni):**

- **`useUserVideos` filtra client-side** — Il hook React scarica tutti i video e filtra per `uploader` in JavaScript. Manca endpoint backend `GET /api/videos/?uploader={id}`. Con crescita dei video, performance degrada linearmente. Richiede aggiunta di `filterset_fields = ['uploader']` al `VideoViewSet` (django-filter gia installato).

- **Hook `useDeleteComment`, `useDeleteVideo`, `useUpdateRating` mancanti** — Gli endpoint backend `DELETE /api/comments/{id}/`, `DELETE /api/videos/{id}/`, `PATCH /api/ratings/{id}/` esistono e funzionano. Mancano i corrispondenti hook React Query nel frontend (`src/lib/hooks/`). Non bloccanti ma necessari per completare il CRUD frontend.

- **Contest settimanali parzialmente implementati** — Funzionano: creazione implicita (`get_or_create_current_contest`), chiusura automatica (APScheduler), algoritmo spareggio (`desempate.py`), endpoint vincitori (`/api/contests/winners/`). Mancano: validazione durata video con reject automatico (FR54), backoffice admin frontend per creazione/monitoraggio contest (FR55), pagina contest completa nel frontend.

- **Paginazione `followers/following` non implementata** — Gli endpoint dichiarano paginazione in OpenAPI ma il codice ritorna array piatti. Il frontend con `normalizePaginated<T>()` potrebbe gestire l'inconsistenza, ma il contratto API e' violato.

**Basso (miglioramenti e debt tecnico):**

- Campo `bio` su `User` — `TextField` opzionale, il frontend ha gia `ProfileEditForm` che si aspetta il campo. Migrazione semplice.
- Campo `allow_download` su `Video` — `BooleanField` default True/False, necessario per FR12-FR14. Migrazione semplice.
- Campo `is_disabled` su `Comment` — `BooleanField` default False, necessario per FR45 (moderazione) e FR36 (ricalcolo popup). Richiede filtro `is_disabled=False` in tutte le query commenti.
- `ApiError` tipo definito ma mai usato — In `src/types/`, error handling attuale via toast inline con Sonner. Dead code.
- `PAGE_SIZE` costante mai usata — Definita in constants ma non utilizzata nelle chiamate API. Dead code.
- Bug `RoleBasedPermission.has_object_permission()` — Controlla `obj.user` ma `Video` ha `obj.uploader` — bug su delete Video. Fix: controllare `getattr(obj, 'uploader', None) or getattr(obj, 'user', None)`.
- Bug import `Response` in `user_views.py` — Follow/unfollow actions crashano a runtime. Fix: aggiungere `from rest_framework.response import Response`.
- `CorsMiddleware` posizionato dopo `CommonMiddleware` — Deve essere prima per funzionamento corretto. Fix: riordinare in `MIDDLEWARE` in `settings.py`.

### Due Sistemi di Contest — Componenti Architetturali Distinti

**Sistema 1: Contest Settimanali (parzialmente implementato)**

- **Modello**: `Contest` (`cs_clips/models/contest.py`) con campi `name`, `tag` (clutch/funny/fail), `start_date`, `end_date`, `is_closed`, `closed_at`, `winner` (FK a Video)
- **Vincolo unicita**: `unique_together = ('start_date', 'end_date', 'tag')` — un contest per tag per settimana
- **Creazione implicita**: `get_or_create_current_contest(tag)` in `cs_clips/utils/get_date_util.py` — il contest viene creato al primo upload della settimana per quel tag, non via CRUD esplicito
- **Settimana contest**: lunedi -> sabato (non domenica)
- **APScheduler**: cron trigger ogni giovedi 11:33 UTC, `close_contests` management command (`cs_clips/management/commands/close_contests.py`)
- **Algoritmo spareggio**: `cs_clips/utils/desempate.py` con numpy — normalizzazione min-max (percentile) su 3 metriche: numero voti 50%, visualizzazioni 30%, numero commenti 20% (commenti come fallback per like fino a implementazione `VideoLike`)
- **Chiusura manuale**: `POST /api/contests/end/` con `OnlyAdminsPermission`
- **Idempotenza**: sia APScheduler che `EndContestView` verificano `is_closed` prima di chiudere
- **Edge case**: contest chiuso nella stessa settimana genera nuovo contest con suffisso numerico (`(2)`, `(3)`)
- **Endpoint lettura**: `GET /api/contests/winners/` — ritorna Video vincitori (non oggetti Contest), paginato

**Sistema 2: Champions League Bracket (da progettare da zero)**

- **Modelli necessari** (non esistenti):
  - `Bracket` o estensione di `Contest` con tipologia bracket — configurazione torneo (numero partecipanti, numero turni)
  - `ContestEntry` — iscrizione partecipante con clip associata
  - `Matchup` — coppia di entry per turno con risultati (voti per ciascuna clip, vincitore)
- **Logica di progressione turni**: il vincitore di ogni matchup (per media voti interni, nessun fattore esterno) avanza al turno successivo. Generazione automatica bracket a eliminazione diretta
- **UI bracket visualization**: albero grafico interattivo con scontri, clip embedded, voti e risultati per turno. Richiede libreria React dedicata o componente custom SVG/Canvas
- **Backoffice admin**: creazione manuale da admin, monitoraggio progressione, chiusura turni
- **Premi**: Fase 1 premi finanziati Video_clip (skins, crediti in-game shop); Fase 2 partnership con publisher
- **Nessuna infrastruttura esistente** — componente architetturale completamente distinto dal Sistema 1

### Cross-Cutting Concerns Identificati

1. **Autenticazione/Autorizzazione (JWT + Role-Based Permissions)**
   Sistema trasversale a tutti gli endpoint. SimpleJWT genera token, `RoleBasedPermission` controlla accesso per gruppo Django (`toconfirm` read-only, `user` CRUD proprio, `admin` tutto), `OnlyUsersPermission` e `OnlyAdminsPermission` per azioni specifiche. Frontend: `AuthProvider` React Context, interceptor Axios con mutex/queue per 401, cookie `session_active` per middleware Next.js. Il JWT attraversa l'intera catena: frontend (in-memory) -> header HTTP -> backend (autenticazione) -> serializer (utente corrente in `perform_create`).

2. **Gestione errori centralizzata (error_handler.py + ErrorMessage frontend)**
   Backend: `handle_exception_with_serializer` configurato globalmente in `REST_FRAMEWORK['EXCEPTION_HANDLER']`, formato standard `{code, detail}` via `ErrorResponseSerializer`. Mapping: ValidationError->400, NotAuthenticated->401, PermissionDenied->403, NotFound->404, IntegrityError->409. Frontend: componente `ErrorMessage` (`src/components/shared/error-message.tsx`) con props `message`, `onRetry`, `className`. Lezione Epic 1: error handling mancante in 5+ story — ogni pagina con fetch DEVE avere `isError` + `<ErrorMessage onRetry={refetch} />`.

3. **Paginazione (DRF PageNumberPagination + React Query infinite queries)**
   Backend: `PageNumberPagination` globale con `PAGE_SIZE=10`, formato `{count, next, previous, results}`. Frontend: `useInfiniteQuery` con `getNextPageParam` via `extractPageFromUrl()` (parsa URL `next` dal payload Django). Helper `normalizePaginated<T>()` per risposte backend inconsistenti (es. followers/following che ritornano array piatto). Le custom actions nei ViewSet devono usare `self.paginate_queryset()` + `self.get_paginated_response()`.

4. **Cache invalidation (React Query — lezione Epic 1: chiavi precise)**
   Pattern appreso durante Epic 1: MAI invalidare chiavi generiche come `["users"]`. Le chiavi React Query devono essere precise e mirate (es. `["users", userId, "followers"]`). `staleTime` differenziato: 30s default, 60s commenti, 5min utenti. Optimistic updates completi su follow/unfollow con `onMutate` -> `onError` rollback -> `onSettled` invalidate. `placeholderData: (prev) => prev` per paginazione senza layout shift.

5. **Upload e storage media (MinIO presigned URL con vincolo 1h)**
   Pipeline: FormData frontend -> `MultiPartParser` Django -> file temporaneo -> estrazione durata MoviePy -> salvataggio MinIO -> presigned URL in risposta. `django-cleanup` auto-delete file orfani. **Vincolo presigned URL 1h**: rischio operativo per sessioni lunghe. URL video scadono dopo 1 ora — se l'utente tiene aperta una pagina senza ricaricare, il playback fallisce silenziosamente. `@lru_cache(maxsize=1)` sul client MinIO potrebbe restituire URL gia scadute in cache. Nessuna strategia di refresh implementata lato frontend. Richiede decisione architetturale: re-fetch periodico, lazy re-fetch al play, o estensione TTL presigned URL.

6. **Real-time/Notifiche (decisione architetturale pendente)**
   MVP esplicitamente "nessun real-time, fetch-based". La Sidebar Dinamica crea l'illusione di attivita senza WebSocket. Le notifiche (7 tipi definiti nella PRD) richiedono infrastruttura delivery. Opzioni: (a) polling REST — semplice, compatibile con architettura attuale, ma carico su server con molti utenti; (b) WebSocket via Django Channels + Redis — real-time vero, richiede infrastruttura aggiuntiva; (c) SSE — compromesso leggero. La decisione impatta: modello Notification, endpoint API, infrastruttura (Redis, Channels), frontend (EventSource o WebSocket client), Docker Compose.

7. **Accessibilita (ARIA, keyboard nav — lezione Epic 1)**
   Radix UI Primitives (sotto shadcn/ui) forniscono focus management, keyboard navigation, ARIA attributes di base. Lezione Epic 1: a11y retrofittata in 4+ story — deve essere inclusa al primo commit. Requisiti: WCAG 2.1 AA, contrasti su dark theme, navigazione keyboard completa (tab/enter/escape), alt text su thumbnail, player con controlli keyboard, label su tutti i form. Componente `focus:ring` via CSS variable `--ring` del design system.

8. **Responsive design (desktop sidebar + mobile bottom bar)**
   Due layout distinti gestiti da breakpoint `lg` (1024px). Desktop: `LeftSidebar` (240px, collassabile a 64px) + `DesktopNavbar` + opzionale `DynamicSidebar` (>=1280px). Mobile: `Header` (logo "V" + search + avatar) + `MobileBottomBar` (Home, Esplora, Upload, Profilo). Hook `useMediaQuery` (`use-media-query.ts`) per logica condizionale. Login transition con animazione differenziata: desktop (logo intero scala + sposta verso sidebar), mobile ("ideo_clip" dissolve, "V" vola verso header).

9. **Internazionalizzazione (UI in italiano, nessun framework i18n)**
   Regola critica da `project-context.md`: codice (classi, variabili, URL) in inglese, commenti/docstring Python in italiano, messaggi API e `help_text` in italiano, UI frontend (label, placeholder, testi) in italiano. Nessun framework i18n (next-intl, react-i18next) — le stringhe sono hardcoded in italiano nel codice. Se in futuro si richiedesse il multilingua, sarebbe un refactoring significativo.

10. **Validazione input (frontend + backend — DRF serializers)**
    Doppia validazione: frontend (form validation, limiti lunghezza) + backend (DRF serializer `validate()`, `MinValueValidator`/`MaxValueValidator` su Rating, validazione `timestamp_second <= video.duration` su Comment). Business logic sempre nel serializer, mai nella view. `VideoInputSerializer.create()` gestisce assegnazione contest e calcolo durata. Pattern: `perform_create()` per iniettare utente autenticato (`serializer.save(user=request.user)` per Rating/Comment, `serializer.save(uploader=request.user)` per Video).

11. **Logging e monitoring (non implementato)**
    Nessun sistema di logging strutturato configurato. Prometheus 0.22.1 e Flower 2.0.1 presenti in requirements ma non configurati. APScheduler logga su stdout. Nessun error tracking (Sentry, etc.), nessun APM, nessuna dashboard. Per la fase amici non e' bloccante, ma rende il debugging di problemi in produzione significativamente piu difficile.

12. **Testing (nessun test automatizzato — sia backend che frontend)**
    Backend: directory `cs_clips/tests/` cancellata nel reset, da ricreare. `test_spareggio.py` e' un management command manuale, non un test Django. Nessun pytest, conftest.py, coverage, CI. Test richiedono PostgreSQL + MinIO attivi (Docker). Regole: `django.test.TestCase` come base, `APITestCase` + `APIClient` per test API, `force_authenticate()` per JWT, setup utente con gruppo obbligatorio. Frontend: nessun test (Vitest + RTL da implementare). L'assenza di test automatizzati e' un rischio trasversale che impatta ogni modifica futura.

13. **Asimmetria frontend-avanti (frontend come specifica vivente)**
    Concern trasversale unico di questo progetto: il frontend e' piu avanzato del backend. Ogni hook in `src/lib/hooks/` che chiama un endpoint inesistente (es. `by-username`), ogni tipo TypeScript in `src/types/` che definisce campi non presenti nell'API (es. `bio`, `followers_count`, `is_followed_by_me`), ogni componente che renderizza dati non disponibili (es. like count su commenti) e' di fatto un requisito implicito. Il backend deve essere sviluppato "inseguendo" il frontend. Questo inverte il flusso tradizionale (API-first) e richiede che le story backend siano prioritizzate in base a cio che il frontend gia consuma. Il rischio e' che il frontend accumuli workaround (filtri client-side, fallback a valori default, endpoint finti) che poi diventano debito tecnico.

## Starter Template Evaluation

### Dominio Tecnologico Primario

Full-stack brownfield: Django REST API (backend) + Next.js React App (frontend). Entrambi i lati sono gia inizializzati e operativi con codice in produzione-sviluppo.

### Valutazione Starter — Progetto Brownfield

Questo progetto **non richiede un nuovo starter template**. Entrambi gli stack sono gia inizializzati:

**Backend — Inizializzato manualmente (non da starter):**
- `django-admin startproject project_clip` + `startapp cs_clips` con ristrutturazione manuale verso architettura modulare
- Nessun starter CLI usato — struttura custom `models/` package, `api/{dominio}/`, `exceptions/`

**Frontend — Inizializzato con `create-next-app`:**
- `npx create-next-app@latest` con opzioni: TypeScript, App Router, TailwindCSS, ESLint, `src/` directory, import alias `@/*`
- Successivamente arricchito con: shadcn/ui (`npx shadcn@latest init`), React Query, Axios, Framer Motion

### Stack Tecnologico Stabilito

**Decisioni Architetturali gia Prese dal Codebase:**

**Linguaggio e Runtime:**
- Backend: Python 3.x, Django 5.1.6, DRF 3.15.1
- Frontend: TypeScript 5 strict, React 19, Next.js 16.1.6
- Nessuna possibilita di cambio senza riscrittura completa

**Soluzione Styling:**
- TailwindCSS v4 con configurazione in-CSS (`@theme inline` in `globals.css`)
- shadcn/ui (variante New York, tema neutral, icone Lucide)
- Palette oklch dark-theme oriented con variabili CSS custom
- `cn()` utility (clsx + tailwind-merge) per merge classi

**Build Tooling:**
- Frontend: Turbopack (Next.js built-in), `next build` per produzione
- Backend: nessun build step (Python interpretato)
- Docker Compose per infrastruttura (PostgreSQL, MinIO, pgAdmin)

**Testing Framework:**
- Backend: nessuno configurato (Django TestCase + APITestCase raccomandati da project-context.md)
- Frontend: nessuno configurato (Vitest + React Testing Library raccomandati)
- Deficit critico — da colmare come cross-cutting concern

**Organizzazione Codice:**
- Backend: `cs_clips/models/{modello}.py`, `cs_clips/api/{dominio}/{dominio}_{tipo}.py`, barrel exports via `__init__.py`
- Frontend: `src/app/(auth|main)/`, `src/components/{dominio}/`, `src/lib/api/`, `src/lib/hooks/`, `src/types/`

**Esperienza Sviluppo:**
- Hot reload: Django `runserver` (auto-reload), Next.js Fast Refresh (Turbopack)
- Debug: Django Debug Toolbar non installato, React DevTools + React Query DevTools non configurati
- Linting: ESLint 9 FlatConfig (core-web-vitals) per frontend, nessun linter Python
- Nessun pre-commit hook, nessun Prettier, nessun formatter automatico

**Nota:** Non e' necessaria una story di inizializzazione progetto. La prima story implementativa deve invece colmare i gap infrastrutturali (testing, linting) come parte del setup di sviluppo.

### Gap Infrastruttura Sviluppo — "Story 0" Prerequisiti

I seguenti gap infrastrutturali devono essere colmati **prima** di qualsiasi feature story. Non sono feature — sono acceleratori che rendono ogni story successiva piu veloce e sicura.

**Linting e Formatting (backend):**
- **ruff** come linter + formatter Python — sostituisce flake8, black, isort in un unico tool
- Configurazione in `pyproject.toml` con regole allineate alle 118 regole di `project-context.md`
- Senza enforcement automatico, ogni agente AI produce codice con stili diversi

**Linting e Formatting (frontend):**
- ESLint 9 FlatConfig gia presente ma solo `core-web-vitals` — estendere con regole React hooks, import order
- Prettier non configurato — aggiungere per formatting consistente di TSX/CSS

**Editor Configuration:**
- `.editorconfig` alla root — tab vs spaces, line endings, trailing whitespace
- Particolarmente critico su Windows (piattaforma di sviluppo)

**Debug Tools (dev-only):**
- **Django Debug Toolbar** — visibility su query SQL, N+1 detection, cache hits. Con N+1 queries come problema ricorrente (Epic 1 retro), e' uno strumento essenziale. Richiede 5 righe di config in `settings.py`
- **React Query DevTools** — gia installato come dipendenza di `@tanstack/react-query`, basta un import nel `QueryProvider`. Indispensabile per debugging cache invalidation, stale data, refetch patterns

**Validazione Environment:**
- Validazione env vars al build time — `env.ts` con Zod (`z.string().url()`) per catturare config mancanti. Attualmente `NEXT_PUBLIC_API_URL` fallback silenzioso a `http://127.0.0.1:8000` senza warning

### Strategia Testing Risk-Based

**Principio**: test a livello piu basso sono i piu preziosi. Unit > Integration > E2E.

**Backend — Baseline Critica (5 test che, se falliscono, l'app e' rotta):**

1. **Auth flow** — registrazione crea utente con gruppo `toconfirm`, login ritorna JWT valido, refresh rinnova token
2. **Permissions** — `RoleBasedPermission` enforces gruppi (`toconfirm` read-only, `user` CRUD proprio, `admin` tutto), `has_object_permission` funziona su Video (campo `uploader`, non `user`)
3. **Upload pipeline** — upload video -> estrazione durata MoviePy -> salvataggio MinIO -> presigned URL valido in risposta
4. **Contest closure** — `close_contests` chiude solo contest scaduti, assegna vincitore corretto, e' idempotente
5. **Algoritmo spareggio** — `desempate.py` con dati noti produce vincitore atteso, gestisce parita, gestisce contest senza video

**Prerequisito test backend:**
- `conftest.py` con fixture riusabili: `authenticated_user` (utente con gruppo `user` + token), `admin_user`, `sample_video` (con file MinIO), `api_client_authenticated` (APIClient con `force_authenticate`)
- Docker (PostgreSQL + MinIO) necessario per test — non SQLite

**Frontend — Baseline Critica (hook con logica complessa):**
- `useFollow`/`useUnfollow` — optimistic update su 4+ query keys con rollback in `onError`
- `useUploadVideo` — gestione FormData, progress, invalidazione `videos.all`
- `useComments` — fetch eager multi-pagina per costruzione `popupMap`

**Prerequisito test frontend:**
- Vitest + React Testing Library
- MSW (Mock Service Worker) per mock API senza dipendenza dal backend

### CI/CD Minimale Raccomandato

Pipeline GitHub Actions con quality gates:

```
trigger: push su main + pull request

jobs:
  backend:
    - ruff check (lint)
    - ruff format --check (formatting)
    - python manage.py test (con PostgreSQL + MinIO in services)

  frontend:
    - npm run lint (ESLint)
    - npx vitest run (test)
    - npm run build (verifica compilazione)
```

Nessun deploy automatico nella fase attuale — solo quality gates per prevenire regressioni.

## Decisioni Architetturali Core

### Analisi Priorità Decisioni

**Decisioni Già Prese (dal codebase e Step 3):**
- Auth: JWT stateless SimpleJWT (access 12h, refresh 1d, rotation attiva)
- Storage: MinIO S3-compatible (presigned URL 1h)
- Database: PostgreSQL 16 + psycopg 3.2.4
- API: REST con DRF 3.15.1
- Frontend framework: Next.js 16.1.6 App Router + React 19
- State management: React Query + Axios (interceptor mutex/queue per 401)
- Styling: TailwindCSS v4 + shadcn/ui (New York, neutral, Lucide)
- Error handling: centralizzato (`error_handler.py` + `ErrorMessage` frontend)
- Paginazione: `PageNumberPagination` PAGE_SIZE=10 + `useInfiniteQuery`
- Deploy: Docker Compose (PostgreSQL, MinIO, pgAdmin)
- Contest settimanali: APScheduler in-process (cron giovedì 11:33 UTC)
- Responsive: dual layout desktop (sidebar) / mobile (bottom bar)
- i18n: italiano hardcoded, nessun framework i18n

**Decisioni Critiche Risolte: 6**

---

### D1: Notifiche Delivery → Polling REST

- **Decisione**: Endpoint `GET /api/notifications/` con polling periodico dal frontend
- **Intervallo**: 15 secondi (non 30s — feedback loop più rapido, carico trascurabile per 50 utenti: ~200 req/min)
- **Rationale**: Zero infrastruttura aggiuntiva — nessun Redis, nessun Channels, nessun WebSocket. Compatibile con l'architettura attuale (SimpleJWT + REST). Per 50 utenti concorrenti il carico è trascurabile
- **Modello `Notification`**: campi `recipient` (FK User), `sender` (FK User nullable), `type` (7 tipi PRD: commento ricevuto, like ricevuto, commento promosso a popup, contest aperto, invito bracket, turno disponibile, risultati contest), `is_read` (BooleanField), `created_at` (DateTimeField), **FK espliciti nullable** (`video` FK, `comment` FK, `contest` FK, `bracket` FK) — NO `GenericForeignKey` per evitare N+1 queries, join impossibili e complessità nei test
- **Alternativa scartata (GenericFK)**: `GenericForeignKey` richiederebbe query extra per risolvere `content_object`, niente `select_related`, setup `ContentType` nei test fragile e verbose. Con FK espliciti o JSONField i test sono triviali e le query performanti
- **Migrazione futura**: se il polling diventa un bottleneck (>500 utenti), migrazione a SSE o WebSocket. L'endpoint REST rimane comunque per lettura/mark-as-read
- **Impatta**: nuovo modello `Notification`, endpoint API `notifications/`, hook React Query `useNotifications` con `refetchInterval: 15000`

### D2: Champions League Bracket → Modelli Separati (Opzione B)

- **Decisione**: Modelli `Bracket`, `ContestEntry`, `Matchup` completamente indipendenti da `Contest`
- **Rationale**: I due sistemi (settimanale auto-gestito vs bracket eliminazione diretta) hanno cicli di vita, regole di business e UI completamente diversi. Condividere un modello base creerebbe complessità inutile
- **Struttura file**: `cs_clips/models/bracket.py`, `cs_clips/models/contest_entry.py`, `cs_clips/models/matchup.py`
- **Dominio API separato**: `cs_clips/api/brackets/` con views, serializers e urls propri — NON sotto `/api/contests/`. I due sistemi non condividono nulla, trattarli come domini API distinti previene confusione nelle URL e nei permessi
- **Impatta**: 3 nuovi modelli, nuovo dominio API `/api/brackets/`, UI bracket visualization, backoffice admin

### D3: Presigned URL Refresh → Lazy Re-fetch al Play

- **Decisione**: Al fallimento del `<video>`, il frontend ri-chiama `videos.detail(id)` per ottenere una nuova presigned URL
- **Retry cap**: massimo 2 tentativi. Se entrambi falliscono, mostrare messaggio "Video non disponibile, ricarica la pagina"
- **UX re-fetch silenzioso**: durante il re-fetch il player mostra un mini-spinner (lo stesso del caricamento iniziale), MAI un flash di errore. L'utente non deve percepire il problema tecnico
- **Implementazione**: catch `onerror` nel player video → mostra spinner → `refetch()` React Query → nuovo URL → retry playback → se fallisce dopo 2 tentativi → messaggio fallback
- **Vincolo `@lru_cache`**: verificare che `@lru_cache(maxsize=1)` sul client MinIO in `VideoOutputSerializer` non restituisca URL stantie. Il re-fetch deve produrre una URL effettivamente nuova — potrebbe essere necessario invalidare la cache o rimuovere `@lru_cache` dal metodo di generazione URL
- **Impatta**: componente player video, hook `useVideo`, `VideoOutputSerializer` (verifica lru_cache)

### D4: Testing Stack

- **Backend**: `django.test.TestCase` + `APITestCase` con `conftest.py` per fixture condivise
- **Frontend**: Vitest + React Testing Library + MSW (Mock Service Worker)
- **Rationale**: Stack raccomandato da `project-context.md`, compatibile con infrastruttura esistente (PostgreSQL + MinIO per backend), zero dipendenza backend per test frontend (MSW intercetta HTTP)
- **Scope preciso Story 0 — conftest.py con esattamente 5 fixture**:
  1. `authenticated_user` — utente con gruppo `user` + token JWT
  2. `admin_user` — utente con gruppo `admin` + token JWT
  3. `sample_video` — video con file MinIO reale caricato
  4. `api_client_authenticated` — `APIClient` con `force_authenticate()`
  5. `sample_contest` — contest attivo con tag e date validi
- **Scope preciso Story 0 — MSW handlers per 5 endpoint critici**:
  1. `POST /api/token/` (login)
  2. `POST /api/users/` (register)
  3. `GET /api/videos/` (videos list)
  4. `GET /api/videos/{id}/` (video detail)
  5. `GET /api/users/{id}/` (user profile)
- **Altre fixture e handlers si aggiungono incrementalmente**, story-by-story
- **Impatta**: Story 0 prerequisiti, CI/CD pipeline

### D5: Linter Backend → ruff

- **Decisione**: `ruff` come unico linter + formatter Python
- **Configurazione**: `pyproject.toml` con regole allineate alle 118 regole `project-context.md`
- **Rationale**: Sostituisce flake8 + black + isort in un singolo tool. Performance 10-100x superiore. Configurazione unificata
- **Impatta**: Story 0, CI/CD pipeline

### D6: Rate Limiting API → DRF Throttling Built-in

- **Decisione**: `REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']` con classi built-in
- **Rates**: `anon: 100/hour`, `user: 1000/hour`, `upload: 10/hour` (custom `ScopedRateThrottle` su `VideoViewSet`)
- **Rationale**: Zero dipendenze aggiuntive, configurazione in `settings.py`. Per 50 utenti concorrenti è più che sufficiente
- **Timing**: configurare i throttle rates in `settings.py` subito in Story 0 — non differire al deploy. Costa 5 righe di configurazione e serve come documentazione vivente dei limiti del sistema. Differire al deploy rischia che venga dimenticato
- **Migrazione futura**: se necessario rate limiting distribuito, migrazione a `django-ratelimit` + Redis
- **Impatta**: `settings.py` (Story 0), `VideoViewSet` (scope custom per upload)

### D7: Rimozione Dipendenze Inutilizzate — Celery e Redis

- **Decisione**: Rimuovere `celery==5.5.3` e `redis==5.2.1` da `requirements.txt`
- **Rationale**: APScheduler gira in-process senza dipendenze esterne. Celery e Redis sono installati ma non configurati — nessun `celery.py`, nessun `@shared_task`, nessun `CELERY_BROKER_URL`. Peso morto che genera confusione ("perché ci sono se non li usiamo?")
- **Quando reinstallare**: se in futuro servono task asincroni pesanti (transcoding H.264, notifiche push, elaborazione batch), si reinstallano con la configurazione appropriata (`celery.py`, broker URL, worker separato)
- **Impatta**: `requirements.txt` (Story 0)

---

### Decisioni Differite (Post-MVP)

- **Transcoding H.264**: rimandato fino a quando non si presentano problemi di compatibilità browser con formati originali
- **Keycloak migration**: JWT SimpleJWT sufficiente per MVP, Keycloak per multi-tenant/SSO
- **CDN**: presigned URL MinIO dirette per ora, CDN quando latenza diventa un problema
- **Logging strutturato**: Prometheus/Flower presenti in requirements ma non configurati — da attivare al deploy
- **Scaling orizzontale APScheduler**: lock distribuito (Redis lock o database advisory lock) necessario solo con multiple istanze Django
- **WebSocket/SSE notifiche**: migrazione da polling REST solo se polling diventa bottleneck (>500 utenti)

### Analisi Impatto Decisioni

**Sequenza Implementazione:**
1. D5 (ruff) + D4 (testing fixtures) + D6 (throttle rates) + D7 (rimozione celery/redis) → **Story 0 prerequisiti**
2. D1 (notifiche polling) → richiede modello `Notification` con FK espliciti + endpoint + hook frontend con `refetchInterval: 15000`
3. D3 (presigned URL refresh) → modifica player video (spinner + retry cap 2 + verifica lru_cache)
4. D2 (bracket) → Epic dedicato, indipendente — può procedere in parallelo con Tier 2

**Dipendenze Cross-Componente:**
- D1 (notifiche) dipende da `VideoLike` e `CommentLike` per i tipi "like ricevuto" e "commento promosso a popup"
- D2 (bracket) è completamente indipendente — dominio API separato, modelli separati, può procedere in parallelo
- D4 (testing), D5 (ruff), D6 (throttle), D7 (cleanup) sono prerequisiti per tutte le altre decisioni — compongono Story 0
- D3 (presigned URL) è autocontenuto nel player video, nessuna dipendenza da altre decisioni

## Implementation Patterns & Consistency Rules

**Punti di conflitto potenziali identificati: 12 aree** dove agenti AI diversi potrebbero fare scelte incompatibili. Tutti i pattern sono estratti dal codebase esistente e dalle 118 regole di `project-context.md`.

### Naming Patterns

**Database (Django ORM — già stabiliti, non modificare):**
- Tabelle: Django auto-genera in `snake_case` plurale (`cs_clips_video`, `cs_clips_contest`)
- Colonne: `snake_case` (`created_at`, `timestamp_second`, `is_closed`)
- FK: `{relation}_id` auto (`uploader_id`, `contest_id`)
- M2M: tabella ponte auto (`cs_clips_user_following`)
- Indici compositi: `unique_together` (`('user', 'video')` su Rating)
- Enum: `TextChoices` con valori lowercase (`'clutch'`, `'funny'`, `'fail'`)

**API Endpoint (già stabiliti):**
- Risorse: plurale, kebab-case (`/api/videos/`, `/api/contests/winners/`)
- Actions: kebab-case nel `url_path` (`url_path='top-rated'`, `url_path='following'`)
- Query params: snake_case (`?page=1`, `?range=week`)
- Nuovi domini: `/api/{dominio_plurale}/` — es. `/api/brackets/`, `/api/notifications/`

**File Backend (già stabiliti):**
- Modelli: `cs_clips/models/{modello_singolare}.py` — es. `video.py`, `notification.py`
- Views: `cs_clips/api/{dominio}/{dominio}_views.py` — es. `video_views.py`
- Serializers: `cs_clips/api/{dominio}/{dominio}_serializers.py`
- Routing: SOLO in `cs_clips/urls.py` — **NON creare `{dominio}_urls.py` nelle subdirectory** (i file esistenti sono dead code)
- Utils: `cs_clips/utils/{funzione}.py` — un file per funzione
- Test: `cs_clips/tests/test_{modulo}.py`

**File Frontend (già stabiliti):**
- Componenti: `kebab-case.tsx` — es. `clip-card.tsx`, `follow-button.tsx`
- Hook: `use-{feature}.ts` — es. `use-videos.ts`, `use-notifications.ts`
- API modules: `{dominio}.ts` singolare — es. `videos.ts`, `notifications.ts`
- Types: `src/types/{dominio}.ts` + barrel export da `index.ts`
- Test componenti: `src/components/{dominio}/__tests__/{componente}.test.tsx` (kebab-case, coerente con naming sorgente)
- Test hook: `src/lib/hooks/__tests__/use-{feature}.test.ts`
- MSW handlers: `src/test/handlers.ts` (centralizzato)

**Classi e Funzioni (già stabiliti):**
- Classi Python: `PascalCase` + suffisso ruolo (`VideoViewSet`, `VideoOutputSerializer`, `OnlyAdminsPermission`)
- Funzioni Python: `snake_case` (`get_or_create_current_contest`, `handle_exception_with_serializer`)
- Componenti React: `PascalCase` con named export (`export function ClipCard`)
- Props interface: `{ComponentName}Props` (`ClipCardProps`, `ErrorMessageProps`)

### Structure Patterns

**Creazione Nuovo Modello — Checklist Obbligatoria:**

1. Creare file `cs_clips/models/{modello}.py`
2. Aggiungere export in `cs_clips/models/__init__.py`
3. Usare `get_user_model()` per FK a User, MAI `from django.contrib.auth.models import User`
4. Specificare `related_name` su ogni FK
5. Specificare `on_delete` esplicito: `CASCADE` per relazioni forti, `SET_NULL` per deboli
6. `help_text` in italiano su ogni campo
7. Creare migrazione: `python manage.py makemigrations`
8. Registrare in `cs_clips/admin.py`
9. Se il modello richiede gruppi/permessi: creare via data migration, NON solo runtime

**Creazione Nuovo Dominio API — Checklist Obbligatoria:**

1. Creare directory `cs_clips/api/{dominio}/` con `__init__.py`
2. Creare `{dominio}_views.py` con ViewSet o APIView
3. Creare `{dominio}_serializers.py` con Input/Output serializer separati
4. Registrare route in `cs_clips/urls.py` — **NON creare `{dominio}_urls.py` separato**
5. `permission_classes` espliciti su ogni ViewSet
6. `read_only_fields` dichiarati in ogni serializer `Meta`
7. Documentare con `@extend_schema` su ViewSet e ogni `@action`
8. Per ViewSet CRUD: implementare `get_serializer_class()` con serializer diversi per azione

**Creazione Nuovo Dominio Frontend — Checklist Simmetrica:**

1. Creare modulo API `src/lib/api/{dominio}.ts` con pattern standard (import `apiClient`, export oggetto con metodi CRUD, `normalizePaginated<T>()` per liste)
2. Creare hook `src/lib/hooks/use-{dominio}.ts`
3. Aggiungere query keys in `src/lib/query-keys.ts` — pattern: `dominio.all`, `dominio.list(page)`, `dominio.detail(id)`. MAI stringhe inline
4. Creare type `src/types/{dominio}.ts` e aggiungere barrel export in `src/types/index.ts`
5. MSW handler in `src/test/handlers.ts` per gli endpoint del dominio

### Format Patterns

**Risposte API (NON deviare):**
- Liste: `{count, next, previous, results}` — SEMPRE paginato, MAI array piatto
- Detail: oggetto singolo diretto (nessun wrapper)
- Errori: `{code, detail}` via `ErrorResponseSerializer`
- Successo azioni: `{detail: "Messaggio in italiano."}` con HTTP 200
- Creazione: oggetto creato con HTTP 201
- Delete: HTTP 204 No Content
- JSON fields: `snake_case` (DRF default)
- Date: ISO 8601 string (`"2026-02-28T11:33:00Z"`)

**Custom Actions con paginazione — Pattern obbligatorio:**

```python
@extend_schema(parameters=[...])
@action(detail=False, methods=['get'], url_path='my-action')
def my_action(self, request):
    queryset = self.get_queryset().filter(...)
    page = self.paginate_queryset(queryset)
    serializer = self.get_serializer(page, many=True)
    return self.get_paginated_response(serializer.data)
```

MAI ritornare `Response(serializer.data)` da un'action che ritorna liste.

**Serializer Multipli — Pattern `get_serializer_class()`:**

```python
class MyViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == 'create':
            return MyInputSerializer
        if self.action in ('update', 'partial_update'):
            return MyUpdateSerializer
        return MyOutputSerializer
```

Ogni ViewSet CRUD deve avere almeno `InputSerializer` (campi scrivibili) e `OutputSerializer` (campi leggibili + calcolati). MAI un singolo serializer per tutto.

### Process Patterns

**Serializer Validation — Quando usare cosa:**
- `validate_{field}()` → validazione singolo campo isolato (whitelist valori)
- `validate()` → validazione cross-field (`timestamp_second <= video.duration`)
- `validators=[MinValueValidator()]` → vincoli numerici semplici
- Business logic complessa → in `create()`/`update()` del serializer, MAI nella view

**`perform_create()` — Iniezione utente:**

```python
# Rating, Comment: campo `user`
def perform_create(self, serializer):
    serializer.save(user=self.request.user)

# Video: campo `uploader`
def perform_create(self, serializer):
    serializer.save(uploader=self.request.user)
```

MAI passare l'utente come campo del serializer input.

**Incrementi atomici:**

```python
# CORRETTO
video.views = F('views') + 1
video.save(update_fields=['views'])
video.refresh_from_db()

# VIETATO — race condition
video.views += 1
video.save()
```

**Loading States Frontend — Pattern standard:**

```tsx
const { data, isLoading, isError, refetch } = useQuery({...});
if (isLoading) return <Skeleton />; // Skeleton per contenuto strutturato, Spinner per azioni
if (isError) return <ErrorMessage onRetry={refetch} />;
```

MAI schermo vuoto durante loading. MAI omettere `isError` + `<ErrorMessage>`.

**React Query Mutation — Template standard:**

```tsx
export function useCreateThing() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateThingInput) => thingsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.things.all });
    },
  });
}
```

Per optimistic updates (follow, like):
```tsx
onMutate: async (id) => {
  await queryClient.cancelQueries({ queryKey: queryKeys.things.detail(id) });
  const previous = queryClient.getQueryData(queryKeys.things.detail(id));
  queryClient.setQueryData(queryKeys.things.detail(id), (old) => ({...old, liked: true}));
  return { previous };
},
onError: (_err, id, context) => {
  queryClient.setQueryData(queryKeys.things.detail(id), context?.previous);
},
onSettled: (_data, _err, id) => {
  queryClient.invalidateQueries({ queryKey: queryKeys.things.detail(id) });
},
```

**API Module Frontend — Template standard per nuovo dominio:**

```tsx
import { apiClient } from "./client";
import type { PaginatedResponse, MyType } from "@/types";
import { normalizePaginated } from "@/lib/utils";

export const myDomainApi = {
  getAll: (page = 1) =>
    apiClient.get<PaginatedResponse<MyType>>("/my-domain/", { params: { page } })
      .then((r) => normalizePaginated(r.data)),
  getById: (id: number) =>
    apiClient.get<MyType>(`/my-domain/${id}/`).then((r) => r.data),
  create: (data: CreateMyTypeInput) =>
    apiClient.post<MyType>("/my-domain/", data).then((r) => r.data),
  delete: (id: number) =>
    apiClient.delete(`/my-domain/${id}/`),
};
```

**Regola `"use client"` — Next.js App Router:**
- `"use client"` SOLO se il componente usa hooks (`useState`, `useEffect`, `useQuery`, `useMutation`) o event handlers (`onClick`, `onChange`)
- Senza hooks/eventi → Server Component (default) — beneficia di SSR, zero JS al client
- L'unica RSC con fetch server-side è `/clip/[id]/page.tsx` (`generateMetadata` per SEO)

**Import Ordering:**

Python (ruff enforced):
1. Standard library (`datetime`, `pathlib`, `tempfile`)
2. Third-party (`django.*`, `rest_framework.*`, `drf_spectacular.*`)
3. Project-specific relativi (`.models`, `.api.*`, `.utils.*`)

TypeScript (convenzione):
1. React/Next.js (`"react"`, `"next/link"`)
2. Librerie esterne (`"@tanstack/react-query"`, `"lucide-react"`, `"framer-motion"`)
3. Componenti UI (`"@/components/ui/*"`)
4. Componenti progetto (`"@/components/*"`)
5. Lib/hooks/api (`"@/lib/*"`)
6. Types (`"@/types"`) — sempre con `import type`

**Docstring Python — Formato one-liner italiano:**

```python
def close_contests(self):
    """Chiude tutti i contest scaduti e assegna il vincitore."""
```

Multi-liner per funzioni complesse:
```python
def create(self, validated_data):
    """
    Crea un video con estrazione durata e assegnazione contest.

    1. Salva il file su MinIO
    2. Estrae la durata con MoviePy
    3. Assegna al contest corrente per tag
    """
```

### Regole di Enforcement — Definition of Done

**Ogni agente AI DEVE verificare prima di considerare completa una task:**

- Nessun modello senza `related_name` su ogni FK
- Nessun ViewSet senza `permission_classes` espliciti
- Nessuna lista API senza paginazione (`self.get_paginated_response()`)
- Nessun `@action` senza `@extend_schema`
- Nessun serializer CRUD senza separazione Input/Output
- Nessuna pagina frontend senza `isError` + `<ErrorMessage onRetry={refetch} />`
- Nessun componente con hooks senza `"use client"`
- Nessun import User diretto — sempre `get_user_model()`
- Nessun utente test senza gruppo assegnato
- Nessun increment senza `F()` expression
- Nessuna stringa query key inline — sempre `queryKeys.dominio.azione()`
- Nessun dominio frontend senza modulo API + hook + type + query keys
- Nessuna directory Python senza `__init__.py`
- Messaggi UI e help_text in italiano, codice in inglese

### Anti-Pattern Vietati

- `from django.contrib.auth.models import User` → `get_user_model()`
- `obj.field += 1; obj.save()` → `F('field') + 1`
- `Response(serializer.data)` su liste → `self.get_paginated_response()`
- Contest CRUD ViewSet → contest creati implicitamente via `get_or_create_current_contest()`
- Utenti senza gruppo → viola `blank=False` su `groups`
- `import from "motion/react"` → `import from "framer-motion"`
- `{dominio}_urls.py` nelle subdirectory API → routing solo in `cs_clips/urls.py`
- Singolo serializer per ViewSet CRUD → separare Input/Output
- `@action` senza `@extend_schema` → documenta sempre per OpenAPI
- Stringhe query key inline (`["notifications"]`) → usa `queryKeys.dominio`
- `"use client"` su componenti senza hooks/eventi → lasciare come Server Component

## Project Structure & Boundaries

### Struttura Completa del Progetto

```
Video_clip/
├── .env                              # Variabili ambiente root (DB, MinIO)
├── .gitignore
├── .editorconfig                     # [Story 0] tab/spaces, line endings
├── compose.yml                       # PostgreSQL, MinIO, pgAdmin, minio-init
├── package.json                      # Orchestrazione NPM (concurrently + wait-on)
├── package-lock.json
│
├── .github/                          # [Story 0] CI/CD
│   └── workflows/
│       └── ci.yml                    # ruff + test backend + lint + test + build frontend
│
├── backend/
│   ├── .env                          # Django SECRET_KEY, DB_URL, MinIO creds
│   ├── .env.example
│   ├── manage.py
│   ├── requirements.txt              # [D7] senza celery/redis
│   ├── pyproject.toml                # [D5] config ruff
│   ├── schema.yaml                   # OpenAPI generato da drf-spectacular
│   │
│   ├── project_clip/                 # Django project config
│   │   ├── __init__.py
│   │   ├── settings.py              # [D6] throttle rates inclusi
│   │   ├── urls.py                   # Include cs_clips.urls
│   │   └── wsgi.py
│   │
│   ├── cs_clips/                     # Django app principale
│   │   ├── apps.py                   # CsClipsConfig.ready() → APScheduler
│   │   ├── scheduler.py              # APScheduler config
│   │   ├── permissions.py            # RoleBasedPermission, OnlyUsers, OnlyAdmins
│   │   ├── urls.py                   # UNICO punto di routing API
│   │   │
│   │   ├── models/                   # Un file per modello
│   │   │   ├── __init__.py           # Barrel export di tutti i modelli
│   │   │   ├── user.py               # Custom User (AbstractUser)
│   │   │   ├── video.py
│   │   │   ├── contest.py
│   │   │   ├── comment.py
│   │   │   ├── rating.py
│   │   │   ├── video_like.py         # [DA CREARE] FR28
│   │   │   ├── comment_like.py       # [DA CREARE] FR27
│   │   │   ├── notification.py       # [DA CREARE] D1
│   │   │   ├── bracket.py            # [DA CREARE] D2
│   │   │   ├── contest_entry.py      # [DA CREARE] D2
│   │   │   └── matchup.py            # [DA CREARE] D2
│   │   │
│   │   ├── api/                      # Dominio-per-directory
│   │   │   ├── videos/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── video_views.py
│   │   │   │   └── video_serializers.py
│   │   │   ├── users/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user_views.py
│   │   │   │   └── user_serializers.py
│   │   │   ├── comments/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── comment_views.py
│   │   │   │   └── comment_serializers.py
│   │   │   ├── ratings/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── rating_views.py
│   │   │   │   └── rating_serializers.py
│   │   │   ├── contests/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── contest_views.py
│   │   │   │   └── contest_serializers.py
│   │   │   ├── notifications/         # [DA CREARE] D1
│   │   │   │   ├── __init__.py
│   │   │   │   ├── notification_views.py
│   │   │   │   └── notification_serializers.py
│   │   │   └── brackets/              # [DA CREARE] D2
│   │   │       ├── __init__.py
│   │   │       ├── bracket_views.py
│   │   │       └── bracket_serializers.py
│   │   │
│   │   ├── exceptions/
│   │   │   ├── __init__.py
│   │   │   ├── error_handler.py
│   │   │   └── error_response_serializer.py
│   │   │
│   │   ├── utils/
│   │   │   ├── get_date_util.py       # get_or_create_current_contest()
│   │   │   └── desempate.py           # Algoritmo spareggio contest
│   │   │
│   │   ├── management/
│   │   │   ├── __init__.py
│   │   │   └── commands/
│   │   │       ├── __init__.py
│   │   │       └── close_contests.py
│   │   │
│   │   ├── migrations/
│   │   │   ├── 0001_initial.py
│   │   │   └── 0002_alter_video_file.py
│   │   │
│   │   ├── tests/                     # [Story 0] da ricreare
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py            # [D4] 5 fixture base
│   │   │   ├── test_auth.py           # Auth flow critico
│   │   │   ├── test_permissions.py    # RoleBasedPermission
│   │   │   ├── test_upload.py         # Upload pipeline
│   │   │   ├── test_contests.py       # Contest closure + spareggio
│   │   │   └── test_videos.py         # CRUD video
│   │   │
│   │   └── admin.py
│   │
│   ├── scripts/
│   │   └── minio_init.sh             # Init bucket MinIO
│   │
│   └── policy/
│       └── ...                        # MinIO policies
│
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── next.config.ts
│   ├── tsconfig.json
│   ├── postcss.config.mjs
│   ├── eslint.config.mjs              # ESLint 9 FlatConfig
│   ├── components.json                # shadcn/ui config
│   │
│   ├── public/                        # Static assets
│   │
│   ├── src/
│   │   ├── globals.css                # TailwindCSS v4 @theme inline
│   │   ├── middleware.ts              # Next.js middleware (cookie session_active)
│   │   │
│   │   ├── app/
│   │   │   ├── layout.tsx             # Root layout + Providers
│   │   │   ├── (auth)/                # Route group auth
│   │   │   │   ├── layout.tsx
│   │   │   │   ├── login/page.tsx
│   │   │   │   └── register/page.tsx
│   │   │   └── (main)/               # Route group app
│   │   │       ├── layout.tsx         # Sidebar + Navbar + BottomBar
│   │   │       ├── feed/page.tsx
│   │   │       ├── clip/[id]/page.tsx # RSC — SSR + generateMetadata
│   │   │       ├── profilo/[username]/page.tsx
│   │   │       ├── contest/page.tsx
│   │   │       ├── esplora/page.tsx
│   │   │       ├── upload/page.tsx
│   │   │       ├── cerca/page.tsx
│   │   │       └── impostazioni/page.tsx
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                    # shadcn/ui primitives (18 componenti)
│   │   │   ├── shared/                # ErrorMessage, LoadingSpinner, TagBadge, etc.
│   │   │   ├── layout/               # LeftSidebar, Header, DesktopNavbar, MobileBottomBar
│   │   │   ├── feed/                  # ClipCard, FeedGrid, FeedTabs
│   │   │   ├── video/                 # VideoPlayer, VideoInfo, PopupOverlay, DynamicSidebar
│   │   │   ├── comments/             # CommentSection, CommentList, CommentForm
│   │   │   ├── user/                  # UserAvatar, FollowButton, ProfileEditForm, etc.
│   │   │   └── auth/                  # LoginTransitionOverlay, LoginTransitionProvider
│   │   │
│   │   ├── lib/
│   │   │   ├── api/
│   │   │   │   ├── client.ts          # Axios + JWT interceptor
│   │   │   │   ├── videos.ts
│   │   │   │   ├── comments.ts
│   │   │   │   ├── ratings.ts
│   │   │   │   ├── users.ts
│   │   │   │   ├── contests.ts
│   │   │   │   ├── notifications.ts   # [DA CREARE] D1
│   │   │   │   └── brackets.ts        # [DA CREARE] D2
│   │   │   ├── hooks/
│   │   │   │   ├── use-videos.ts
│   │   │   │   ├── use-comments.ts
│   │   │   │   ├── use-ratings.ts
│   │   │   │   ├── use-users.ts
│   │   │   │   ├── use-auth.ts
│   │   │   │   ├── use-media-query.ts
│   │   │   │   ├── use-notifications.ts  # [DA CREARE] D1
│   │   │   │   ├── use-brackets.ts       # [DA CREARE] D2
│   │   │   │   └── __tests__/            # [Story 0]
│   │   │   │       ├── use-videos.test.ts
│   │   │   │       └── use-comments.test.ts
│   │   │   ├── query-keys.ts         # Query keys centralizzati
│   │   │   ├── constants.ts
│   │   │   └── utils.ts              # cn(), extractPageFromUrl(), normalizePaginated()
│   │   │
│   │   ├── providers/
│   │   │   ├── auth-provider.tsx
│   │   │   ├── query-provider.tsx     # React Query + DevTools
│   │   │   └── login-transition-provider.tsx
│   │   │
│   │   └── types/
│   │       ├── index.ts              # Barrel export
│   │       ├── video.ts
│   │       ├── user.ts
│   │       ├── comment.ts
│   │       ├── rating.ts
│   │       ├── contest.ts
│   │       ├── api.ts
│   │       ├── notification.ts       # [DA CREARE] D1
│   │       └── bracket.ts            # [DA CREARE] D2
│   │
│   └── src/test/                      # [Story 0] MSW setup
│       ├── setup.ts                   # beforeAll/afterAll MSW server
│       └── handlers.ts               # MSW handlers centralizzati
│
├── docs/                              # Documentazione progetto
│   ├── index.md
│   ├── project-overview.md
│   ├── architecture-backend.md
│   ├── architecture-frontend.md
│   ├── integration-architecture.md
│   ├── api-contracts-backend.md
│   ├── data-models-backend.md
│   ├── component-inventory-frontend.md
│   ├── state-management-frontend.md
│   ├── source-tree-analysis.md
│   └── development-guide.md
│
└── _bmad-output/                      # Artefatti BMAD
    ├── planning-artifacts/
    │   ├── prd.md
    │   ├── architecture.md            # ← QUESTO DOCUMENTO
    │   └── ux-design-specification.md
    └── project-context.md
```

### Confini Architetturali

**Confini API (Backend → Frontend):**

| Dominio | Base Path | ViewSet/View | Stato |
|---------|-----------|-------------|-------|
| Auth | `/api/token/` | `CustomTokenObtainPairView` | Funzionante |
| Users | `/api/users/` | `UserViewSet` | Parziale (manca by-username) |
| Videos | `/api/videos/` | `VideoViewSet` | Funzionante |
| Comments | `/api/comments/` | `CommentViewSet` | Funzionante |
| Ratings | `/api/ratings/` | `RatingViewSet` | Funzionante |
| Contests | `/api/contests/` | `ContestWinnersView`, `EndContestView` | Parziale |
| Notifications | `/api/notifications/` | `NotificationViewSet` | [DA CREARE] |
| Brackets | `/api/brackets/` | `BracketViewSet` | [DA CREARE] |

**Confini Dati (Backend → Storage):**

- Django ORM → PostgreSQL 16 (psycopg 3.2.4, `dj-database-url`)
- Django → MinIO (presigned URL 1h, `django-minio-storage` + client `minio`)
- APScheduler → in-process (zero dipendenze esterne)

**Confini Componenti (Frontend):**

- `(auth)/` → pagine login/register, nessun layout main
- `(main)/` → tutte le pagine app, layout con sidebar/navbar/bottombar
- `providers/` → context globali (Auth, Query, LoginTransition)
- `lib/api/` → unico punto di contatto con backend (via Axios `apiClient`)
- `lib/hooks/` → unico punto di accesso a React Query (mai `useQuery` diretto nei componenti)

### Mapping Requisiti → Struttura

**Tier 1 — Core Loop:**

| FR | Descrizione | Backend | Frontend |
|----|------------|---------|----------|
| FR1-FR2 | Auth (registrazione + login) | `api/users/user_views.py`, `project_clip/urls.py` (token) | `(auth)/login/`, `(auth)/register/`, `providers/auth-provider.tsx` |
| FR7-FR11 | Upload clip | `api/videos/video_views.py`, `api/videos/video_serializers.py` | `(main)/upload/page.tsx`, `hooks/use-videos.ts` |
| FR15 | Presigned URL | `api/videos/video_serializers.py` (VideoOutputSerializer) | `components/video/video-player.tsx` |
| FR17 | Feed following | `api/videos/video_views.py` (@action following) | `(main)/feed/page.tsx`, `components/feed/` |
| FR23-FR24 | Commenti | `api/comments/` | `components/comments/` |

**Tier 2 — Social Layer:**

| FR | Descrizione | Backend | Frontend |
|----|------------|---------|----------|
| FR4-FR6 | Follow/unfollow | `api/users/user_views.py` (@action follow/unfollow) | `components/user/follow-button.tsx`, `hooks/use-users.ts` |
| FR27-FR28 | Like video/commenti | `models/video_like.py`, `models/comment_like.py` [DA CREARE] | `hooks/use-videos.ts`, `hooks/use-comments.ts` |
| FR50-FR52 | Notifiche | `api/notifications/` [DA CREARE] | `hooks/use-notifications.ts` [DA CREARE] |

**Tier 3 — Differenziatori:**

| FR | Descrizione | Backend | Frontend |
|----|------------|---------|----------|
| FR39a-FR43a | Contest settimanali | `api/contests/`, `utils/desempate.py`, `management/commands/close_contests.py` | `(main)/contest/page.tsx` |
| FR39c-FR44b | Bracket Champions League | `api/brackets/` [DA CREARE] | `components/brackets/` [DA CREARE] |

**Cross-Cutting Concerns:**

| Concern | Backend | Frontend |
|---------|---------|----------|
| Auth JWT | `permissions.py`, SimpleJWT config in `settings.py` | `providers/auth-provider.tsx`, `lib/api/client.ts` |
| Error handling | `exceptions/error_handler.py` | `components/shared/error-message.tsx` |
| Paginazione | `PageNumberPagination` in `settings.py` | `lib/utils.ts` (normalizePaginated, extractPageFromUrl) |
| Cache invalidation | — | `lib/query-keys.ts`, optimistic updates in hooks |
| Upload media | MinIO storage, `django-cleanup` | `hooks/use-videos.ts` (useUploadVideo) |

### Flusso Dati

```
[Browser]
  ↓ HTTPS (JWT in header)
[Next.js Frontend]
  ↓ Axios apiClient → REST JSON
[Django DRF Backend]
  ↓ ORM          ↓ minio client
[PostgreSQL]    [MinIO Storage]
                  ↓ presigned URL (1h TTL)
                [Browser <video> playback]
```

---

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**
Tutte le 7 decisioni architetturali (D1-D7) sono compatibili tra loro:
- D1 (Polling REST 15s) funziona con D6 (Throttle DRF 2000/hour) — margine sufficiente: 240 req/hour polling + ~200 navigazione = ~440, ben sotto 2000
- D2 (Modelli bracket separati) non conflittua con nessun'altra decisione
- D3 (Lazy re-fetch presigned URL) si integra con MinIO e con il pattern retry frontend
- D4 (Testing stack) copre sia backend (Django TestCase) sia frontend (Vitest/RTL/MSW)
- D5 (ruff) è ortogonale a tutte le altre decisioni
- D7 (Rimozione celery/redis) è coerente con APScheduler in-process

**Pattern Consistency:**
- Naming conventions coerenti: `snake_case` backend, `camelCase` frontend, `kebab-case` file frontend
- API response wrapper `{count, next, previous, results}` dalla paginazione DRF — nessun wrapper custom
- Serializer pattern: 1 `serializers.py` per dominio API, multipli serializer per modello dove necessario
- Query keys: `queryKeys` object centralizzato in `lib/query-keys.ts`

**Structure Alignment:**
- Struttura `api/{dominio}/` backend allineata con `hooks/use-{dominio}.ts` frontend
- Modelli in `models/` package (1 file/modello) + `__init__.py` re-export
- Exception handler centralizzato in `exceptions/error_handler.py`

**Decisione Aggiuntiva — Backoffice Admin (Party Mode):**
Per l'MVP, il backoffice amministrativo è gestito esclusivamente da **Django Admin** (`admin.py`). Non è prevista un'interfaccia admin custom nel frontend. Questo è sufficiente per le operazioni CRUD di moderazione e gestione contest.

### Requirements Coverage Validation ✅

**Copertura per Tier (55 FR totali):**

| Tier | FR | Copertura Architetturale | Note |
|------|-----|--------------------------|------|
| Tier 1 — Core Loop | FR1-FR3, FR7-FR26, FR29-FR30, FR37-FR38 | ✅ Completa | Auth, profilo, upload, feed, rating, contest base |
| Tier 2 — Social Layer | FR4-FR6, FR27-FR28 | ⚠️ Parziale | Follow OK; Like richiede `VideoLike` + `CommentLike` [DA CREARE]; campo `bio` User [DA CREARE] |
| Tier 3 — Differenziatori | FR39a-FR44b, FR50-FR52 | ⚠️ Parziale | Contest settimanali OK; Bracket + Notifiche da implementare |

**FR31-FR36 (Popup commenti) — BLOCCATI:**
I requisiti FR31-FR36 (popup commenti con like/dislike) sono **bloccati** fino all'implementazione del modello `CommentLike`. Il frontend ha i componenti UI ma le API per like/dislike commenti non esistono ancora. Priorità: Tier 2, da implementare insieme a `VideoLike`.

**Campo `bio` User — Tier 2 Social Layer:**
Il campo `bio` nel modello `User` è riclassificato come **Tier 2** (Social Layer), non bassa priorità. È necessario per il profilo utente completo e fa parte dell'esperienza social core.

**Non-Functional Requirements:**
- Performance: Polling 15s accettabile per MVP, presigned URL 1h TTL
- Security: JWT auth, throttling 2000/hour, CORS whitelist, validazione upload (dimensione + tipo MIME)
- Scalability: Architettura stateless, MinIO separato, PostgreSQL — pronti per scale-out
- Compliance: `django-cleanup` per file orfani, presigned URL con scadenza

### Implementation Readiness Validation ✅

**Decision Completeness:**
- 7 decisioni documentate con versioni e motivazioni
- Pattern di implementazione per ogni area (naming, struttura, formato, comunicazione, processo)
- 118 regole in `project-context.md` per guida agenti AI
- Esempi concreti per ogni pattern

**Structure Completeness:**
- Directory tree completa con annotazioni `[DA CREARE]` e `[Story 0]`
- Mapping FR → file specifici per ogni tier
- Integration points chiaramente specificati (JWT, MinIO, APScheduler)

**Pattern Completeness:**
- Naming: `snake_case` / `camelCase` / `kebab-case` ben definiti
- API: DRF ViewSet + `@action` + `@extend_schema` obbligatorio
- Frontend: custom hooks + React Query + Zustand per auth
- Error handling: `CUSTOM_EXCEPTION_HANDLER` backend, `ErrorMessage` component frontend
- Testing: fixtures condivise, naming `test_{action}_{scenario}_{expected}`

### Gap Analysis Results

**Gap Critici — Nessuno:**
Tutte le decisioni architetturali necessarie per iniziare l'implementazione sono documentate.

**Gap Importanti (Tier 2-3, non bloccanti per Tier 1):**

| Gap | Priorità | Quando Risolvere |
|-----|----------|-----------------|
| Modello `CommentLike` | Tier 2 | Prima di FR31-FR36 |
| Modello `VideoLike` | Tier 2 | Prima di FR27-FR28 |
| Campo `bio` in User | Tier 2 | Prima del profilo social completo |
| Modello `Notification` + API | Tier 3 | Prima di FR50-FR52 |
| Modelli Bracket (`BracketTournament`, `BracketRound`, `BracketMatch`) | Tier 3 | Prima di FR39c-FR44b |
| `allow_download` in Video | Basso | Feature opzionale |
| `is_disabled` in Comment | Basso | Feature moderazione |

**Gap Nice-to-Have:**
- WebSocket per notifiche real-time (post-MVP, attualmente polling)
- CDN davanti a MinIO (ottimizzazione performance)
- Rate limiting più granulare per endpoint

### Validation Issues Addressed

**Issue #1 — Throttle Rate (Risolto in Party Mode):**
Il rate originale di 1000/hour era insufficiente con polling 15s (240 req/hour solo per notifiche). Alzato a **2000/hour** per D6, con margine adeguato.

**Issue #2 — FR31-FR36 Bloccati (Documentato in Party Mode):**
Aggiunta nota esplicita che i FR popup commenti sono bloccati da `CommentLike` mancante.

**Issue #3 — Django Admin come Backoffice (Documentato in Party Mode):**
Decisione architetturale mancante ora documentata: Django Admin è il backoffice per l'MVP.

### Architecture Completeness Checklist

**✅ Requirements Analysis**

- [x] Contesto progetto analizzato (brownfield, frontend-ahead)
- [x] Scala e complessità valutate (55 FR, 3 tier)
- [x] Vincoli tecnici identificati (Django 5.1.6, Next.js 16.1.6, MinIO)
- [x] Cross-cutting concerns mappati (auth, error handling, paginazione, cache)

**✅ Architectural Decisions**

- [x] 7 decisioni critiche documentate con versioni (D1-D7)
- [x] Technology stack completamente specificato
- [x] Pattern di integrazione definiti (REST, JWT, presigned URL)
- [x] Considerazioni performance indirizzate (polling 15s, throttle 2000/hour)

**✅ Implementation Patterns**

- [x] Naming conventions stabilite (snake_case/camelCase/kebab-case)
- [x] Structure patterns definiti (api/{dominio}/, models/ package)
- [x] Communication patterns specificati (REST JSON, JWT header)
- [x] Process patterns documentati (error handling, loading states, retry)

**✅ Project Structure**

- [x] Directory tree completa con annotazioni
- [x] Component boundaries stabiliti (backend domains, frontend features)
- [x] Integration points mappati (JWT, MinIO, APScheduler)
- [x] Requirements → structure mapping completo

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION

**Confidence Level:** HIGH — basato su:
- Codebase brownfield esistente con pattern già stabiliti
- 118 regole in project-context.md per guidare agenti AI
- Frontend come "living specification" per le API
- Stack tecnologico maturo e ben documentato

**Key Strengths:**
- Architettura semplice e pragmatica (no over-engineering)
- Frontend-ahead fornisce contratti API impliciti
- Pattern chiari e verificabili per consistenza agenti
- Tier hierarchy permette implementazione incrementale
- Django Admin come backoffice elimina complessità admin custom

**Areas for Future Enhancement:**
- WebSocket per notifiche real-time (post-MVP)
- CDN per ottimizzazione delivery media
- Monitoring e observability (Sentry, logging strutturato)
- CI/CD pipeline completa (attualmente solo locale)

### Story 0 — Criterio di Accettazione (Party Mode)

Prima di qualsiasi story funzionale, Story 0 deve soddisfare:

1. **ruff** lint con 0 errori su tutto il backend
2. **Almeno 1 test backend** che passa (Django TestCase)
3. **Almeno 1 test frontend** che passa (Vitest)
4. **Build frontend** (`npm run build`) senza errori
5. **CI verde** (se configurato)

### Story 0 — Bug [FIX-READY] Prerequisiti (Party Mode)

I seguenti 7 bug devono essere risolti in Story 0 come prerequisiti per test funzionanti:

| Bug | Descrizione | File |
|-----|-------------|------|
| FIX-1 | `STATICFILES_DIRS` contiene path inesistente | `settings.py` |
| FIX-2 | `DEFAULT_FILE_STORAGE` deprecato in Django 5.x | `settings.py` |
| FIX-3 | Import circolare potenziale in `models/__init__.py` | `models/__init__.py` |
| FIX-4 | `django-cleanup` non in `INSTALLED_APPS` | `settings.py` |
| FIX-5 | `CORS_ALLOWED_ORIGINS` hardcoded | `settings.py` |
| FIX-6 | Manca `DEFAULT_AUTO_FIELD` | `settings.py` |
| FIX-7 | `AUTH_USER_MODEL` dopo `INSTALLED_APPS` con migrazioni | `settings.py` |

### Implementation Handoff

**AI Agent Guidelines:**

- Seguire tutte le decisioni architetturali esattamente come documentate (D1-D7)
- Usare i pattern di implementazione consistentemente in tutti i componenti
- Rispettare struttura progetto e boundaries (`api/{dominio}/`, `models/`, `hooks/`)
- Consultare `project-context.md` (118 regole) per ogni domanda architetturale
- Annotazioni `[DA CREARE]` nel directory tree indicano file da implementare
- Annotazioni `[Story 0]` indicano prerequisiti infrastrutturali

**First Implementation Priority:**
Story 0 — Setup infrastruttura: ruff, testing fixtures, throttle config, 7 bug fix, CI base
