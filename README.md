# Video Clip - Monorepo

Piattaforma per condivisione e contest di video clip gaming.

**Stack:** Django 5.1.6 (REST API) + Next.js 16 (React 19) + PostgreSQL 16 (Docker)

---

## Avvio Rapido

> Prerequisiti: [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) avviato, [Node.js](https://nodejs.org/) >= 18, Python venv configurato

Dalla root del progetto:

```bash
npm install        # solo la prima volta
npm run dev        # avvia tutto e apre il browser
```

Questo comando:
1. Avvia i container Docker (PostgreSQL + pgAdmin)
2. Attende che il database sia pronto
3. Lancia il backend Django (`localhost:8000`) e il frontend Next.js (`localhost:3000`) in parallelo
4. Apre automaticamente Swagger (`/api/docs/`) e la pagina di login nel browser

**Stop:** `Ctrl+C` nel terminale, poi `npm run docker:down` per fermare i container.

### Script disponibili

| Comando | Descrizione |
|---------|-------------|
| `npm run dev` | Avvio completo (Docker + backend + frontend + browser) |
| `npm run docker:up` | Avvia solo i container Docker |
| `npm run docker:down` | Ferma i container Docker |
| `npm run backend` | Avvia solo il backend Django |
| `npm run frontend` | Avvia solo il frontend Next.js |

---

## Setup Iniziale

### 1. Database (Docker)

Installare [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/), poi:

```bash
docker compose up -d
```

### 2. Backend (Django)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows CMD
# oppure: .venv/Scripts/Activate.ps1   # PowerShell

pip install -r backend/requirements.txt
cd backend
python manage.py migrate
```

NB: Se non riesci con i comandi da console e stai utilizzando VSCode:
https://code.visualstudio.com/docs/python/environments

### 3. Frontend (Next.js)

```bash
cd frontend
npm install
```

### 4. Variabili d'ambiente

Creare un file `.env` nella root del progetto con le variabili necessarie per PostgreSQL, pgAdmin e Django.

---

## Struttura Progetto

```
Video_clip/
├── .env                  # Variabili d'ambiente (gitignored)
├── compose.yml           # Docker: PostgreSQL + pgAdmin
├── package.json          # Script orchestrazione monorepo
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── cs_clips/         # App Django principale
│   └── project_clip/     # Settings Django
├── frontend/
│   ├── package.json
│   └── src/              # App Next.js
└── db/                   # Volume PostgreSQL (gitignored)
```

## Link Utili

- **Swagger API docs:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **Frontend:** http://localhost:3000
