---
project_name: 'Video_clip'
user_name: 'AcchippameQuisso'
date: '2026-02-28'
sections_completed: ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'code_quality', 'workflow_rules', 'critical_rules']
status: 'complete'
rule_count: 118
optimized_for_llm: true
---

# Project Context per Agenti AI

_Questo file contiene regole critiche e pattern che gli agenti AI devono seguire quando implementano codice in questo progetto. Focus su dettagli non ovvi che gli agenti potrebbero altrimenti perdere._

---

## Technology Stack & Versioni

### Backend
- **Python 3.x + Django 5.1.6** — Custom User Model (`cs_clips.User`)
- **Django REST Framework 3.15.1** — API layer, `PageNumberPagination` PAGE_SIZE=10
- **SimpleJWT 5.3.1** — access 12h, refresh 1d, rotate=True
- **PostgreSQL 16** (Docker) — driver **psycopg 3.2.4** attivo (psycopg2-binary 2.9.10 e' legacy, NON importare psycopg2)
- **MinIO 7.2.15** (S3-compatible object storage):
  - `django-minio-storage 0.5.8` — storage backend Django (`MinioMediaStorage` in settings)
  - `minio` client Python — usato nei serializer per generare presigned URL
  - `django-minio-backend 3.8.0` — configurazione bucket
- **django-cleanup 9.0.0** — auto-delete file su model delete. NON fare delete manuale di file nei model
- **drf-spectacular 0.28.0** — Swagger + ReDoc (`/api/docs/`, `/api/redoc/`)
- **django-cors-headers 4.7.0** — `CORS_ALLOW_ALL_ORIGINS = DEBUG` (True solo in dev), `CORS_ALLOWED_ORIGINS` configurabile via env var
- **django-filter 24.3** — filtri su ViewSet via `filterset_fields`
- **APScheduler 3.11.0** (django-apscheduler 0.7.0) — chiusura contest automatica giovedi' 11:33
- **moviepy 2.2.1** — `from moviepy import VideoFileClip` (v2 syntax, NON v1). Prerequisito di sistema: **ffmpeg** deve essere installato
- **Pillow 11.1.0**, imageio-ffmpeg 0.6.0
- **numpy 2.2.6** — spareggio ponderato contest
- **Celery/Redis/Flower** — RIMOSSI da requirements.txt (Story 0.1). NON usare — nessun task asincrono e' supportato. Per task schedulati usare SOLO APScheduler

### Frontend
- **Next.js 16.1.6** (Turbopack) + **React 19.2.3** + **TypeScript 5** (strict, target ES2017)
- **TailwindCSS 4** — config-in-CSS (no tailwind.config.*), tema in `globals.css` via `@theme inline`
- **Shadcn/UI** — style "new-york", CSS variables, icone Lucide
- **Radix UI 1.4.3** — primitivi accessibilita'
- **Framer Motion 12.34.0** — import da `"framer-motion"` (NON `"motion/react"`)
- **TanStack React Query 5.90** — server state, staleTime default 30s, retry 1
- **Axios 1.13.5** — interceptor JWT con mutex/queue per refresh concorrenti
- **next-themes 0.4.6** — dark mode (app always-dark, gaming-inspired oklch palette)
- **Sonner 2.0.7** — toast notifications
- **Geist 1.7.0** — font di progetto

### Infrastruttura
- **Docker Compose**: PostgreSQL 16 + pgAdmin4 + MinIO (Django gira in locale, NON in container)
- **Monorepo**: `package.json` root con `concurrently` + `wait-on` per orchestrazione dev
- **`npm run dev`**: avvio completo (Docker + backend + frontend + apre browser)

### Testing
- **Django TestCase** built-in — nessun pytest, nessun coverage, nessuna CI configurata
- Test richiedono **DB PostgreSQL attivo** (Docker) — no SQLite
- Eseguire con: `python manage.py test` da `backend/`

## Regole Specifiche Python/Django

### Custom User Model
- Il progetto usa `cs_clips.User` (AbstractUser), configurato in `AUTH_USER_MODEL`
- SEMPRE usare `get_user_model()` per referenziare il modello User
- MAI importare `django.contrib.auth.models.User` direttamente
- Pattern: `from django.contrib.auth import get_user_model` → `User = get_user_model()`

### Struttura Backend Modulare
- **Modelli**: package `cs_clips/models/` — un file per modello, esportati da `__init__.py`
- **API**: `cs_clips/api/{dominio}/` — ogni dominio ha `{dominio}_views.py`, `{dominio}_serializers.py`, `{dominio}_urls.py`
- **Eccezioni**: `cs_clips/exceptions/` — `error_handler.py` + `error_response_serializer.py`
- **Utilities**: `cs_clips/utils/` — un file per funzionalita' specifica
- **Management commands**: `cs_clips/management/commands/`
- I file `{dominio}_urls.py` nelle sottocartelle api/ sono dead code — il routing passa SOLO da `cs_clips/urls.py`

### Error Handling Centralizzato
- Configurato globalmente in `REST_FRAMEWORK['EXCEPTION_HANDLER']` → `handle_exception_with_serializer`
- NON serve piu' sovrascrivere `handle_exception()` nei singoli ViewSet
- Risposta errore standard: `{"code": "...", "detail": "..."}` via `ErrorResponseSerializer`
- Mapping: ValidationError→400, NotAuthenticated→401, PermissionDenied→403, NotFound→404, IntegrityError→409
- Per ValidationError con dict: formatta come "Campo 'field': error1, error2 | Campo 'field2': ..."

### Import & Configurazione
- Import relativi per moduli interni app (`.models`, `.api.videos.video_serializers`)
- Import assoluti per Django/DRF
- `.env` nella root progetto (NON in `backend/`)
- NOTA: le credenziali MinIO in settings.py sono attualmente HARDCODED (TODO: migrare a .env)

### Gestione File Media
- Storage: MinIO via `django-minio-storage` — file caricati nel bucket root (`upload_to=""`)
- `django-cleanup` gestisce auto-delete file su model delete — NON fare override di `Model.delete()` per cancellare file
- Durata video calcolata automaticamente in `VideoInputSerializer.create()` via moviepy
- Presigned URL generate nel `VideoOutputSerializer` via client `minio` Python con `@lru_cache(maxsize=1)`, scadenza 1 ora

## Regole Specifiche Framework — Backend (DRF/JWT)

### ViewSet & Routing
- **Pattern A** — `ModelViewSet` + `DefaultRouter`: Comments, Ratings (CRUD standard)
- **Pattern B** — `ModelViewSet` con serializer multipli + `@action`: Videos, Users
  - `get_serializer_class()` ritorna serializer diverso per action (create/update/list)
  - `parser_classes = [MultiPartParser, FormParser]` per upload file
- **Pattern C** — `APIView` standalone: EndContestView (POST), ContestWinnersView (GET)
- **Pattern D** — `ModelViewSet` con `get_permissions()` override: UserViewSet (`AllowAny` solo per `create`)
- I Contest NON hanno ViewSet CRUD — creati implicitamente da `get_or_create_current_contest()`
- URL base API: `/api/` → include `cs_clips.urls` (unico punto di routing)
- Tutti gli endpoint list DEVONO ritornare formato paginato Django (`{count, next, previous, results}`), MAI array raw

### Autenticazione JWT
- Endpoint: `/api/token/` (obtain), `/api/token/refresh/`
- `CustomTokenObtainPairView` aggiorna `last_login` ad ogni login
- Tutti gli endpoint richiedono `IsAuthenticated` di default
- Registrazione utente (`UserViewSet.create`) e' l'unico endpoint `AllowAny`

### Sistema Permessi (Role-Based)
- Gruppi Django: `toconfirm` (read-only), `user` (CRUD proprio), `admin` (chiusura contest), superuser flag (tutto)
- `RoleBasedPermission`: permesso globale su tutti i ViewSet
- `OnlyUsersPermission`: per azioni riservate a utenti confermati (follow/unfollow)
- `OnlyAdminsPermission`: controlla gruppo `'admin'` OPPURE flag `is_superuser` — sono due cose diverse
- Nuovi utenti → gruppo `toconfirm` automaticamente in `perform_create()`
- Delete: utenti `user` possono eliminare SOLO i propri contenuti
- ATTENZIONE: il campo FK proprietario varia per modello — `uploader=` per Video, `user=` per Rating/Comment

### Pattern Serializer
- `perform_create()` per iniettare utente autenticato: `serializer.save(user=request.user)` per Rating/Comment, `serializer.save(uploader=request.user, ...)` per Video
- Campi calcolati: `SerializerMethodField` (es. `get_average_rating`, `get_file_url`)
- Campi relazionati read-only: `ReadOnlyField(source='relazione.campo')`
- Validazione business logic → `validate()` nel serializer, NON nella view
- `VideoInputSerializer.create()`: calcola durata via moviepy, assegna contest via `get_or_create_current_contest(tag)`
- `VideoUpdateSerializer.update()`: se tag cambia, riassegna contest

### Pattern Database
- Incrementi atomici: usare `models.F('campo') + 1` poi `refresh_from_db()`, MAI `obj.campo += 1`
- Contest creati implicitamente via `get_or_create_current_contest(tag)` al video upload
- Settimana contest: lunedi' → sabato (NON domenica)
- Paginazione globale `PAGE_SIZE=10`, nelle custom actions: `self.paginate_queryset()` → `self.get_paginated_response()`

## Regole Specifiche Framework — Frontend (Next.js/React)

### Architettura Route
- **Route groups**: `(auth)/` (login, registrati) e `(main)/` (area protetta con shell layout)
- **Auth guard**: nel layout di `(main)/`, NON in middleware — redirect client-side via `useEffect`
- **RSC/Client split**: solo `/clip/[id]/page.tsx` e' RSC (SSR fetch + `generateMetadata` per SEO). Tutte le altre pagine sono `"use client"`
- **Componenti**: named export (mai default export, tranne page.tsx di Next.js)
- **Import**: sempre `@/` alias (mai path relativi `../../`)

### React Query
- `useQuery` per singoli item, `useInfiniteQuery` per feed paginati
- `getNextPageParam` usa `extractPageFromUrl()` (parsa URL `next` di Django)
- Optimistic updates completi su follow/unfollow (`onMutate` → `onError` rollback → `onSettled` invalidate)
- `staleTime: 5min` per user data, `30s` per search, global default `30s`
- `placeholderData: (prev) => prev` per paginazione senza layout shift
- Chiavi React Query precise e mirate — MAI invalidare chiavi generiche come `["users"]`
- **`useComments` fa fetch eager di TUTTE le pagine** (waterfall loop) per costruire `popupMap` e `markerPositions` sulla timeline video. E' by design — NON refactorare a lazy load

### Auth Frontend
- `AuthProvider` React Context (user, isAuthenticated, login, logout, register)
- Access token in memoria (variabile modulo), refresh token in localStorage
- Cookie `session_active=1` per awareness SSR/middleware
- Interceptor Axios con mutex/queue per 401 concorrenti → refresh → retry
- Logout decoupled: evento DOM `auth:logout` + toast Sonner
- `API_BASE_URL` legge da `process.env.NEXT_PUBLIC_API_URL`, fallback `http://127.0.0.1:8000`

### Error Handling Frontend
- Ogni pagina con fetch DEVE avere `isError` + `<ErrorMessage onRetry={refetch} />`
- `ErrorMessage` accetta `message`, `onRetry`, `className`

## Regole di Testing

### Setup Utente nei Test (CRITICO — fare PRIMA di tutto)
- `User.groups` ha `blank=False` — ogni utente DEVE avere almeno un gruppo
- Pattern obbligatorio per creare utenti nei test:
  ```python
  from django.contrib.auth import get_user_model
  from django.contrib.auth.models import Group
  User = get_user_model()
  user = User.objects.create_user(username='test', password='test', email='test@test.com')
  group, _ = Group.objects.get_or_create(name='user')
  user.groups.add(group)
  ```
- MAI usare `User.objects.create_user()` senza assegnare un gruppo subito dopo

### Stato Attuale
- Non esiste una test suite formale — nessun pytest, nessun conftest.py, nessuna CI
- `test_spareggio.py` e' un management command manuale (`python manage.py test_spareggio`), NON un test Django — NON usarlo come pattern per test automatici
- La directory `backend/cs_clips/tests/` va ricreata con `__init__.py` (cancellata nel backend reset)

### Regole per Nuovi Test
- Usare `django.test.TestCase` come base class (supporto transazioni DB automatico)
- Per test API: usare `rest_framework.test.APITestCase` + `APIClient`
- Test file in `backend/cs_clips/tests/` — naming: `test_<modulo>.py`
- JWT nei test: usare `force_authenticate()` (piu' semplice), oppure ottenere token via `TokenObtainPairView`
- File video nei test: usare `tempfile.NamedTemporaryFile(suffix=".mp4")` o `SimpleUploadedFile`
- Database: PostgreSQL richiesto (no SQLite) — i test necessitano del DB Docker attivo
- Test che coinvolgono `Video.file` richiedono **MinIO attivo** (Docker). Per test senza file reale, mockare lo storage
- Eseguire con: `python manage.py test` dalla directory `backend/`

### Isolamento Test
- I test NON devono assumere dati pre-esistenti nel DB — ogni test crea i propri dati in `setUp()`
- Nessun test deve dipendere dall'ordine di esecuzione
- Django TestCase fa rollback DB automatico, ma file su MinIO NO — considerare cleanup manuale se necessario

## Qualita' Codice e Stile

### Convenzioni di Naming
- File Python: `snake_case` con prefisso dominio (es. `comment_views.py`, `video_serializers.py`)
- Classi: `PascalCase` (es. `VideoViewSet`, `RatingSerializer`)
- Funzioni/variabili: `snake_case` (es. `get_or_create_current_contest`)
- URL path: `kebab-case` (es. `top-rated`, `contest-winners`)
- Enum: `TextChoices` con valori lowercase (es. `'clutch'`, `'funny'`, `'fail'`)
- File frontend: `kebab-case.tsx` (es. `clip-card.tsx`, `follow-button.tsx`)
- Componenti React: `PascalCase` (es. `ClipCard`, `FollowButton`)
- Tipi TypeScript: un file per dominio in `src/types/`, barrel export da `index.ts`

### Organizzazione Codice
- Backend: struttura modulare — vedi sezione "Struttura Backend Modulare"
- Frontend: `src/components/{dominio}/`, `src/lib/api/`, `src/lib/hooks/`, `src/providers/`, `src/types/`
- Shadcn/UI primitivi: `src/components/ui/` (NON modificare direttamente)
- Componenti condivisi: `src/components/shared/`

### Lingua (CRITICO)
- **Codice** (classi, variabili, URL path, nomi file): inglese
- **Commenti e docstring Python**: italiano
- **Messaggi API e help_text nei modelli**: italiano
- **UI frontend (label, placeholder, testi)**: italiano
- Un agente NON deve mai generare messaggi utente in inglese

### Pattern di Qualita' Impliciti
- Ogni ViewSet DEVE avere `permission_classes` esplicito
- `read_only_fields` sempre dichiarati nei serializer Meta
- `related_name` sempre specificato nelle ForeignKey
- `on_delete` esplicito: `CASCADE` per relazioni forti, `SET_NULL` per relazioni deboli
- `unique_together` per vincoli di unicita' compositi
- Nessun linter/formatter configurato (no flake8, black, isort, ruff, prettier)

### Documentazione
- TODO inline: `#TODO` (formato senza spazio dopo #)
- API docs: `@extend_schema` di drf-spectacular per endpoint con parametri custom

## Regole Workflow di Sviluppo

### Struttura Progetto
- Root: `.env`, `compose.yml`, `package.json` (orchestrazione monorepo), `.gitignore`
- `backend/`: tutto il codice Django (`manage.py`, app `cs_clips`, progetto `project_clip`)
- `frontend/`: app Next.js 16 (React 19, TailwindCSS 4, Shadcn)
- `db/`: volume PostgreSQL Docker (gitignored)
- `minio_data/`: volume MinIO Docker (gitignored)
- `.venv/`: virtual environment Python (gitignored)

### Setup Locale
- **Prerequisiti**: Docker Desktop avviato, Node.js >= 18, Python venv configurato, ffmpeg installato
- **Avvio completo**: `npm run dev` dalla root (avvia Docker, attende DB, lancia backend + frontend, apre browser)
- **Stop**: `Ctrl+C` nel terminale, poi `npm run docker:down` per i container
- **Avvio manuale**: `docker compose up -d` → `.venv/Scripts/activate` → `python manage.py runserver` da `backend/` → `npm run dev` da `frontend/`
- **Variabili d'ambiente**: tutte in `.env` nella root progetto (NON in `backend/`)

### Script NPM (root package.json)
- `npm run dev` — avvio completo
- `npm run docker:up` / `npm run docker:down` — gestione container Docker
- `npm run backend` — solo backend Django
- `npm run frontend` — solo frontend Next.js

### Git & Collaborazione
- Branch principale: `main`
- Nessuna CI/CD configurata
- `.gitignore` protegge: `.env`, `.venv/`, `db/`, `minio_data/`, `media/`, `__pycache__`

### Migrazioni Django
- Nuovi modelli/campi → `python manage.py makemigrations` poi `migrate`
- Nuovi gruppi utente → creare via data migration (NON solo `get_or_create()` runtime)
- Migrazioni numerate sequenzialmente in `cs_clips/migrations/`

## Regole Critiche da Non Dimenticare

### Anti-Pattern da Evitare
- MAI creare un ContestViewSet/CRUD per Contest — sono gestiti implicitamente
- MAI usare `obj.campo += 1` per incrementi — usare `F()` expression
- MAI importare `User` direttamente da `django.contrib.auth.models` — vale nel codice E nei test
- MAI generare messaggi utente/help_text in inglese
- MAI creare gruppi utente solo via codice runtime senza migration
- MAI assumere che Django giri in Docker — gira in locale
- MAI creare utenti senza assegnare un gruppo (`User.groups` ha `blank=False`)
- MAI fare override di `Model.delete()` per cancellare file — c'e' django-cleanup
- MAI usare Celery/Redis — non sono configurati
- MAI ritornare array raw da endpoint list — sempre formato paginato Django

### Edge Case Contest
- Contest settimanali: lunedi' → sabato (NON domenica), creati on-demand al primo upload della settimana
- Un contest chiuso nella stessa settimana genera un nuovo contest con suffisso numerico (`(2)`, `(3)`)
- Il tag del video DEVE corrispondere al tag del contest
- Spareggio: algoritmo ponderato (ratings: 0.5, comments: 0.2, views: 0.3) normalizzato con numpy
- APScheduler chiude contest automaticamente ogni giovedi' alle 11:33
- Chiusura manuale anche possibile via `POST /api/contests/end/` (richiede gruppo `admin` o `is_superuser`)
- APScheduler e EndContestView devono essere idempotenti — verificare `is_closed` prima di chiudere un contest
- `ContestWinnersView` restituisce Video vincitori, NON oggetti Contest

### Bug/Limiti Noti
- `[FIX-READY]` `get_average_rating()` in `VideoOutputSerializer` itera `obj.ratings.all()` in Python — N+1 query, usare `Avg()` annotation
- `[FIX-READY]` Scheduler: log message dice "11:24" ma il cron effettivo e' 11:33
- `[FIX-READY]` `RoleBasedPermission.has_object_permission()` blocca GET/PUT/PATCH per gruppo 'user' — solo DELETE e' gestito, tutto il resto cade a `return False`. Utenti normali non possono fare retrieve/update su nessun oggetto
- `[WORKAROUND]` `VideoInputSerializer.create()` fa rollback manuale senza `transaction.atomic()` — rischio record orfani. Non fixare senza ridisegnare il flusso
- `[WORKAROUND]` Video con `duration=0` (default vecchi record): `timestamp_second` puo' essere solo 0

### Gap Backend/Frontend (da colmare)
- **Modelli mancanti**: VideoLike, CommentLike, Notification
- **Campi mancanti**: `User.bio`, `Video.allow_download`, `Comment.is_disabled`
- **Endpoint mancanti**: user lookup by-username, `followers_count`/`following_count`/`is_followed_by_me` nel serializer User
- Il frontend ha tipi TypeScript per tutti questi campi — le API call falliranno a runtime fino a implementazione
- **NON implementare questi gap senza una story approvata** che definisca schema e API

### Validazione Dati
- Rating: valori 1-5 (NON 1-10), validato con MinValueValidator/MaxValueValidator
- Comment.timestamp_second: deve essere >= 0 e <= video.duration
- Contest.Tag choices: `'clutch'`, `'funny'`, `'fail'` — usare sempre questi valori esatti

### Sicurezza
- JWT obbligatorio su tutti gli endpoint tranne registrazione
- Password hashata via `create_user()`, MAI salvare password in chiaro
- `SECRET_KEY` in `.env`, mai hardcoded in settings
- Gruppo `toconfirm` = read-only fino a promozione manuale a `user`
- Credenziali MinIO attualmente hardcoded in settings — TODO da risolvere

### Relazioni tra Modelli (Mappa)
- User ←(`uploader`, related: `uploaded_videos`)→ Video (CASCADE)
- User ←(`user`, related: `ratings`)→ Rating (CASCADE)
- User ←(`user`, related: `comments`)→ Comment (CASCADE)
- User ←(`following`, related: `followers`)→ User (ManyToMany, symmetrical=False)
- User ←(`groups`, related: `custom_user_set`)→ Group (ManyToMany, blank=False — RICHIEDE almeno un gruppo)
- Contest ←(`contest`, related: `videos`)→ Video (SET_NULL)
- Contest ←(`winner`, related: `won_contests`)→ Video (SET_NULL)
- Video ←(`video`, related: `ratings`)→ Rating (CASCADE)
- Video ←(`video`, related: `comments`)→ Comment (CASCADE)
- Rating: unique_together (user, video)
- Contest: unique_together (start_date, end_date, tag)

---

## Linee Guida di Utilizzo

**Per Agenti AI:**
- Leggere questo file PRIMA di implementare qualsiasi codice
- Seguire TUTTE le regole esattamente come documentate
- In caso di dubbio, preferire l'opzione piu' restrittiva
- Aggiornare questo file se emergono nuovi pattern

**Per Umani:**
- Mantenere questo file snello e focalizzato sulle esigenze degli agenti
- Aggiornare quando lo stack tecnologico cambia
- Rivedere periodicamente per rimuovere regole obsolete

Ultimo aggiornamento: 2026-02-28
