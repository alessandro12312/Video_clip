# Video_clip — Indice Documentazione

> Generato automaticamente il 2026-02-14 | Workflow: document-project v1.2.0

---

## Panoramica Progetto

- **Tipo:** Monorepo (backend attivo, frontend da sviluppare)
- **Linguaggio principale:** Python 3.x
- **Architettura:** API-centric monolith (Django REST Framework)
- **Database:** PostgreSQL 16 (Docker)
- **Autenticazione:** JWT stateless (SimpleJWT)

---

## Riferimento Rapido

### Backend (cs_clips)

- **Stack:** Django 5.1.6 + DRF 3.15.1 + PostgreSQL 16
- **Entry point:** `backend/manage.py` → `project_clip.wsgi`
- **Pattern:** ViewSet-based REST con DefaultRouter
- **API Base:** `http://127.0.0.1:8000/api/`
- **Swagger:** `http://127.0.0.1:8000/api/docs/`

### Frontend

- **Stato:** Da sviluppare (directory `frontend/` vuota)
- **Vincoli:** API REST pronta, necessario CORS per collegamento

---

## Documentazione Generata

- [Panoramica Progetto](./project-overview.md) — Cos'è Video_clip, funzionalità, stack
- [Architettura](./architecture.md) — Pattern architetturale, diagrammi, gap e limitazioni
- [Contratti API](./api-contracts.md) — Tutti gli endpoint con request/response/permessi
- [Modelli Dati](./data-models.md) — Schema database, relazioni, vincoli, diagramma ER
- [Analisi Albero Sorgente](./source-tree-analysis.md) — Struttura directory annotata con entry points
- [Guida Sviluppo](./development-guide.md) — Setup, comandi, convenzioni, testing, deploy

---

## Documentazione Esistente

- [README.md](../README.md) — Setup rapido del progetto (IT)
- [project-context.md](../_bmad-output/project-context.md) — Contesto AI per sviluppo (87 regole)

---

## Per Iniziare

### Sviluppo Backend

1. `docker compose up -d` — Avvia PostgreSQL + pgAdmin
2. `cd backend && .venv\Scripts\Activate.ps1` — Attiva ambiente
3. `pip install -r requirements.txt` — Installa dipendenze
4. `python manage.py migrate` — Applica migrazioni
5. `python manage.py runserver` — Avvia server
6. Visita http://127.0.0.1:8000/api/docs/ — Esplora API

### Pianificazione Frontend

1. Leggi [api-contracts.md](./api-contracts.md) per capire tutti gli endpoint disponibili
2. Leggi [data-models.md](./data-models.md) per capire la struttura dati
3. Leggi la sezione "Note per lo Sviluppo Frontend" in entrambi i documenti
4. Consulta [architecture.md](./architecture.md) per i gap da colmare (CORS, async tasks)

---

## Sviluppo AI-Assistito

Questa documentazione è ottimizzata per essere usata come input per workflow AI:

- **Per un brownfield PRD:** Punta il workflow PRD a questo `index.md`
- **Per feature UI:** Referenzia `api-contracts.md` + `data-models.md`
- **Per feature API:** Referenzia `architecture.md` + `api-contracts.md`
- **Per contesto agente:** Referenzia `project-context.md` in `_bmad-output/`
