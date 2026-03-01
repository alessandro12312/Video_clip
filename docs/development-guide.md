# Guida Sviluppo — Video_clip

> Generato automaticamente il 2026-02-28 | Deep Scan | Workflow: document-project v1.2.0

---

## Prerequisiti

| Strumento | Versione | Scopo |
|---|---|---|
| **Python** | 3.x | Backend Django |
| **Node.js** | 18+ | Frontend Next.js |
| **Docker** + **Docker Compose** | latest | PostgreSQL, pgAdmin, MinIO |
| **Git** | latest | Version control |

---

## Setup Iniziale

### 1. Clona il repository

```bash
git clone <repo-url> Video_clip
cd Video_clip
```

### 2. Configura variabili ambiente

```bash
cp .env.example .env
# Modifica .env con i tuoi valori (DB, MinIO, pgAdmin)
```

### 3. Avvia infrastruttura Docker

```bash
docker compose up -d
# Avvia: PostgreSQL (5432), pgAdmin (5050), MinIO (9000/9001)
# minio-init crea automaticamente bucket e policy
```

### 4. Setup Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # (opzionale)
python manage.py runserver
```

Backend disponibile su `http://127.0.0.1:8000/`

### 5. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend disponibile su `http://localhost:3000/`

---

## Comandi Principali

### Backend

| Comando | Scopo |
|---|---|
| `python manage.py runserver` | Avvia server sviluppo |
| `python manage.py migrate` | Applica migrazioni |
| `python manage.py makemigrations` | Genera migrazioni |
| `python manage.py createsuperuser` | Crea utente admin |
| `python manage.py close_contests` | Chiudi contest scaduti (manuale) |
| `python manage.py spectacular --file schema.yaml` | Genera schema OpenAPI |

### Frontend

| Comando | Scopo |
|---|---|
| `npm run dev` | Avvia server sviluppo (port 3000) |
| `npm run build` | Build produzione |
| `npm run start` | Avvia build produzione |
| `npm run lint` | Esegui ESLint |

### Infrastruttura

| Comando | Scopo |
|---|---|
| `docker compose up -d` | Avvia tutti i servizi |
| `docker compose down` | Ferma tutti i servizi |
| `docker compose logs -f db` | Log PostgreSQL |
| `docker compose logs -f minio` | Log MinIO |

---

## URL Sviluppo

| Servizio | URL |
|---|---|
| **Frontend** | http://localhost:3000 |
| **Backend API** | http://127.0.0.1:8000/api/ |
| **Swagger UI** | http://127.0.0.1:8000/api/docs/ |
| **ReDoc** | http://127.0.0.1:8000/api/redoc/ |
| **Django Admin** | http://127.0.0.1:8000/admin/ |
| **pgAdmin** | http://localhost:5050 |
| **MinIO Console** | http://localhost:9001 |

---

## Convenzioni Codice

### Backend (Python/Django)

- **Struttura modulare**: `cs_clips/api/{dominio}/` con `{dominio}_views.py`, `{dominio}_serializers.py`, `{dominio}_urls.py`
- **Modelli**: 1 file per modello in `cs_clips/models/`, export via `__init__.py`
- **ViewSet**: ModelViewSet per CRUD, `@action` per operazioni custom
- **Permessi**: `RoleBasedPermission` default, override con `get_permissions()`
- **Errori**: gestione centralizzata in `cs_clips/exceptions/`
- **Naming**: snake_case per tutto (file, funzioni, variabili)

### Frontend (TypeScript/React)

- **App Router**: route groups `(auth)` e `(main)` per layout diversi
- **Componenti**: organizzati per dominio in `src/components/{dominio}/`
- **Hooks**: React Query per ogni operazione dati in `src/lib/hooks/`
- **API**: moduli separati in `src/lib/api/{dominio}.ts`
- **Tipi**: definizioni TypeScript in `src/types/`
- **Stile**: TailwindCSS v4, utility `cn()` per merge classi
- **UI**: shadcn/ui (New York) + Radix UI per primitivi
- **Naming**: kebab-case per file, PascalCase per componenti

---

## Testing

### Backend

Nessun test automatizzato presente. Struttura consigliata:
```
backend/cs_clips/tests/
├── __init__.py
├── test_models.py
├── test_views.py
└── test_video_upload.py
```

### Frontend

Nessun framework di test configurato. Consigliato: Vitest + React Testing Library.

### Test Manuali

1. **API**: Swagger UI (`/api/docs/`) per testare endpoint
2. **Auth flow**: Registra → Login → Verifica token → Refresh
3. **Upload**: Carica video → Verifica MinIO → Verifica durata estratta
4. **Contest**: Crea video con tag → Chiudi contest → Verifica vincitore

---

## Deploy

### Prerequisiti Produzione

1. **CORS**: configurare `CORS_ALLOWED_ORIGINS` (non `ALLOW_ALL`)
2. **SECRET_KEY**: generare chiave sicura
3. **DEBUG**: impostare `False`
4. **HTTPS**: SSL per MinIO presigned URL
5. **Celery**: configurare per task asincroni

### Docker Compose (attuale — solo sviluppo)

Non include servizi backend/frontend containerizzati, Nginx, SSL, backup.

---

## Variabili Ambiente

### Root `.env` (compose.yml)

| Variabile | Scopo |
|---|---|
| `POSTGRES_USER/PASSWORD/DB/PORT` | Configurazione PostgreSQL |
| `PGADMIN_EMAIL/PASSWORD/PORT` | Configurazione pgAdmin |
| `MINIO_ROOT_USER/PASSWORD` | Configurazione MinIO |
| `MINIO_API_PORT/CONSOLE_PORT` | Porte MinIO |

### Backend

| Variabile | Scopo |
|---|---|
| `DJANGO_DEBUG` | Debug mode |
| `SECRET_KEY` | Django secret key |
| `DATABASE_URL` | URL PostgreSQL |

### Frontend

| Variabile | Scopo |
|---|---|
| `NEXT_PUBLIC_API_URL` | URL backend (default `http://127.0.0.1:8000`) |

---

## CI/CD

Nessun pipeline configurato. Consigliato:
1. **Lint**: ESLint (frontend) + ruff (backend)
2. **Test**: pytest (backend) + vitest (frontend)
3. **Build**: `next build` + Docker image
4. **Deploy**: Docker Compose produzione o Kubernetes
