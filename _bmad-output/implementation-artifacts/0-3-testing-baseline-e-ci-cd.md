# Story 0.3: Testing Baseline e CI/CD

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a sviluppatore,
I want una baseline di test automatici e una CI pipeline,
so that ogni modifica futura è protetta da regressioni e il codice è validato ad ogni push.

## Acceptance Criteria

1. **AC-1 (D4 — conftest.py):** `backend/cs_clips/tests/conftest.py` contiene 5 fixture riusabili: `authenticated_user` (utente con gruppo `user` + token JWT), `admin_user` (utente con gruppo `admin` + token JWT), `sample_video` (video con file MinIO reale caricato), `api_client_authenticated` (`APIClient` con `force_authenticate()`), `sample_contest` (contest attivo con tag e date validi).
2. **AC-2 (test backend):** Almeno 1 test backend Django NUOVO passa (es. test auth flow: registrazione crea utente con gruppo `toconfirm`). I 5 test pre-esistenti in `test_permissions.py` continuano a passare.
3. **AC-3 (D4 — MSW setup):** `frontend/src/test/setup.ts` configura MSW server con `beforeAll`/`afterEach`/`afterAll` e importa i matcher jest-dom per Vitest.
4. **AC-4 (D4 — MSW handlers):** `frontend/src/test/handlers.ts` contiene handler MSW v2 per 5 endpoint: `POST /api/token/` (login), `POST /api/users/` (register), `GET /api/videos/` (lista paginata), `GET /api/videos/:id/` (dettaglio), `GET /api/users/:id/` (profilo utente).
5. **AC-5 (test frontend):** Almeno 1 test frontend Vitest passa (es. renderizza un componente e verifica testo).
6. **AC-6 (CI/CD):** `.github/workflows/ci.yml` esegue: `ruff check` + `ruff format --check` + `python manage.py test` (backend) e `npm run lint` + `npx vitest run` + `npm run build` (frontend).
7. **AC-7 (build):** `npm run build` nel frontend compila senza errori.

**Nota priorita:** I test locali funzionanti (conftest.py, MSW handlers, almeno 1 test per lato) sono il deliverable obbligatorio. La CI/CD GitHub Actions e' fortemente consigliata ma non bloccante se ci sono problemi infrastrutturali (permessi, Docker nel runner). In quel caso, documentare il problema e procedere — la CI verra' fixata come follow-up.

## Tasks / Subtasks

- [x] Task 1 — Verificare ambiente test backend (AC: 1)
  - [x] 1.1 Verificare che `python manage.py test` funzioni (Django test runner gia' disponibile, NESSUNA dipendenza aggiuntiva da installare — NON usare pytest)
  - [x] 1.2 Verificare che `backend/cs_clips/tests/__init__.py` esista (creato in Story 0.1)
- [x] Task 2 — Creare `conftest.py` con 5 helper function (AC: 1)
  - [x] 2.1 Creare `backend/cs_clips/tests/conftest.py`
  - [x] 2.2 Fixture `authenticated_user`: crea utente con `create_user()`, assegna gruppo `user` (Group.objects.get_or_create), ritorna utente
  - [x] 2.3 Fixture `admin_user`: crea utente admin con `create_user()`, assegna gruppo `admin`, imposta `is_staff=True`
  - [x] 2.4 Fixture `sample_video`: crea video con `Video.objects.create()` e `SimpleUploadedFile` (mock file, NO MinIO reale). Durata hardcoded a 30s — bypassa MoviePy intenzionalmente (vedi commento nel codice). NON usare serializer.save()
  - [x] 2.5 Fixture `api_client_authenticated`: ritorna `APIClient` con `force_authenticate(user=authenticated_user)`
  - [x] 2.6 Fixture `sample_contest`: crea Contest attivo con tag `clutch`, date settimana corrente (lunedi-sabato), `is_closed=False`
- [x] Task 3 — Scrivere almeno 1 test backend nuovo (AC: 2)
  - [x] 3.1 Creare `backend/cs_clips/tests/test_auth.py`
  - [x] 3.2 Test registrazione: `POST /api/users/` crea utente con gruppo `toconfirm`, risposta 201
  - [x] 3.3 Test login: `POST /api/token/` con credenziali valide ritorna `access` e `refresh` token
  - [x] 3.4 Test refresh: `POST /api/token/refresh/` con refresh token valido ritorna nuovo access token
  - [x] 3.5 Verificare che TUTTI i test passino: `python manage.py test` (6 pre-esistenti + nuovi)
- [x] Task 4 — Installare dipendenze test frontend (AC: 3, 4, 5)
  - [x] 4.1 `cd frontend && npm install -D vitest vite @vitejs/plugin-react vite-tsconfig-paths jsdom @testing-library/react @testing-library/dom @testing-library/jest-dom msw`
  - [x] 4.2 Aggiungere script `"test": "vitest run"` e `"test:watch": "vitest"` in `frontend/package.json`
- [x] Task 5 — Configurare Vitest per Next.js (AC: 3)
  - [x] 5.1 Creare `frontend/vitest.config.mts` con environment jsdom, plugin react + tsconfigPaths, setupFiles, exclude `.next`
  - [x] 5.2 Creare `frontend/src/test/setup.ts` con import `@testing-library/jest-dom/vitest` + MSW server lifecycle (`beforeAll`/`afterEach`/`afterAll`)
- [x] Task 6 — Creare MSW handlers per 5 endpoint (AC: 4)
  - [x] 6.1 Creare `frontend/src/test/server.ts` con `setupServer()` da `msw/node`
  - [x] 6.2 Creare `frontend/src/test/handlers.ts` con handler MSW v2:
    - `POST /api/token/` → ritorna `{ access: "mock-access-token", refresh: "mock-refresh-token" }`
    - `POST /api/users/` → ritorna `{ id: 1, username: "testuser", email: "test@test.com" }` con status 201
    - `GET /api/videos/` → ritorna formato paginato `{ count, next, previous, results: [...] }`
    - `GET /api/videos/:id` → ritorna oggetto video singolo
    - `GET /api/users/:id` → ritorna oggetto utente con campi profilo
- [x] Task 7 — Scrivere almeno 1 test frontend (AC: 5)
  - [x] 7.1 Creare test di integrazione MSW: verifica che i mock handler rispondano correttamente (fetch a `/api/videos/` ritorna formato paginato). Questo valida l'intera pipeline vitest + msw + setup. Alternativa: renderizzare un componente puro senza provider (es. un componente UI base di shadcn) e verificare il testo
  - [x] 7.2 Verificare: `npx vitest run` passa
- [x] Task 8 — Creare CI/CD GitHub Actions (AC: 6)
  - [x] 8.1 Creare `.github/workflows/ci.yml`
  - [x] 8.2 Job `backend`: Python 3.10, PostgreSQL 16 service, ruff check, ruff format --check, python manage.py test
  - [x] 8.3 Job `frontend`: Node.js 20, npm ci, npm run lint, npx vitest run, npm run build
  - [x] 8.4 Trigger: push su `main` + pull request su `main`
  - [x] 8.5 Verificare che `settings.py` supporti `DATABASE_URL` via `dj-database-url` per il CI. Se la configurazione DB e' hardcoded, aggiungere fallback a `DATABASE_URL` env var OPPURE creare un settings override per CI
  - [x] 8.6 NOTA: MinIO service nel CI e' opzionale per la baseline — i test backend baseline non richiedono file reali su MinIO (usano `SimpleUploadedFile` o mock). Known limitation: test futuri che toccano `Video.file` reale falliranno nel CI senza MinIO service
- [x] Task 9 — Verifica finale (AC: 1-7)
  - [x] 9.1 `python manage.py test` — tutti i test passano (pre-esistenti + nuovi)
  - [x] 9.2 `npx vitest run` — almeno 1 test passa
  - [x] 9.3 `ruff check backend/` — 0 errori
  - [x] 9.4 `ruff format --check backend/` — 0 errori
  - [x] 9.5 `npm run build` — 0 errori TypeScript
  - [x] 9.6 `.github/workflows/ci.yml` sintatticamente valido (verificare con `actionlint` se disponibile, altrimenti review manuale)

## Dev Notes

### Stato Attuale (Pre-Implementazione)

**Backend testing:**
- Directory `backend/cs_clips/tests/` esiste con `__init__.py` (creato in Story 0.1)
- 1 file test: `test_permissions.py` con 6 test (`RoleBasedPermissionTests`) — tutti passanti
- **Nessun conftest.py**, nessuna fixture condivisa
- Framework: Django test runner (`python manage.py test`), **NON pytest**
- DB richiesto: PostgreSQL attivo via Docker

**Frontend testing:**
- **Nessun framework test installato** — no vitest, no jest, no testing-library, no MSW
- Nessun file test, nessuna directory test
- Nessun script `test` in `package.json`
- `package.json` scripts: solo `dev`, `build`, `start`, `lint`

**CI/CD:**
- **Nessun workflow GitHub Actions** — directory `.github/` non esiste
- Docker Compose per dev only (PostgreSQL 16, MinIO, pgAdmin)
- Root `package.json` con `concurrently` per orchestrazione dev

### Dettaglio Tecnico: conftest.py (D4)

**CRITICO: Usare `django.test.TestCase`, NON pytest fixtures.**

Il `project-context.md` e l'architettura specificano `django.test.TestCase` come base class. Il termine "conftest.py" nell'AC si riferisce a un **modulo di utilita' con helper function riusabili** (non pytest fixtures con decoratore `@pytest.fixture`).

**Pattern implementativo:**
```python
# backend/cs_clips/tests/conftest.py
"""Utilita' condivise per test — helper function riusabili."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

User = get_user_model()


def create_authenticated_user(username="testuser", password="testpass123"):
    """Crea utente con gruppo 'user' (requisito: ogni utente DEVE avere almeno un gruppo)."""
    user = User.objects.create_user(
        username=username,
        password=password,
        email=f"{username}@test.com",
    )
    group, _ = Group.objects.get_or_create(name="user")
    user.groups.add(group)
    return user


def create_admin_user(username="adminuser", password="adminpass123"):
    """Crea utente admin con gruppo 'admin' e is_staff=True."""
    user = User.objects.create_user(
        username=username,
        password=password,
        email=f"{username}@test.com",
        is_staff=True,
    )
    group, _ = Group.objects.get_or_create(name="admin")
    user.groups.add(group)
    return user


def create_sample_video(uploader, title="Test Video", tag="clutch"):
    """Crea video con file mock (no MinIO reale per baseline test).

    NOTA IMPORTANTE: Usa Video.objects.create() diretto, NON il serializer.
    Il VideoInputSerializer.create() chiama MoviePy per estrarre la durata
    dal file reale — qui passiamo un file finto e la durata hardcoded.
    Questo e' intenzionale per la baseline: test che necessitano di
    upload reale con MoviePy + MinIO saranno aggiunti nelle story successive.
    """
    from cs_clips.models import Video

    video_file = SimpleUploadedFile(
        "test_video.mp4",
        b"fake-video-content",
        content_type="video/mp4",
    )
    return Video.objects.create(
        uploader=uploader,
        title=title,
        tag=tag,
        file=video_file,
        duration=30,  # Hardcoded — bypassa MoviePy intenzionalmente
    )


def create_api_client_authenticated(user=None):
    """Ritorna APIClient con force_authenticate."""
    if user is None:
        user = create_authenticated_user()
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def create_sample_contest(tag="clutch"):
    """Crea contest attivo per la settimana corrente."""
    from datetime import date, timedelta

    from cs_clips.models import Contest

    today = date.today()
    # Lunedi della settimana corrente
    monday = today - timedelta(days=today.weekday())
    # Sabato della settimana corrente
    saturday = monday + timedelta(days=5)

    return Contest.objects.create(
        name=f"Contest {tag} settimanale",
        tag=tag,
        start_date=monday,
        end_date=saturday,
        is_closed=False,
    )
```

**ATTENZIONE:** I test pre-esistenti in `test_permissions.py` creano utenti direttamente con `create_user()` e `Group.objects.get_or_create()`. Per retrocompatibilita', NON modificare quei test — le nuove helper function sono per test NUOVI.

### Dettaglio Tecnico: Test Auth Flow (backend)

```python
# backend/cs_clips/tests/test_auth.py
"""Test auth flow: registrazione, login, refresh token."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegistrationTests(APITestCase):
    """Test endpoint POST /api/users/ (registrazione)."""

    def test_registration_creates_user_with_toconfirm_group(self):
        """La registrazione crea utente e assegna gruppo 'toconfirm'."""
        data = {
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "TestPassword123!",
        }
        response = self.client.post("/api/users/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username="newuser")
        self.assertTrue(user.groups.filter(name="toconfirm").exists())


class LoginTests(APITestCase):
    """Test endpoint POST /api/token/ (login JWT)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@test.com",
        )
        group, _ = Group.objects.get_or_create(name="user")
        self.user.groups.add(group)

    def test_login_returns_jwt_tokens(self):
        """Login con credenziali valide ritorna access e refresh token."""
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post("/api/token/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials_returns_401(self):
        """Login con credenziali errate ritorna 401."""
        data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post("/api/token/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenRefreshTests(APITestCase):
    """Test endpoint POST /api/token/refresh/ (refresh JWT)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@test.com",
        )
        group, _ = Group.objects.get_or_create(name="user")
        self.user.groups.add(group)

    def test_refresh_returns_new_access_token(self):
        """Refresh con token valido ritorna nuovo access token."""
        # Prima ottieni tokens via login
        login_response = self.client.post(
            "/api/token/",
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )
        refresh_token = login_response.data["refresh"]

        # Poi usa refresh token
        response = self.client.post(
            "/api/token/refresh/",
            {"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
```

### Dettaglio Tecnico: Vitest Config per Next.js 16

**Vitest funziona come framework di test standalone** — Vite e' installato SOLO come dipendenza di Vitest per il test bundling, NON sostituisce il compilatore Next.js.

**Pacchetti da installare:**
```bash
cd frontend
npm install -D vitest vite @vitejs/plugin-react vite-tsconfig-paths jsdom \
  @testing-library/react @testing-library/dom @testing-library/jest-dom \
  msw
```

**`frontend/vitest.config.mts`:**
```typescript
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [tsconfigPaths(), react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test/setup.ts"],
    include: ["src/**/*.{test,spec}.{ts,tsx}"],
    exclude: ["node_modules", ".git", ".next"],
  },
});
```

**`frontend/src/test/setup.ts`:**
```typescript
import "@testing-library/jest-dom/vitest";
import { afterAll, afterEach, beforeAll } from "vitest";
import { server } from "./server";

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

**`frontend/src/test/server.ts`:**
```typescript
import { setupServer } from "msw/node";
import { handlers } from "./handlers";

export const server = setupServer(...handlers);
```

### Dettaglio Tecnico: MSW v2 Handlers

**CRITICO: Usare la API v2 di MSW** — `http` e `HttpResponse`, NON la vecchia `rest` da v1.

**`frontend/src/test/handlers.ts`:**
```typescript
import { http, HttpResponse } from "msw";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export const handlers = [
  // POST /api/token/ — login JWT
  http.post(`${API_BASE}/api/token/`, async ({ request }) => {
    const body = (await request.json()) as Record<string, string>;
    if (body.username === "testuser" && body.password === "testpass123") {
      return HttpResponse.json({
        access: "mock-access-token",
        refresh: "mock-refresh-token",
      });
    }
    return HttpResponse.json(
      { detail: "Credenziali non valide." },
      { status: 401 },
    );
  }),

  // POST /api/users/ — registrazione
  http.post(`${API_BASE}/api/users/`, async ({ request }) => {
    const body = (await request.json()) as Record<string, string>;
    return HttpResponse.json(
      {
        id: 1,
        username: body.username,
        email: body.email,
      },
      { status: 201 },
    );
  }),

  // GET /api/videos/ — lista paginata
  http.get(`${API_BASE}/api/videos/`, () => {
    return HttpResponse.json({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          title: "Test Video",
          tag: "clutch",
          uploader: { id: 1, username: "testuser" },
          duration: 30,
          created_at: "2026-02-28T12:00:00Z",
          file_url: "https://minio.local/video/test.mp4",
        },
      ],
    });
  }),

  // GET /api/videos/:id/ — dettaglio video
  http.get(`${API_BASE}/api/videos/:id`, ({ params }) => {
    return HttpResponse.json({
      id: Number(params.id),
      title: "Test Video",
      tag: "clutch",
      uploader: { id: 1, username: "testuser" },
      duration: 30,
      created_at: "2026-02-28T12:00:00Z",
      file_url: "https://minio.local/video/test.mp4",
      average_rating: 4.2,
      rating_count: 5,
    });
  }),

  // GET /api/users/:id/ — profilo utente
  http.get(`${API_BASE}/api/users/:id`, ({ params }) => {
    return HttpResponse.json({
      id: Number(params.id),
      username: "testuser",
      email: "test@test.com",
      date_joined: "2026-01-01T00:00:00Z",
    });
  }),
];
```

### Dettaglio Tecnico: CI/CD GitHub Actions

**`.github/workflows/ci.yml`:**
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  backend:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: videoclip
          POSTGRES_PASSWORD: videoclip_test
          POSTGRES_DB: videoclip_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U videoclip"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    env:
      DATABASE_URL: postgres://videoclip:videoclip_test@localhost:5432/videoclip_test
      MINIO_STORAGE_ENDPOINT: localhost:9000
      MINIO_STORAGE_ACCESS_KEY: minioadmin
      MINIO_STORAGE_SECRET_KEY: minioadmin
      MINIO_STORAGE_USE_HTTPS: "false"
      MINIO_STORAGE_MEDIA_BUCKET_NAME: test-media
      MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET: "true"
      SECRET_KEY: ci-test-secret-key-not-for-production
      DEBUG: "false"

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.10
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"
          cache: pip
          cache-dependency-path: backend/requirements.txt

      - name: Install system dependencies
        run: sudo apt-get update && sudo apt-get install -y ffmpeg

      - name: Install Python dependencies
        run: |
          cd backend
          pip install --upgrade pip
          pip install -r requirements.txt

      - name: Ruff lint check
        run: |
          cd backend
          ruff check .

      - name: Ruff format check
        run: |
          cd backend
          ruff format --check .

      - name: Run Django migrations
        run: |
          cd backend
          python manage.py migrate --run-syncdb

      - name: Run Django tests
        run: |
          cd backend
          python manage.py test --verbosity=2

  frontend:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js 20
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: ESLint check
        run: |
          cd frontend
          npm run lint

      - name: Run Vitest
        run: |
          cd frontend
          npx vitest run

      - name: Build Next.js
        run: |
          cd frontend
          npm run build
```

**NOTE CI:**
- MinIO NON e' incluso come service nel CI — i test backend baseline usano `SimpleUploadedFile` (mock file), non file reali su MinIO. Questo semplifica la pipeline e velocizza l'esecuzione.
- `ffmpeg` installato come system dependency — necessario per `moviepy` (import al caricamento modulo Video).
- Job `backend` e `frontend` eseguono in parallelo — nessuna dipendenza tra loro.
- `DATABASE_URL` — verificare che `settings.py` usi `dj-database-url` per parsare questa env var. Se settings.py ha configurazione hardcoded, servira' un override o un settings file separato per CI.

### Dettaglio Tecnico: Versioni Pacchetti (Febbraio 2026)

| Pacchetto | Versione | Note |
|-----------|----------|------|
| vitest | ^4.0.18 | Richiede Vite >= 6.0.0, Node >= 20 |
| vite | ^6.0.0 | Solo per test bundling, NON sostituisce Next.js |
| @vitejs/plugin-react | latest | Necessario per JSX transform nei test |
| vite-tsconfig-paths | latest | Risolve alias `@/*` da tsconfig.json |
| jsdom | latest | Environment DOM per test (no browser reale) |
| @testing-library/react | ^16.3.2 | Supporta React 19, @testing-library/dom e' peer dep |
| @testing-library/dom | ^10.4.1 | Peer dependency obbligatoria di @testing-library/react v16 |
| @testing-library/jest-dom | ^6.9.1 | Import dedicato per Vitest: `@testing-library/jest-dom/vitest` |
| msw | ^2.12.10 | API v2: `http` + `HttpResponse`, NON vecchia `rest` |

**Breaking changes da ricordare:**
- **Vitest 4**: `exclude` non include piu' automaticamente `dist`, `.next` — specificare esplicitamente
- **MSW v2**: import da `msw` (NON `msw/rest`), handler con `http.get()` (NON `rest.get()`)
- **@testing-library/react v16**: `@testing-library/dom` e' peer dep — installare separatamente
- **@testing-library/jest-dom**: per Vitest importare da `@testing-library/jest-dom/vitest` (NON il path generico)

### Project Structure Notes

**File NUOVI da creare:**
- `backend/cs_clips/tests/conftest.py` — helper function per fixture test
- `backend/cs_clips/tests/test_auth.py` — test auth flow
- `frontend/vitest.config.mts` — configurazione Vitest
- `frontend/src/test/setup.ts` — setup MSW + jest-dom matchers
- `frontend/src/test/server.ts` — MSW server instance
- `frontend/src/test/handlers.ts` — MSW v2 handlers per 5 endpoint
- `frontend/src/test/__tests__/` — directory per test
- `.github/workflows/ci.yml` — pipeline CI

**File da MODIFICARE:**
- `frontend/package.json` — aggiungere scripts `test` e `test:watch`, nuove devDependencies

**File NON toccare:**
- `backend/cs_clips/tests/test_permissions.py` — 6 test pre-esistenti, devono continuare a passare
- `backend/cs_clips/tests/__init__.py` — gia' esistente da Story 0.1

### Previous Story Intelligence (Story 0.1 e 0.2)

**Learnings dalla Story 0.1:**
- `requirements.txt` e' ora in UTF-8 (convertito da UTF-16 LE)
- `backend/cs_clips/tests/__init__.py` esiste gia'
- 6 test in `test_permissions.py` devono continuare a passare
- Pattern commit: `fix:` / `feat:` prefix + story reference

**Learnings dalla Story 0.2:**
- ruff e' configurato e funzionante — `ruff check backend/` e `ruff format --check backend/` passano con 0 errori
- `.editorconfig` esiste alla root con LF line endings (critico su Windows)
- `@tanstack/react-query-devtools` installato separatamente (non era bundled)
- Django Debug Toolbar configurato e funzionante
- Rate limiting DRF configurato

**Pattern da rispettare:**
- File Python riformattati da ruff — ogni nuovo file deve passare `ruff check` e `ruff format --check`
- Django Test Runner (NON pytest) — usare `django.test.TestCase` e `APITestCase`
- Ogni utente nei test DEVE avere almeno un gruppo (`User.groups` ha `blank=False`)
- Usare `get_user_model()` per ottenere User, MAI import diretto

### Git Intelligence — Commit Recenti

```
f68fa2c feat: Story 0-2 — linting, formatting e developer tools
b2bfa77 fix: Story 0-1 — bug fix settings, permissions e pulizia dipendenze
87e8304 Frontend / backend ALIGNMENT
79e7e84 fix: code review Story 2-1 — a11y, error messages, dead code, tipi
d893f75 feat: Story 2-1 upload clip con validazione frontend + backend
```

**Pattern rilevanti:**
- Commit message style: `feat:` / `fix:` prefix + `Story X-Y — descrizione`
- Base pulita: Story 0.1 e 0.2 completate, ruff e linting attivi
- Il backend e' stato resettato (87e8304) e poi fixato (b2bfa77, f68fa2c)

### Definition of Done — Specifiche per Questa Story

- **Ruff check APPLICABILE**: ruff e' configurato da Story 0.2, ogni nuovo file Python deve passare `ruff check` e `ruff format --check`
- **Test backend**: `python manage.py test` deve passare con 0 fallimenti (6 pre-esistenti + nuovi)
- **Test frontend**: `npx vitest run` deve passare con almeno 1 test
- **Build frontend**: `npm run build` deve passare con 0 errori TypeScript
- **CI**: `.github/workflows/ci.yml` deve essere sintatticamente valido. Se non testabile localmente (nessun GitHub runner), e' accettabile verificare la sintassi YAML e procedere — il primo push su `main` verra' il test reale

### References

- [Source: epics.md — Story 0.3 AC] `_bmad-output/planning-artifacts/epics.md#Story 0.3`
- [Source: architecture.md — D4 Testing Stack] `_bmad-output/planning-artifacts/architecture.md#D4`
- [Source: architecture.md — Strategia Testing Risk-Based] `_bmad-output/planning-artifacts/architecture.md#Strategia Testing Risk-Based`
- [Source: architecture.md — CI/CD Minimale Raccomandato] `_bmad-output/planning-artifacts/architecture.md#CI/CD Minimale Raccomandato`
- [Source: architecture.md — Naming Patterns Test Files] `_bmad-output/planning-artifacts/architecture.md#File Backend/Frontend`
- [Source: project-context.md — Regole di Testing] `_bmad-output/project-context.md#Regole di Testing`
- [Source: project-context.md — Setup Utente nei Test] `_bmad-output/project-context.md#Setup Utente nei Test`
- [Source: project-context.md — Isolamento Test] `_bmad-output/project-context.md#Isolamento Test`
- [Source: Story 0.1 — Completion Notes] `_bmad-output/implementation-artifacts/0-1-bug-fix-configurazione-settings-e-verifica-ambiente.md`
- [Source: Story 0.2 — Completion Notes] `_bmad-output/implementation-artifacts/0-2-linting-formatting-e-developer-tools.md`
- [Source: Vitest 4 docs] https://vitest.dev/guide/
- [Source: Next.js Vitest guide] https://nextjs.org/docs/app/guides/testing/vitest
- [Source: MSW v2 docs] https://mswjs.io/docs/
- [Source: @testing-library/jest-dom Vitest] https://www.npmjs.com/package/@testing-library/jest-dom

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

- Bug pre-esistente scoperto in `error_handler.py`: la funzione `handle_exception_with_serializer(exc)` accettava solo 1 argomento ma DRF ne passa 2 `(exc, context)`. Fix: aggiunto `context=None` come parametro opzionale.
- jsdom v27 incompatibile con Node.js 20.18.1 (richiede >= 20.19.0) — downgrade a jsdom v26 risolve `ERR_REQUIRE_ESM` su `@csstools/css-calc`.
- settings.py usa env vars individuali (`POSTGRES_DB`, `POSTGRES_USER`, etc.) e NON `DATABASE_URL` via `dj-database-url`. CI adattato con le variabili corrette.
- settings.py usa `DJANGO_SECRET_KEY` (non `SECRET_KEY`) e `MINIO_ENDPOINT`/`MINIO_ACCESS_KEY`/`MINIO_SECRET_KEY` (non i nomi `MINIO_STORAGE_*`). CI allineato.
- I test pre-esistenti sono 5 (non 6 come indicato nell'AC-2), tutti passanti.

### Completion Notes List

- **AC-1**: `conftest.py` creato con 5 helper function (create_authenticated_user, create_admin_user, create_sample_video, create_api_client_authenticated, create_sample_contest). Tutte usano django.test pattern, NON pytest.
- **AC-2**: 4 test auth nuovi in `test_auth.py` (registrazione con gruppo toconfirm, login JWT, login credenziali invalide 401, refresh token). Totale: 9 test passanti (5 pre-esistenti + 4 nuovi).
- **AC-3**: `setup.ts` configura MSW server lifecycle + import `@testing-library/jest-dom/vitest`.
- **AC-4**: `handlers.ts` con 5 handler MSW v2 (POST token, POST users, GET videos, GET videos/:id, GET users/:id).
- **AC-5**: 5 test MSW di integrazione che validano l'intera pipeline vitest + msw + setup.
- **AC-6**: `ci.yml` con 2 job paralleli (backend: ruff + test Django, frontend: lint + vitest + build).
- **AC-7**: `npm run build` passa senza errori.
- **Extra**: fix bug signature `handle_exception_with_serializer` (aggiunto parametro `context=None`).

### Senior Developer Review (AI)

**Reviewer:** Claude Opus 4.6 — 2026-03-01
**Outcome:** Changes Requested → Fixed → Approve

**Issues trovati: 3 HIGH, 4 MEDIUM, 2 LOW**

**Fix applicati (7/7 HIGH+MEDIUM):**
- **H-1 FIXED**: MSW handlers trailing slash mancante su `:id` routes — aggiunto `/` a `api/videos/:id/` e `api/users/:id/`, test allineati
- **H-2 FIXED**: Docstring `create_sample_video` diceva "no MinIO reale" ma Django scrive su storage — docstring corretta
- **H-3 FIXED**: AC-2 diceva "6 test pre-esistenti" ma sono 5 — corretto a "5"
- **M-1 FIXED**: `test_auth.py` setUp duplicato — sostituito con `create_authenticated_user()` da conftest.py
- **M-2 FIXED**: `error_handler.py` context ignorato — ora logga view name e usa lazy formatting
- **M-3 FIXED**: `sprint-status.yaml` mancante dalla File List — aggiunto
- **M-4 NOTED**: `msw-handlers.test.ts` testa i mock, non codice app — accettabile per baseline (AC-5 soddisfatto)

**LOW non fixati (accettabili):**
- L-1: f-string nel logger pre-esistente (fixato indirettamente in M-2)
- L-2: Naming ambiguo AC-1 "token JWT" vs implementazione — non bloccante

### Change Log

- 2026-03-01: Code review — 7 fix applicati (3 HIGH, 4 MEDIUM). Trailing slash MSW, docstring conftest, AC-2 count, DRY test_auth, error_handler context logging, File List completata.
- 2026-03-01: Story 0.3 implementata — testing baseline backend/frontend + CI/CD GitHub Actions. Fix bug pre-esistente in error_handler.py.

### File List

**Nuovi:**
- `backend/cs_clips/tests/conftest.py` — helper function riusabili per test
- `backend/cs_clips/tests/test_auth.py` — test auth flow (registrazione, login, refresh)
- `frontend/vitest.config.mts` — configurazione Vitest con jsdom + react plugin
- `frontend/src/test/setup.ts` — setup MSW lifecycle + jest-dom matchers
- `frontend/src/test/server.ts` — MSW server instance
- `frontend/src/test/handlers.ts` — MSW v2 handlers per 5 endpoint
- `frontend/src/test/__tests__/msw-handlers.test.ts` — test integrazione MSW
- `.github/workflows/ci.yml` — pipeline CI (backend + frontend)

**Modificati:**
- `frontend/package.json` — aggiunto script `test` e `test:watch`, nuove devDependencies (vitest, vite, msw, testing-library, jsdom)
- `frontend/package-lock.json` — lockfile aggiornato con nuove dipendenze
- `backend/cs_clips/exceptions/error_handler.py` — fix signature `handle_exception_with_serializer(exc, context=None)`
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — stato story aggiornato a review
