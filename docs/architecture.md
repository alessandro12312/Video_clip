# Architettura - Video_clip Backend

> Generato automaticamente il 2026-02-14 | Scan level: deep

## Sommario

Video_clip è una piattaforma di contest video settimanali costruita come monorepo con un backend Django REST API e un frontend da sviluppare. Il backend espone un'API RESTful completa per la gestione di utenti, video, rating, commenti e contest con sistema di spareggio ponderato.

---

## Stack Tecnologico

| Layer | Tecnologia | Versione | Ruolo |
|-------|-----------|----------|-------|
| Framework | Django | 5.1.6 | Web framework principale |
| API | Django REST Framework | 3.15.1 | REST API, serializzazione, ViewSets |
| Database | PostgreSQL | 16 | Storage relazionale |
| Driver DB | psycopg | 3.2.4 | Connessione PostgreSQL (v3) |
| Auth | SimpleJWT | 5.3.1 | Autenticazione JWT stateless |
| API Docs | drf-spectacular | 0.28.0 | OpenAPI 3.0 auto-generato |
| Video | moviepy | 2.2.1 | Calcolo durata video |
| Immagini | Pillow | 11.1.0 | Elaborazione immagini |
| Calcolo | numpy | 2.2.6 | Algoritmo spareggio ponderato |
| Container | Docker Compose | - | Orchestrazione PostgreSQL + pgAdmin |

---

## Pattern Architetturale

### Stile: API-Centric Monolith

```
┌─────────────────────────────────────────────────┐
│                    Client                        │
│           (Frontend — da sviluppare)             │
└──────────────────────┬──────────────────────────┘
                       │ HTTP/REST + JWT
                       ▼
┌─────────────────────────────────────────────────┐
│              Django REST Framework               │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  Router   │  │  JWT     │  │  Spectacular  │  │
│  │ (URLs)    │  │  Auth    │  │  (OpenAPI)    │  │
│  └────┬──────┘  └────┬─────┘  └───────────────┘  │
│       │              │                            │
│  ┌────▼──────────────▼─────┐                     │
│  │      ViewSets / Views   │                     │
│  │  User│Video│Rating│Comm │                     │
│  │  Contest Winners│End    │                     │
│  └────────────┬────────────┘                     │
│               │                                  │
│  ┌────────────▼────────────┐                     │
│  │     Permissions         │                     │
│  │  RoleBased│OnlyUsers    │                     │
│  └────────────┬────────────┘                     │
│               │                                  │
│  ┌────────────▼────────────┐                     │
│  │     Serializers         │                     │
│  │  Validation│Transform   │                     │
│  └────────────┬────────────┘                     │
│               │                                  │
│  ┌────────────▼────────────┐  ┌───────────────┐  │
│  │     Django ORM          │  │    Utils       │  │
│  │     (Models)            │  │  desempate     │  │
│  │                         │  │  getDateUtil   │  │
│  └────────────┬────────────┘  └───────────────┘  │
└───────────────┼──────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────┐
│              PostgreSQL 16                       │
│              (Docker Container)                  │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐  │
│  │  User  │ │ Video  │ │ Rating │ │ Comment  │  │
│  │        │ │        │ │        │ │          │  │
│  └────────┘ └────────┘ └────────┘ └──────────┘  │
│  ┌────────┐ ┌────────┐                          │
│  │Contest │ │ Group  │                          │
│  └────────┘ └────────┘                          │
└─────────────────────────────────────────────────┘
```

### Caratteristiche dell'architettura

- **Monolith single-app:** Tutta la logica in `cs_clips` (appropriato per la scala attuale)
- **ViewSet pattern:** CRUD automatico tramite DRF ModelViewSet + azioni custom
- **Stateless auth:** JWT senza sessioni server-side
- **Sincrono:** Nessun task asincrono (processing video sincrono nella request)
- **File storage locale:** Media serviti dal filesystem locale

---

## Architettura Dati

### Schema Relazionale

5 modelli principali con le seguenti relazioni:

- **User** ↔ **User** (M:M self-referential via `following`)
- **User** → **Video** (1:N via `uploader`, CASCADE)
- **User** → **Rating** (1:N, CASCADE)
- **User** → **Comment** (1:N, CASCADE)
- **Video** → **Contest** (N:1, SET_NULL)
- **Video** ← **Rating** (1:N, CASCADE, unique per user-video)
- **Video** ← **Comment** (1:N, CASCADE)
- **Contest** → **Video** (1:1 via `winner`, SET_NULL)
- **User** ↔ **Group** (M:N, Django built-in)

### Vincoli chiave

- `Rating: unique_together(user, video)` — Un voto per utente per video
- `Contest: unique_together(start_date, end_date, tag)` — Un contest per settimana per tag
- `User: email unique` — Email obbligatoria e unica
- `Comment: timestamp_second <= video.duration` — Validazione nel serializer

→ Dettagli completi in [data-models.md](./data-models.md)

---

## Design API

### Struttura

- **Base URL:** `/api/`
- **Formato:** JSON
- **Auth:** Bearer JWT token
- **Paginazione:** PageNumberPagination, 10 elementi per pagina
- **Schema:** OpenAPI 3.0 auto-generato

### Risorse

| Risorsa | Tipo | Endpoint | Azioni custom |
|---------|------|----------|---------------|
| Users | ViewSet | `/api/users/` | follow, unfollow, followers, following |
| Videos | ViewSet | `/api/videos/` | top-rated, following, views |
| Ratings | ViewSet | `/api/ratings/` | — |
| Comments | ViewSet | `/api/comments/` | — |
| Contests | APIView | `/api/contests/` | winners, end |
| Auth | JWT | `/api/token/` | obtain, refresh |

→ Dettagli completi in [api-contracts.md](./api-contracts.md)

---

## Sicurezza e Autenticazione

### Flusso di autenticazione

```
1. POST /api/users/        → Registrazione (AllowAny)
   └── Utente assegnato a gruppo "toconfirm"

2. POST /api/token/         → Login, ottieni access + refresh token
   └── Access: 12 ore | Refresh: 1 giorno | Rotation attiva

3. Authorization: Bearer <access_token>
   └── Header su ogni richiesta autenticata

4. POST /api/token/refresh/  → Rinnova access token
```

### Modello di permessi

```
superuser ──► Accesso completo a tutto
    │
  user ──────► CRUD completo, DELETE solo propri contenuti
    │
toconfirm ──► Solo lettura (SAFE_METHODS)
    │
 anonimo ──── Solo registrazione
```

---

## Logica di Business Chiave

### Contest Settimanali

1. Ogni settimana (lun-dom), per ogni tag (`clutch`, `funny`, `fail`), esiste un contest
2. Il contest viene creato automaticamente al primo upload video per quel tag
3. I video sono assegnati al contest della settimana corrente in base al loro tag
4. La chiusura è manuale (endpoint `POST /api/contests/end/`)

### Algoritmo di Spareggio

Quando più video hanno la stessa media voto, l'algoritmo `desempate_ponderato`:
1. Normalizza (percentile) tre metriche: numero rating, commenti, visualizzazioni
2. Applica pesi: ratings 50%, views 30%, comments 20%
3. Il video con score combinato più alto vince

### Commenti Timestampati

I commenti sono ancorati a un secondo specifico del video (`timestamp_second`), permettendo la funzionalità "commenti sincronizzati con la riproduzione" nel frontend.

---

## Gap e Limitazioni Attuali

### Critiche per il frontend

| Gap | Impatto | Soluzione suggerita |
|-----|---------|-------------------|
| **Nessun CORS** | Frontend su porta diversa non potrà chiamare l'API | Aggiungere `django-cors-headers` |
| **Processing video sincrono** | Upload di video grandi può causare timeout | Valutare Celery + Redis per task asincroni |
| **Followers non paginati** | Performance con molti follower | Aggiungere paginazione agli endpoint followers/following |

### Per la produzione

| Gap | Impatto | Priorità |
|-----|---------|----------|
| SECRET_KEY hardcoded | Vulnerabilità sicurezza | Alta |
| DEBUG=True default | Info leak in produzione | Alta |
| Nessun Dockerfile backend | Non containerizzabile | Media |
| Nessun CI/CD | Deploy manuale | Media |
| Nessuna suite di test | Regressioni non rilevate | Media |
| Storage media locale | Non scalabile | Bassa (per ora) |

### TODO nel codice

| File | TODO | Descrizione |
|------|------|-------------|
| permissions.py | `#TODO controlla bene i gruppi` | Rivedere logica permessi |
| views.py:299 | `#TODO rivedi authorization` | EndContestView: forse solo per admin |
| views.py:360 | `#TODO rivedi authorization` | ContestWinnersView: permessi da verificare |
| serializers.py:12 | `#TODO crea un serializer semplificato` | UserSerializer senza lista followers/following |
| models.py:57 | `#TODO: rimuovere in produzione` | Default tag Contest |
| models.py:87-91 | `#TODO: rimuovere in produzione` | Default tag e duration Video |
| models.py:132 | `#TODO: rimuovere in produzione` | Default timestamp_second Comment |

---

## Strategia di Testing

### Stato attuale

- Nessuna suite di test automatizzata
- Un management command (`test_spareggio.py`) per test manuale dell'algoritmo di spareggio
- Framework disponibile: Django `TestCase`

### Approccio consigliato

| Livello | Target | Framework |
|---------|--------|-----------|
| Unit test | Models, Serializers, Utils | Django TestCase |
| Integration test | ViewSets, Permissions | DRF APITestCase |
| API test | Endpoint E2E | DRF APIClient |

---

## Deployment

### Architettura corrente (sviluppo)

```
┌─────────────────────┐
│   Django Dev Server  │ ← python manage.py runserver
│   localhost:8000     │
└──────────┬──────────┘
           │ localhost:5432
┌──────────▼──────────┐  ┌──────────────────┐
│   PostgreSQL 16     │  │   pgAdmin 4      │
│   (Docker)          │  │   (Docker)       │
│   :5432             │  │   :8080          │
└─────────────────────┘  └──────────────────┘
```

### Architettura target (produzione suggerita)

```
┌─────────────────────┐
│      Nginx          │ ← Reverse proxy + static/media
│      :80/:443       │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Gunicorn/uWSGI     │ ← WSGI server
│  (Docker container) │
└──────────┬──────────┘
           │
┌──────────▼──────────┐  ┌──────────────────┐
│   PostgreSQL 16     │  │   Redis          │
│   (Docker)          │  │   (per Celery)   │
└─────────────────────┘  └──────────────────┘
```
