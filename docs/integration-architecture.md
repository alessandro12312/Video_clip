# Architettura di Integrazione — Video_clip

> Generato automaticamente il 2026-02-28 | Deep Scan | Workflow: document-project v1.2.0

---

## Panoramica

Video_clip è un monorepo con 2 parti attive che comunicano via REST API:

```
┌─────────────────┐        REST API         ┌─────────────────┐
│    Frontend      │ ◄──── JSON/JWT ────►    │    Backend       │
│  (Next.js 16)    │                         │  (Django 5.1.6)  │
│  Port: 3000      │                         │  Port: 8000      │
└────────┬─────────┘                         └────────┬─────────┘
         │                                            │
         │ Cookie session_active                      │ psycopg3
         │ localStorage refresh_token                 │
         │                                   ┌────────▼─────────┐
         │                                   │   PostgreSQL 16   │
         │                                   │   Port: 5432      │
         │                                   └──────────────────┘
         │                                            │
         │                                   ┌────────▼─────────┐
         │                                   │   MinIO (S3)      │
         │ ◄─── Presigned URL (1h) ─────     │   Port: 9000/9001 │
         │                                   └──────────────────┘
```

---

## Punti di Integrazione

### 1. Frontend → Backend (REST API)

| Aspetto | Dettaglio |
|---|---|
| **Protocollo** | HTTP REST (JSON) |
| **Base URL** | `http://127.0.0.1:8000/api/` |
| **Autenticazione** | JWT Bearer token (header `Authorization`) |
| **Client** | Axios con interceptors (`src/lib/api/client.ts`) |
| **Token Strategy** | Access in-memory, refresh in localStorage |
| **Refresh Flow** | 401 → mutex queue → POST `/api/token/refresh/` → retry |

**Endpoint chiamati dal frontend** (7 moduli API):

| Modulo | Endpoint principali | Note |
|---|---|---|
| auth | `/api/token/`, `/api/token/refresh/`, `/api/users/` | Usa axios diretto (no interceptor) |
| users | `/api/users/{id}/`, `follow`, `unfollow`, `followers`, `following` | Optimistic updates su follow |
| videos | `/api/videos/`, `following`, `top-rated`, `{id}/views/` | Infinite queries, FormData upload |
| comments | `/api/comments/` | Loop multi-pagina per tutti i commenti |
| ratings | `/api/ratings/` | Create + PATCH |
| contests | `/api/contests/winners/` | Solo lettura |

### 2. Frontend: Route Protection

| Aspetto | Dettaglio |
|---|---|
| **Middleware** | `src/middleware.ts` |
| **Meccanismo** | Cookie `session_active` (impostato da `setTokens()`) |
| **Route protette** | `(main)/*` → redirect a `/login` se no cookie |
| **Route pubbliche** | `(auth)/*`, `clip/[id]` |

### 3. Backend → PostgreSQL

| Aspetto | Dettaglio |
|---|---|
| **Driver** | psycopg 3.2.4 |
| **Config** | `DATABASES` in `settings.py` via `dj-database-url` |
| **Modelli** | 5 tabelle + 3 tabelle M2M |
| **Migrazioni** | Django ORM (2 migrazioni attive) |

### 4. Backend → MinIO (S3)

| Aspetto | Dettaglio |
|---|---|
| **Client** | `minio_storage.storage.MinioMediaStorage` |
| **Bucket media** | `video` |
| **Bucket backup** | `video-backup` |
| **URL file** | Presigned URL con scadenza 1 ora |
| **Upload** | `MultiPartParser` → salvataggio MinIO → URL presigned in risposta |
| **Cleanup** | `django_cleanup` elimina file quando il modello è cancellato |
| **Init** | `scripts/minio_init.sh` via `minio-init` container Docker |

### 5. Backend: Scheduler (APScheduler)

| Aspetto | Dettaglio |
|---|---|
| **Trigger** | Cron: ogni giovedì alle 11:33 UTC |
| **Job** | `close_contests` management command |
| **Avvio** | Automatico in `CsClipsConfig.ready()` |
| **Funzione** | Chiude contest scaduti e assegna vincitori |

---

## Flusso Dati Principali

### Upload Video

```
Frontend                          Backend                         MinIO
────────                          ───────                         ─────
1. FormData(title, file, tag)
   POST /api/videos/          →
                                  2. Salva file temp
                                  3. Estrai durata (MoviePy)
                                  4. get_or_create_contest(tag)
                                  5. Salva Video model          →  6. Upload file su bucket
                                  7. Genera presigned URL       ←
                                  8. Response 201 + file_url
                              ←
9. Invalida cache videos.all
```

### Flusso Autenticazione

```
Frontend                          Backend
────────                          ───────
1. POST /api/token/
   {username, password}       →
                                  2. Verifica credenziali
                                  3. Genera JWT pair
                                  4. Aggiorna last_login
                              ←   5. {access, refresh}
6. setTokens(access, refresh)
   - access → memoria
   - refresh → localStorage
   - cookie session_active → 1

--- Richiesta successiva ---
7. GET /api/videos/
   Authorization: Bearer {access}  →
                                  8. JWTAuthentication.authenticate()
                              ←   9. Response 200

--- Token scaduto ---
10. GET /api/any/
    Authorization: Bearer {expired}  →
                                  11. 401 Unauthorized
                              ←
12. Interceptor rileva 401
13. POST /api/token/refresh/
    {refresh}                  →
                                  14. Verifica refresh
                                  15. Genera nuovo pair
                              ←   16. {access, refresh}
17. setTokens(new_access, new_refresh)
18. Retry richiesta originale  →
```

### Chiusura Contest (Background)

```
APScheduler (ogni giovedì 11:33)
    ↓
close_contests management command
    ↓
Per ogni contest con end_date < oggi e is_closed=False:
    ↓
1. Annota video con Avg('ratings__value')
2. Trova video con media massima
3. Se pareggio → desempate_ponderato(voti 50%, views 30%, commenti 20%)
4. Imposta winner, is_closed=True, closed_at=now()
```

---

## Dipendenze Condivise

| Risorsa | Usata da | Note |
|---|---|---|
| PostgreSQL 16 | Backend | Database principale |
| MinIO | Backend (storage) + Frontend (presigned URL) | File video |
| JWT Tokens | Backend (genera) + Frontend (consume/refresh) | Autenticazione |
| `.env` root | compose.yml + Backend | Config infra |

---

## Gap e Limitazioni

1. **CORS**: `CORS_ALLOW_ALL_ORIGINS = True` — adeguato per sviluppo, da configurare per produzione
2. **Celery/Redis**: pacchetti installati ma non configurati — APScheduler usato al posto
3. **No WebSocket**: comunicazione solo request-response, no real-time updates
4. **Endpoint mancanti**: frontend chiama `/api/users/by-username/{username}/` che non esiste nel backend
5. **Paginazione followers/following**: frontend si aspetta formato paginato, backend ritorna array piatto
6. **Filtro video per utente**: frontend filtra client-side (performance issue), manca `?uploader=` backend
