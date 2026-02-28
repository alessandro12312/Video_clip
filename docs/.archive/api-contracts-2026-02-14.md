# Contratti API - Video_clip Backend

> Generato automaticamente il 2026-02-14 | Scan level: deep

## Panoramica

API REST basata su Django REST Framework con autenticazione JWT.

- **Base URL:** `http://127.0.0.1:8000/api/`
- **Autenticazione:** JWT (SimpleJWT) — Bearer token nell'header `Authorization`
- **Formato risposte:** JSON
- **Paginazione:** PageNumberPagination (PAGE_SIZE=10), parametro `?page=N`
- **Schema OpenAPI:** Generato runtime da drf-spectacular

---

## Autenticazione

### POST `/api/token/`

Ottieni coppia di token JWT (access + refresh).

- **Permessi:** AllowAny
- **Request Body:**

```json
{
  "username": "string",
  "password": "string"
}
```

- **Response 200:**

```json
{
  "access": "eyJ...",
  "refresh": "eyJ..."
}
```

- **Note:** Aggiorna automaticamente `last_login` dell'utente (CustomTokenObtainPairView).

### POST `/api/token/refresh/`

Rinnova il token di accesso.

- **Permessi:** AllowAny
- **Request Body:**

```json
{
  "refresh": "eyJ..."
}
```

- **Response 200:**

```json
{
  "access": "eyJ..."
}
```

- **Note:** Rotation attiva — il refresh token viene ruotato ad ogni uso.

### Configurazione JWT

| Parametro | Valore |
|-----------|--------|
| ACCESS_TOKEN_LIFETIME | 12 ore |
| REFRESH_TOKEN_LIFETIME | 1 giorno |
| ROTATE_REFRESH_TOKENS | True |

---

## Utenti (UserViewSet)

**Base path:** `/api/users/`
**Permessi:** IsAuthenticated + RoleBasedPermission (eccetto registrazione)

### POST `/api/users/` — Registrazione

- **Permessi:** AllowAny
- **Serializer:** UserRegistrationSerializer
- **Request Body:**

```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

- **Response 201:** Dati utente creato
- **Side effect:** Utente assegnato automaticamente al gruppo `toconfirm`

### GET `/api/users/` — Lista utenti

- **Permessi:** IsAuthenticated + RoleBasedPermission
- **Response 200:** Lista paginata di utenti

```json
{
  "count": 10,
  "next": "http://.../api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "string",
      "email": "string",
      "created_at": "datetime",
      "updated_at": "datetime",
      "followers": [1, 2],
      "following": [3, 4]
    }
  ]
}
```

### GET `/api/users/{id}/` — Dettaglio utente

- **Response 200:** Singolo oggetto utente (stesso schema della lista)

### PUT/PATCH `/api/users/{id}/` — Aggiorna utente

- **Permessi:** IsAuthenticated + RoleBasedPermission
- **Request Body:** Campi da aggiornare

### DELETE `/api/users/{id}/` — Elimina utente

- **Permessi:** Solo il proprietario o superuser

### POST `/api/users/{id}/follow/` — Segui utente

- **Permessi:** OnlyUsersPermission (gruppo `user` o superuser)
- **Validazione:** Non puoi seguire te stesso
- **Response 200:**

```json
{
  "detail": "Hai iniziato a seguire {username}."
}
```

### POST `/api/users/{id}/unfollow/` — Smetti di seguire

- **Permessi:** OnlyUsersPermission
- **Response 200:**

```json
{
  "detail": "Hai smesso di seguire {username}."
}
```

### GET `/api/users/{id}/followers/` — Lista follower

- **Response 200:** Array di oggetti utente (non paginato)

### GET `/api/users/{id}/following/` — Lista following

- **Response 200:** Array di oggetti utente (non paginato)

---

## Video (VideoViewSet)

**Base path:** `/api/videos/`
**Permessi:** IsAuthenticated + RoleBasedPermission
**Ordinamento default:** `-created_at` (dal più recente)

### POST `/api/videos/` — Upload video

- **Content-Type:** `multipart/form-data`
- **Request Body:**

```
title: string (max 100 char)
file: file (video)
tag: string (clutch|funny|fail) — OBBLIGATORIO
```

- **Response 201:**

```json
{
  "id": 1,
  "title": "string",
  "file": "http://.../media/videos/filename.mp4",
  "uploader": "username",
  "average_rating": 0.0,
  "views": 0,
  "created_at": "datetime",
  "updated_at": "datetime",
  "contest": 1,
  "tag": "clutch"
}
```

- **Side effects:**
  - `duration` calcolata automaticamente via moviepy (sincrono)
  - `contest` assegnato automaticamente tramite `get_or_create_current_contest(tag)`
  - `uploader` impostato dall'utente autenticato
  - Se calcolo durata fallisce → record eliminato, errore 400

### GET `/api/videos/` — Lista video

- **Response 200:** Lista paginata, ordinata per `-created_at`

### GET `/api/videos/{id}/` — Dettaglio video

### PUT/PATCH `/api/videos/{id}/` — Aggiorna video

### DELETE `/api/videos/{id}/` — Elimina video

- **Side effect:** Cancella anche il file fisico da `media/videos/`

### GET `/api/videos/top-rated/` — Video più votati

- **Query params:**
  - `range`: `day` | `week` | `month` | `year` | `all` (default: `all`)
- **Logica:** Ordina per media voto (annotated `Avg('ratings__value')`) decrescente
- **Response 200:** Lista paginata di video con `average_rating`

### GET `/api/videos/following/` — Video dagli utenti seguiti

- **Logica:** Filtra video degli utenti che l'utente autenticato segue
- **Ordinamento:** `-created_at`
- **Response 200:** Lista paginata

### POST `/api/videos/{id}/views/` — Incrementa visualizzazioni

- **Logica:** Incremento atomico (`F('views') + 1`)
- **Uso previsto:** Chiamato dal frontend ogni 5-10 secondi durante la riproduzione
- **Response 200:**

```json
{
  "views": 42
}
```

---

## Rating (RatingViewSet)

**Base path:** `/api/ratings/`
**Permessi:** IsAuthenticated + RoleBasedPermission

### POST `/api/ratings/` — Crea voto

- **Request Body:**

```json
{
  "video": 1,
  "value": 4
}
```

- **Vincoli:**
  - `value`: 1-5 (MinValueValidator, MaxValueValidator)
  - `unique_together: (user, video)` — un voto per utente per video
- **Response 201:**

```json
{
  "id": 1,
  "user": "username",
  "video": 1,
  "value": 4,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### GET `/api/ratings/` — Lista voti

### GET/PUT/PATCH/DELETE `/api/ratings/{id}/`

---

## Commenti (CommentViewSet)

**Base path:** `/api/comments/`
**Permessi:** IsAuthenticated + RoleBasedPermission

### POST `/api/comments/` — Crea commento

- **Request Body:**

```json
{
  "video": 1,
  "content": "Bel momento!",
  "timestamp_second": 45
}
```

- **Validazione custom:**
  - `timestamp_second` >= 0
  - `timestamp_second` <= durata del video
  - Il video deve avere una durata impostata
- **Response 201:**

```json
{
  "id": 1,
  "user": "username",
  "video": 1,
  "content": "Bel momento!",
  "timestamp_second": 45,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### GET `/api/comments/` — Lista commenti

### GET/PUT/PATCH/DELETE `/api/comments/{id}/`

---

## Contest

### GET `/api/contests/winners/` — Vincitori dei contest

- **Permessi:** IsAuthenticated
- **Logica:** Contest chiusi con vincitore, ordinati per `closed_at` decrescente
- **Response 200:** Lista paginata di oggetti Video (i vincitori)

### POST `/api/contests/end/` — Chiudi contest corrente

- **Permessi:** IsAuthenticated (TODO: dovrebbe essere solo admin)
- **Logica:**
  1. Trova contest attivo (non chiuso, date correnti)
  2. Annota media voto per ogni video del contest
  3. Se un solo video ha la media più alta → vincitore
  4. Se parità → algoritmo `desempate_ponderato()`:
     - Pesi: ratings (0.5), commenti (0.2), visualizzazioni (0.3)
     - Normalizzazione percentile con numpy
  5. Salva vincitore e chiude il contest
- **Response 200:**

```json
{
  "contest": {
    "id": 1,
    "name": "2025giugno2clutch",
    "start_date": "2025-06-09",
    "end_date": "2025-06-15",
    "closed_at": "datetime",
    "winner_id": 5
  },
  "winner": { "...VideoSerializer..." },
  "finalists": [ "...solo se c'è stato spareggio..." ]
}
```

---

## Documentazione API (Runtime)

| Endpoint | Tipo |
|----------|------|
| `GET /api/docs/` | Swagger UI |
| `GET /api/redoc/` | ReDoc |
| `GET /api/schema/` | OpenAPI 3.0 JSON |

---

## Gestione Errori

Formato standard per tutti gli errori (centralizzato in `handle_exception_with_serializer`):

```json
{
  "code": "ValidationError",
  "detail": "Campo 'tag': Questo campo è obbligatorio."
}
```

| Codice HTTP | Tipo | Quando |
|-------------|------|--------|
| 400 | ValidationError | Input non valido |
| 401 | NotAuthenticated | Token mancante/scaduto |
| 403 | PermissionDenied | Permessi insufficienti |
| 404 | NotFound | Risorsa non trovata |
| 409 | Conflict | Vincolo di unicità violato |
| 500 | InternalServerError | Errore generico |

---

## Sistema Permessi

### Gruppi (Ruoli)

| Gruppo | Lettura | Scrittura | Eliminazione |
|--------|---------|-----------|--------------|
| `toconfirm` | Si | No | No |
| `user` | Si | Si | Solo propri contenuti |
| `superuser` | Si | Si | Tutto |

### Classi di Permesso

- **RoleBasedPermission:** Permesso principale basato su gruppi Django
- **OnlyUsersPermission:** Restringe a utenti del gruppo `user` o superuser

---

## Note per lo Sviluppo Frontend

1. **CORS non configurato** — Necessario aggiungere `django-cors-headers` prima di collegare qualsiasi frontend
2. **Upload video** — Usare `multipart/form-data`, il processing è sincrono (potenziali timeout con video grandi)
3. **Incremento views** — Chiamare `POST /api/videos/{id}/views/` ogni 5-10 secondi durante la riproduzione
4. **Commenti timestampati** — I commenti sono ancorati a un secondo specifico del video
5. **Contest automatici** — I contest si creano automaticamente su base settimanale (lun-dom) per tag
6. **Paginazione** — Tutte le liste sono paginate a 10 elementi, usare `?page=N`
7. **Followers/Following** — Le liste followers/following NON sono paginate (potenziale problema di performance)
