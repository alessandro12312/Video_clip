---
project_name: 'Video_clip'
user_name: 'AcchippameQuisso'
date: '2026-02-13'
sections_completed: ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'code_quality', 'workflow_rules', 'critical_rules']
status: 'complete'
rule_count: 87
optimized_for_llm: true
---

# Project Context per Agenti AI

_Questo file contiene regole critiche e pattern che gli agenti AI devono seguire quando implementano codice in questo progetto. Focus su dettagli non ovvi che gli agenti potrebbero altrimenti perdere._

---

## Technology Stack & Versioni

### Core
- **Backend:** Python 3.x + Django 5.1.6
- **API:** Django REST Framework 3.15.1
- **Database:** PostgreSQL 16 (Docker), driver **psycopg 3.2.4** (NON psycopg2)
- **Auth:** SimpleJWT 5.3.1 (access 12h, refresh 1d, rotate=True)
- **Docs API:** drf-spectacular 0.28.0 (Swagger + ReDoc)
- **CORS:** django-cors-headers 4.9.0 (consente Next.js dev su localhost:3000)
- **Filtering:** django-filter 24.3 (filtri su ViewSet via `filterset_fields`)

### Media Processing
- **moviepy 2.2.1** - Import: `from moviepy import VideoFileClip` (v2 syntax)
- **Pillow 11.1.0**, imageio-ffmpeg 0.6.0

### Utility
- **numpy 2.2.6** (spareggio ponderato contest)
- **python-dotenv 1.0.1** + django-environ 0.12.0

### Frontend
- **Next.js 16.1.6** (Turbopack) + React 19 + TypeScript 5
- **UI:** TailwindCSS 4, Shadcn, Radix UI, Framer Motion, Lucide icons
- **State/Data:** TanStack React Query, Axios, jwt-decode
- **Temi:** next-themes (dark mode)

### Infrastruttura
- **Docker Compose:** solo PostgreSQL 16 + pgAdmin4 (Django gira in locale, NON in container)
- **Monorepo:** `package.json` root con `concurrently` + `wait-on` per orchestrazione dev
- **Paginazione globale:** PageNumberPagination, PAGE_SIZE=10

### Note Critiche per Agenti
- MAI usare `from django.contrib.auth.models import User` → usare `get_user_model()`
- Il file `.env` è nella root del progetto, NON in `backend/`
- psycopg 3.x ha API diversa da psycopg2 - non confondere
- moviepy 2.x: import cambiati rispetto alla v1

## Regole Specifiche Python/Django

### Custom User Model
- Il progetto usa `cs_clips.User` (AbstractUser), configurato in `AUTH_USER_MODEL`
- SEMPRE usare `get_user_model()` per referenziare il modello User
- MAI importare `django.contrib.auth.models.User` direttamente
- Pattern: `from django.contrib.auth import get_user_model` → `User = get_user_model()`

### Error Handling Centralizzato
- Tutti i ViewSet usano `handle_exception_with_serializer(exc)` in `views.py`
- Risposta errore standard: `{"code": "...", "detail": "..."}` via `ErrorResponseSerializer`
- Mapping: ValidationError→400, NotAuthenticated→401, PermissionDenied→403, NotFound→404, IntegrityError→409
- Ogni nuovo ViewSet DEVE sovrascrivere `handle_exception()` delegando a questa funzione

### Import & Configurazione
- Import relativi per moduli interni app (`.models`, `.serializers`)
- Import assoluti per Django/DRF
- `.env` nella root progetto, caricato con `load_dotenv(BASE_DIR.parent / '.env')`
- Configurazioni sensibili via `os.getenv()`

### Gestione File Media
- Override di `Model.delete()` su Video per cancellare il file fisico da disco
- Upload path: `media/videos/` (relativo a `backend/`)
- Durata video calcolata automaticamente nel serializer `create()` via moviepy

## Regole Specifiche Framework (DRF/JWT)

### ViewSet & Routing
- CRUD standard: `ModelViewSet` + `DefaultRouter` (users, videos, ratings, comments)
- Endpoint non-CRUD: `APIView` standalone (es. EndContestView, ContestWinnersView)
- Sotto-risorse: `@action(detail=True/False)` con `url_path` esplicito
- URL base API: `/api/` → include `cs_clips.urls`
- I Contest NON hanno ViewSet CRUD - vengono creati implicitamente da `get_or_create_current_contest()`

### Autenticazione JWT
- Endpoint: `/api/token/` (obtain), `/api/token/refresh/`
- `CustomTokenObtainPairView` aggiorna `last_login` ad ogni login
- Tutti gli endpoint richiedono `IsAuthenticated` di default
- Registrazione utente (`UserViewSet.create`) è l'unico endpoint `AllowAny`

### Sistema Permessi (Role-Based)
- Gruppi Django: `toconfirm` (read-only), `user` (CRUD), `superuser` (tutto)
- `RoleBasedPermission`: permesso globale su tutti i ViewSet
- `OnlyUsersPermission`: per azioni riservate a utenti confermati
- Nuovi utenti → gruppo `toconfirm` automaticamente in `perform_create()`
- Delete: utenti `user` possono eliminare SOLO i propri contenuti
- ATTENZIONE: il campo proprietario varia per modello (`Video.uploader`, `Rating.user`, `Comment.user`)

### Pattern Serializer
- `perform_create()` per iniettare utente autenticato: `serializer.save(user=request.user)`
- Campi calcolati: `SerializerMethodField` (es. `get_average_rating`)
- Campi relazionati read-only: `ReadOnlyField(source='relazione.campo')`
- VideoSerializer.create() calcola durata e fa rollback (delete) se fallisce
- Validazione business logic → `validate()` nel serializer, NON nella view

### Pattern Database
- Incrementi atomici: usare `models.F('campo') + 1` poi `refresh_from_db()`, MAI `obj.campo += 1`
- Contest creati implicitamente via `get_or_create_current_contest(tag)` al video upload

### Paginazione
- Globale: `PageNumberPagination`, `PAGE_SIZE=10`
- Nelle custom actions: `self.paginate_queryset()` → `self.get_paginated_response()`

## Regole di Testing

### Stato Attuale
- Non esiste una test suite formale (no `tests.py`, no `conftest.py`, no pytest)
- Unico test: management command `test_spareggio.py` (test manuale spareggio ponderato)
- Framework di test: Django TestCase (built-in) - nessun pytest configurato

### Regole per Nuovi Test
- Usare `django.test.TestCase` come base class (supporto transazioni DB automatico)
- Test file in `backend/cs_clips/tests/` (creare directory se necessario)
- Naming: `test_<modulo>.py` (es. `test_views.py`, `test_serializers.py`, `test_models.py`)
- Usare `get_user_model()` anche nei test, MAI import diretto del modello User
- Per test API: usare `rest_framework.test.APITestCase` + `APIClient`
- JWT nei test: ottenere token via `TokenObtainPairView` o usare `force_authenticate()`
- File video nei test: usare `tempfile.NamedTemporaryFile(suffix=".mp4")` (pattern da `test_spareggio.py`)
- Database: PostgreSQL richiesto (no SQLite) - i test necessitano del DB Docker attivo
- Eseguire con: `python manage.py test` dalla directory `backend/`

## Qualità Codice e Stile

### Convenzioni di Naming
- File Python: `snake_case` (es. `serializers.py`, `permissions.py`)
- Classi: `PascalCase` (es. `VideoViewSet`, `RatingSerializer`)
- Funzioni/variabili: `snake_case` (es. `get_or_create_current_contest`)
- URL path: `kebab-case` (es. `top-rated`, `contest-winners`)
- Enum: `TextChoices` con valori lowercase (es. `'clutch'`, `'funny'`, `'fail'`)
- NOTA: `getDateUtil.py` usa camelCase nel nome file (eccezione storica)

### Organizzazione Codice
- App singola `cs_clips`: models, views, serializers, permissions, urls, admin
- Progetto `project_clip`: settings, urls root, wsgi
- Utilities: `cs_clips/utils/` (un file per funzionalità specifica)
- Management commands: `cs_clips/management/commands/`

### Lingua (CRITICO)
- **Codice** (classi, variabili, URL path): inglese
- **Commenti e docstring**: italiano
- **Messaggi API e help_text nei modelli**: italiano
- Un agente NON deve mai generare messaggi utente in inglese

### Pattern di Qualità Impliciti
- Ogni ViewSet DEVE avere `permission_classes` esplicito
- `read_only_fields` sempre dichiarati nei serializer Meta
- `related_name` sempre specificato nelle ForeignKey
- `on_delete` esplicito: `CASCADE` per relazioni forti, `SET_NULL` per relazioni deboli
- `unique_together` per vincoli di unicità compositi

### Debito Tecnico Noto (TODO)
- Modelli con `default=` provvisori marcati `#TODO: rimuovere in produzione`
- Permessi da rivedere su EndContestView e ContestWinnersView
- Serializer User da semplificare (senza lista followers/following)
- Nuovi gruppi utente → creare via migration, NON solo `get_or_create()` runtime

### Documentazione
- TODO inline: `#TODO` (formato senza spazio dopo #)
- API docs: `@extend_schema` di drf-spectacular per endpoint con parametri custom
- Nessun linter/formatter configurato (no flake8, black, isort, ruff)

## Regole Workflow di Sviluppo

### Struttura Progetto
- Root: `.env`, `compose.yml`, `package.json` (orchestrazione monorepo), `.gitignore`
- `backend/`: tutto il codice Django (`manage.py`, app `cs_clips`, progetto `project_clip`)
- `frontend/`: app Next.js 16 (React 19, TailwindCSS 4, Shadcn)
- `db/`: volume PostgreSQL Docker (gitignored)
- `media/videos/`: upload video utenti (gitignored)
- `.venv/`: virtual environment Python (gitignored)

### Setup Locale - Avvio Rapido (consigliato)
- **Prerequisiti:** Docker Desktop avviato, Node.js >= 18, Python venv configurato
- **Avvio completo:** `npm run dev` dalla root (avvia Docker, attende DB, lancia backend + frontend, apre browser)
- **Stop:** `Ctrl+C` nel terminale (ferma backend e frontend), poi `npm run docker:down` per i container

### Setup Locale - Avvio Manuale
- Avviare PostgreSQL: `docker compose up -d` dalla root
- Attivare venv: `.venv/Scripts/activate` (Windows)
- Migrazioni: `python manage.py migrate` da `backend/`
- Server dev: `python manage.py runserver` da `backend/`
- Frontend dev: `npm run dev` da `frontend/`
- Variabili d'ambiente: tutte in `.env` nella root progetto

### Script NPM (root package.json)
- `npm run dev` — avvio completo (Docker + backend + frontend + apre browser)
- `npm run docker:up` / `npm run docker:down` — gestione container Docker
- `npm run backend` — solo backend Django
- `npm run frontend` — solo frontend Next.js

### Git & Collaborazione
- Branch principale: `main`
- Progetto collaborativo con fork esterni (merge da fork)
- Nessuna CI/CD configurata
- `.gitignore` protegge: `.env`, `.venv/`, `db/`, `media/videos/`, `__pycache__`

### Migrazioni Django
- Nuovi modelli/campi → `python manage.py makemigrations` poi `migrate`
- Nuovi gruppi utente → creare via data migration (non solo codice runtime)
- Migrazioni numerate sequenzialmente in `cs_clips/migrations/`

## Regole Critiche da Non Dimenticare

### Anti-Pattern da Evitare
- MAI creare un ContestViewSet/CRUD per Contest - sono gestiti implicitamente
- MAI usare `obj.campo += 1` per incrementi - usare `F()` expression
- MAI importare `User` direttamente da `django.contrib.auth.models`
- MAI generare messaggi utente/help_text in inglese
- MAI creare gruppi utente solo via codice runtime senza migration
- MAI assumere che Django giri in Docker - gira in locale
- MAI creare utenti senza assegnare un gruppo (`User.groups` ha `blank=False`)

### Edge Case Contest
- Contest settimanali: lunedì → domenica, creati on-demand al primo upload della settimana
- Un contest chiuso nella stessa settimana genera un nuovo contest con suffisso numerico
- Il tag del video DEVE corrispondere al tag del contest
- Spareggio: algoritmo ponderato (ratings: 0.5, comments: 0.2, views: 0.3) normalizzato con numpy
- Chiusura contest è MANUALE via `POST /api/contests/end/` - nessun cron/task automatico
- `ContestWinnersView` restituisce Video vincitori, NON oggetti Contest

### Bug/Limiti Noti
- `RoleBasedPermission.has_object_permission()` controlla `obj.user` ma Video ha `obj.uploader` - possibile bug su delete Video da utente `user`
- `VideoSerializer.create()` fa rollback manuale senza `transaction.atomic()` - rischio record orfani
- Video con `duration=0` (default vecchi record): `timestamp_second` può essere solo 0

### Validazione Dati
- Rating: valori 1-5 (NON 1-10), validato con MinValueValidator/MaxValueValidator
- Comment.timestamp_second: deve essere >= 0 e <= video.duration
- Contest.Tag choices: `'clutch'`, `'funny'`, `'fail'` - usare sempre questi valori esatti

### Sicurezza
- JWT obbligatorio su tutti gli endpoint tranne registrazione
- Password hashata via `create_user()`, MAI salvare password in chiaro
- `SECRET_KEY` in `.env`, mai hardcoded in settings
- Gruppo `toconfirm` = read-only fino a promozione manuale a `user`

### Relazioni tra Modelli (Mappa)
- User ←(uploader)→ Video (CASCADE)
- User ←(user)→ Rating (CASCADE)
- User ←(user)→ Comment (CASCADE)
- User ←(following)→ User (ManyToMany, symmetrical=False)
- User ←(groups)→ Group (ManyToMany, blank=False - RICHIEDE almeno un gruppo)
- Contest ←(contest)→ Video (SET_NULL)
- Contest ←(winner)→ Video (SET_NULL)
- Video ←(video)→ Rating (CASCADE)
- Video ←(video)→ Comment (CASCADE)
- Rating: unique_together (user, video)
- Contest: unique_together (start_date, end_date, tag)

---

## Linee Guida di Utilizzo

**Per Agenti AI:**
- Leggere questo file PRIMA di implementare qualsiasi codice
- Seguire TUTTE le regole esattamente come documentate
- In caso di dubbio, preferire l'opzione più restrittiva
- Aggiornare questo file se emergono nuovi pattern

**Per Umani:**
- Mantenere questo file snello e focalizzato sulle esigenze degli agenti
- Aggiornare quando lo stack tecnologico cambia
- Rivedere periodicamente per rimuovere regole obsolete
- Rimuovere regole che diventano ovvie nel tempo

Ultimo aggiornamento: 2026-02-13
