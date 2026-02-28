# Contratti API — Backend Video_clip

> Generato automaticamente il 2026-02-28 | Deep Scan | Workflow: document-project v1.2.0

---

## Indice

1. [Informazioni Generali](#informazioni-generali)
2. [Autenticazione JWT](#autenticazione-jwt)
3. [Paginazione](#paginazione)
4. [Formato Risposta Errori](#formato-risposta-errori)
5. [Classi di Permessi](#classi-di-permessi)
6. [Gestione File Upload](#gestione-file-upload)
7. [Endpoint per Dominio](#endpoint-per-dominio)

---

## Informazioni Generali

| Chiave | Valore |
|---|---|
| **Base URL** | `/api/` |
| **Framework** | Django REST Framework 3.15.1 + drf-spectacular 0.28.0 |
| **Database** | PostgreSQL 16 |
| **Storage File** | MinIO (S3-compatible) |
| **Swagger UI** | `/api/docs/` |
| **ReDoc** | `/api/redoc/` |
| **Schema OpenAPI** | `/api/schema/` |

### Routing Principale

- `project_clip/urls.py` — Root: `/admin/`, `/api/` (include cs_clips.urls), `/api/token/`, `/api/token/refresh/`, `/api/schema/`, `/api/docs/`, `/api/redoc/`
- `cs_clips/urls.py` — Router DRF: `users`, `videos`, `ratings`, `comments` + endpoint custom contest

---

## Autenticazione JWT

| Parametro | Valore |
|---|---|
| **Tipo** | Bearer JWT |
| **Header** | `Authorization: Bearer <access_token>` |
| **Access Token Lifetime** | 12 ore |
| **Refresh Token Lifetime** | 1 giorno |
| **Token Rotation** | Attiva |

---

## Paginazione

| Parametro | Valore |
|---|---|
| **Classe** | `PageNumberPagination` |
| **Page Size** | 10 |
| **Query Params** | `?page=N&page_size=N` |

```json
{
  "count": 42,
  "next": "http://host/api/videos/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Formato Risposta Errori

Handler centralizzato: `cs_clips/exceptions/error_handler.py`

```json
{
  "code": "ValidationError",
  "detail": "Campo 'title': Questo campo è obbligatorio."
}
```

| Eccezione | `code` | HTTP |
|---|---|---|
| `ValidationError` | `ValidationError` | 400 |
| `NotAuthenticated` | `NotAuthenticated` | 401 |
| `PermissionDenied` | `PermissionDenied` | 403 |
| `NotFound` / `Http404` | `NotFound` | 404 |
| `IntegrityError` | `Conflict` | 409 |
| Altra eccezione | Nome classe | 500 |

---

## Classi di Permessi

### `RoleBasedPermission`
- **Superuser**: accesso totale
- **Gruppo `toconfirm`**: solo lettura (GET, HEAD, OPTIONS)
- **Gruppo `user`**: CRUD completo, DELETE solo su propri contenuti
- **Nessun gruppo**: accesso negato

### `OnlyUsersPermission`
- Accesso solo a superuser o gruppo `user`

### `OnlyAdminsPermission`
- Accesso solo a superuser o gruppo `admin`

---

## Gestione File Upload

| Parametro | Valore |
|---|---|
| **Storage** | MinIO bucket `video` |
| **Parser** | `MultiPartParser`, `FormParser` |
| **URL File** | Presigned URL, valida 1 ora |
| **Durata** | Estratta automaticamente via MoviePy/FFmpeg |
| **Cleanup** | `django_cleanup` rimuove file orfani |

---

## Endpoint per Dominio

### Riepilogo Completo

| # | Metodo | URL | Permessi | Paginato |
|---|---|---|---|---|
| 1 | POST | `/api/token/` | AllowAny | No |
| 2 | POST | `/api/token/refresh/` | AllowAny | No |
| 3 | GET | `/api/users/` | Auth + RoleBased | Sì |
| 4 | POST | `/api/users/` | AllowAny | No |
| 5 | GET | `/api/users/{id}/` | Auth + RoleBased | No |
| 6 | PUT | `/api/users/{id}/` | Auth + RoleBased | No |
| 7 | PATCH | `/api/users/{id}/` | Auth + RoleBased | No |
| 8 | DELETE | `/api/users/{id}/` | Auth + RoleBased | No |
| 9 | POST | `/api/users/{id}/follow/` | OnlyUsers | No |
| 10 | POST | `/api/users/{id}/unfollow/` | OnlyUsers | No |
| 11 | GET | `/api/users/{id}/followers/` | Auth + RoleBased | No* |
| 12 | GET | `/api/users/{id}/following/` | Auth + RoleBased | No* |
| 13 | GET | `/api/videos/` | Auth + RoleBased | Sì |
| 14 | POST | `/api/videos/` | Auth + RoleBased | No |
| 15 | GET | `/api/videos/{id}/` | Auth + RoleBased | No |
| 16 | PUT | `/api/videos/{id}/` | Auth + RoleBased | No |
| 17 | PATCH | `/api/videos/{id}/` | Auth + RoleBased | No |
| 18 | DELETE | `/api/videos/{id}/` | Auth + RoleBased | No |
| 19 | POST | `/api/videos/{id}/views/` | Auth + RoleBased | No |
| 20 | GET | `/api/videos/following/` | Auth + RoleBased | Sì |
| 21 | GET | `/api/videos/top-rated/` | Auth + RoleBased | Sì |
| 22 | GET | `/api/ratings/` | Auth + RoleBased | Sì |
| 23 | POST | `/api/ratings/` | Auth + RoleBased | No |
| 24 | GET | `/api/ratings/{id}/` | Auth + RoleBased | No |
| 25 | PUT | `/api/ratings/{id}/` | Auth + RoleBased | No |
| 26 | PATCH | `/api/ratings/{id}/` | Auth + RoleBased | No |
| 27 | DELETE | `/api/ratings/{id}/` | Auth + RoleBased | No |
| 28 | GET | `/api/comments/` | Auth + RoleBased | Sì |
| 29 | POST | `/api/comments/` | Auth + RoleBased | No |
| 30 | GET | `/api/comments/{id}/` | Auth + RoleBased | No |
| 31 | PUT | `/api/comments/{id}/` | Auth + RoleBased | No |
| 32 | PATCH | `/api/comments/{id}/` | Auth + RoleBased | No |
| 33 | DELETE | `/api/comments/{id}/` | Auth + RoleBased | No |
| 34 | GET | `/api/contests/winners/` | Auth | Sì |
| 35 | POST | `/api/contests/end/` | OnlyAdmins | No |

*\* Endpoint followers/following dichiarano paginazione OpenAPI ma non la implementano.*

---

### Autenticazione

#### `POST /api/token/` — Login JWT
- **Permessi**: AllowAny
- **Request**: `{ "username": "string", "password": "string" }`
- **Response 200**: `{ "access": "eyJ...", "refresh": "eyJ..." }`
- **Note**: Aggiorna `last_login` dell'utente

#### `POST /api/token/refresh/` — Refresh JWT
- **Permessi**: AllowAny
- **Request**: `{ "refresh": "eyJ..." }`
- **Response 200**: `{ "access": "eyJ...", "refresh": "eyJ..." }` (token rotation attiva)

---

### Utenti

**ViewSet**: `UserViewSet` (ModelViewSet) — Serializer: `UserSerializer`

**Campi serializer**: `id, username, email, created_at, updated_at, followers, following`

#### `POST /api/users/` — Registrazione
- **Permessi**: AllowAny
- **Serializer**: `UserRegistrationSerializer`
- **Request**: `{ "username": "string", "email": "user@example.com", "password": "string" }`
- **Note**: Utente assegnato al gruppo `toconfirm` (solo lettura fino a conferma)

#### `POST /api/users/{id}/follow/` — Segui utente
- **Permessi**: OnlyUsersPermission
- **Response 200**: `{ "detail": "Hai iniziato a seguire mario." }`
- **Errore 400**: `{ "detail": "Non puoi seguire te stesso." }`

#### `POST /api/users/{id}/unfollow/` — Smetti di seguire
- **Permessi**: OnlyUsersPermission
- **Response 200**: `{ "detail": "Hai smesso di seguire mario." }`

#### `GET /api/users/{id}/followers/` — Lista follower
- **Paginazione**: **Non implementata** (array piatto, non paginato)

#### `GET /api/users/{id}/following/` — Lista seguiti
- **Paginazione**: **Non implementata** (array piatto, non paginato)

---

### Video

**ViewSet**: `VideoViewSet` (ModelViewSet) — Parser: `MultiPartParser`, `FormParser`

**Serializer output**: `VideoOutputSerializer` — Campi: `id, title, duration, file, file_url, uploader, average_rating, created_at, updated_at, contest, tag`
- `uploader`: stringa (username)
- `average_rating`: calcolato al volo (media rating)
- `file_url`: presigned URL MinIO valida 1 ora

**Serializer input**: `VideoInputSerializer` — Campi: `title, file, tag`

**Serializer update**: `VideoUpdateSerializer` — Campi: `title, tag` (cambio tag riassegna contest)

#### `POST /api/videos/` — Carica video
- **Content-Type**: `multipart/form-data`
- **Campi**: `title` (CharField max 100), `file` (binary), `tag` (clutch|funny|fail)
- **Auto**: uploader = utente corrente, contest = corrente per tag, duration = estratta da FFmpeg

#### `POST /api/videos/{id}/views/` — Incrementa visualizzazioni
- **Request**: body vuoto
- **Response 200**: `{ "views": 42 }`
- **Note**: Usa `F('views') + 1` (atomic, no race condition)

#### `GET /api/videos/following/` — Feed utenti seguiti
- **Paginazione**: Sì
- **Ordinamento**: `-created_at`

#### `GET /api/videos/top-rated/` — Classifica top rated
- **Query param**: `range` = `day|week|month|year|all` (default: `all`)
- **Paginazione**: Sì
- **Ordinamento**: `-average_rating` (annotazione `Avg`)

---

### Valutazioni (Ratings)

**ViewSet**: `RatingViewSet` (ModelViewSet) — Serializer: `RatingSerializer`

**Campi**: `id, user (username), video (ID), value, created_at, updated_at`

#### `POST /api/ratings/` — Crea valutazione
- **Request**: `{ "video": 5, "value": 4 }`
- **Vincoli**: value 1-5, `unique_together(user, video)` — duplicato genera 409 Conflict
- **Auto**: user = utente corrente

---

### Commenti

**ViewSet**: `CommentViewSet` (ModelViewSet) — Serializer: `CommentSerializer`

**Campi**: `id, user (username), video (ID), content, timestamp_second, created_at, updated_at`

#### `POST /api/comments/` — Crea commento
- **Request**: `{ "video": 5, "content": "Bel video!", "timestamp_second": 15 }`
- **Validazione**: `timestamp_second` >= 0 e <= durata video
- **Auto**: user = utente corrente

---

### Contest

#### `GET /api/contests/winners/` — Lista vincitori
- **Permessi**: IsAuthenticated
- **Paginazione**: Sì
- **Response**: Video vincitori ordinati per `closed_at` del contest

#### `POST /api/contests/end/` — Chiudi contest
- **Permessi**: OnlyAdminsPermission
- **Request**: `{ "tag": "clutch" }`
- **Response 200**: `{ "contest": {...}, "winner": {...}, "finalists": null|[...] }`
- **Spareggio**: normalizzazione percentile (voti 50%, views 30%, commenti 20%)

---

## Bug e Anomalie Noti

1. **`VideoSerializer` inesistente**: `video_views.py` righe 92/104 — update/partial_update referenziano `VideoSerializer` (non esiste), causerebbe `NameError`
2. **Import `Response` mancante**: `user_views.py` usa `Response` senza importarlo
3. **Paginazione followers/following non implementata**: dichiarata in OpenAPI ma codice ritorna array piatto
4. **Nessun filtro video per utente/contest**: mancano query params `?uploader=ID` o `?contest=ID`
5. **`ContestSerializer` mai usato**: definito ma nessuna view lo utilizza
6. **Tag accettato da body e query string** in `EndContestView`: potenziale ambiguità
