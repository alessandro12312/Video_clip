# Panoramica Progetto — Video_clip

> Aggiornato il 2026-03-08 | Deep Scan | Workflow: document-project v1.2.0

---

## Cos'è Video_clip

**Video_clip** è una piattaforma web per contest settimanali di video clip gaming. Gli utenti possono caricare brevi clip, votare i migliori, commentare con timestamp e seguire altri utenti. Ogni settimana vengono premiati i vincitori nelle categorie **Clutch**, **Funny** e **Fail**.

---

## Funzionalità Principali

| Feature | Stato | Note |
|---|---|---|
| Registrazione e login (JWT) | Implementato | Token rotation, refresh automatico |
| Caricamento video | Implementato | Upload su MinIO, estrazione durata FFmpeg |
| Feed video (following + esplora) | Implementato | Snap scroll card-by-card, card-as-player inline |
| Classifica top-rated | Implementato | Filtro temporale (giorno/settimana/mese/anno/tutti) |
| Sistema rating 1-5 stelle | Implementato | Un voto per utente per video |
| Commenti con timestamp | Implementato | Popup overlay + sidebar chat, marker timeline |
| Follow/unfollow utenti | Implementato | Optimistic updates nel frontend |
| Contest settimanali | Implementato | Auto-chiusura con spareggio ponderato |
| Profilo utente | Implementato | Bio, video caricati, followers/following |
| Download video | Implementato | Campo allow_download, DownloadButton |
| Eliminazione video | Implementato | Solo proprietario, AlertDialog conferma |
| Eliminazione commenti | Implementato | Solo autore, con invalidazione cache |
| Vista pubblica clip | Implementato | Pagina clip accessibile senza login (SSR metadata) |
| Video likes | Non implementato | Bottone placeholder presente, modello VideoLike da creare |
| Comment likes | Non implementato | Modello CommentLike da creare |
| Notifiche | Non implementato | Modello Notification da creare |

---

## Struttura Repository

| Tipo | Dettaglio |
|---|---|
| **Repository** | Monorepo |
| **Parti attive** | 2 (backend + frontend) |
| **Infrastruttura** | Docker Compose (PostgreSQL, pgAdmin, MinIO) |

| Parte | Tipo | Stack | Path |
|---|---|---|---|
| **Backend** | Django REST API | Django 5.1.6 + DRF 3.15.1 + PostgreSQL 16 + MinIO | `backend/` |
| **Frontend** | Next.js React App | Next.js 16.1.6 + React 19 + TailwindCSS 4 + React Query 5 | `frontend/` |

---

## Stack Tecnologico

### Backend

| Categoria | Tecnologia | Versione |
|---|---|---|
| Framework | Django + DRF | 5.1.6 / 3.15.1 |
| Database | PostgreSQL + psycopg | 16 / 3.2.4 |
| Auth | SimpleJWT | 5.3.1 |
| Storage | MinIO (S3) | 7.2.15 |
| Video | moviepy + FFmpeg | 2.2.1 |
| Scheduler | APScheduler | 3.11.0 |
| API Docs | drf-spectacular | 0.28.0 |

### Frontend

| Categoria | Tecnologia | Versione |
|---|---|---|
| Framework | Next.js (App Router) | 16.1.6 |
| UI | React + Radix UI + shadcn/ui | 19.2.3 |
| Styling | TailwindCSS v4 | ^4 |
| State | React Query | 5.90.21 |
| HTTP | axios | 1.13.5 |
| Animation | framer-motion | 12.34.0 |

### Infrastruttura

| Servizio | Tecnologia | Porta |
|---|---|---|
| Database | PostgreSQL 16 | 5432 |
| Admin DB | pgAdmin 4 | 5050 |
| Object Storage | MinIO | 9000 / 9001 |

---

## Architettura

```
┌───────────┐    REST API     ┌───────────┐    SQL      ┌────────────┐
│ Frontend  │ ◄── JSON/JWT ──►│  Backend  │ ◄── ORM ──►│ PostgreSQL │
│ Next.js   │                 │  Django   │              └────────────┘
│ Port 3000 │                 │  Port 8000│    S3
└───────────┘                 │           │ ◄─────────►┌────────────┐
                              └───────────┘             │   MinIO    │
                                                        └────────────┘
```

- **Backend**: API-centric monolith, ViewSet-based REST, 35 endpoint
- **Frontend**: SPA con SSR, App Router, React Query server state
- **Comunicazione**: REST API + JWT, presigned URL per file video

---

## Numeri del Progetto

| Metrica | Valore |
|---|---|
| Endpoint API | 35 |
| Modelli dati | 5 + 3 M2M |
| Componenti frontend | 54 |
| React Query hooks | 22 |
| Pagine frontend | 13 |

---

## Documentazione Generata

- [Panoramica Progetto](./project-overview.md) — Questo file
- [Architettura Backend](./architecture-backend.md) — Pattern, stack, gap
- [Architettura Frontend](./architecture-frontend.md) — Componenti, state, design system
- [Integrazione](./integration-architecture.md) — Come le parti comunicano
- [Contratti API](./api-contracts-backend.md) — 35 endpoint con request/response
- [Modelli Dati](./data-models-backend.md) — Schema database, relazioni, vincoli, ER
- [Componenti Frontend](./component-inventory-frontend.md) — 54 componenti inventariati
- [State Management](./state-management-frontend.md) — React Query hooks, API layer, tipi
- [Albero Sorgente](./source-tree-analysis.md) — Struttura directory annotata
- [Guida Sviluppo](./development-guide.md) — Setup, comandi, convenzioni

---

## Link Rapidi

| Risorsa | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://127.0.0.1:8000/api/ |
| Swagger UI | http://127.0.0.1:8000/api/docs/ |
| Django Admin | http://127.0.0.1:8000/admin/ |
| pgAdmin | http://localhost:5050 |
| MinIO Console | http://localhost:9001 |
