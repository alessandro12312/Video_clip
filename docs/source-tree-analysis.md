# Analisi Albero Sorgente - Video_clip

> Generato automaticamente il 2026-02-14 | Scan level: deep

## Struttura Completa del Progetto

```
Video_clip/                              # 📁 Root del monorepo
├── .env                                 # 🔑 Variabili d'ambiente (PostgreSQL, pgAdmin)
├── .gitignore                           # Git ignore rules
├── compose.yml                          # 🐳 Docker Compose (PostgreSQL + pgAdmin)
├── README.md                            # 📄 Documentazione setup progetto (IT)
│
├── backend/                             # 🟢 PARTE ATTIVA — Django REST API
│   ├── manage.py                        # ⚡ Entry point Django
│   ├── requirements.txt                 # 📦 Dipendenze Python
│   │
│   ├── project_clip/                    # ⚙️ Configurazione Django
│   │   ├── __init__.py
│   │   ├── settings.py                  # ⚙️ Settings: DB, JWT, DRF, media
│   │   ├── urls.py                      # 🌐 URL routing principale (admin, api, token, docs)
│   │   └── wsgi.py                      # 🚀 WSGI entry point
│   │
│   ├── cs_clips/                        # 📱 App Django principale
│   │   ├── __init__.py
│   │   ├── admin.py                     # 👤 Configurazione Django Admin
│   │   ├── models.py                    # 🗄️ 5 modelli ORM (User, Contest, Video, Rating, Comment)
│   │   ├── views.py                     # 🎯 ViewSets + APIViews (381 righe)
│   │   ├── serializers.py               # 📋 7 serializer DRF
│   │   ├── permissions.py               # 🔒 Classi permesso (RoleBasedPermission, OnlyUsersPermission)
│   │   ├── urls.py                      # 🔀 Router DRF + endpoint custom
│   │   │
│   │   ├── utils/                       # 🔧 Utility
│   │   │   ├── desempate.py             # 🏆 Algoritmo spareggio ponderato (numpy)
│   │   │   └── getDateUtil.py           # 📅 Gestione contest settimanali
│   │   │
│   │   ├── management/                  # 🛠️ Management commands
│   │   │   └── commands/
│   │   │       └── test_spareggio.py    # 🧪 Test manuale algoritmo spareggio
│   │   │
│   │   └── migrations/                  # 📊 14 migrazioni database
│   │       ├── 0001_initial.py          # Modelli base
│   │       ├── 0002_create_groups.py    # Gruppi ruoli
│   │       ├── 0003-0012_...            # Evoluzioni schema
│   │       ├── 0013_..._tag_duration.py # Tag contest, durata video, timestamp commenti
│   │       └── 0014_..._following.py    # Sistema followers
│   │
│   └── media/                           # 📁 File caricati (runtime)
│       └── videos/                      # 🎬 Video uploadati dagli utenti
│           └── .gitkeep
│
├── frontend/                            # 🔴 VUOTO — Da sviluppare
│
├── db/                                  # 💾 Volume PostgreSQL (Docker runtime)
│   └── .gitkeep
│
├── docs/                                # 📚 Documentazione generata
│   ├── index.md                         # (da generare)
│   ├── api-contracts.md                 # ✅ Contratti API completi
│   ├── data-models.md                   # ✅ Schema database
│   ├── source-tree-analysis.md          # ✅ Questo file
│   └── project-scan-report.json         # Stato workflow
│
└── _bmad-output/                        # 🤖 Artefatti BMAD
    └── project-context.md               # Contesto AI per sviluppo (87 regole)
```

---

## Directory Critiche

### `backend/cs_clips/` — Core dell'applicazione

Contiene tutta la logica di business:
- **models.py** — Definizione dello schema dati (5 modelli, relazioni, vincoli)
- **views.py** — Tutti gli endpoint API (4 ViewSets + 2 APIViews, 381 righe)
- **serializers.py** — Trasformazione dati (validazione, calcolo durata video)
- **permissions.py** — Logica di autorizzazione basata su ruoli
- **urls.py** — Routing API con DefaultRouter DRF

### `backend/project_clip/` — Configurazione Django

- **settings.py** — Configurazione completa: database, JWT, DRF, media, paginazione
- **urls.py** — Entry point URL: routing verso app, auth, Swagger

### `backend/cs_clips/utils/` — Logica di business specializzata

- **desempate.py** — Algoritmo di spareggio con normalizzazione numpy (pesi: ratings 50%, views 30%, comments 20%)
- **getDateUtil.py** — Creazione automatica contest settimanali con naming italiano

### `backend/cs_clips/migrations/` — Evoluzione schema

14 migrazioni che tracciano l'evoluzione del database dalla struttura iniziale (User, Video, Rating, Comment) fino alle feature più recenti (contest con tag, durata video, followers).

---

## Entry Points

| Entry Point | File | Descrizione |
|------------|------|-------------|
| **Django Management** | `backend/manage.py` | CLI Django (runserver, migrate, etc.) |
| **WSGI Application** | `backend/project_clip/wsgi.py` | Punto di avvio per web server |
| **API Root** | `backend/project_clip/urls.py` | Routing principale → `/api/`, `/admin/`, `/api/docs/` |
| **Docker Services** | `compose.yml` | PostgreSQL 16 (porta 5432) + pgAdmin (porta 8080) |

---

## Pattern di Organizzazione

- **Struttura monorepo:** `backend/` e `frontend/` come parti separate con servizi condivisi via Docker
- **Django single-app:** Tutta la logica in un'unica app `cs_clips` (appropriato per dimensione attuale)
- **Flat utils:** Utility in sottocartella dedicata (`utils/`) anziché app separate
- **Media locale:** File video serviti dal filesystem locale (non cloud storage)
- **Nessun test formale:** Solo un management command di test manuale, nessuna suite di test automatizzata
