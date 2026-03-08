# Story 4.1: Backend Contest Settimanale — Endpoint e Listing

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utente registrato,
I want vedere i contest settimanali disponibili e i loro dettagli,
So that posso decidere a quale contest partecipare.

## Acceptance Criteria

1. **Given** un utente autenticato
   **When** chiama `GET /api/contests/`
   **Then** riceve la lista paginata dei contest (attivi e chiusi) con campi: id, name, tag, start_date, end_date, is_closed, winner, video_count (FR38)
   **And** ordinamento di default: `-start_date` (piu recenti prima)

2. **Given** un utente autenticato
   **When** chiama `GET /api/contests/{id}/`
   **Then** riceve il dettaglio del singolo contest con winner nested (VideoOutputSerializer se chiuso) e video_count

3. **Given** un utente che carica una clip con tag "clutch"
   **When** la clip viene salvata
   **Then** viene auto-assegnata al contest settimanale corrente per quel tag via `get_or_create_current_contest('clutch')` (FR39a, FR39b)
   **And** questo meccanismo esiste GIA e NON va modificato

4. **Given** nessun contest attivo per il tag "funny" nella settimana corrente
   **When** un utente carica una clip con tag "funny"
   **Then** un nuovo contest settimanale viene creato automaticamente (FR39a)
   **And** questo meccanismo esiste GIA e NON va modificato

5. **Given** un contest settimanale scaduto
   **When** APScheduler esegue `close_contests` (giovedi 11:33 UTC)
   **Then** il contest viene chiuso, il vincitore viene assegnato (media voti + spareggio se parimerito) (FR41a, FR42a)
   **And** la chiusura e idempotente (ri-esecuzione non cambia risultato)
   **And** questo meccanismo esiste GIA e NON va modificato

6. **Given** un utente che chiama `GET /api/contests/?tag=funny`
   **When** il filtro viene applicato
   **Then** riceve solo i contest con tag "funny"

7. **Given** un utente che chiama `GET /api/contests/?is_closed=true`
   **When** il filtro viene applicato
   **Then** riceve solo i contest chiusi

## Tasks / Subtasks

- [x] Task 1: Creare `ContestListOutputSerializer` e aggiornare `ContestSerializer` (AC: #1, #2)
  - [x] 1.1 In `contest_serializers.py`: creare `ContestListOutputSerializer` con campi: id, name, tag, start_date, end_date, is_closed, closed_at, winner (intero FK), video_count (annotato)
  - [x] 1.2 Creare `ContestDetailOutputSerializer` che estende il list con winner nested come `VideoOutputSerializer` (se winner non null)
  - [x] 1.3 Aggiungere `read_only_fields` espliciti per tutti i campi (contest non sono editabili via API)
  - [x] 1.4 `video_count` come `serializers.IntegerField(read_only=True)` — verra annotato nel queryset

- [x] Task 2: Creare `ContestViewSet` read-only con filtri (AC: #1, #2, #6, #7)
  - [x] 2.1 In `contest_views.py`: creare `ContestViewSet(viewsets.ReadOnlyModelViewSet)` — solo list + retrieve
  - [x] 2.2 `get_queryset()`: annotare `video_count=Count('videos')`, ordinare per `-start_date`
  - [x] 2.3 `get_serializer_class()`: `ContestListOutputSerializer` per list, `ContestDetailOutputSerializer` per retrieve
  - [x] 2.4 `permission_classes = [IsAuthenticated]`
  - [x] 2.5 `http_method_names = ['get', 'head', 'options', 'post']` (post per @action end)
  - [x] 2.6 Aggiungere `filterset_fields = ['tag', 'is_closed']` con django-filter
  - [x] 2.7 Aggiungere `@extend_schema` su classe e actions per documentazione OpenAPI

- [x] Task 3: Registrare route in `urls.py` (AC: #1, #2)
  - [x] 3.1 In `cs_clips/urls.py`: registrato `router.register(r"contests", ContestViewSet, basename="contest")`
  - [x] 3.2 Consolidato `ContestWinnersView` e `EndContestView` come `@action` nel ViewSet — zero conflitti routing
  - [x] 3.3 Import `ContestViewSet` nel file urls, rimossi import vecchi

- [x] Task 4: Scrivere test per i nuovi endpoint (AC: tutti)
  - [x] 4.1 Creare `backend/cs_clips/tests/test_contests_list.py` con `APITestCase`
  - [x] 4.2 Test: `GET /api/contests/` ritorna lista paginata (status 200, formato `{count, next, previous, results}`)
  - [x] 4.3 Test: `GET /api/contests/{id}/` ritorna dettaglio contest con video_count
  - [x] 4.4 Test: filtro `?tag=funny` ritorna solo contest con quel tag
  - [x] 4.5 Test: filtro `?is_closed=true` ritorna solo contest chiusi
  - [x] 4.6 Test: contest chiuso include winner (non null) nel serializer
  - [x] 4.7 Test: utente non autenticato riceve 401
  - [x] 4.8 Test: lista vuota ritorna `{count: 0, results: []}`

- [x] Task 5: Verifica qualita (AC: tutti)
  - [x] 5.1 `ruff check backend/` — 0 errori
  - [x] 5.2 `ruff format --check backend/` — 0 errori (file nuovi/modificati)
  - [x] 5.3 `python manage.py test` — 211 test, 210 pass, 1 fail pre-esistente (test_registration_assigns_toconfirm_group)
  - [x] 5.4 `GET /api/contests/winners/` e `POST /api/contests/end/` funzionano via @action (URL path identici, test pre-esistenti passano)

## Dev Notes

### Stato attuale — Infrastruttura contest GIA funzionante

Il backend contest ha gia una base solida. Questa story aggiunge SOLO l'endpoint di listing/detail.

| Componente | File | Stato |
|-----------|------|-------|
| Modello `Contest` | `backend/cs_clips/models/contest.py` | Completo — name, tag, start_date, end_date, is_closed, closed_at, winner FK |
| `get_or_create_current_contest()` | `backend/cs_clips/utils/get_date_util.py` | Completo — settimana lun-sab, nome auto-generato |
| `desempate_ponderato()` | `backend/cs_clips/utils/desempate.py` | Completo — pesi 50% voti, 30% views, 20% like |
| `close_contests` command | `backend/cs_clips/management/commands/close_contests.py` | Completo — chiusura + spareggio |
| `EndContestView` | `backend/cs_clips/api/contests/contest_views.py` | Completo — POST admin-only |
| `ContestWinnersView` | `backend/cs_clips/api/contests/contest_views.py` | Completo — GET vincitori paginato |
| `ContestSerializer` | `backend/cs_clips/api/contests/contest_serializers.py` | Minimale — solo campi base, non usato in views |
| Video.contest FK | `backend/cs_clips/models/video.py` | Completo — `contest = FK(Contest, SET_NULL, related_name="videos")` |
| APScheduler | `backend/cs_clips/apps.py` + `scheduler.py` | Completo — giovedi 11:33 UTC |

**Cosa manca (scope di questa story):**
1. `GET /api/contests/` — lista paginata con filtri tag/is_closed
2. `GET /api/contests/{id}/` — dettaglio singolo contest
3. `ContestViewSet` read-only registrato nel router
4. Serializer con annotazione `video_count` e winner nested
5. Test per i nuovi endpoint

### Approccio implementativo

**ReadOnlyModelViewSet** — i contest NON sono creati/editati via API. Sono creati implicitamente da `get_or_create_current_contest()` e chiusi da APScheduler o `EndContestView`. Il ViewSet offre SOLO lettura.

**Routing — Attenzione ai conflitti:**
Il router DRF registrera `/api/contests/` e `/api/contests/{pk}/`. Le route manuali esistenti (`contests/winners/`, `contests/end/`) devono rimanere. L'ordine in `urlpatterns` e critico:
```python
# Le route manuali PRIMA dell'include del router, oppure...
# Il router PRIMA e le route manuali dopo (il router non cattura "winners" o "end" come pk se sono path separati)
```
Soluzione raccomandata: registrare il ViewSet nel router e lasciare le route manuali dopo. Il router crea path `/api/contests/` e `/api/contests/{pk}/` — `winners/` e `end/` non sono catturati dal router perche sono path espliciti definiti prima.

**Alternativa migliore:** convertire `ContestWinnersView` e `EndContestView` in `@action` del `ContestViewSet`:
- `@action(detail=False, methods=['get'], url_path='winners')` — sostituisce `ContestWinnersView`
- `@action(detail=False, methods=['post'], url_path='end')` — sostituisce `EndContestView`
Questo consolida tutto in un unico ViewSet e elimina i conflitti di routing. Richiede spostare la logica delle views esistenti nelle action.

**DECISIONE: Consolidare in ContestViewSet con @action.** Motivazione:
- Eliminare rischio conflitti routing
- Pattern coerente con il resto del codebase (VideoViewSet usa @action per `following`, `top-rated`, `like`, `popup-comments`)
- Codice morto `contest_urls.py` puo essere eliminato
- Un singolo ViewSet per tutto il dominio contest

### Schema annotazione queryset

```python
from django.db.models import Count

def get_queryset(self):
    return Contest.objects.annotate(
        video_count=Count('videos')
    ).order_by('-start_date')
```

### Serializer strategy

```python
class ContestListOutputSerializer(serializers.ModelSerializer):
    video_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Contest
        fields = ['id', 'name', 'tag', 'start_date', 'end_date',
                  'is_closed', 'closed_at', 'winner', 'video_count']
        read_only_fields = fields

class ContestDetailOutputSerializer(ContestListOutputSerializer):
    winner_detail = VideoOutputSerializer(source='winner', read_only=True)

    class Meta(ContestListOutputSerializer.Meta):
        fields = ContestListOutputSerializer.Meta.fields + ['winner_detail']
        read_only_fields = fields
```

### File `contest_urls.py` — dead code da rimuovere

Il file `backend/cs_clips/api/contests/contest_urls.py` esiste ma NON e importato da nessuna parte. E dead code. Va eliminato durante questa story come cleanup.

### Test helpers disponibili in conftest.py

```python
# Gia disponibili:
create_authenticated_user()    # utente con gruppo 'user' + token
create_api_client_authenticated()  # APIClient con force_authenticate
create_sample_contest()         # contest attivo con tag e date validi
```

### Conftest helper per test contest

`create_sample_contest()` e gia disponibile in conftest. Per i test servira:
- Contest attivo (is_closed=False) con video associati
- Contest chiuso (is_closed=True) con winner
- Contest con diversi tag per test filtri

### Project Structure Notes

- Tutti i file backend gia esistono — solo modifiche a file esistenti
- File da creare: `backend/cs_clips/tests/test_contests_list.py` (nuovo file test)
- File da eliminare: `backend/cs_clips/api/contests/contest_urls.py` (dead code)
- Nessun file frontend in questa story — e puramente backend
- Allineamento con struttura: `cs_clips/api/contests/` per views e serializers, `cs_clips/urls.py` per routing

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-4.1] — AC BDD: listing paginato, auto-assegnazione contest, chiusura APScheduler
- [Source: _bmad-output/planning-artifacts/architecture.md#Sistema-Contest-Settimanali] — Modello Contest, `get_or_create_current_contest`, APScheduler, spareggio
- [Source: _bmad-output/planning-artifacts/architecture.md#ViewSet-Routing] — Pattern B (ModelViewSet + @action), Pattern C (APIView standalone)
- [Source: _bmad-output/planning-artifacts/architecture.md#Format-Patterns] — Custom action con paginazione, serializer multipli
- [Source: _bmad-output/planning-artifacts/architecture.md#Anti-Pattern] — Contest NON hanno CRUD ViewSet (creati implicitamente)
- [Source: _bmad-output/project-context.md#Edge-Case-Contest] — Settimana lun-sab, suffisso numerico, idempotenza chiusura
- [Source: _bmad-output/project-context.md#ViewSet-Routing] — Pattern C per EndContestView, Pattern B per ViewSet con @action
- [Source: backend/cs_clips/api/contests/contest_views.py] — EndContestView e ContestWinnersView esistenti
- [Source: backend/cs_clips/api/contests/contest_serializers.py] — ContestSerializer minimale esistente
- [Source: backend/cs_clips/models/contest.py] — Modello completo con unique_together
- [Source: backend/cs_clips/urls.py] — Route manuali contests/winners/ e contests/end/
- [Source: MEMORY.md#Backend-State] — 193 test backend (192 pass, 1 fail pre-esistente)

### Intelligence dalla Story precedente (3.5 — ultima Epic 3)

- **193 test backend** baseline (192 pass, 1 fail pre-esistente `test_registration_assigns_toconfirm_group`)
- **Ruff 0 errori** baseline
- **Pattern annotation queryset**: `Count(distinct=True)` + `Exists()` — consolidato in Epic 1-3
- **Pattern `@action` con paginazione**: `self.paginate_queryset()` + `self.get_paginated_response()` — usato in VideoViewSet
- **`@extend_schema`** su ogni action — obbligatorio per OpenAPI
- **`http_method_names`** restrittivo — bloccare metodi non necessari
- **read_only_fields espliciti** — ogni campo calcolato/identita DEVE essere read_only
- **Test assertions complete**: status code + formato risposta + contenuto specifico

### Git Intelligence — Pattern recenti

Ultimi commit rilevanti:
- `612f66c` — Epic 3 completo: like UI, popup overlay, spareggio like, comment markers
- `da01a68` — Story 3.1: modelli VideoLike/CommentLike + endpoint like/unlike + annotazioni

Pattern commit: prefisso `feat:` per feature, riepilogo conciso.
Suggerito: `feat: Story 4.1 — ContestViewSet read-only con listing, filtri e detail`

### Rischi e edge case

1. **Conflitto routing**: il router DRF potrebbe catturare `winners` e `end` come `{pk}`. Mitigazione: consolidare tutto in ContestViewSet con @action.
2. **Contest senza video**: `video_count=0` e un caso valido — contest creato ma nessun upload. Il serializer deve gestirlo (no crash).
3. **Winner nullo**: contest attivi hanno `winner=null`. Il `ContestDetailOutputSerializer` deve gestire winner_detail come null (non crash su `VideoOutputSerializer(None)`).
4. **Backwards compatibility**: `ContestWinnersView` e `EndContestView` vengono migrati in @action — gli URL path devono rimanere identici (`/api/contests/winners/`, `/api/contests/end/`).
5. **Spareggio pesi aggiornati**: il `desempate.py` attuale usa `likes.count()` (non piu comments). Pesi: 50% voti, 30% views, 20% like. NON modificare.

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

Nessun debug critico — implementazione lineare senza blocchi.

### Completion Notes List

- **Task 1**: Creati `ContestListOutputSerializer` (9 campi, tutti read_only, video_count annotato) e `ContestDetailOutputSerializer` (estende list con winner_detail nested via VideoOutputSerializer). ContestSerializer originale preservato per retrocompatibilita.
- **Task 2**: Creato `ContestViewSet(ReadOnlyModelViewSet)` con `get_queryset()` annotato (`Count('videos')`), `get_serializer_class()` per list/retrieve, `filterset_fields=['tag','is_closed']`, `@extend_schema_view` per OpenAPI. Consolidati `EndContestView` e `ContestWinnersView` come `@action(url_path='end')` e `@action(url_path='winners')` — URL path identici, zero rischio conflitto routing.
- **Task 3**: Registrato `router.register(r"contests", ContestViewSet, basename="contest")` in urls.py. Rimossi path manuali e import vecchi (`ContestWinnersView`, `EndContestView`). Eliminato dead code `contest_urls.py`.
- **Task 4**: 19 test in `test_contests_list.py` — 5 classi: ContestListTests (6 test), ContestDetailTests (4 test), ContestFilterTests (4 test), ContestActionRoutingTests (3 test), ContestAuthTests (2 test). Copertura: lista paginata, campi, ordinamento, video_count, winner_detail nested, filtri tag/is_closed, routing winners/end @action, 401 non-auth, lista vuota.
- **Task 5**: ruff check 0 errori, ruff format 0 errori (file nuovi/modificati), 214 test totali (213 pass, 1 fail pre-esistente noto).

### File List

- `backend/cs_clips/api/contests/contest_serializers.py` — modificato: aggiunti ContestListOutputSerializer e ContestDetailOutputSerializer
- `backend/cs_clips/api/contests/contest_views.py` — modificato: riscritto con ContestViewSet (ReadOnlyModelViewSet + @action winners/end)
- `backend/cs_clips/api/contests/contest_urls.py` — eliminato: dead code, route consolidate nel router
- `backend/cs_clips/urls.py` — modificato: registrato ContestViewSet nel router, rimossi path manuali
- `backend/cs_clips/tests/test_contests_list.py` — creato: 19 test per listing, detail, filtri, routing actions, auth
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — modificato: status 4-1 → in-progress → review
- `_bmad-output/implementation-artifacts/4-1-backend-contest-settimanale-endpoint-e-listing.md` — modificato: task completati, dev record

## Change Log

- **2026-03-08**: Story 4.1 implementata — ContestViewSet read-only con listing paginato, detail con winner nested, filtri tag/is_closed, consolidamento EndContestView e ContestWinnersView come @action, eliminazione dead code contest_urls.py, 16 nuovi test.
- **2026-03-08**: Code review fix — [H1] select_related('winner') in winners action (N+1 eliminato), [H2] select_related('winner') in get_queryset() per retrieve, [H3] django.forms.ValidationError → rest_framework.exceptions.ValidationError in end action (500→400), [M1] winners refactored da Python list a QuerySet, [M2] +3 smoke test routing winners/end @action, [M3] fix docstring AC reference in ContestAuthTests. 214 test (213 pass, 1 fail pre-esistente).
