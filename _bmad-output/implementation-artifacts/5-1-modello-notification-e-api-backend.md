# Story 5.1: Modello Notification e API Backend

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a sviluppatore,
I want il modello Notification con endpoint REST e creazione automatica per eventi chiave,
So that il sistema può tracciare e servire notifiche agli utenti.

## Acceptance Criteria

1. **Given** il modello `Notification` non esistente
   **When** viene creato in `cs_clips/models/notification.py`
   **Then** ha campi: `recipient` (FK User), `sender` (FK User nullable), `type` (CharField choices: comment_received, like_received, comment_promoted, contest_opened, bracket_invite, bracket_turn, contest_results), `is_read` (BooleanField default False), `created_at` (DateTimeField auto_now_add), `video` (FK nullable), `comment` (FK nullable), `contest` (FK nullable) (D1)
   **And** NON usa `GenericForeignKey`
   **And** ha `related_name` su ogni FK e `help_text` in italiano
   **And** è registrato in `admin.py` e esportato da `models/__init__.py`

2. **Given** un utente autenticato
   **When** chiama `GET /api/notifications/`
   **Then** riceve la lista paginata delle proprie notifiche ordinate per `-created_at` (FR51)

3. **Given** un utente autenticato
   **When** chiama `GET /api/notifications/unread-count/`
   **Then** riceve `{"count": N}` con il numero di notifiche non lette (FR52)

4. **Given** un utente autenticato
   **When** chiama `POST /api/notifications/{id}/mark-read/`
   **Then** la notifica viene marcata come letta (`is_read=True`)

5. **Given** un utente autenticato
   **When** chiama `POST /api/notifications/mark-all-read/`
   **Then** tutte le notifiche non lette vengono marcate come lette

6. **Given** un evento che genera notifica (commento ricevuto, like su clip, like su commento, commento promosso a popup, contest aperto)
   **When** l'evento si verifica
   **Then** una `Notification` viene creata automaticamente per il destinatario (FR50)
   **And** NON vengono create notifiche self-referenziali (sender == recipient)

## Tasks / Subtasks

- [x] Task 1: Modello Notification (AC: #1)
  - [x] 1.1 Creare `backend/cs_clips/models/notification.py` con modello `Notification`
  - [x] 1.2 Aggiungere export in `backend/cs_clips/models/__init__.py`
  - [x] 1.3 Creare e applicare migrazione: `python manage.py makemigrations` + `migrate`
  - [x] 1.4 Registrare `NotificationAdmin` in `admin.py` con list_display, list_filter, search_fields

- [x] Task 2: API Notifications — ViewSet e routing (AC: #2, #3, #4, #5)
  - [x] 2.1 Creare `backend/cs_clips/api/notifications/notification_serializers.py` con `NotificationSerializer`
  - [x] 2.2 Creare `backend/cs_clips/api/notifications/notification_views.py` con `NotificationViewSet`
  - [x] 2.3 Registrare in `cs_clips/urls.py`: `router.register(r"notifications", NotificationViewSet, basename="notification")`
  - [x] 2.4 `list` action: filtra per `recipient=request.user`, ordina per `-created_at`
  - [x] 2.5 `@action unread-count`: `GET` ritorna `{"count": N}` con `filter(is_read=False).count()`
  - [x] 2.6 `@action mark-read`: `POST` su singola notifica, verifica ownership
  - [x] 2.7 `@action mark-all-read`: `POST` aggiorna in bulk `filter(recipient=request.user, is_read=False)`

- [x] Task 3: Creazione automatica notifiche — helper + signal integration (AC: #6)
  - [x] 3.1 Creare `backend/cs_clips/utils/notification_helpers.py` con funzione `create_notification(recipient, sender, type, video=None, comment=None, contest=None)` che skippa se sender==recipient
  - [x] 3.2 Aggiungere creazione notifica `comment_received` in `CommentViewSet.perform_create()` — notifica al proprietario del video
  - [x] 3.3 Aggiungere creazione notifica `like_received` in `VideoViewSet.like()` (POST) — notifica al proprietario del video
  - [x] 3.4 Aggiungere creazione notifica `like_received` in `CommentViewSet.like()` (POST) — notifica al proprietario del commento
  - [x] 3.5 Aggiungere creazione notifica `contest_opened` — in `get_or_create_current_contest()` quando un nuovo contest viene creato, notifica a TUTTI gli utenti del gruppo 'user' (bulk create)

- [x] Task 4: Test backend (AC: tutti)
  - [x] 4.1 Creare `backend/cs_clips/tests/test_notifications.py`
  - [x] 4.2 Test modello: creazione Notification con tutti i campi, __str__, ordering
  - [x] 4.3 Test API: GET /api/notifications/ ritorna solo notifiche del richiedente (non di altri utenti)
  - [x] 4.4 Test API: GET /api/notifications/ paginazione e ordinamento -created_at
  - [x] 4.5 Test API: GET /api/notifications/unread-count/ ritorna conteggio corretto
  - [x] 4.6 Test API: POST /api/notifications/{id}/mark-read/ marca come letta
  - [x] 4.7 Test API: POST /api/notifications/{id}/mark-read/ non permette di marcare notifiche altrui (403 o 404)
  - [x] 4.8 Test API: POST /api/notifications/mark-all-read/ marca tutte come lette
  - [x] 4.9 Test auto-creazione: commento su video di altro utente crea notifica comment_received
  - [x] 4.10 Test auto-creazione: like su video di altro utente crea notifica like_received
  - [x] 4.11 Test auto-creazione: commento su PROPRIO video NON crea notifica (self-skip)
  - [x] 4.12 Test utente non autenticato riceve 401

- [x] Task 5: Verifica qualità (AC: tutti)
  - [x] 5.1 `ruff check backend/` — 0 errori
  - [x] 5.2 `ruff format --check backend/` — 0 errori
  - [x] 5.3 `python manage.py test` — tutti i test passano (nessuna regressione + nuovi test)
  - [x] 5.4 Verifica che il frontend compili senza errori: `npm run build`

## Dev Notes

### Stato attuale — Cosa esiste già

**Modelli esistenti (7):** User, Video, Contest, Rating, Comment, VideoLike, CommentLike
**Modelli da creare (1):** Notification

**Dominio API da creare:** `cs_clips/api/notifications/` con `notification_views.py` + `notification_serializers.py`

**Pattern di riferimento diretto** — Il modello Notification segue esattamente il pattern dei modelli Like (VideoLike, CommentLike):
- FK esplicite (no GenericFK), `related_name`, `help_text` in italiano
- `unique_together` NON necessario per Notification (un utente può ricevere più notifiche dello stesso tipo)
- `ordering = ["-created_at"]` come standard

### Modello Notification — Specifiche dettagliate

```python
# backend/cs_clips/models/notification.py
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Notification(models.Model):
    class Type(models.TextChoices):
        COMMENT_RECEIVED = "comment_received", "Commento ricevuto"
        LIKE_RECEIVED = "like_received", "Like ricevuto"
        COMMENT_PROMOTED = "comment_promoted", "Commento promosso a popup"
        CONTEST_OPENED = "contest_opened", "Nuovo contest aperto"
        BRACKET_INVITE = "bracket_invite", "Invito bracket"
        BRACKET_TURN = "bracket_turn", "Turno bracket disponibile"
        CONTEST_RESULTS = "contest_results", "Risultati contest"

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="Utente che riceve la notifica",
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
        null=True,
        blank=True,
        help_text="Utente che ha generato l'evento (null per eventi di sistema)",
    )
    type = models.CharField(
        max_length=30,
        choices=Type.choices,
        help_text="Tipo di notifica",
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Se la notifica è stata letta",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e ora di creazione",
    )
    video = models.ForeignKey(
        "Video",
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
        help_text="Video collegato alla notifica (opzionale)",
    )
    comment = models.ForeignKey(
        "Comment",
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
        help_text="Commento collegato alla notifica (opzionale)",
    )
    contest = models.ForeignKey(
        "Contest",
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
        help_text="Contest collegato alla notifica (opzionale)",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notifica"
        verbose_name_plural = "Notifiche"
        indexes = [
            models.Index(
                fields=["recipient", "-created_at"],
                name="idx_notification_recipient_date",
            ),
            models.Index(
                fields=["recipient", "is_read"],
                name="idx_notification_recipient_read",
            ),
        ]

    def __str__(self):
        return f"[{self.get_type_display()}] → {self.recipient.username}"
```

### NotificationViewSet — Specifiche dettagliate

```python
# Pattern: ModelViewSet con queryset filtrato per recipient=request.user
# http_method_names: ["get", "post", "head", "options"] — NO PUT, PATCH, DELETE
# Le notifiche sono create automaticamente e non possono essere modificate/cancellate dall'utente

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    # list → paginato, -created_at (dal Meta del modello)
    # create → DISABILITATO (override create che ritorna 405)

    # @action unread-count → GET, detail=False
    # @action mark-read → POST, detail=True
    # @action mark-all-read → POST, detail=False
```

**ATTENZIONE — Ownership check per mark-read**: l'azione `mark-read` su singola notifica DEVE verificare che la notifica appartenga al `request.user`. Il `get_queryset()` filtrato per `recipient` garantisce che `self.get_object()` ritorna 404 per notifiche altrui — pattern analogo a altri ViewSet. NON serve un check esplicito.

### NotificationSerializer — Specifiche

```python
class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source="sender.username")
    video_title = serializers.ReadOnlyField(source="video.title")
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "sender",
            "sender_username",
            "type",
            "type_display",
            "is_read",
            "created_at",
            "video",
            "video_title",
            "comment",
            "contest",
        ]
        read_only_fields = [
            "id", "recipient", "sender", "sender_username",
            "type", "type_display", "is_read", "created_at",
            "video", "video_title", "comment", "contest",
        ]
```

### Helper create_notification — Specifiche

```python
# backend/cs_clips/utils/notification_helpers.py

def create_notification(recipient, sender=None, type=None, video=None, comment=None, contest=None):
    """Crea una notifica, skippando se sender == recipient (no self-notification)."""
    if sender and sender == recipient:
        return None
    from cs_clips.models import Notification
    return Notification.objects.create(
        recipient=recipient,
        sender=sender,
        type=type,
        video=video,
        comment=comment,
        contest=contest,
    )
```

### Punti di integrazione — Dove aggiungere chiamate

| Evento | File da modificare | Punto di inserimento | Tipo notifica | Destinatario |
|--------|-------------------|---------------------|---------------|-------------|
| Nuovo commento su video | `comment_views.py` | `perform_create()` dopo `serializer.save()` | `comment_received` | `video.uploader` |
| Like su video | `video_views.py` | `like()` nel ramo POST, dopo `VideoLike.objects.create()` | `like_received` | `video.uploader` |
| Like su commento | `comment_views.py` | `like()` nel ramo POST, dopo `CommentLike.objects.create()` | `like_received` | `comment.user` |
| Nuovo contest creato | `get_date_util.py` | in `get_or_create_current_contest()` se `created=True` | `contest_opened` | Tutti utenti gruppo 'user' |

**NOTA su contest_opened**: per la notifica `contest_opened` serve un bulk create. Pattern:
```python
from django.contrib.auth.models import Group
users = Group.objects.get(name="user").user_set.all()
Notification.objects.bulk_create([
    Notification(recipient=u, type=Notification.Type.CONTEST_OPENED, contest=contest)
    for u in users
])
```

**NOTA su comment_promoted**: la promozione di un commento a popup NON è un evento discreto nel codebase attuale — è un calcolo on-the-fly in `popup_comments()`. Per ora NON implementare `comment_promoted`. Se necessario, sarà un'evoluzione futura.

### Anti-pattern da evitare

1. **NON usare `GenericForeignKey`** — FK esplicite per video, comment, contest (come specificato in D1)
2. **NON usare Django signals (post_save)** per creare notifiche — inserire la logica direttamente nelle views. I signals sono impliciti, difficili da debuggare, e non hanno accesso al `request.user` senza workaround
3. **NON creare notifiche self-referenziali** — se l'utente commenta il proprio video o mette like al proprio contenuto, non creare notifica
4. **NON usare Celery/Redis** per inviare notifiche — non sono configurati. Le notifiche vengono create sincrono, il frontend le recupera via polling (Story 5.2)
5. **NON creare `notification_urls.py`** — il routing passa SOLO da `cs_clips/urls.py` (pattern stabilito dalla Story 4.1 che ha eliminato `contest_urls.py`)
6. **NON importare `User` da `django.contrib.auth.models`** — SEMPRE `from django.contrib.auth import get_user_model`
7. **NON ritornare array raw** — sempre formato paginato Django `{count, next, previous, results}`
8. **NON fare `Notification.objects.filter(recipient=user).update(is_read=True)` senza constraint** — usare `filter(is_read=False)` per efficienza

### Rischi e edge case

1. **Notifica per like su video senza uploader**: impossibile per FK CASCADE — se il video esiste, l'uploader esiste
2. **Contest opened a MOLTI utenti**: `bulk_create` è efficiente ma potrebbe generare molte righe. Per MVP con <50 utenti non è un problema. Monitorare se il numero cresce
3. **Commento su video di utente cancellato**: CASCADE sulle FK gestisce automaticamente — il video non esiste più, il commento non può essere creato
4. **Notifica duplicata per like toggle veloce**: `VideoLike` ha `unique_together` — non è possibile creare due like sullo stesso video. La notifica viene creata solo al POST, non al DELETE+POST
5. **`get_or_create_current_contest` chiamata in contesto serializer**: la funzione è già usata in `VideoViewSet.perform_create()` — l'aggiunta della notifica qui è sicura
6. **Ordering del queryset**: `-created_at` nel `Meta.ordering` garantisce l'ordine anche senza `order_by()` esplicito nel ViewSet

### Decisione architetturale D1 — Polling REST (NON real-time)

La PRD specifica esplicitamente "nessun real-time, fetch-based". La Story 5.2 implementerà il polling frontend con `refetchInterval: 15000` (15 secondi). Questa story backend fornisce solo gli endpoint REST. Non installare Django Channels, non configurare WebSocket.

### Project Structure Notes

**File da creare:**
- `backend/cs_clips/models/notification.py` — modello Notification
- `backend/cs_clips/api/notifications/notification_views.py` — NotificationViewSet
- `backend/cs_clips/api/notifications/notification_serializers.py` — NotificationSerializer
- `backend/cs_clips/api/notifications/__init__.py` — package init
- `backend/cs_clips/utils/notification_helpers.py` — helper create_notification
- `backend/cs_clips/tests/test_notifications.py` — test suite

**File da modificare:**
- `backend/cs_clips/models/__init__.py` — aggiungere export Notification
- `backend/cs_clips/admin.py` — aggiungere NotificationAdmin
- `backend/cs_clips/urls.py` — registrare notifications nel router
- `backend/cs_clips/api/comments/comment_views.py` — aggiungere notifica in `perform_create()` e `like()` POST
- `backend/cs_clips/api/videos/video_views.py` — aggiungere notifica in `like()` POST
- `backend/cs_clips/utils/get_date_util.py` — aggiungere notifica `contest_opened` se nuovo contest creato

**File da NON toccare:**
- `backend/cs_clips/api/contests/contest_views.py` — nessuna modifica necessaria
- Frontend — scope solo backend per questa story

### Intelligence dalla Story 4.2 (precedente)

- **221 test backend** baseline (220 pass, 1 fail pre-esistente `test_registration_assigns_toconfirm_group`)
- **`@extend_schema`** obbligatorio su ogni action per OpenAPI
- **`select_related()`** su FK per N+1 prevention — applicare su `sender` e `video` nel queryset notifiche
- **Dead code cleanup**: `contest_urls.py` eliminato — pattern confermato: NO file urls separati
- **Pattern Code review**: H1 select_related, H2 N+1 prevention — anticipare in questa story
- **Scelta architetturale confermata**: inline mutation nel ViewSet (non in hooks condivisi) — applicare lo stesso pattern per create_notification inline nelle views

### Git Intelligence — Pattern recenti

Ultimi commit:
- `612f66c` — Epic 3 completo: like UI, popup overlay, spareggio like, comment markers

Pattern commit: prefisso `feat:` per feature, riepilogo conciso.
Suggerito: `feat: Story 5.1 — modello Notification + API backend + auto-creazione notifiche`

### Performance Considerations

- **Index composto `(recipient, -created_at)`**: query principale del frontend (lista notifiche per utente, ordinate per data)
- **Index composto `(recipient, is_read)`**: per conteggio unread-count efficiente
- **`select_related("sender", "video")`** nel queryset: evita N+1 sulla lista notifiche (serializer usa `sender.username` e `video.title`)
- **`bulk_create` per contest_opened**: evita N query INSERT separate

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-5.1] — AC BDD: modello Notification, API REST, auto-creazione
- [Source: _bmad-output/planning-artifacts/epics.md#Epic-5] — FRs: FR50, FR51, FR52, D1
- [Source: _bmad-output/planning-artifacts/architecture.md#Real-time-Notifiche] — Decisione D1: polling REST, NO WebSocket
- [Source: _bmad-output/planning-artifacts/architecture.md#Gap-Backend] — Modello Notification mancante, 7 tipi
- [Source: _bmad-output/project-context.md#Struttura-Backend-Modulare] — Pattern `api/{dominio}/`, 1 file per modello
- [Source: _bmad-output/project-context.md#Custom-User-Model] — `get_user_model()` obbligatorio
- [Source: _bmad-output/project-context.md#Anti-Pattern] — No Celery, no GenericFK, no array raw
- [Source: backend/cs_clips/models/video_like.py] — Pattern modello Like (FK esplicite, related_name, help_text)
- [Source: backend/cs_clips/models/comment_like.py] — Pattern analogo
- [Source: backend/cs_clips/api/comments/comment_views.py] — perform_create(), like() — punti di integrazione
- [Source: backend/cs_clips/api/videos/video_views.py] — like() — punto di integrazione
- [Source: backend/cs_clips/utils/get_date_util.py] — get_or_create_current_contest() — punto di integrazione
- [Source: backend/cs_clips/tests/conftest.py] — Helper test: create_authenticated_user, create_sample_video, create_sample_contest
- [Source: _bmad-output/implementation-artifacts/4-2-votazione-contest-e-classifica-frontend.md] — Story precedente: pattern, learnings

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Index name troppo lungo (>30 char): rinominati `idx_notification_recipient_date` → `idx_notif_recipient_date` e analogo per `_read`
- Tabella `cs_clips_notification` già presente in DB da tentativo precedente: drop + re-migrate
- Custom User model usa `related_name="custom_user_set"` su groups: corretto `user_group.user_set.all()` → `User.objects.filter(groups=user_group)` in `get_date_util.py`

### Completion Notes List

- ✅ Modello Notification con 7 tipi, FK esplicite (no GenericFK), related_name, help_text in italiano, 2 indici composti
- ✅ NotificationViewSet con list (paginato, -created_at), unread-count, mark-read, mark-all-read, create disabilitato (405)
- ✅ NotificationSerializer con sender_username, video_title, type_display — tutti read_only
- ✅ select_related("sender", "video") per N+1 prevention
- ✅ Helper create_notification con self-skip (sender == recipient)
- ✅ Auto-creazione: comment_received, like_received (video+commento), contest_opened (bulk_create)
- ✅ @extend_schema su ogni action per OpenAPI
- ✅ 15 test nuovi, tutti passanti. 236 test totali, 1 solo fail pre-esistente (test_registration_assigns_toconfirm_group)
- ✅ ruff check + ruff format: 0 errori. Frontend build: OK

### Implementation Plan

Implementazione diretta dal dev notes della story — modello esatto come da specifica, ViewSet con queryset filtrato per recipient, helper inline nelle views (no signals), bulk_create per contest_opened.

### File List

**File creati:**
- `backend/cs_clips/models/notification.py`
- `backend/cs_clips/api/notifications/__init__.py`
- `backend/cs_clips/api/notifications/notification_serializers.py`
- `backend/cs_clips/api/notifications/notification_views.py`
- `backend/cs_clips/utils/notification_helpers.py`
- `backend/cs_clips/tests/test_notifications.py`
- `backend/cs_clips/migrations/0008_notification.py`

**File modificati:**
- `backend/cs_clips/models/__init__.py` — export Notification
- `backend/cs_clips/admin.py` — NotificationAdmin
- `backend/cs_clips/urls.py` — router.register notifications
- `backend/cs_clips/api/comments/comment_views.py` — notifica in perform_create() e like()
- `backend/cs_clips/api/videos/video_views.py` — notifica in like()
- `backend/cs_clips/utils/get_date_util.py` — notifica contest_opened in get_or_create_current_contest()

## Change Log

- 2026-03-08: Story 5.1 implementata — modello Notification (8 modelli totali), API REST con 4 endpoint, auto-creazione notifiche per 4 eventi (comment_received, like_received video, like_received commento, contest_opened), 15 test backend
- 2026-03-08: Code review (AI) — 5 fix applicati: H1 test comment-like notification, H2 test contest_opened, M1 SET_NULL su FK nullable, M2 logging Group.DoesNotExist, M3 video=comment.video in like notif. 240 test (1 fail pre-esistente), ruff 0 errori
