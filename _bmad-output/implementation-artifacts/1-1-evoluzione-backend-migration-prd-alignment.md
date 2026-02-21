# Story 1.1: Evoluzione Backend — Migration PRD Alignment

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want il backend allineato ai requisiti del PRD con i nuovi modelli e campi,
So that il frontend possa integrarsi con tutti gli endpoint necessari.

## Acceptance Criteria

1. **Batch migration "PRD alignment"** — Eseguendo la migration, vengono creati:
   - Modello `CommentLike` (user FK + comment FK, `unique_together`, CASCADE)
   - Modello `VideoLike` (user FK + video FK, `unique_together`, CASCADE)
   - Modello `Notification` (recipient FK, type enum con TextChoices, content text, `related_object_id` PositiveIntegerField, `read` bool default False, `created_at`)
   - Campo `allow_download` su Video (BooleanField, default=True)
   - Campo `is_disabled` su Comment (BooleanField, default=False)

2. **Endpoint popup-comments** — `GET /api/videos/{id}/popup-comments/` restituisce lista JSON:
   ```json
   [{"timestamp": 18, "comment_id": 42, "text": "quel flick!", "author": "marco", "like_count": 7}]
   ```
   - Filtra solo commenti con `is_disabled=False` e `timestamp_second > 0`
   - Per ogni timestamp unico, restituisce SOLO il commento con più like (via CommentLike count)
   - Soglia minima: almeno 1 like per essere incluso
   - Ordinato per `timestamp_second` crescente

3. **Endpoint like/unlike clip** — Due action separate su VideoViewSet (coerente con pattern follow/unfollow):
   - `POST /api/videos/{id}/like/` — crea VideoLike, ritorna `{"like_count": N}`
   - `POST /api/videos/{id}/unlike/` — rimuove VideoLike, ritorna `{"like_count": N}`
   - Vincolo unicità: un solo like per utente per video (constraint DB `unique_together`)
   - `like` su video già likato → 400 con `{"detail": "Hai già messo like"}`
   - `unlike` su video non likato → 400 con `{"detail": "Non hai messo like a questo video"}`

4. **Endpoint like/unlike commento** — Due action separate su CommentViewSet (stesso pattern):
   - `POST /api/comments/{id}/like/` — crea CommentLike, ritorna `{"like_count": N}`
   - `POST /api/comments/{id}/unlike/` — rimuove CommentLike, ritorna `{"like_count": N}`
   - Vincolo unicità: un solo like per utente per commento (constraint DB `unique_together`)
   - Stessa gestione errori di AC #3

5. **Tutte le migration applicabili** senza conflitti con le 14 migration esistenti
   - Migration schema per nuovi modelli/campi (auto-generata: `0015_prd_alignment.py`)
   - Data migration per gruppo `moderator` (`0016_create_moderator_group.py`)

6. **Campo `allow_download`** — Visibile nel VideoSerializer e filtrabile via `filterset_fields`

7. **Commenti disabilitati** — I commenti con `is_disabled=True` sono esclusi dalle query pubbliche di CommentViewSet tramite `get_queryset()` condizionale. La logica completa di bypass per moderatori sarà implementata in Story 4.3

## Tasks / Subtasks

- [x] Task 1: Creare nuovi modelli e migration (AC: #1, #5)
  - [x] 1.1 Modello `VideoLike` con FK user + video, unique_together, CASCADE, created_at
  - [x] 1.2 Modello `CommentLike` con FK user + comment, unique_together, CASCADE, created_at
  - [x] 1.3 Modello `Notification` con recipient FK, type TextChoices, content, related_object_id, read, created_at
  - [x] 1.4 Aggiungere campo `allow_download` BooleanField(default=True) su Video
  - [x] 1.5 Aggiungere campo `is_disabled` BooleanField(default=False) su Comment
  - [x] 1.6 Generare e applicare migration schema (`makemigrations` + `migrate`)
  - [x] 1.7 Creare data migration per gruppo `moderator` (`0016_create_moderator_group.py`)

- [x] Task 2: Creare/aggiornare serializers (AC: #2-4, #6)
  - [x] 2.1 `PopupCommentSerializer` (fields: timestamp, comment_id, text, author, like_count)
  - [x] 2.2 Aggiornare `VideoSerializer` — aggiungere `allow_download`, `like_count` (SerializerMethodField con Count annotation)
  - [x] 2.3 Aggiornare `CommentSerializer` — aggiungere `is_disabled`, `like_count` (SerializerMethodField con Count annotation)

- [x] Task 3: Creare/aggiornare views e endpoint (AC: #2-4, #7)
  - [x] 3.1 `@action popup_comments` su VideoViewSet — raggruppamento Python per timestamp (vedi Dev Notes)
  - [x] 3.2 `@action like` (POST) su VideoViewSet — crea VideoLike con get_or_create
  - [x] 3.3 `@action unlike` (POST) su VideoViewSet — rimuove VideoLike
  - [x] 3.4 `@action like` (POST) su CommentViewSet — crea CommentLike con get_or_create
  - [x] 3.5 `@action unlike` (POST) su CommentViewSet — rimuove CommentLike
  - [x] 3.6 Aggiornare `CommentViewSet.get_queryset()` — escludere `is_disabled=True` per utenti normali

- [x] Task 4: Registrare in admin.py (AC: #1)
  - [x] 4.1 Registrare `VideoLike`, `CommentLike`, `Notification` in admin.py

- [x] Task 5: Verifica e cleanup (AC: #5)
  - [x] 5.1 Verificare migration applicabili senza conflitti con le 14 esistenti
  - [x] 5.2 Verificare endpoint popup-comments, like/unlike via Swagger (drf-spectacular)
  - [x] 5.3 Verificare constraint unique_together su VideoLike e CommentLike (tentare double-like → 400)

## Dev Notes

### Stato Backend Attuale (Analisi Completa)

**Modelli esistenti** (in `backend/cs_clips/models.py`):
- `User` (AbstractUser) — email unique, following M2M self-referential, groups required
- `Contest` — tag TextChoices (clutch/funny/fail), unique_together(start_date, end_date, tag), winner FK nullable
- `Video` — uploader FK(User, CASCADE), contest FK(Contest, SET_NULL), file FileField, duration, views, tag. Custom `delete()` cancella file fisico
- `Rating` — user FK + video FK, unique_together, value 1-5 con validators
- `Comment` — user FK + video FK, content TextField, timestamp_second PositiveIntegerField

**14 migration esistenti** — la nuova migration sarà `0015_prd_alignment.py`

**Pattern da seguire OBBLIGATORIAMENTE:**

1. **ForeignKey pattern** (da Rating/Comment):
   ```python
   user = models.ForeignKey(
       settings.AUTH_USER_MODEL,  # MAI 'auth.User'
       on_delete=models.CASCADE,
       related_name='video_likes'
   )
   ```

2. **unique_together pattern** (da Rating):
   ```python
   class Meta:
       unique_together = ('user', 'video')
   ```

3. **Timestamp pattern** (da tutti i modelli):
   ```python
   created_at = models.DateTimeField(auto_now_add=True)
   ```

4. **TextChoices enum pattern** (da Contest.Tag):
   ```python
   class NotificationType(models.TextChoices):
       COMMENT = 'comment', 'Commento ricevuto'
       COMMENT_LIKE = 'comment_like', 'Like al commento'
       VIDEO_LIKE = 'video_like', 'Like alla clip'
       POPUP_PROMOTED = 'popup_promoted', 'Commento promosso a popup'
       CONTEST_INVITE = 'contest_invite', 'Invito contest'
       CONTEST_TURN = 'contest_turn', 'Turno contest disponibile'
   ```

5. **ViewSet custom action pattern** (da VideoViewSet.views, follow/unfollow):
   ```python
   @action(detail=True, methods=['post'], url_path='like')
   def like(self, request, pk=None):
       video = self.get_object()
       like, created = VideoLike.objects.get_or_create(user=request.user, video=video)
       if not created:
           return Response({"detail": "Hai già messo like"}, status=400)
       return Response({"like_count": video.likes.count()})
   ```

6. **Error handling pattern** — OGNI nuovo ViewSet DEVE sovrascrivere `handle_exception`:
   ```python
   def handle_exception(self, exc):
       return handle_exception_with_serializer(exc)
   ```

7. **perform_create pattern** (da tutti i ViewSet):
   ```python
   def perform_create(self, serializer):
       serializer.save(user=self.request.user)  # o recipient=self.request.user per notifiche
   ```

8. **Paginazione custom action** (da VideoViewSet.videos_from_following):
   ```python
   page = self.paginate_queryset(queryset)
   if page is not None:
       serializer = self.get_serializer(page, many=True)
       return self.get_paginated_response(serializer.data)
   ```

### Decisioni Architetturali (Party Mode Review)

| Decisione | Scelta | Rationale |
|---|---|---|
| popup-comments query | **Raggruppamento Python** (no Subquery ORM) | Leggibile, performante a 50 utenti, facile da evolvere |
| Like pattern | **Due action separate** (`like`/`unlike`, entrambi POST) | Coerente con `follow`/`unfollow` esistente nel codebase |
| like_count | **`Count()` annotation** (no denormalizzazione) | MVP 50 utenti, `# TODO: denormalizzare se performance diventa un problema` |
| Notification endpoints | **Solo modello** in questa story, endpoint CRUD in Epic 4 | Scope ridotto, focus su ciò che sblocca il frontend |
| Gruppo moderator | **Data migration** in questa story | Infrastruttura base, costo minimo (5 righe) |
| popup-comments paginazione | **Nessuna paginazione** — risposta piatta | Clip max 60s, soglia 1 like → max ~60 entries nel payload |
| Filtro commenti disabilitati | **`get_queryset()` base** — esclude `is_disabled=True` per tutti | Bypass moderatore rimandato a Story 4.3 |

### Mapping Notification.type → related_object_id

Il campo `related_object_id` è un `PositiveIntegerField` generico. Il frontend risolve il tipo di oggetto dal campo `type`:

| `type` enum | `related_object_id` punta a | Uso frontend |
|---|---|---|
| `comment` | Comment.id | Naviga a `/clip/{video_id}?t={timestamp}` |
| `comment_like` | Comment.id | Naviga a `/clip/{video_id}` |
| `video_like` | Video.id | Naviga a `/clip/{video_id}` |
| `popup_promoted` | Comment.id | Naviga a `/clip/{video_id}?t={timestamp}` |
| `contest_invite` | Contest.id | Naviga a `/contest/{contest_id}` |
| `contest_turn` | Contest.id | Naviga a `/contest/{contest_id}` |

### Endpoint popup-comments — Implementazione (Raggruppamento Python)

**Nessuna paginazione.** Risposta piatta, endpoint `@action(detail=True)` su VideoViewSet:

```python
@action(detail=True, methods=['get'], url_path='popup-comments')
def popup_comments(self, request, pk=None):
    video = self.get_object()
    comments = (
        Comment.objects
        .filter(video=video, is_disabled=False, timestamp_second__gt=0)
        .annotate(like_count=Count('likes'))  # 'likes' = related_name di CommentLike
        .filter(like_count__gte=1)
        .order_by('timestamp_second', '-like_count')
    )
    # Raggruppamento Python: per ogni timestamp, prendi solo il top comment
    seen = {}
    for c in comments:
        if c.timestamp_second not in seen:
            seen[c.timestamp_second] = c
    # Serializza il risultato
    result = [
        {
            "timestamp": c.timestamp_second,
            "comment_id": c.id,
            "text": c.content,
            "author": c.user.username,
            "like_count": c.like_count,
        }
        for c in seen.values()
    ]
    return Response(result)
```

**Perché raggruppamento Python:** clip max 60s + soglia 1 like = dataset piccolo (max ~60 righe). Nessun vantaggio da query SQL complessa con `Subquery`/`DISTINCT ON`. Più leggibile, testabile e debuggabile.

### Regole Critiche dal Project Context

- **SEMPRE** `get_user_model()` — MAI `from django.contrib.auth.models import User`
- **SEMPRE** `handle_exception()` override in ogni ViewSet
- **SEMPRE** `related_name` esplicito su tutte le FK
- **SEMPRE** `read_only_fields` nei serializer Meta
- **SEMPRE** messaggi/help_text in italiano
- **SEMPRE** codice (classi, variabili, URL path) in inglese
- **SEMPRE** `on_delete` esplicito: CASCADE per relazioni forti
- **Incrementi atomici**: `F('campo') + 1` poi `refresh_from_db()`, MAI `obj.campo += 1`
- **Validazione business logic** → nel serializer `validate()`, NON nella view
- **Nuovi gruppi utente** → creare via data migration, NON solo `get_or_create()` runtime
- **Django gira in locale**, NON in Docker (solo PostgreSQL in Docker)
- **psycopg 3.x** (NON psycopg2)
- File `.env` nella ROOT del progetto, NON in `backend/`

### Bug Noti da NON Replicare

- `RoleBasedPermission.has_object_permission()` controlla `obj.user` ma Video usa `obj.uploader` — per VideoLike usare `obj.user` (coerente con Rating)
- `VideoSerializer.create()` fa rollback manuale senza `transaction.atomic()` — per le nuove operazioni usare `transaction.atomic()` dove serve

### Project Structure Notes

- Tutti i nuovi modelli vanno in `backend/cs_clips/models.py` (app singola)
- Tutti i nuovi serializer vanno in `backend/cs_clips/serializers.py`
- Tutte le nuove views vanno in `backend/cs_clips/views.py`
- URL: registrare `NotificationViewSet` nel router in `backend/cs_clips/urls.py`
- Like su video/commenti: custom `@action` nei rispettivi ViewSet esistenti (NON ViewSet separati)
- Admin: registrare nuovi modelli in `backend/cs_clips/admin.py`
- Migration: `backend/cs_clips/migrations/0015_prd_alignment.py` (auto-generata)
- Data migration separata per gruppo `moderator`: `0016_create_moderator_group.py`

### Architettura — Decisioni che Impattano Questa Story

- **Rating esistente mantenuto per contest (Release B)** — VideoLike è un modello SEPARATO da Rating. Rating 1-5 per contest, VideoLike binary per feed
- **CommentLike abilita tutto il sistema popup** — senza CommentLike non funzionano: popup overlay, sidebar dinamica, calcolo top comment
- **is_disabled = soft-delete** — i commenti disabilitati restano in DB ma sono filtrati dalle query pubbliche. Serve per ricalcolo popup post-moderazione
- **Notification generico** — `related_object_id` è un PositiveIntegerField (non GenericForeignKey) per semplicità. Il frontend risolverà il tipo di oggetto dal `type` enum
- **allow_download default True** — tutti i video esistenti avranno download abilitato (backward compatible)

### Sequenza Implementazione (Dipendenze Reali)

```
Task 1 (Modelli + Migration) ──► Task 1.7 (Data migration moderator)
       │
       ▼
Task 2 (Serializers) ──► Task 3 (Views/Actions)
                              │
                              ▼
                         Task 4 (Admin) ──► Task 5 (Verifica)
```

1. **Modelli** → VideoLike, CommentLike, Notification, nuovi campi su Video/Comment
2. **Migration schema** → `makemigrations` + `migrate` (verifica no conflitti con 14 esistenti)
3. **Data migration** → gruppo `moderator`
4. **Serializers** → PopupCommentSerializer + aggiornamento VideoSerializer e CommentSerializer
5. **Views/Actions** → popup-comments, like/unlike su Video e Comment, get_queryset filtro is_disabled
6. **Admin** → registrazione nuovi modelli
7. **Verifica** → Swagger UI, constraint unique_together, double-like test

### Scope — Cosa NON è in Questa Story

Questi item sono esplicitamente rimandati alle story successive:
- **Endpoint CRUD notifiche** (GET lista, PATCH read, unread-count) → Epic 4, Story 4.1-4.2
- **NotificationViewSet e relativo router** → Epic 4, Story 4.1-4.2
- **Bypass filtro is_disabled per moderatori** → Epic 4, Story 4.3
- **Aggiornamento RoleBasedPermission per gruppo moderator** → Epic 4, Story 4.3
- **Creazione automatica notifiche su eventi** (like, commento, popup promosso) → Epic 4, Story 4.1

### Git Intelligence

Ultimi commit rilevanti:
- `927d3f4` — "integrazione frontend Next.js, CORS, filtri e miglioramenti API" (ultimo commit)
- `aae4c82` — "Refactory & BMAD Implementation"
- `14e2b61` — "followers + bozza role permissions" (aggiunta follow/unfollow)

Pattern stabiliti: ViewSet + DefaultRouter, custom actions con `@action`, error handling centralizzato.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.1]
- [Source: _bmad-output/planning-artifacts/architecture.md#Data Architecture]
- [Source: _bmad-output/planning-artifacts/architecture.md#Core Architectural Decisions]
- [Source: _bmad-output/project-context.md#Regole Specifiche Python/Django]
- [Source: _bmad-output/project-context.md#Regole Critiche da Non Dimenticare]
- [Source: backend/cs_clips/models.py — modelli esistenti]
- [Source: backend/cs_clips/views.py — pattern ViewSet e custom actions]
- [Source: backend/cs_clips/serializers.py — pattern serializer]
- [Source: backend/cs_clips/urls.py — router setup]
- [Source: backend/cs_clips/permissions.py — RoleBasedPermission, OnlyUsersPermission]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Test iniziali falliti per bug pre-esistente in `RoleBasedPermission.has_object_permission()` che non restituisce `True` per il gruppo 'user' su metodi non-DELETE. Risolto aggiungendo `permission_classes=[OnlyUsersPermission]` sulle custom action (stesso pattern di follow/unfollow).

### Completion Notes List

- **Task 1:** Creati 3 nuovi modelli (`VideoLike`, `CommentLike`, `Notification`) e 2 nuovi campi (`allow_download` su Video, `is_disabled` su Comment). Migration `0015_prd_alignment.py` auto-generata e applicata. Data migration `0016_create_moderator_group.py` creata e applicata. Tutti i pattern del codebase rispettati (`settings.AUTH_USER_MODEL`, `related_name`, `unique_together`, `CASCADE`, `TextChoices`).
- **Task 2:** Creato `PopupCommentSerializer` (read-only). Aggiornato `VideoSerializer` con `allow_download` e `like_count` (SerializerMethodField). Aggiornato `CommentSerializer` con `is_disabled` e `like_count` (SerializerMethodField).
- **Task 3:** Implementati 5 nuovi endpoint: `popup-comments` (GET), `like`/`unlike` su Video (POST), `like`/`unlike` su Comment (POST). Filtro `is_disabled=True` su `CommentViewSet.get_queryset()`. Aggiunto `filterset_fields = ['allow_download']` su VideoViewSet. Tutte le custom action usano `permission_classes` espliciti coerenti con pattern follow/unfollow.
- **Task 4:** Registrati `VideoLike`, `CommentLike`, `Notification` in admin.py.
- **Task 5:** Tutte le 16 migration applicate senza conflitti. `python manage.py check` superato. 34 test (14 modelli + 20 endpoint/API) tutti superati.

### Change Log

- 2026-02-14: Implementazione completa Story 1.1 — nuovi modelli, campi, serializers, endpoint, admin, migration, test suite (34 test)
- 2026-02-14: Code review — Fix sicurezza (is_disabled read-only), fix N+1 query (select_related + annotate), rimosso dead code (filterset_fields in serializer), collegato PopupCommentSerializer all'endpoint

### File List

- `backend/cs_clips/models.py` — Aggiunto import `settings`, rimosso import `User` da auth.models. Aggiunti modelli `VideoLike`, `CommentLike`, `Notification`. Aggiunto campo `allow_download` su `Video`, `is_disabled` su `Comment`.
- `backend/cs_clips/serializers.py` — Aggiunto import nuovi modelli. Creato `PopupCommentSerializer`. Aggiornato `VideoSerializer` (allow_download, like_count). Aggiornato `CommentSerializer` (is_disabled, like_count). [Review fix] Rimosso `filterset_fields` da Meta (dead code). `is_disabled` aggiunto a `read_only_fields`. `get_like_count` usa annotazione con fallback.
- `backend/cs_clips/views.py` — Aggiunto import `VideoLike`, `CommentLike`, `PopupCommentSerializer`, `Count`. Aggiunte action `popup_comments`, `like`, `unlike` su `VideoViewSet`. Aggiunte action `like`, `unlike` su `CommentViewSet`. Aggiunto `get_queryset()` filtro is_disabled su `CommentViewSet`. Aggiunto `filterset_fields` su `VideoViewSet`. [Review fix] `get_queryset()` con `annotate(like_count)` su VideoViewSet e CommentViewSet. `select_related('user')` su popup_comments. `PopupCommentSerializer` usato nella response.
- `backend/cs_clips/permissions.py` — Utilizzato `OnlyUsersPermission` sulle custom action like/unlike (fix permessi pre-esistente).
- `backend/cs_clips/admin.py` — Registrati `VideoLike`, `CommentLike`, `Notification`.
- `backend/cs_clips/migrations/0015_prd_alignment.py` — Migration schema auto-generata (nuovi modelli e campi).
- `backend/cs_clips/migrations/0016_create_moderator_group.py` — Data migration per gruppo moderator.
- `backend/cs_clips/tests/__init__.py` — Package test creato.
- `backend/cs_clips/tests/test_models.py` — 14 test unitari per nuovi modelli e campi.
- `backend/cs_clips/tests/test_views.py` — 20 test API per endpoint like/unlike, popup-comments, filtro commenti disabilitati, serializer fields.
