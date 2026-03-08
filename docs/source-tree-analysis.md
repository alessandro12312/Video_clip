# Analisi Albero Sorgente — Video_clip

> Aggiornato il 2026-03-08 | Deep Scan | Workflow: document-project v1.2.0

---

## Struttura Root

```
Video_clip/
├── .env                         # Variabili ambiente (Docker, DB, MinIO)
├── .gitignore
├── README.md                    # Setup rapido monorepo
├── compose.yml                  # Docker: PostgreSQL 16, pgAdmin, MinIO
├── package.json                 # Root package (solo per tools)
│
├── backend/                     # 🔵 Django REST API (Python)
├── frontend/                    # 🟣 Next.js React App (TypeScript)
├── docs/                        # 📄 Documentazione generata
├── _bmad/                       # 🔧 BMAD workflow engine
└── _bmad-output/                # 📋 Artefatti pianificazione BMAD
```

---

## Backend — Django REST API

```
backend/
├── manage.py                    # ⭐ ENTRY POINT — Django CLI
├── requirements.txt             # Dipendenze Python (77 packages)
├── .env.example                 # Template variabili ambiente
├── CLAUDE.md                    # Istruzioni agente AI
├── schema.yaml                  # Schema OpenAPI generato (drf-spectacular)
│
├── project_clip/                # 📦 Configurazione Django
│   ├── __init__.py
│   ├── settings.py              # ⭐ Settings: DB, JWT, MinIO, CORS, REST
│   ├── urls.py                  # ⭐ Root URL: /admin/, /api/, /api/token/
│   └── wsgi.py                  # WSGI entry point (produzione)
│
├── cs_clips/                    # 📦 App principale
│   ├── __init__.py
│   ├── apps.py                  # AppConfig + avvio APScheduler
│   ├── admin.py                 # Admin personalizzato (5 modelli)
│   ├── permissions.py           # RoleBasedPermission, OnlyUsersPermission, OnlyAdminsPermission
│   ├── scheduler.py             # APScheduler: cron chiusura contest (giovedì 11:33)
│   ├── urls.py                  # Router DRF: users, videos, ratings, comments + contest
│   │
│   ├── models/                  # 🗃️ Modelli dati (1 file per modello)
│   │   ├── __init__.py          # Barrel export
│   │   ├── user.py              # User (extends AbstractUser) — email unique, following M2M
│   │   ├── video.py             # Video — title, file (MinIO), duration, tag, views
│   │   ├── contest.py           # Contest — tag (clutch/funny/fail), winner, date range
│   │   ├── comment.py           # Comment — content, timestamp_second
│   │   └── rating.py            # Rating — value 1-5, unique(user, video)
│   │
│   ├── api/                     # 🌐 Endpoint REST (per dominio)
│   │   ├── comments/
│   │   │   ├── comment_views.py
│   │   │   ├── comment_serializers.py
│   │   │   └── comment_urls.py
│   │   ├── contests/
│   │   │   ├── contest_views.py     # ContestWinnersView, EndContestView
│   │   │   ├── contest_serializers.py
│   │   │   └── contest_urls.py
│   │   ├── ratings/
│   │   │   ├── rating_views.py
│   │   │   ├── rating_serializers.py
│   │   │   └── rating_urls.py
│   │   ├── users/
│   │   │   ├── user_views.py        # UserViewSet + CustomTokenObtainPairView
│   │   │   ├── user_serializers.py
│   │   │   └── user_urls.py
│   │   └── videos/
│   │       ├── video_views.py       # VideoViewSet (upload, views, following, top-rated)
│   │       ├── video_serializers.py # Input/Output/Update serializers
│   │       └── video_urls.py
│   │
│   ├── exceptions/              # ⚠️ Gestione errori centralizzata
│   │   ├── error_handler.py     # handle_exception_with_serializer
│   │   └── error_response_serializer.py
│   │
│   ├── utils/                   # 🔧 Utility
│   │   ├── desempate.py         # Algoritmo spareggio contest (numpy)
│   │   └── get_date_util.py     # get_or_create_current_contest()
│   │
│   ├── management/              # 🔧 Management commands
│   │   └── commands/
│   │       └── close_contests.py    # Auto-chiusura contest scaduti
│   │
│   └── migrations/              # 📊 Migrazioni DB
│       ├── 0001_initial.py      # Schema completo (5 modelli)
│       └── 0002_alter_video_file.py
│
├── policy/                      # 📋 Policy MinIO
│   └── admin.json
│
└── scripts/                     # 📋 Script infrastruttura
    └── minio_init.sh            # Init bucket MinIO
```

### Directory Critiche Backend

| Directory | Scopo | Frequenza Modifica |
|---|---|---|
| `cs_clips/api/` | Endpoint REST (views + serializers + urls) | Alta |
| `cs_clips/models/` | Schema dati e business logic | Media |
| `project_clip/settings.py` | Configurazione globale | Bassa |
| `cs_clips/permissions.py` | Controllo accessi | Bassa |
| `cs_clips/utils/` | Logica di business (spareggio, date) | Media |

---

## Frontend — Next.js React App

```
frontend/
├── package.json                 # ⭐ Dipendenze + scripts (dev, build, start, lint)
├── next.config.ts               # Config Next.js (minimale)
├── tsconfig.json                # TypeScript strict, path alias @/*
├── postcss.config.mjs           # TailwindCSS v4 via PostCSS
├── eslint.config.mjs            # ESLint 9 FlatConfig (core-web-vitals)
├── components.json              # shadcn/ui config (New York, neutral, lucide)
│
├── public/                      # 📁 Asset statici
│   └── *.svg                    # Icone placeholder
│
└── src/                         # 📦 Codice sorgente
    ├── middleware.ts             # ⭐ Auth middleware (route protection via cookie)
    │
    ├── app/                     # 🗂️ App Router (route groups)
    │   ├── layout.tsx           # ⭐ ROOT LAYOUT — Providers, Geist, dark mode
    │   ├── page.tsx             # Landing/redirect
    │   ├── globals.css          # 🎨 Tema: gradient, glass, animazioni custom
    │   ├── error.tsx            # Error boundary globale
    │   ├── not-found.tsx        # Pagina 404
    │   │
    │   ├── (auth)/              # 🔐 Route group autenticazione
    │   │   ├── layout.tsx       # Layout centrato (max-w-500px)
    │   │   ├── login/page.tsx
    │   │   └── register/page.tsx
    │   │
    │   ├── (main)/              # 🏠 Route group app (protetto)
    │   │   ├── layout.tsx       # Sidebar + header + bottombar
    │   │   ├── home/page.tsx        # Feed following
    │   │   ├── esplora/page.tsx     # Esplora video
    │   │   ├── carica/page.tsx      # Upload wizard (3 step)
    │   │   ├── profilo/page.tsx     # Profilo utente
    │   │   ├── contest/page.tsx     # Vincitori
    │   │   └── settings/page.tsx    # Impostazioni
    │   │
    │   └── clip/[id]/           # 🎬 Dettaglio video (route dinamica)
    │       ├── layout.tsx       # Layout condizionale (auth/public)
    │       ├── page.tsx         # Server component (metadata + ID)
    │       └── clip-content.tsx # Client component (player, commenti, rating)
    │
    ├── components/              # 🧩 Componenti (54 totali)
    │   ├── layout/              # Navigazione (5): Sidebar, Header, BottomBar, NavBar, UserMenu
    │   ├── feed/                # Feed (5): CardAsPlayer, CardAsPlayerSkeleton, FeedGrid, ClipCard*, ClipCardSkeleton*
    │   ├── video/               # Video (5): Player, Controls, ProgressBar, Popup, Marker
    │   ├── comments/            # Commenti (5): Section, Form, List, Item, CommentSidebar
    │   ├── rating/              # Rating (1): StarRating
    │   ├── user/                # Utente (7): Avatar, Follow, Profile, Search, etc.
    │   ├── shared/              # Condivisi (8): EmptyState, Error, Spinner, InfiniteScroll, etc.
    │   └── ui/                  # shadcn/ui (18): AlertDialog, Button, Card, Dialog, Input, etc.
    │
    ├── lib/                     # 📚 Librerie
    │   ├── api/                 # HTTP: client.ts + 6 moduli (auth, users, videos, etc.)
    │   ├── hooks/               # React Query + utility: 22 hooks (incl. useSnapScroll)
    │   ├── query-keys.ts        # Factory chiavi cache
    │   ├── constants.ts         # Config app
    │   └── utils.ts             # cn(), format, extractPage, formatMMSS, parseMMSS
    │
    ├── providers/               # 🔌 Providers (3)
    │   ├── auth-provider.tsx    # JWT auth (in-memory + localStorage)
    │   ├── query-provider.tsx   # React Query (staleTime 30s)
    │   └── login-transition-provider.tsx
    │
    └── types/                   # 📐 TypeScript (7 files)
        ├── api.ts, user.ts, video.ts, comment.ts, rating.ts, contest.ts
        └── index.ts             # Barrel export
```

### Directory Critiche Frontend

| Directory | Scopo | Frequenza Modifica |
|---|---|---|
| `src/components/` | Componenti UI (54 totali) | Alta |
| `src/lib/api/` | Client HTTP e moduli API | Media |
| `src/lib/hooks/` | React Query + utility hooks (22) | Media |
| `src/app/` | Pagine e layout (13 pagine) | Alta |
| `src/providers/` | Auth, Query, Transition | Bassa |

---

## Infrastruttura (compose.yml)

```
Docker Compose Services:
├── db (postgres:16)             # Database — Port 5432 — Volume: ./db
├── pgadmin (dpage/pgadmin4)     # Admin DB — Port 5050
├── minio (minio/minio:latest)   # Object Storage — Port 9000 (API) / 9001 (Console)
│   └── Volume: ./minio_data
└── minio-init (minio/mc)        # Init bucket + policy
    └── Script: backend/scripts/minio_init.sh
```

---

## Punti di Integrazione

```
Frontend ◄──── REST API (JSON/JWT) ────► Backend ──── psycopg3 ────► PostgreSQL
                                              │
                                              ├──── MinIO SDK ────► MinIO (S3)
                                              │
Frontend ◄──── Presigned URL (1h) ──────── MinIO
```
