# Story 6.2: API Bracket e Votazione Matchup

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utente registrato,
I want iscrivermi a un bracket, votare nei matchup e visualizzare la progressione,
So that posso partecipare alla competizione Champions League e seguirne l'andamento.

## Acceptance Criteria

1. **Given** un utente autenticato e un bracket in stato "registration"
   **When** chiama `POST /api/brackets/{id}/enter/` con `{ "video_id": <int> }`
   **Then** viene creata una `ContestEntry(bracket, user, video)` e risponde 201
   **And** un'iscrizione duplicata (stesso bracket+user) ritorna 409 Conflict
   **And** un bracket non in stato "registration" ritorna 400
   **And** un bracket pieno (`entries.count() >= max_participants`) ritorna 400
   **And** viene creata una notifica `bracket_invite` per l'utente (conferma iscrizione)

2. **Given** un utente autenticato e un matchup attivo (non completato, entrambe le entry presenti)
   **When** chiama `POST /api/matchups/{id}/vote/` con `{ "entry": <entry_id>, "value": <1-5> }`
   **Then** viene creato un `MatchupVote(matchup, user, entry, value)` e risponde 201
   **And** un voto duplicato (stesso matchup+user) ritorna 409
   **And** `value` fuori range 1-5 ritorna 400
   **And** `entry` non appartenente al matchup ritorna 400
   **And** voto su matchup completato ritorna 400

3. **Given** un matchup con voti registrati
   **When** un admin chiama `POST /api/matchups/{id}/close/`
   **Then** il sistema calcola la media voti per entry e assegna il vincitore (media piu' alta)
   **And** in caso di parita' vince entry_1 (determinismo, nessun fattore esterno — FR43b)
   **And** il vincitore avanza automaticamente al turno successivo (`close_matchup` esistente)
   **And** viene creata una notifica `bracket_turn` per i partecipanti del prossimo matchup
   **And** se e' il turno finale, il bracket diventa "completed"

4. **Given** un utente (anche non autenticato)
   **When** chiama `GET /api/brackets/`
   **Then** riceve la lista paginata dei bracket (tutti gli stati)
   **And** filtro opzionale `?status=active` / `?status=registration` / `?status=completed`
   **And** ogni item include: id, name, description, status, max_participants, current_round, entries_count, created_by (username), created_at, prize_description

5. **Given** un utente (anche non autenticato)
   **When** chiama `GET /api/brackets/{id}/`
   **Then** riceve dettaglio bracket con matchup raggruppati per turno
   **And** ogni matchup include: id, round_number, position, entry_1 (user+video nested), entry_2 (user+video nested), winner, is_completed, avg_rating_1, avg_rating_2
   **And** include `my_entry` (la ContestEntry dell'utente corrente, se iscritto, null se non autenticato)
   **And** include `entries_count` (numero iscritti)

6. **Given** il dominio API separato (D2)
   **When** gli endpoint vengono creati
   **Then** risiedono in `cs_clips/api/brackets/` con views e serializers propri
   **And** i ViewSet sono registrati in `cs_clips/urls.py` sul router principale
   **And** `http_method_names` restrittivo su ogni ViewSet

7. **Given** i nuovi endpoint
   **When** vengono testati
   **Then** copertura completa: 201/400/404/409 per enter, vote, close + list/detail con annotazioni + permessi + notifiche

## Tasks / Subtasks

- [x] Task 1: Modello MatchupVote (AC: #2)
  - [x] 1.1 Creare `backend/cs_clips/models/matchup_vote.py` con modello `MatchupVote`:
    - `matchup` (FK Matchup CASCADE, related_name="votes")
    - `user` (FK User CASCADE, related_name="matchup_votes")
    - `entry` (FK ContestEntry CASCADE, related_name="received_votes") — l'entry votata
    - `value` (PositiveSmallIntegerField, validators MinValue(1) MaxValue(5))
    - `created_at` (DateTimeField auto_now_add)
    - `unique_together = ("matchup", "user")` — un voto per utente per matchup
    - `help_text` in italiano, `ordering = ["-created_at"]`
  - [x] 1.2 Aggiungere export in `backend/cs_clips/models/__init__.py`
  - [x] 1.3 Aggiungere `MatchupVoteAdmin` in `admin.py`: list_display, list_filter, autocomplete_fields
  - [x] 1.4 Creare migrazione: `python manage.py makemigrations`
  - [x] 1.5 Applicare migrazione: `python manage.py migrate`

- [x] Task 2: Serializers bracket (AC: #4, #5)
  - [x] 2.1 Creare `backend/cs_clips/api/brackets/__init__.py`
  - [x] 2.2 Creare `backend/cs_clips/api/brackets/bracket_serializers.py`:
    - `ContestEntryNestedSerializer` — user (id, username), video (id, title, thumbnail_url) read-only
    - `MatchupOutputSerializer` — tutti i campi + entry_1/entry_2 nested + avg_rating_1/avg_rating_2 annotati
    - `BracketListOutputSerializer` — campi base + entries_count annotato + created_by username
    - `BracketDetailOutputSerializer` — eredita list + matchups_by_round (SerializerMethodField raggruppati per round_number) + my_entry
    - `EnterBracketInputSerializer` — solo `video_id` (IntegerField)
    - `VoteMatchupInputSerializer` — `entry` (PrimaryKeyRelatedField) + `value` (IntegerField min 1 max 5)

- [x] Task 3: ViewSet BracketViewSet (AC: #1, #4, #5)
  - [x] 3.1 Creare `backend/cs_clips/api/brackets/bracket_views.py`
  - [x] 3.2 `BracketViewSet(ReadOnlyModelViewSet)`:
    - `http_method_names = ["get", "post", "head", "options"]`
    - `get_permissions()`: AllowAny per list/retrieve, IsAuthenticated per enter
    - `get_queryset()`: annotazione entries_count + select_related created_by
    - `get_serializer_class()`: list vs retrieve
    - `filterset_fields = ["status"]`
  - [x] 3.3 Custom action `enter`:
    - `@action(detail=True, methods=["post"], url_path="enter", permission_classes=[IsAuthenticated])`
    - Validazione: bracket.status == "registration", entries.count() < max_participants, video esiste
    - Creazione ContestEntry con IntegrityError catch per 409
    - Creazione Notification `bracket_invite` per l'utente iscritto
    - Risposta 201 con ContestEntryNestedSerializer

- [x] Task 4: ViewSet MatchupViewSet (AC: #2, #3)
  - [x] 4.1 Aggiungere `MatchupViewSet(mixins.RetrieveModelMixin, GenericViewSet)` in `bracket_views.py`
  - [x] 4.2 `http_method_names = ["get", "post", "head", "options"]`
  - [x] 4.3 `get_permissions()`: AllowAny per retrieve, IsAuthenticated per vote, OnlyAdminsPermission per close
  - [x] 4.4 `get_queryset()`: annotazione avg_rating_1/avg_rating_2 + select_related entry/user/video
  - [x] 4.5 Custom action `vote`:
    - `@action(detail=True, methods=["post"], url_path="vote", permission_classes=[IsAuthenticated])`
    - Validazione: matchup non completato, entry appartiene al matchup, value 1-5
    - `MatchupVote.objects.create()` con IntegrityError catch per 409
    - Risposta 201
  - [x] 4.6 Custom action `close`:
    - `@action(detail=True, methods=["post"], url_path="close", permission_classes=[OnlyAdminsPermission])`
    - Calcolo media voti per entry_1 e entry_2
    - Determinazione vincitore: media piu' alta; parita' → entry_1 vince
    - Chiamata `close_matchup(matchup, winner_entry)` da `bracket_logic.py`
    - Creazione Notification `bracket_turn` per partecipanti prossimo matchup
    - Risposta 200

- [x] Task 5: Registrazione URL (AC: #6)
  - [x] 5.1 In `backend/cs_clips/urls.py`:
    - Import `BracketViewSet, MatchupViewSet` da `cs_clips.api.brackets.bracket_views`
    - `router.register(r"brackets", BracketViewSet, basename="bracket")`
    - `router.register(r"matchups", MatchupViewSet, basename="matchup")`

- [x] Task 6: Test backend (AC: #7)
  - [x] 6.1 Creare `backend/cs_clips/tests/test_bracket_api.py`
  - [x] 6.2 Test list brackets: 200, paginazione, filtro status, entries_count annotato
  - [x] 6.3 Test detail bracket: 200, matchups_by_round raggruppati, my_entry per utente iscritto
  - [x] 6.4 Test detail bracket non autenticato: 200 (AllowAny), my_entry=null
  - [x] 6.5 Test enter bracket: 201, ContestEntry creata, notifica bracket_invite creata
  - [x] 6.6 Test enter bracket duplicato: 409
  - [x] 6.7 Test enter bracket non in registration: 400
  - [x] 6.8 Test enter bracket pieno: 400
  - [x] 6.9 Test vote matchup: 201, MatchupVote creato
  - [x] 6.10 Test vote matchup duplicato: 409
  - [x] 6.11 Test vote matchup completato: 400
  - [x] 6.12 Test vote entry non del matchup: 400
  - [x] 6.13 Test vote value fuori range: 400
  - [x] 6.14 Test close matchup (admin): 200, vincitore assegnato, avanzamento al turno successivo
  - [x] 6.15 Test close matchup (non admin): 403
  - [x] 6.16 Test close matchup finale: bracket diventa "completed"
  - [x] 6.17 Test notifica bracket_turn creata dopo close

- [x] Task 7: Verifica qualita' (AC: tutti)
  - [x] 7.1 `ruff check backend/` — 0 errori
  - [x] 7.2 `ruff format --check backend/` — 0 errori
  - [x] 7.3 `python manage.py test` — tutti i test passano (nessuna regressione)
  - [x] 7.4 `npm run build` — non necessario (nessuna modifica frontend)

## Dev Notes

### Stato attuale — Cosa esiste gia'

**Modelli esistenti (11):** User, Video, Contest, Rating, Comment, VideoLike, CommentLike, Notification, Bracket, ContestEntry, Matchup
**Modello da creare (1):** MatchupVote

**Logica bracket esistente (`utils/bracket_logic.py`):**
- `generate_bracket(bracket)` — genera matchup eliminazione diretta con bye (usata da admin action)
- `advance_winner(matchup)` — propaga vincitore al turno successivo
- `close_matchup(matchup, winner_entry)` — chiude matchup e chiama advance_winner

**Decisione architetturale D2:** Bracket completamente separato da Contest. Endpoint in `/api/brackets/` e `/api/matchups/`, NON sotto `/api/contests/`.

### Pattern di riferimento — Da seguire ESATTAMENTE

**ViewSet — Pattern ContestViewSet (ReadOnlyModelViewSet + custom actions):**
```python
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

class BracketViewSet(ReadOnlyModelViewSet):
    http_method_names = ["get", "post", "head", "options"]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Bracket.objects.annotate(
            entries_count=Count("entries", distinct=True),
        ).select_related("created_by")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BracketDetailOutputSerializer
        return BracketListOutputSerializer

    @action(detail=True, methods=["post"], url_path="enter")
    def enter(self, request, pk=None):
        # ...
```

**Serializer — Pattern Output/Input separati (read_only_fields espliciti):**
```python
class BracketListOutputSerializer(serializers.ModelSerializer):
    entries_count = serializers.IntegerField(read_only=True)
    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = Bracket
        fields = [
            "id", "name", "description", "status", "max_participants",
            "current_round", "entries_count", "created_by", "created_by_username",
            "created_at", "prize_description",
        ]
        read_only_fields = fields
```

**Annotazione avg_rating per matchup (pattern da contest_views.videos):**
```python
from django.db.models import Avg, Q, F

def get_queryset(self):
    return Matchup.objects.select_related(
        "bracket", "entry_1__user", "entry_1__video",
        "entry_2__user", "entry_2__video", "winner",
    ).annotate(
        avg_rating_1=Avg("votes__value", filter=Q(votes__entry=F("entry_1"))),
        avg_rating_2=Avg("votes__value", filter=Q(votes__entry=F("entry_2"))),
    )
```

**Gestione 409 Conflict per duplicati (pattern VideoLike):**
```python
from django.db import IntegrityError

try:
    MatchupVote.objects.create(matchup=matchup, user=request.user, entry=entry, value=value)
except IntegrityError:
    return Response(
        {"detail": "Hai gia' votato per questo matchup."},
        status=status.HTTP_409_CONFLICT,
    )
```

**Paginazione DRF — SEMPRE `page is not None` (mai `if page`):**
```python
page = self.paginate_queryset(qs)
if page is not None:
    serializer = self.get_serializer(page, many=True)
    return self.get_paginated_response(serializer.data)
serializer = self.get_serializer(qs, many=True)
return Response(serializer.data)
```

**Notifiche — Pattern inline dalle views:**
```python
from cs_clips.models import Notification

Notification.objects.create(
    recipient=user,
    sender=request.user,
    notification_type="bracket_invite",
    video=entry.video,
)
```

**URL registration — Pattern da `cs_clips/urls.py`:**
```python
from cs_clips.api.brackets.bracket_views import BracketViewSet, MatchupViewSet

router.register(r"brackets", BracketViewSet, basename="bracket")
router.register(r"matchups", MatchupViewSet, basename="matchup")
```

### Modello MatchupVote — Specifica completa

```python
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class MatchupVote(models.Model):
    """Voto di un utente su un matchup bracket."""

    matchup = models.ForeignKey(
        "Matchup",
        on_delete=models.CASCADE,
        related_name="votes",
        help_text="Matchup votato",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matchup_votes",
        help_text="Utente che ha votato",
    )
    entry = models.ForeignKey(
        "ContestEntry",
        on_delete=models.CASCADE,
        related_name="received_votes",
        help_text="Entry votata dall'utente",
    )
    value = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Voto da 1 a 5",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e ora del voto",
    )

    class Meta:
        unique_together = ("matchup", "user")
        ordering = ["-created_at"]
        verbose_name = "Voto matchup"
        verbose_name_plural = "Voti matchup"

    def __str__(self):
        return f"Voto {self.value} di {self.user} su matchup {self.matchup_id}"
```

### Logica chiusura matchup con media voti (close action)

```python
def close(self, request, pk=None):
    matchup = self.get_object()
    if matchup.is_completed:
        return Response({"detail": "Matchup gia' completato."}, status=400)
    if not matchup.entry_1 or not matchup.entry_2:
        return Response({"detail": "Matchup incompleto."}, status=400)

    # Calcola medie voti
    votes = matchup.votes.all()
    avg_1 = votes.filter(entry=matchup.entry_1).aggregate(avg=Avg("value"))["avg"] or 0
    avg_2 = votes.filter(entry=matchup.entry_2).aggregate(avg=Avg("value"))["avg"] or 0

    # Vincitore: media piu' alta, parita' → entry_1 (determinismo FR43b)
    winner = matchup.entry_1 if avg_1 >= avg_2 else matchup.entry_2

    # Chiude matchup e propaga avanzamento (funzione esistente)
    from cs_clips.utils.bracket_logic import close_matchup
    close_matchup(matchup, winner)

    # Notifica bracket_turn per i partecipanti del prossimo matchup
    next_matchup = matchup.bracket.matchups.filter(
        round_number=matchup.round_number + 1,
        position=matchup.position // 2,
    ).first()
    if next_matchup:
        for entry in [next_matchup.entry_1, next_matchup.entry_2]:
            if entry:
                Notification.objects.create(
                    recipient=entry.user,
                    notification_type="bracket_turn",
                    sender=request.user,
                    video=entry.video,
                )

    return Response({"detail": "Matchup chiuso.", "winner_entry_id": winner.id})
```

### Vincoli e Attenzioni

1. **NON modificare `bracket_logic.py`** — usare `close_matchup()` e `advance_winner()` cosi' come sono
2. **NON creare componenti frontend** — il frontend bracket va nella Story 6.3
3. **NON modificare Contest o video_views** — i due sistemi sono completamente separati (D2)
4. **Import User:** `settings.AUTH_USER_MODEL` per FK, `get_user_model()` per codice runtime
5. **Custom User `related_name`:** `groups` ha `related_name="custom_user_set"` — NON usare `group.user_set`
6. **`User.groups` ha `blank=False`:** ogni utente nei test DEVE avere almeno un gruppo assegnato (pattern: `Group.objects.get_or_create(name="user")` + `user.groups.add(group)`)
7. **Test con PostgreSQL attivo:** i test richiedono Docker con DB attivo
8. **`read_only_fields` espliciti:** ogni campo calcolato/annotato DEVE essere read_only al primo commit
9. **Messaggi errore in italiano** nelle Response e ValidationError
10. **`@extend_schema` su ogni ViewSet e action** per drf-spectacular (documentazione Swagger)
11. **Notifica `bracket_invite`:** tipo gia' registrato nel modello Notification (choices). Creazione inline nella enter action
12. **Notifica `bracket_turn`:** tipo gia' registrato. Creazione inline nella close action
13. **Nessun fattore esterno nel calcolo vincitore (FR43b):** solo media voti interni al matchup, NO view count, NO like count
14. **257 test totali attuali:** 256 pass, 1 fail pre-esistente (`test_registration_assigns_toconfirm_group`) — non rompere nulla

### File da creare/modificare

**Nuovi file:**
- `backend/cs_clips/models/matchup_vote.py` — modello MatchupVote
- `backend/cs_clips/api/brackets/__init__.py` — init vuoto
- `backend/cs_clips/api/brackets/bracket_views.py` — BracketViewSet + MatchupViewSet
- `backend/cs_clips/api/brackets/bracket_serializers.py` — tutti i serializer
- `backend/cs_clips/tests/test_bracket_api.py` — test API
- `backend/cs_clips/migrations/0011_matchupvote.py` — migrazione (auto-generata)

**File da modificare:**
- `backend/cs_clips/models/__init__.py` — aggiungere export MatchupVote
- `backend/cs_clips/admin.py` — aggiungere MatchupVoteAdmin
- `backend/cs_clips/urls.py` — registrare BracketViewSet e MatchupViewSet sul router

### Test helper — Fixture conftest.py gia' disponibili

Da `conftest.py` esistente:
- `create_authenticated_user()` — crea utente con gruppo "user" e token JWT
- `create_api_client_authenticated()` — restituisce APIClient autenticato
- `create_toconfirm_user()` — utente con gruppo "toconfirm" (sola lettura)

**Setup test bracket API (pattern):**
```python
@pytest.fixture
def bracket_with_entries(db):
    """Crea bracket in registration con 4 entry per test API."""
    admin = create_authenticated_user(username="admin", is_superuser=True)
    bracket = Bracket.objects.create(
        name="Test Bracket", max_participants=8, created_by=admin
    )
    entries = []
    for i in range(4):
        user = create_authenticated_user(username=f"player{i}")
        video = Video.objects.create(title=f"Clip {i}", uploader=user, ...)
        entry = ContestEntry.objects.create(bracket=bracket, user=user, video=video)
        entries.append(entry)
    return bracket, entries, admin
```

### Project Structure Notes

- Il dominio `api/brackets/` segue la struttura `api/{dominio}/` esistente (comments, contests, notifications, ratings, users, videos)
- I ViewSet vengono registrati centralmente in `urls.py` sul DefaultRouter (come tutti gli altri)
- Il modello MatchupVote segue il pattern di VideoLike (FK + unique_together + validators)
- Nessun file `bracket_urls.py` separato — le URL passano tutte dal router centrale (pattern contests/notifications)

### Previous Story Intelligence (Story 6.1)

**Learnings dalla Story 6.1:**
- Admin action test: `RequestFactory` richiede `FallbackStorage` per `MessageMiddleware`
- `ruff format` potrebbe richiedere riformattazione — eseguire `ruff format` proattivamente
- I modelli bracket usano `settings.AUTH_USER_MODEL` per FK (non `get_user_model()`)
- `transaction.atomic()` gia' presente in `generate_bracket` e `close_matchup`
- `bracket.current_round` aggiornato automaticamente da `advance_winner` quando tutti i matchup del turno completati
- Validazione `max_participants` gia' in `generate_bracket` (verifica `entries.count() >= 2`)
- Code review fix integrati: transaction.atomic, validazione max_participants, validazione winner in close_matchup, current_round progressione

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 6, Story 6.2] — AC e user story
- [Source: _bmad-output/planning-artifacts/prd.md#FR39c] — Iscrizione bracket con clip
- [Source: _bmad-output/planning-artifacts/prd.md#FR42b] — Votazione 1-5 su matchup
- [Source: _bmad-output/planning-artifacts/prd.md#FR43b] — Media voti interni, nessun fattore esterno
- [Source: _bmad-output/planning-artifacts/prd.md#FR44] — Visualizzazione stato e progressione
- [Source: _bmad-output/planning-artifacts/architecture.md#D2] — Bracket separato da Contest
- [Source: _bmad-output/planning-artifacts/architecture.md#API Patterns] — Dominio API separato
- [Source: _bmad-output/implementation-artifacts/6-1-modelli-bracket-backend-e-logica-turni.md] — Story precedente
- [Source: backend/cs_clips/api/contests/contest_views.py] — Pattern ReadOnlyModelViewSet + actions
- [Source: backend/cs_clips/api/contests/contest_serializers.py] — Pattern Output serializer
- [Source: backend/cs_clips/permissions.py] — RoleBasedPermission, OnlyAdminsPermission
- [Source: backend/cs_clips/utils/bracket_logic.py] — close_matchup, advance_winner

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Test round keys sono `int` (non `str`) nel dict `matchups_by_round` — corretto nei test
- Notification field e' `type` (non `notification_type`) — corretto nelle views
- Docker non era avviato — avviato Docker Desktop prima di test/migrazione
- Migrazione 0011 creata manualmente (MinIO init blocca `manage.py` senza Docker)

### Completion Notes List

- ✅ Modello MatchupVote creato con FK, validators, unique_together, help_text italiano
- ✅ 6 serializer creati: ContestEntryNested, MatchupOutput, BracketListOutput, BracketDetailOutput, EnterBracketInput, VoteMatchupInput
- ✅ BracketViewSet (ReadOnlyModelViewSet) con list/retrieve AllowAny, enter IsAuthenticated, filtro status, entries_count annotato
- ✅ MatchupViewSet (RetrieveModelMixin+GenericViewSet) con vote IsAuthenticated, close OnlyAdminsPermission, avg_rating annotato
- ✅ Logica close: media voti, parita' → entry_1 vince (FR43b), close_matchup() per avanzamento, notifica bracket_turn
- ✅ URL registrate sul router centrale: /api/brackets/, /api/matchups/
- ✅ @extend_schema su ogni ViewSet e action per drf-spectacular
- ✅ 32 test API (tutti passano): list, detail, enter (201/400/409), vote (201/400/409), close (200/403), bracket_completed, notifiche
- ✅ Regression suite: 291 test, unico fail pre-esistente (test_registration_assigns_toconfirm_group)
- ✅ ruff check + ruff format: 0 errori

### Change Log

- 2026-03-15: Story 6.2 implementata — API bracket con BracketViewSet, MatchupViewSet, modello MatchupVote, 30 test

### File List

**Nuovi file:**
- `backend/cs_clips/models/matchup_vote.py` — modello MatchupVote
- `backend/cs_clips/migrations/0011_matchupvote.py` — migrazione
- `backend/cs_clips/api/brackets/__init__.py` — init package
- `backend/cs_clips/api/brackets/bracket_serializers.py` — 6 serializer
- `backend/cs_clips/api/brackets/bracket_views.py` — BracketViewSet + MatchupViewSet
- `backend/cs_clips/tests/test_bracket_api.py` — 30 test API

**File modificati:**
- `backend/cs_clips/models/__init__.py` — export MatchupVote
- `backend/cs_clips/admin.py` — MatchupVoteAdmin
- `backend/cs_clips/urls.py` — registrazione BracketViewSet + MatchupViewSet
