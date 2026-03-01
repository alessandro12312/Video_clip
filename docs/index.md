# Video_clip — Indice Documentazione

> Generato automaticamente il 2026-02-28 | Workflow: document-project v1.2.0

---

## Panoramica Progetto

- **Tipo:** Monorepo con 2 parti attive (backend + frontend)
- **Linguaggio principale:** Python (backend) + TypeScript (frontend)
- **Architettura:** API-centric monolith + SPA con SSR
- **Database:** PostgreSQL 16 (Docker)
- **Storage:** MinIO S3-compatible (Docker)
- **Autenticazione:** JWT stateless (SimpleJWT + axios interceptors)

---

## Riferimento Rapido

### Backend (cs_clips)

- **Stack:** Django 5.1.6 + DRF 3.15.1 + PostgreSQL 16 + MinIO
- **Entry point:** `backend/manage.py` → `project_clip.wsgi`
- **Pattern:** ViewSet-based REST con DefaultRouter, modulare per dominio
- **API Base:** `http://127.0.0.1:8000/api/`
- **Swagger:** `http://127.0.0.1:8000/api/docs/`
- **Endpoint:** 35 in 5 domini (users, videos, comments, ratings, contests)
- **Modelli:** 5 core + 3 tabelle M2M

### Frontend

- **Stack:** Next.js 16.1.6 + React 19 + TailwindCSS 4 + React Query 5
- **Entry point:** `frontend/src/app/layout.tsx`
- **Pattern:** App Router, route groups (auth)/(main), React Query server state
- **URL:** `http://localhost:3000`
- **Componenti:** 52 (35 custom + 17 shadcn/ui)
- **Hooks:** 21 React Query hooks + 3 utility hooks
- **Tema:** Dark gaming (viola→ciano gradient, glassmorphism)

---

## Documentazione Generata

### Panoramica e Architettura

- [Panoramica Progetto](./project-overview.md) — Cos'è Video_clip, funzionalità, stack, numeri
- [Architettura Backend](./architecture-backend.md) — Pattern API, auth, storage, scheduler, gap
- [Architettura Frontend](./architecture-frontend.md) — App Router, design system, componenti, state
- [Architettura di Integrazione](./integration-architecture.md) — Come backend e frontend comunicano

### Riferimento Tecnico — Backend

- [Contratti API](./api-contracts-backend.md) — 35 endpoint con request/response/permessi/errori
- [Modelli Dati](./data-models-backend.md) — Schema DB, relazioni, vincoli, diagramma ER, admin

### Riferimento Tecnico — Frontend

- [Inventario Componenti](./component-inventory-frontend.md) — 52 componenti categorizzati con props
- [State Management & API Layer](./state-management-frontend.md) — Hooks, API modules, providers, tipi

### Struttura e Sviluppo

- [Analisi Albero Sorgente](./source-tree-analysis.md) — Directory annotata con entry points
- [Guida Sviluppo](./development-guide.md) — Setup, comandi, convenzioni, testing, deploy

---

## Documentazione Esistente

- [README.md](../README.md) — Setup rapido monorepo
- [backend/CLAUDE.md](../backend/CLAUDE.md) — Istruzioni agente AI per backend
- [project-context.md](../_bmad-output/project-context.md) — Contesto AI (118 regole)

---

## Per Iniziare

### Sviluppo Completo (Backend + Frontend)

1. `docker compose up -d` — Avvia PostgreSQL + pgAdmin + MinIO
2. `cd backend && python -m venv .venv && .venv\Scripts\Activate.ps1`
3. `pip install -r requirements.txt && python manage.py migrate`
4. `python manage.py runserver` — Backend su http://127.0.0.1:8000
5. In un altro terminale: `cd frontend && npm install && npm run dev` — Frontend su http://localhost:3000

### Solo Backend

1. `docker compose up -d` — Avvia infrastruttura
2. `cd backend && .venv\Scripts\Activate.ps1 && python manage.py runserver`
3. Visita http://127.0.0.1:8000/api/docs/ — Swagger UI

### Solo Frontend

1. `cd frontend && npm run dev`
2. Visita http://localhost:3000
3. **Nota**: Richiede backend attivo per le API

---

## Sviluppo AI-Assistito

Questa documentazione è ottimizzata per workflow AI:

- **Per un brownfield PRD:** Punta il workflow PRD a questo `index.md`
- **Per feature backend:** Referenzia `api-contracts-backend.md` + `data-models-backend.md` + `architecture-backend.md`
- **Per feature frontend:** Referenzia `component-inventory-frontend.md` + `state-management-frontend.md` + `architecture-frontend.md`
- **Per feature full-stack:** Referenzia `integration-architecture.md` + architettura di entrambe le parti
- **Per contesto agente:** Referenzia `project-context.md` in `_bmad-output/`
