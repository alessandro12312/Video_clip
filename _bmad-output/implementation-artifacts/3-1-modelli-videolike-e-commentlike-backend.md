# Story 3.1: Modelli VideoLike e CommentLike Backend

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a sviluppatore,
I want i modelli VideoLike e CommentLike con endpoint CRUD,
so that il sistema di like è disponibile per il frontend e per il calcolo dei popup.

## Acceptance Criteria

1. **Modelli Django** — `VideoLike` e `CommentLike` creati come file separati in `cs_clips/models/`
   - `VideoLike`: campi `user` (FK `get_user_model()`), `video` (FK Video), `created_at` (auto_now_add), con `unique_together = ('user', 'video')` e `related_name='likes'` su entrambe le FK
   - `CommentLike`: campi `user` (FK `get_user_model()`), `comment` (FK Comment), `created_at` (auto_now_add), con `unique_together = ('user', 'comment')` e `related_name='likes'` su entrambe le FK
   - Entrambi registrati in `admin.py` e esportati da `models/__init__.py`
   - Migrazione Django creata e applicabile

2. **Endpoint Like Video** — `POST /api/videos/{id}/like/` crea un VideoLike (FR28)
   - Secondo like dallo stesso utente → errore 409 (IntegrityError → `{code, detail}`)
   - `DELETE /api/videos/{id}/like/` rimuove il VideoLike (unlike)

3. **Endpoint Like Commento** — `POST /api/comments/{id}/like/` crea un CommentLike (FR27)
   - Secondo like dallo stesso utente → errore 409
   - `DELETE /api/comments/{id}/like/` rimuove il CommentLike (unlike)

4. **Annotazioni VideoOutputSerializer** — include `like_count` (intero, annotazione `Count`) e `is_liked_by_me` (booleano, `Exists` relativo all'utente autenticato)

5. **Annotazioni CommentSerializer (output)** — include `like_count` (intero) e `is_liked_by_me` (booleano)

6. **Test completi** — copertura modelli, endpoint like/unlike, errore duplicato 409, annotazioni like_count/is_liked_by_me nei serializer

## Tasks / Subtasks

- [x] Task 1: Creare modello VideoLike (AC: #1)
  - [x] 1.1 File `cs_clips/models/video_like.py` con FK user (get_user_model), FK video, created_at, unique_together, related_name, help_text italiano, on_delete CASCADE
  - [x] 1.2 Export in `cs_clips/models/__init__.py`
  - [x] 1.3 Registrare in `cs_clips/admin.py` (pattern: list_display con user, video, created_at)

- [x] Task 2: Creare modello CommentLike (AC: #1)
  - [x] 2.1 File `cs_clips/models/comment_like.py` con FK user (get_user_model), FK comment, created_at, unique_together, related_name, help_text italiano, on_delete CASCADE
  - [x] 2.2 Export in `cs_clips/models/__init__.py`
  - [x] 2.3 Registrare in `cs_clips/admin.py`

- [x] Task 3: Migrazione Django (AC: #1)
  - [x] 3.1 `python manage.py makemigrations` — genera migrazione per VideoLike e CommentLike
  - [x] 3.2 Verificare migrazione generata (FK, unique_together, related_name)

- [x] Task 4: Endpoint like/unlike su VideoViewSet (AC: #2)
  - [x] 4.1 `@action(detail=True, methods=["post", "delete"], url_path="like")` → crea VideoLike, ritorna 201
  - [x] 4.2 DELETE → elimina VideoLike, ritorna 204
  - [x] 4.3 `@extend_schema` sull'action
  - [x] 4.4 IntegrityError su like duplicato → 409 gestito dall'error handler centralizzato

- [x] Task 5: Endpoint like/unlike su CommentViewSet (AC: #3)
  - [x] 5.1 `@action(detail=True, methods=["post", "delete"], url_path="like")` → crea CommentLike, ritorna 201
  - [x] 5.2 DELETE → elimina CommentLike, ritorna 204
  - [x] 5.3 `@extend_schema` sull'action
  - [x] 5.4 IntegrityError su like duplicato → 409

- [x] Task 6: Annotazioni like_count e is_liked_by_me su VideoOutputSerializer (AC: #4)
  - [x] 6.1 In `VideoViewSet.get_queryset()`: aggiunto `Count('likes', distinct=True)` per like_count
  - [x] 6.2 Per utenti autenticati: `Exists(VideoLike.objects.filter(...))` per is_liked_by_me
  - [x] 6.3 Per utenti anonimi (SSR retrieve): `Value(False)` per is_liked_by_me
  - [x] 6.4 Campi `like_count` e `is_liked_by_me` come `read_only_fields` nel VideoOutputSerializer

- [x] Task 7: Annotazioni like_count e is_liked_by_me su CommentSerializer (AC: #5)
  - [x] 7.1 In `CommentViewSet.get_queryset()`: aggiunto `Count('likes', distinct=True)` per like_count
  - [x] 7.2 `Exists(CommentLike.objects.filter(...))` per is_liked_by_me
  - [x] 7.3 Gestito utente non autenticato con `Value(False)`
  - [x] 7.4 Campi `like_count` e `is_liked_by_me` come `read_only_fields` nel CommentSerializer

- [x] Task 8: Test (AC: #6)
  - [x] 8.1 File `cs_clips/tests/test_likes.py`
  - [x] 8.2 Test creazione VideoLike (POST 201)
  - [x] 8.3 Test like duplicato VideoLike (POST 409)
  - [x] 8.4 Test unlike VideoLike (DELETE 204)
  - [x] 8.5 Test unlike inesistente VideoLike (DELETE 404)
  - [x] 8.6 Test creazione CommentLike (POST 201)
  - [x] 8.7 Test like duplicato CommentLike (POST 409)
  - [x] 8.8 Test unlike CommentLike (DELETE 204)
  - [x] 8.9 Test unlike inesistente CommentLike (DELETE 404)
  - [x] 8.10 Test annotazione like_count e is_liked_by_me su video detail
  - [x] 8.11 Test annotazione like_count e is_liked_by_me su comment list
  - [x] 8.12 Test permessi: utente toconfirm non può fare like (RoleBasedPermission)
  - [x] 8.13 Test like su video/commento inesistente → 404

- [x] Task 9: Verifica qualità (AC: tutti)
  - [x] 9.1 `ruff check backend/` — 0 errori
  - [x] 9.2 `ruff format backend/` — 0 diff
  - [x] 9.3 `python manage.py test` — 176 test, 175 OK, 1 fallimento pre-esistente (test_registration_assigns_toconfirm_group — non correlato a questa story)

- [x] Task 10: Review follow-ups (AI Code Review)
  - [x] 10.1 Test 409 duplicato: aggiunto assert su `response.data["code"]` e `response.data["detail"]` (M1)
  - [x] 10.2 Test cascade delete CommentLike: aggiunto `test_cascade_delete_comment` (M2)
  - [x] 10.3 Test annotazioni utente anonimo: aggiunto `AnonymousUserAnnotationTest` per SSR retrieve (M3)

## Dev Notes

### Architettura e Pattern Obbligatori

- **Struttura file modelli**: un file per modello in `cs_clips/models/` — `video_like.py`, `comment_like.py`. Export barrel in `__init__.py`
- **FK User**: SEMPRE `get_user_model()`, MAI `from django.contrib.auth.models import User` [Source: project-context.md#Custom-User-Model]
- **on_delete**: `CASCADE` — se l'utente, il video o il commento vengono eliminati, i like vengono rimossi
- **related_name**: `likes` su FK video/comment, coerente con pattern `ratings` e `comments` esistenti. Per FK user: `video_likes`/`comment_likes` per evitare clash con altri modelli
- **help_text**: in italiano su ogni campo [Source: project-context.md#Lingua]
- **unique_together**: enforza un like per utente per video/commento a livello DB

### Pattern @action per Like/Unlike

Gli endpoint like/unlike sono `@action(detail=True)` sul ViewSet esistente (NON un ViewSet separato):
- `POST /api/videos/{id}/like/` → `@action(detail=True, methods=["post"], url_path="like")`
- `DELETE /api/videos/{id}/like/` → stessa action con methods `["delete"]`, oppure action separata

**Attenzione**: DRF `@action` supporta `methods=["post", "delete"]` nella stessa action. Usare `self.request.method` per differenziare il comportamento (come il pattern follow/unfollow su UserViewSet).

**Pattern di implementazione** (basato su follow/unfollow esistente in `user_views.py`):
```python
@extend_schema(request=None, responses={201: None, 409: ErrorResponseSerializer})
@action(detail=True, methods=["post"], url_path="like", permission_classes=[IsAuthenticated, OnlyUsersPermission])
def like(self, request, pk=None):
    """Mette like a un video."""
    video = self.get_object()
    VideoLike.objects.create(user=request.user, video=video)
    return Response({"detail": "Like aggiunto."}, status=status.HTTP_201_CREATED)

@extend_schema(request=None, responses={204: None, 404: ErrorResponseSerializer})
@action(detail=True, methods=["delete"], url_path="like", permission_classes=[IsAuthenticated, OnlyUsersPermission])
def unlike(self, request, pk=None):
    """Rimuove il like da un video."""
    video = self.get_object()
    deleted, _ = VideoLike.objects.filter(user=request.user, video=video).delete()
    if not deleted:
        raise NotFound("Like non trovato.")
    return Response(status=status.HTTP_204_NO_CONTENT)
```

**ATTENZIONE URL CONFLICT**: DRF non può avere due `@action` con lo stesso `url_path="like"` ma metodi diversi. La soluzione è **una sola action con methods=["post", "delete"]** e branching interno:
```python
@action(detail=True, methods=["post", "delete"], url_path="like")
def like(self, request, pk=None):
    video = self.get_object()
    if request.method == "POST":
        # crea like
    elif request.method == "DELETE":
        # rimuovi like
```

### Pattern Annotazioni (da VideoViewSet esistente)

Il `get_queryset()` di VideoViewSet già usa annotazioni per `avg_rating`, `my_rating_id`, `my_rating_value`. Aggiungere like_count e is_liked_by_me seguendo lo stesso pattern:

```python
# In get_queryset():
queryset = queryset.annotate(
    like_count=Count("likes", distinct=True),
)
if self.request.user.is_authenticated:
    queryset = queryset.annotate(
        is_liked_by_me=Exists(
            VideoLike.objects.filter(video=OuterRef("pk"), user=self.request.user)
        ),
    )
else:
    queryset = queryset.annotate(is_liked_by_me=Value(False))
```

**Lezione Epic 1+2**: `Count(distinct=True)` per evitare moltiplicazione con altri join (ratings, comments). `Exists()` è più efficiente di `Count > 0` per booleani. [Source: MEMORY.md#Epic-1+2-Retro]

### CommentViewSet — Attenzione alla querybase filtrata

`CommentViewSet.get_queryset()` attualmente ritorna `Comment.objects.filter(is_disabled=False)`. Le annotazioni devono essere aggiunte alla queryset filtrata. Verificare che `CommentViewSet` non sovrascriva `get_queryset()` in modo incompatibile.

### Error Handling — IntegrityError 409

L'error handler centralizzato (`cs_clips/exceptions/error_handler.py`) mappa `IntegrityError → 409` con formato `{code, detail}`. **NON serve** catturare `IntegrityError` manualmente nelle action — il sistema centralizzato lo gestisce automaticamente. [Source: project-context.md#Error-Handling-Centralizzato]

### Permessi

- Like/unlike richiedono `IsAuthenticated` + `OnlyUsersPermission` (utenti nel gruppo `user`, NON `toconfirm`)
- Il `RoleBasedPermission` globale già protegge il ViewSet — le action ereditano i permessi del ViewSet
- Se necessario override specifico: `permission_classes` nel decorator `@action`

### Test — conftest.py helpers disponibili

Usare i seguenti helper esistenti in `cs_clips/tests/conftest.py`:
- `create_authenticated_user(username, password)` — utente con gruppo "user"
- `create_toconfirm_user()` — utente read-only
- `create_api_client_authenticated(user)` — APIClient con force_authenticate
- `create_sample_video(uploader, title, tag)` — Video con file (richiede MinIO)

**Pattern test assertioni** (lezione Epic 1+2):
- Verificare status code + formato risposta + contenuto specifico
- Per 409: verificare `response.data["code"]` e `response.data["detail"]`
- Per annotazioni: verificare presenza campi `like_count` e `is_liked_by_me` nella risposta serializzata

### Frontend — Nessuna modifica in questa story

I tipi TypeScript `Video` e `Comment` attualmente **NON** hanno `like_count` e `is_liked_by_me`. Questi campi verranno aggiunti nella Story 3.2 (UI Like Frontend). Il backend ritorna i campi aggiuntivi — il frontend li ignora fino alla Story 3.2.

### Project Structure Notes

- **Nuovi file backend**: `cs_clips/models/video_like.py`, `cs_clips/models/comment_like.py`, `cs_clips/tests/test_likes.py`
- **File modificati backend**: `cs_clips/models/__init__.py`, `cs_clips/admin.py`, `cs_clips/api/videos/video_views.py`, `cs_clips/api/videos/video_serializers.py`, `cs_clips/api/comments/comment_views.py`, `cs_clips/api/comments/comment_serializers.py`
- **Nessun file frontend modificato** — story backend-only
- Allineamento con struttura progetto: `cs_clips/models/` (1 file/modello), `cs_clips/api/{dominio}/` (views+serializers per dominio)
- Nessun conflitto con struttura esistente

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic-3-Story-3.1] — Acceptance criteria BDD completi
- [Source: _bmad-output/planning-artifacts/architecture.md#Implementation-Patterns] — Checklist creazione modello, pattern @action, annotazioni
- [Source: _bmad-output/project-context.md#Struttura-Backend-Modulare] — Struttura file e naming
- [Source: _bmad-output/project-context.md#Error-Handling-Centralizzato] — IntegrityError → 409 automatico
- [Source: _bmad-output/project-context.md#Custom-User-Model] — get_user_model() obbligatorio
- [Source: _bmad-output/project-context.md#Pattern-Serializer] — read_only_fields, perform_create
- [Source: _bmad-output/project-context.md#Regole-Testing] — APITestCase, force_authenticate, PostgreSQL+MinIO
- [Source: _bmad-output/implementation-artifacts/epic-intermedio-retro-2026-03-02.md] — Dipendenze Epic 3 soddisfatte, debito tecnico noto
- [Source: MEMORY.md#Epic-1+2-Retro] — Count(distinct=True), Exists(), test assertions complete, read_only_fields espliciti

### Git Intelligence — Pattern Recenti

Ultimi commit rilevanti:
- `798d229` — snap scroll feed + clip detail view modes (Epic Intermedio finale)
- `32dbc0f` — Epic 2 stories 2.2-2.5 + Epic Intermedio (card-as-player, download, commenti, delete, rating update)
- `8d20865` — Story 2.1 upload clip con validazione completa e allow_download

Pattern osservati: commit granulari per story, prefisso `feat:` per feature, riepilogo conciso nel titolo.

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Migrazione 0007: tabelle già esistenti nel DB dev (probabilmente da branch precedente) → risolto con `migrate --fake`
- Test pre-esistente `test_registration_assigns_toconfirm_group` fallisce perché il gruppo `toconfirm` non viene creato tramite data migration nel DB di test → non correlato a questa story

### Completion Notes List

- Creati modelli VideoLike e CommentLike con FK user (get_user_model), FK video/comment, unique_together, CASCADE, help_text italiano
- Implementata singola `@action(methods=["post", "delete"], url_path="like")` su VideoViewSet e CommentViewSet (evita URL conflict DRF)
- IntegrityError su like duplicato gestita automaticamente dall'error handler centralizzato → 409
- Annotazioni `like_count` (Count distinct) e `is_liked_by_me` (Exists) aggiunte a get_queryset() di VideoViewSet e CommentViewSet
- Utenti anonimi (SSR) ricevono `is_liked_by_me=False` via Value(False)
- 21 test nuovi in test_likes.py: modelli, endpoint CRUD, annotazioni, permessi
- Aggiornato test_upload_validation.py per includere nuovi campi expected nella response shape
- ruff check 0 errori, ruff format 0 diff

### File List

**Nuovi file:**
- `backend/cs_clips/models/video_like.py` — Modello VideoLike
- `backend/cs_clips/models/comment_like.py` — Modello CommentLike
- `backend/cs_clips/migrations/0007_commentlike_videolike.py` — Migrazione
- `backend/cs_clips/tests/test_likes.py` — 21 test

**File modificati:**
- `backend/cs_clips/models/__init__.py` — Export VideoLike, CommentLike
- `backend/cs_clips/admin.py` — Registrazione VideoLikeAdmin, CommentLikeAdmin
- `backend/cs_clips/api/videos/video_views.py` — Action like, annotazioni get_queryset
- `backend/cs_clips/api/videos/video_serializers.py` — Campi like_count, is_liked_by_me
- `backend/cs_clips/api/comments/comment_views.py` — Action like, get_queryset con annotazioni
- `backend/cs_clips/api/comments/comment_serializers.py` — Campi like_count, is_liked_by_me
- `backend/cs_clips/tests/test_upload_validation.py` — Aggiunto like_count, is_liked_by_me ai campi attesi

## Change Log

- **2026-03-08** — Story 3.1: Modelli VideoLike e CommentLike con endpoint like/unlike, annotazioni like_count/is_liked_by_me, 21 test
- **2026-03-08** — Code Review: 3 MEDIUM fix (409 body assertions, cascade delete CommentLike, anonymous annotation test) → 23 test totali
