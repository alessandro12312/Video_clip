# Video Clip - Monorepo

Struttura del progetto:
- `backend/` - API Django REST Framework
- `frontend/` - Frontend (da sviluppare)

---

## Backend (Django)

### Setup ambiente Python

- Installare python https://www.python.org/downloads/windows/

- Creare l'ambiente virtuale nella cartella backend:
  ```
  cd backend
  python -m venv .venv
  ```

- Attivare l'ambiente venv python:
  - PowerShell: `.venv\Scripts\Activate.ps1`
  - CMD: `.venv\Scripts\activate`

NB: Se non riesci con i comandi da console e stai utilizzando VSCODE:
  https://code.visualstudio.com/docs/python/environments

- Installare i requirements da console:
  ```
  pip install -r requirements.txt
  ```

- Compila:
  ```
  python manage.py makemigrations
  python manage.py migrate
  ```

### Database (Docker)

- Installare docker: https://docs.docker.com/desktop/setup/install/windows-install/

- Lanciare il docker compose (dalla root del progetto):
  ```
  cd ..
  docker compose up -d
  ```

### Run server

```
cd backend
python manage.py runserver
```

### Swagger

http://127.0.0.1:8000/api/docs/
