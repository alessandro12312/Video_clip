# Guida allo Sviluppo - Video_clip

> Generato automaticamente il 2026-02-14 | Scan level: deep

## Prerequisiti

| Requisito | Versione | Note |
|-----------|----------|------|
| Python | 3.x (consigliato 3.12+) | Linguaggio backend |
| Docker | Latest | Per PostgreSQL e pgAdmin |
| Docker Compose | Incluso in Docker Desktop | Orchestrazione servizi |
| FFmpeg | Via imageio-ffmpeg | Installato automaticamente con requirements |
| Git | Latest | Controllo versione |

---

## Setup Iniziale

### 1. Clona il repository

```bash
git clone <repository-url>
cd Video_clip
```

### 2. Avvia i servizi Docker

```bash
docker compose up -d
```

Questo avvia:
- **PostgreSQL 16** sulla porta 5432 (container: `postgres_db`)
- **pgAdmin 4** sulla porta 8080 (container: `pgadmin`)

Credenziali (da `.env`):
- DB: `root` / `stickStick` / database: `cs_clips`
- pgAdmin: `stick@stick.stick` / `stickStick`

### 3. Setup ambiente Python

```bash
cd backend
python -m venv .venv
```

Attivazione:
- **PowerShell:** `.venv\Scripts\Activate.ps1`
- **CMD:** `.venv\Scripts\activate`
- **Bash/WSL:** `source .venv/Scripts/activate`

### 4. Installa dipendenze

```bash
pip install -r requirements.txt
```

### 5. Applica migrazioni database

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crea superuser (opzionale)

```bash
python manage.py createsuperuser
```

### 7. Avvia il server

```bash
python manage.py runserver
```

Server disponibile su: `http://127.0.0.1:8000/`

---

## Comandi Utili

### Sviluppo quotidiano

```bash
# Avvia servizi DB
docker compose up -d

# Attiva venv e avvia server
cd backend
.venv\Scripts\Activate.ps1
python manage.py runserver
```

### Database

```bash
# Crea nuove migrazioni dopo modifiche ai modelli
python manage.py makemigrations

# Applica migrazioni
python manage.py migrate

# Mostra migrazioni applicate
python manage.py showmigrations

# Accedi alla shell Django
python manage.py shell

# Accedi alla shell del database
python manage.py dbshell
```

### Docker

```bash
# Avvia servizi in background
docker compose up -d

# Ferma servizi
docker compose down

# Visualizza log
docker compose logs -f

# Reset database (ATTENZIONE: cancella tutti i dati)
docker compose down -v
```

### API Documentation

```bash
# Genera schema OpenAPI statico
python manage.py spectacular --file schema.yml
```

- **Swagger UI:** http://127.0.0.1:8000/api/docs/
- **ReDoc:** http://127.0.0.1:8000/api/redoc/
- **Schema raw:** http://127.0.0.1:8000/api/schema/
- **Django Admin:** http://127.0.0.1:8000/admin/

---

## Testing

### Stato attuale

- **Nessuna suite di test automatizzata configurata**
- Esiste un management command manuale: `test_spareggio.py` per testare l'algoritmo di spareggio
- Il framework di test è Django TestCase (built-in)

### Come eseguire i test (quando disponibili)

```bash
python manage.py test
```

### Struttura test consigliata

```
backend/cs_clips/
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_serializers.py
│   └── test_permissions.py
```

---

## Convenzioni di Codice

### Naming

| Elemento | Convenzione | Esempio |
|----------|-------------|---------|
| File Python | snake_case | `serializers.py` |
| Classi | PascalCase | `VideoViewSet` |
| Funzioni | snake_case | `get_or_create_current_contest` |
| URL paths | kebab-case | `top-rated`, `contest-winners` |
| Variabili | snake_case | `average_rating` |

### Lingue

- **Codice** (classi, variabili, path): Inglese
- **Commenti e docstring**: Italiano
- **Messaggi utente e help_text**: Italiano

### Pattern importanti

```python
# Import User model — SEMPRE così
from django.contrib.auth import get_user_model
User = get_user_model()

# MAI così
from django.contrib.auth.models import User  # ❌
```

### Gestione errori

Tutti i ViewSet usano il pattern centralizzato:
```python
def handle_exception(self, exc):
    return handle_exception_with_serializer(exc)
```

Formato risposta errore:
```json
{
  "code": "ValidationError",
  "detail": "Descrizione dell'errore"
}
```

---

## Configurazione Ambiente

### File .env (root del progetto)

```env
# PostgreSQL
POSTGRES_CONTAINER_NAME=postgres_db
POSTGRES_USER=root
POSTGRES_PASSWORD=stickStick
POSTGRES_DB=cs_clips
POSTGRES_PORT=5432

# pgAdmin
PGADMIN_CONTAINER_NAME=pgadmin
PGADMIN_EMAIL=stick@stick.stick
PGADMIN_PASSWORD=stickStick
PGADMIN_PORT=8080
```

### Django Settings chiave

| Setting | Valore | Note |
|---------|--------|------|
| DEBUG | True (default) | Cambiare in produzione |
| SECRET_KEY | Fallback hardcoded | Impostare via env in produzione |
| DATABASE HOST | 127.0.0.1 | Django fuori Docker, DB in Docker |
| PAGE_SIZE | 10 | Paginazione globale |
| ACCESS_TOKEN_LIFETIME | 12 ore | JWT |
| REFRESH_TOKEN_LIFETIME | 1 giorno | JWT |
| MEDIA_ROOT | backend/media | File upload |

---

## Deploy

### Stato attuale

- **Nessuna configurazione di produzione**
- Nessun Dockerfile per il backend
- Nessun CI/CD configurato
- Nessun processo di deploy documentato

### Requisiti minimi per produzione

1. Impostare `DEBUG=False`
2. Configurare `SECRET_KEY` sicura via variabile d'ambiente
3. Aggiungere `django-cors-headers` per il frontend
4. Configurare un web server (Gunicorn/uWSGI + Nginx)
5. Containerizzare il backend (Dockerfile)
6. Configurare storage media (cloud o volume dedicato)
7. Configurare HTTPS
