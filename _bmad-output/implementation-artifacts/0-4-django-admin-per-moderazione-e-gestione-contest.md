# Story 0.4: Django Admin per Moderazione e Gestione Contest

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin/moderatore,
I want gestire utenti, video, commenti e contest tramite Django Admin,
so that posso moderare la piattaforma e gestire i contest senza interfaccia frontend dedicata.

## Acceptance Criteria (BDD)

### AC-1: Disabilitare commenti inappropriati (FR45)

```gherkin
Scenario: Admin disabilita un commento inappropriato
  Given un admin autenticato nell'interfaccia Django Admin
  When accede alla lista commenti e seleziona "Disabilita commenti selezionati"
  Then il campo is_disabled del commento viene impostato a True
  And il commento non appare più nelle risposte API di CommentViewSet
  And il commento resta visibile nell'admin con indicatore "Disabilitato"

Scenario: Admin riabilita un commento disabilitato
  Given un admin autenticato nell'interfaccia Django Admin
  When seleziona un commento disabilitato e sceglie "Abilita commenti selezionati"
  Then il campo is_disabled viene reimpostato a False
  And il commento riappare nelle risposte API
```

### AC-2: Eliminare video (FR46)

```gherkin
Scenario: Admin elimina un video dalla piattaforma
  Given un admin autenticato nell'interfaccia Django Admin
  When elimina un video dalla lista
  Then il record video viene eliminato dal database
  And il file viene rimosso da MinIO tramite django-cleanup
  And i commenti e rating associati vengono eliminati per CASCADE
```

### AC-3: Sospendere account utente (FR47)

```gherkin
Scenario: Admin sospende un account utente
  Given un admin autenticato nell'interfaccia Django Admin
  When accede al dettaglio utente e deseleziona il campo is_active
  Then l'utente non può più autenticarsi (JWT rifiutato)
  And il toggle is_active è visibile nella sezione "Permessi" del UserAdmin
```

### AC-4: Promuovere utenti tra ruoli (FR48)

```gherkin
Scenario: Admin promuove un utente tra gruppi Django
  Given un admin autenticato nell'interfaccia Django Admin
  When modifica il gruppo di un utente
  Then può assegnare/rimuovere i gruppi: toconfirm, user, admin
  And i percorsi di promozione sono: toconfirm → user → admin
  And il campo "Ruolo" nella lista utenti riflette il gruppo corrente
```

### AC-5: Visualizzare video filtrati per uploader (FR49)

```gherkin
Scenario: Admin filtra la lista video per uploader
  Given un admin autenticato nell'interfaccia Django Admin
  When accede alla lista video
  Then vede un filtro laterale "uploader" nella sidebar
  And può filtrare i video per un uploader specifico
```

### AC-6: Gestione contest settimanali (FR55 parziale)

```gherkin
Scenario: Admin crea manualmente un contest settimanale
  Given un admin autenticato nell'interfaccia Django Admin
  When accede alla sezione Contest e clicca "Aggiungi Contest"
  Then può creare un contest con nome, tag, date inizio/fine

Scenario: Admin chiude manualmente un contest aperto
  Given un admin autenticato nell'interfaccia Django Admin
  When seleziona un contest aperto e sceglie "Chiudi contest selezionati"
  Then il contest viene marcato come is_closed=True
  And closed_at viene impostato al timestamp corrente
```

## Tasks / Subtasks

- [x] Task 1: Aggiungere campo `is_disabled` al modello Comment (AC: #1)
  - [x] 1.1 Aggiungere `is_disabled = models.BooleanField(default=False)` in `backend/cs_clips/models/comment.py`
  - [x] 1.2 Eseguire `python manage.py makemigrations cs_clips` e verificare la migrazione generata
  - [x] 1.3 Eseguire `python manage.py migrate` e verificare che il campo esista nel DB

- [x] Task 2: Filtrare commenti disabilitati nel `CommentViewSet` (AC: #1)
  - [x] 2.1 Modificare `queryset` in `backend/cs_clips/api/comments/comment_views.py`: `Comment.objects.filter(is_disabled=False)`
  - [x] 2.2 Verificare che l'endpoint `GET /api/comments/` NON restituisca commenti con `is_disabled=True`
  - [x] 2.3 Verificare che l'endpoint `GET /api/comments/{id}/` restituisca 404 per commenti disabilitati

- [x] Task 3: Estendere `CommentAdmin` per moderazione (AC: #1)
  - [x] 3.1 Aggiungere `is_disabled` a `list_display` con colonna `"content_preview"`
  - [x] 3.2 Aggiungere `list_filter = ("is_disabled",)`
  - [x] 3.3 Implementare action bulk `disabilita_commenti` (update `is_disabled=True`)
  - [x] 3.4 Implementare action bulk `abilita_commenti` (update `is_disabled=False`)
  - [x] 3.5 Aggiungere metodo `content_preview` per mostrare i primi 50 caratteri del commento

- [x] Task 4: Estendere `VideoAdmin` con filtro uploader (AC: #5)
  - [x] 4.1 Aggiungere `"uploader"` a `list_filter` in `backend/cs_clips/admin.py`

- [x] Task 5: Estendere `ContestAdmin` per gestione manuale (AC: #6)
  - [x] 5.1 Implementare action bulk `chiudi_contest` che imposta `is_closed=True` e `closed_at=timezone.now()`
  - [x] 5.2 Aggiungere `readonly_fields = ("closed_at",)` per impedire modifica manuale del timestamp
  - [x] 5.3 Aggiungere `date_hierarchy = "start_date"` per navigazione temporale

- [x] Task 6: Verifiche UserAdmin esistente (AC: #3, #4)
  - [x] 6.1 Verificare che `is_active` sia già visibile e toggle-abile nei fieldsets (sezione "Permessi") — GIA' PRESENTE
  - [x] 6.2 Verificare che `groups` sia già assegnabile — GIA' PRESENTE
  - [x] 6.3 Nessuna modifica necessaria se le verifiche passano

- [x] Task 7: Scrivere test per moderazione admin (AC: #1, #2, #5)
  - [x] 7.1 Creare `backend/cs_clips/tests/test_admin_moderation.py`
  - [x] 7.2 Test: commento con `is_disabled=True` non appare in `GET /api/comments/?video={id}`
  - [x] 7.3 Test: commento con `is_disabled=False` appare normalmente
  - [x] 7.4 Test: admin può eliminare video (CASCADE elimina commenti associati)
  - [x] 7.5 Test: utente non-admin non può accedere alle admin action di moderazione

- [x] Task 8: Compliance e verifica finale
  - [x] 8.1 `ruff check backend/` — 0 errori
  - [x] 8.2 `ruff format --check backend/` — 0 errori
  - [x] 8.3 `python manage.py test` — tutti i test passano (pre-esistenti + nuovi)
  - [x] 8.4 `python manage.py check` — 0 errori
  - [x] 8.5 `npm run build` — compilazione frontend senza errori (nessuna modifica frontend in questa story)

## Dev Notes

### Requisiti Tecnici

**Stack backend rilevante:**
- Django 5.1.6 con admin built-in
- Django REST Framework 3.15.1
- PostgreSQL 16 (via Docker)
- MinIO 7.2.15 (storage S3-compatible per video)
- `django-cleanup` per auto-rimozione file MinIO su model delete
- APScheduler 3.11.0 per auto-chiusura contest (ogni giovedì 11:33 UTC)

**Campo `is_disabled` — specifiche implementative:**
- Tipo: `models.BooleanField(default=False)` — NON è un soft-delete generico
- Scopo: solo moderazione commenti (FR45)
- Il campo NON impatta il modello Comment oltre la visibilità API
- Migrazione backward-compatible (default=False, tutti i commenti esistenti restano attivi)

**Filtro API — comportamento atteso:**
- `CommentViewSet.queryset` → `Comment.objects.filter(is_disabled=False)`
- Django Admin usa il proprio queryset (non impattato) → admin vede TUTTI i commenti
- Endpoint `GET /api/comments/{id}/` → 404 se `is_disabled=True` (il queryset filtrato gestisce automaticamente)

**DELETE Video — catena di eventi:**
1. Admin elimina video da Django Admin
2. Django ORM elimina record Video (e CASCADE elimina Comment + Rating associati)
3. `django-cleanup` intercetta il signal post_delete e rimuove il file da MinIO
4. Nessun codice custom necessario — tutto gestito da framework/librerie

**Sospensione utente — comportamento JWT:**
- `User.is_active = False` → SimpleJWT rifiuta automaticamente i token
- Nessuna modifica a `permissions.py` necessaria
- L'utente sospeso non può fare login né refreshare il token

### Compliance Architetturale

**Pattern da seguire (già stabiliti nelle storie precedenti):**

| Pattern | Convenzione | Fonte |
|---------|------------|-------|
| Modelli | 1 file per modello in `models/`, re-export in `__init__.py` | Story 0-1 |
| Admin | `@admin.register(Model)` decorator, non `admin.site.register()` | `admin.py` esistente |
| Admin actions | Metodo su ModelAdmin con `short_description` attribute | Django 5.1 docs |
| Permessi | `RoleBasedPermission` per ViewSet, `OnlyAdminsPermission` per admin-only | `permissions.py` |
| Error handling | `handle_exception_with_serializer()` in ogni ViewSet | `error_handler.py` |
| Autocomplete | `autocomplete_fields` per FK (richiede `search_fields` sul relativo Admin) | `admin.py` esistente |
| Linting | ruff (line-length 88, py310, rules E/F/I/DJ/UP) | `pyproject.toml` |
| Test | Django TestCase/APITestCase, helpers da `conftest.py`, ogni utente DEVE avere un group | Story 0-3 |

**Django Admin action — pattern di riferimento:**
```python
@admin.action(description="Disabilita commenti selezionati")
def disabilita_commenti(self, request, queryset):
    updated = queryset.update(is_disabled=True)
    self.message_user(request, f"{updated} commenti disabilitati.")
```

**ATTENZIONE — cose da NON fare:**
- NON aggiungere `User.bio` — è Epic 1 (Story 1-2)
- NON aggiungere `Video.allow_download` — è Epic 2 (Story 2-1)
- NON aggiungere modelli VideoLike/CommentLike — è Epic 3 (Story 3-1)
- NON creare interfaccia frontend admin — questa story è SOLO Django Admin built-in
- NON modificare `permissions.py` — le permission admin sono già gestite da `is_staff`/`is_superuser`

### Librerie e Framework

| Libreria | Versione | Uso in questa story |
|----------|---------|---------------------|
| Django | 5.1.6 | Admin interface, ORM, migrations |
| django-cleanup | (in INSTALLED_APPS) | Auto-delete file MinIO su Video.delete() |
| DRF | 3.15.1 | CommentViewSet queryset filter |
| drf-spectacular | (installato) | Schema OpenAPI (nessuna modifica) |

**Nessuna nuova dipendenza richiesta** — tutto si appoggia a pacchetti già installati.

### Struttura File

**File da MODIFICARE:**
```
backend/cs_clips/
├── models/comment.py          ← +1 campo is_disabled
├── admin.py                   ← estensione CommentAdmin, VideoAdmin, ContestAdmin
├── api/comments/comment_views.py  ← filtro queryset is_disabled=False
└── tests/
    └── test_admin_moderation.py   ← NUOVO file test (4-5 test)
```

**File da NON toccare:**
- `models/user.py` — UserAdmin funziona già per AC-3, AC-4
- `models/video.py` — nessuna modifica modello
- `models/contest.py` — nessuna modifica modello (action su admin, non su model)
- `permissions.py` — permission admin gestite da Django `is_staff`
- `api/comments/comment_serializers.py` — `is_disabled` NON va esposto nel serializer (campo interno di moderazione)
- Qualsiasi file frontend — questa story è backend-only

### Testing Requirements

**Framework:** Django `TestCase` / DRF `APITestCase` (NON pytest)

**Helper disponibili** (da `backend/cs_clips/tests/conftest.py`, Story 0-3):
- `create_authenticated_user()` — crea utente con gruppo `user`
- `create_admin_user()` — crea staff user con gruppo `admin`
- `create_sample_video()` — crea video con file mock (no MoviePy)
- `create_api_client_authenticated(user)` — restituisce APIClient autenticato
- `create_sample_contest()` — crea contest per settimana corrente

**Test minimi richiesti (file: `test_admin_moderation.py`):**

| # | Test | AC | Verifica |
|---|------|------|----------|
| 1 | `test_disabled_comment_hidden_from_api` | AC-1 | Commento con `is_disabled=True` → assente da `GET /api/comments/` |
| 2 | `test_enabled_comment_visible_in_api` | AC-1 | Commento con `is_disabled=False` → presente nella risposta API |
| 3 | `test_video_delete_cascades_comments` | AC-2 | Eliminazione video → commenti e rating associati eliminati |
| 4 | `test_non_admin_cannot_disable_comment` | AC-1 | Utente `user` non può settare `is_disabled=True` via API |

**Pattern test di riferimento:**
```python
from django.test import TestCase
from rest_framework.test import APITestCase
from cs_clips.tests.conftest import (
    create_admin_user,
    create_api_client_authenticated,
    create_authenticated_user,
    create_sample_video,
)

class CommentModerationTests(APITestCase):
    def setUp(self):
        self.admin = create_admin_user()
        self.user = create_authenticated_user()
        self.video = create_sample_video(uploader=self.user)
        # Crea commento di test
```

**Vincolo:** ogni utente nei test DEVE avere almeno un gruppo Django (`user` o `admin`).

**Compliance obbligatoria post-test:**
- `ruff check backend/` → 0 errori
- `ruff format --check backend/` → 0 errori
- `python manage.py test` → 0 fallimenti (inclusi i 9 test pre-esistenti)

### Project Structure Notes

- L'admin.py è un singolo file per tutti i 5 modelli — pattern stabilito, NON shardare
- I test sono in `backend/cs_clips/tests/` con naming `test_<dominio>.py`
- Le migrazioni Django vanno in `backend/cs_clips/migrations/` (auto-generate)
- Il `conftest.py` NON è pytest-based — contiene funzioni helper chiamate manualmente nei test

### Intelligenza Story Precedenti

**Story 0-1 (Bug Fix) — lezioni apprese:**
- FIX-4 ha assicurato `django-cleanup` in `INSTALLED_APPS` → prerequisito per AC-2 (delete video)
- FIX-8 ha corretto `RoleBasedPermission.has_object_permission()` → ora supporta sia `obj.uploader` (Video) che `obj.user` (Comment)
- Pattern commit: `fix: Story X-Y — descrizione`

**Story 0-2 (Linting) — standard attivi:**
- ruff configurato in `pyproject.toml`: line-length 88, double quotes, isort
- Django Debug Toolbar attivo in `DEBUG=True`
- DRF throttling: anon 100/h, user 2000/h, upload 10/h

**Story 0-3 (Testing/CI) — infrastruttura test:**
- `conftest.py` con 5 helper functions (non fixture pytest)
- 9 test totali (5 permission + 4 auth) — tutti devono continuare a passare
- CI GitHub Actions: ruff + test backend + lint frontend + vitest + build
- Nota: MinIO non incluso in CI — i test usano `SimpleUploadedFile` (file mock)

### Intelligenza Git

**Ultimi commit rilevanti:**
```
f68fa2c feat: Story 0-2 — linting, formatting e developer tools
b2bfa77 fix: Story 0-1 — bug fix settings, permissions e pulizia dipendenze
```

**Pattern osservati:**
- Commit message: `feat: Story X-Y — descrizione` per nuove feature
- Commit message: `fix: Story X-Y — descrizione` per bug fix
- Code review separati come commit `fix: code review Story X-Y`

**Convenzione commit per questa story:**
```
feat: Story 0-4 — Django Admin moderazione e gestione contest
```

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic-0, Story 0.4] — User story, AC BDD, requisiti FR45-49, FR55
- [Source: _bmad-output/planning-artifacts/architecture.md#Backend-API] — Stack Django 5.1.6, DRF 3.15.1, MinIO, django-cleanup
- [Source: _bmad-output/planning-artifacts/architecture.md#Ruoli-e-Permessi] — Gruppi Django: toconfirm, user, admin
- [Source: _bmad-output/planning-artifacts/prd.md#FR45-FR49] — Requisiti funzionali moderazione
- [Source: _bmad-output/planning-artifacts/prd.md#FR55] — Gestione contest via backoffice
- [Source: backend/cs_clips/admin.py] — Admin esistente con 5 modelli registrati
- [Source: backend/cs_clips/models/comment.py] — Modello Comment senza is_disabled (da aggiungere)
- [Source: backend/cs_clips/api/comments/comment_views.py] — CommentViewSet con queryset non filtrato
- [Source: backend/cs_clips/tests/conftest.py] — 5 helper functions per test
- [Source: Django 5.1 Admin docs](https://docs.djangoproject.com/en/5.1/ref/contrib/admin/) — Riferimento admin actions, list_display, list_filter

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

- Migrazione 0003: colonna `is_disabled` esisteva già nel DB (aggiunta in sessione precedente) → risolto con `migrate --fake`
- `error_handler.py`: aggiunto parametro `context=None` e logging strutturato (compatibilita' DRF EXCEPTION_HANDLER). Non era un fix E501
- `conftest.py`: fix ruff E501 su docstring troppo lunga (file della Story 0-3, non committato)

### Completion Notes List

- **Task 1**: Campo `is_disabled = BooleanField(default=False)` aggiunto al modello Comment con help_text in italiano. Migrazione 0003 generata e applicata (fake, colonna pre-esistente).
- **Task 2**: Queryset CommentViewSet cambiato da `Comment.objects.all()` a `Comment.objects.filter(is_disabled=False)`. Commenti disabilitati invisibili sia in list che in detail (404 automatico).
- **Task 3**: CommentAdmin esteso con `is_disabled` e `content_preview` in list_display, filtro `is_disabled`, action bulk `disabilita_commenti`/`abilita_commenti`, metodo `content_preview` (primi 50 caratteri).
- **Task 4**: Aggiunto filtro `"uploader"` a VideoAdmin list_filter.
- **Task 5**: ContestAdmin esteso con action `chiudi_contest` (idempotente, filtra solo `is_closed=False`), `readonly_fields = ("closed_at",)`, `date_hierarchy = "start_date"`.
- **Task 6**: Verificato che UserAdmin ha già `is_active` toggle e `groups` assegnabili nei fieldsets "Permessi". Nessuna modifica necessaria.
- **Task 7**: Creato `test_admin_moderation.py` con 9 test (4 CommentModeration + 1 VideoCascadeDelete + 3 AdminAction + 1 UserSuspension). Tutti passano.
- **Task 8**: ruff check 0 errori, ruff format 0 errori, 18/18 test OK (9 nuovi + 9 pre-esistenti), Django check 0 issues, npm run build OK.

### Change Log

- 2026-03-01: Implementazione Story 0-4 — Django Admin per moderazione e gestione contest. Aggiunto campo `is_disabled` su Comment, filtro API, estensioni CommentAdmin/VideoAdmin/ContestAdmin, 5 test moderazione. Fix ruff pre-esistenti su error_handler.py e conftest.py.
- 2026-03-01: Code Review (AI) — Fix 5 problemi trovati in review. (1) Riscritto test `test_non_admin_cannot_disable_comment` in `test_is_disabled_not_exposed_via_api_serializer` usando superuser per testare correttamente il meccanismo del serializer (il test originale passava per 403 da RoleBasedPermission, non per esclusione campo dal serializer). (2) Aggiunti 3 test per admin actions Django (disabilita_commenti, abilita_commenti, chiudi_contest). (3) Aggiunto test `test_inactive_user_jwt_rejected` per AC-3. (4) Rimosso parametro `?video=` fuorviante dai test (nessun DjangoFilterBackend configurato). (5) Corretta documentazione error_handler.py nella File List.

### File List

- `backend/cs_clips/models/comment.py` — MODIFICATO (aggiunto campo `is_disabled`)
- `backend/cs_clips/admin.py` — MODIFICATO (esteso CommentAdmin, VideoAdmin, ContestAdmin)
- `backend/cs_clips/api/comments/comment_views.py` — MODIFICATO (queryset filtrato `is_disabled=False`)
- `backend/cs_clips/tests/test_admin_moderation.py` — NUOVO (9 test: moderazione API, admin actions, sospensione utente)
- `backend/cs_clips/migrations/0003_comment_is_disabled_alter_comment_timestamp_second.py` — NUOVO (migrazione)
- `backend/cs_clips/exceptions/error_handler.py` — MODIFICATO (aggiunto parametro `context=None` per compatibilita' con DRF EXCEPTION_HANDLER in settings.py, logging strutturato con class name e view name)
