# Story 6.1: Modelli Bracket Backend e Logica Turni

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a sviluppatore,
I want i modelli Bracket, ContestEntry e Matchup con logica di progressione turni,
So that il sistema può gestire tornei a eliminazione diretta con generazione automatica dei matchup e avanzamento vincitori.

## Acceptance Criteria

1. **Given** i modelli bracket non esistenti
   **When** vengono creati in `cs_clips/models/`
   **Then** `Bracket` ha campi: `name` (CharField max 200), `description` (TextField blank), `status` (CharField choices: registration/active/completed), `max_participants` (PositiveIntegerField), `current_round` (PositiveIntegerField default 1), `created_by` (FK User), `created_at` (DateTimeField auto_now_add), `prize_description` (TextField blank)
   **And** ha `related_name`, `help_text` in italiano, `ordering = ["-created_at"]`
   **And** è registrato in `admin.py` e esportato da `models/__init__.py`

2. **Given** il modello `ContestEntry` non esistente
   **When** viene creato in `cs_clips/models/contest_entry.py`
   **Then** ha campi: `bracket` (FK Bracket CASCADE), `user` (FK User CASCADE), `video` (FK Video CASCADE), `created_at` (DateTimeField auto_now_add)
   **And** ha `unique_together = ('bracket', 'user')` — un utente può iscriversi una sola volta per bracket
   **And** ha `related_name` su ogni FK e `help_text` in italiano

3. **Given** il modello `Matchup` non esistente
   **When** viene creato in `cs_clips/models/matchup.py`
   **Then** ha campi: `bracket` (FK Bracket CASCADE), `round_number` (PositiveIntegerField), `position` (PositiveIntegerField), `entry_1` (FK ContestEntry SET_NULL nullable), `entry_2` (FK ContestEntry SET_NULL nullable), `winner` (FK ContestEntry SET_NULL nullable), `is_completed` (BooleanField default False)
   **And** ha `related_name` su ogni FK e `help_text` in italiano
   **And** ha `unique_together = ('bracket', 'round_number', 'position')` — una posizione per turno per bracket

4. **Given** un bracket con N partecipanti iscritti e status "registration"
   **When** l'admin avvia il torneo (transizione status a "active")
   **Then** il sistema genera automaticamente i matchup del primo turno a eliminazione diretta (FR40b)
   **And** se N non è potenza di 2, i partecipanti in eccesso ricevono un "bye" (avanzamento automatico al turno 2)
   **And** l'ordine dei partecipanti è randomizzato (seed-free, `random.shuffle`)

5. **Given** un matchup completato con vincitore assegnato
   **When** il matchup viene chiuso (`is_completed=True`, `winner` impostato)
   **Then** il vincitore avanza automaticamente al matchup successivo nel turno seguente (posizione calcolata: `position // 2` del turno successivo)

6. **Given** il turno finale (un solo matchup) completato
   **When** l'ultimo matchup viene chiuso
   **Then** il bracket `status` diventa "completed" e `current_round` rimane al turno finale

7. **Given** i 3 nuovi modelli registrati in `admin.py`
   **When** un admin accede al Django Admin
   **Then** può creare/modificare Bracket, vedere ContestEntry e Matchup con `list_display`, `list_filter`, `autocomplete_fields` appropriati
   **And** può avviare il torneo tramite admin action "Avvia torneo"

## Tasks / Subtasks

- [x] Task 1: Modello Bracket (AC: #1)
  - [x] 1.1 Creare `backend/cs_clips/models/bracket.py` con modello `Bracket` e `Status` TextChoices
  - [x] 1.2 Aggiungere export in `backend/cs_clips/models/__init__.py`
  - [x] 1.3 Creare migrazione: `python manage.py makemigrations`

- [x] Task 2: Modello ContestEntry (AC: #2)
  - [x] 2.1 Creare `backend/cs_clips/models/contest_entry.py` con modello `ContestEntry`
  - [x] 2.2 Aggiungere export in `backend/cs_clips/models/__init__.py`
  - [x] 2.3 Creare migrazione: `python manage.py makemigrations`

- [x] Task 3: Modello Matchup (AC: #3)
  - [x] 3.1 Creare `backend/cs_clips/models/matchup.py` con modello `Matchup`
  - [x] 3.2 Aggiungere export in `backend/cs_clips/models/__init__.py`
  - [x] 3.3 Creare migrazione: `python manage.py makemigrations`

- [x] Task 4: Applicare migrazioni (AC: #1, #2, #3)
  - [x] 4.1 `python manage.py migrate` — applicare tutte le migrazioni in sequenza

- [x] Task 5: Logica generazione bracket (AC: #4)
  - [x] 5.1 Creare `backend/cs_clips/utils/bracket_logic.py` con funzione `generate_bracket(bracket)`:
    - Verifica status == "registration" e almeno 2 iscritti
    - Calcola numero turni: `math.ceil(math.log2(N))`
    - Calcola bye: `2**num_rounds - N` partecipanti ricevono bye
    - Shuffle partecipanti (`random.shuffle`)
    - Crea matchup turno 1 (coppie consecutive, bye = matchup con `entry_2=None` e `is_completed=True`, `winner=entry_1`)
    - Crea matchup vuoti per turni successivi (senza entry, posizioni pre-calcolate)
    - Aggiorna `bracket.status = "active"`, `bracket.current_round = 1`
  - [x] 5.2 Creare funzione `advance_winner(matchup)`:
    - Verifica che `matchup.winner` sia impostato
    - Trova il matchup del turno successivo (`round_number + 1`, `position = matchup.position // 2`)
    - Assegna il vincitore a `entry_1` o `entry_2` del matchup successivo (in base a `matchup.position % 2`)
    - Se è l'ultimo matchup del bracket (turno finale completato), aggiorna `bracket.status = "completed"`
  - [x] 5.3 Creare funzione `close_matchup(matchup, winner_entry)`:
    - Imposta `matchup.winner = winner_entry`, `matchup.is_completed = True`
    - Chiama `advance_winner(matchup)` per propagare

- [x] Task 6: Registrazione Admin (AC: #7)
  - [x] 6.1 Aggiungere `BracketAdmin` in `admin.py`: `list_display = ["name", "status", "max_participants", "current_round", "created_by", "created_at"]`, `list_filter = ["status"]`, `search_fields = ["name"]`, `autocomplete_fields = ["created_by"]`
  - [x] 6.2 Aggiungere `ContestEntryAdmin`: `list_display = ["bracket", "user", "video", "created_at"]`, `list_filter = ["bracket"]`, `autocomplete_fields = ["bracket", "user", "video"]`
  - [x] 6.3 Aggiungere `MatchupAdmin`: `list_display = ["bracket", "round_number", "position", "entry_1", "entry_2", "winner", "is_completed"]`, `list_filter = ["bracket", "round_number", "is_completed"]`
  - [x] 6.4 Aggiungere admin action `start_bracket` su `BracketAdmin` che chiama `generate_bracket()`

- [x] Task 7: Test backend (AC: tutti)
  - [x] 7.1 Creare `backend/cs_clips/tests/test_brackets.py`
  - [x] 7.2 Test modello: creazione Bracket con tutti i campi, __str__, Status choices, ordering
  - [x] 7.3 Test modello: creazione ContestEntry, unique_together enforcement (409 su duplicato)
  - [x] 7.4 Test modello: creazione Matchup, unique_together enforcement
  - [x] 7.5 Test generate_bracket: 4 partecipanti → 2 matchup turno 1 + 1 matchup turno 2 (vuoto)
  - [x] 7.6 Test generate_bracket: 3 partecipanti → 1 bye + 2 matchup turno 1 + 1 matchup turno 2
  - [x] 7.7 Test generate_bracket: 8 partecipanti → 4 matchup turno 1 + 2 turno 2 + 1 finale
  - [x] 7.8 Test generate_bracket: meno di 2 partecipanti → errore
  - [x] 7.9 Test generate_bracket: bracket non in "registration" → errore
  - [x] 7.10 Test advance_winner: vincitore avanza al matchup corretto del turno successivo (entry_1 per posizioni pari, entry_2 per dispari)
  - [x] 7.11 Test close_matchup: ultimo matchup del torneo → bracket diventa "completed"
  - [x] 7.12 Test admin action: start_bracket da Django Admin funziona

- [x] Task 8: Verifica qualità (AC: tutti)
  - [x] 8.1 `ruff check backend/` — 0 errori
  - [x] 8.2 `ruff format --check backend/` — 0 errori
  - [x] 8.3 `python manage.py test` — tutti i test passano (nessuna regressione + nuovi test)
  - [x] 8.4 Verifica che il frontend compili senza errori: `npm run build` (nessuna modifica frontend in questa story)

## Dev Notes

### Stato attuale — Cosa esiste già

**Modelli esistenti (8):** User, Video, Contest, Rating, Comment, VideoLike, CommentLike, Notification
**Modelli da creare (3):** Bracket, ContestEntry, Matchup

**Decisione architetturale D2:** I modelli bracket sono completamente separati da Contest (sistema 1 = settimanale auto-gestito, sistema 2 = bracket Champions League). NON condividono modelli, NON condividono endpoint, NON condividono logica.

### Pattern di riferimento — Da seguire ESATTAMENTE

**Modelli — Pattern VideoLike/Notification:**
```python
from django.conf import settings
from django.db import models

class Bracket(models.Model):
    """Torneo bracket a eliminazione diretta."""

    class Status(models.TextChoices):
        REGISTRATION = "registration", "Registrazione aperta"
        ACTIVE = "active", "Torneo in corso"
        COMPLETED = "completed", "Torneo completato"

    name = models.CharField(max_length=200, help_text="Nome del torneo")
    # ... etc
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_brackets",
        help_text="Admin che ha creato il torneo",
    )
```

**Import User — CRITICO:**
- Usare `settings.AUTH_USER_MODEL` per FK a User (stringa, lazy reference) oppure `get_user_model()` in codice runtime
- MAI `from django.contrib.auth.models import User`

**FK on_delete:**
- `CASCADE` per relazioni forti: ContestEntry→Bracket, ContestEntry→User, ContestEntry→Video, Matchup→Bracket
- `SET_NULL` per relazioni deboli/nullable: Matchup→ContestEntry (entry_1, entry_2, winner)

**Admin — Pattern identico ai modelli esistenti:**
```python
@admin.register(Bracket)
class BracketAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "max_participants", "current_round", "created_by", "created_at"]
    list_filter = ["status"]
    search_fields = ["name"]
    autocomplete_fields = ["created_by"]
    readonly_fields = ["created_at"]
    actions = ["start_bracket"]

    @admin.action(description="Avvia torneo (genera matchup)")
    def start_bracket(self, request, queryset):
        from cs_clips.utils.bracket_logic import generate_bracket
        for bracket in queryset.filter(status=Bracket.Status.REGISTRATION):
            generate_bracket(bracket)
        self.message_user(request, f"Tornei avviati: {queryset.count()}")
```

### Logica Bracket — Eliminazione Diretta

**Generazione matchup — Algoritmo:**

Per N partecipanti:
1. `num_rounds = math.ceil(math.log2(N))`
2. `bracket_size = 2 ** num_rounds` (potenza di 2 ≥ N)
3. `num_byes = bracket_size - N`
4. Shuffle partecipanti casualmente
5. I primi `num_byes` partecipanti ricevono bye (matchup con entry_2=None, auto-completato)
6. Creare matchup per tutti i turni con posizioni pre-calcolate

**Esempio con 6 partecipanti:**
- `num_rounds = 3` (ceil(log2(6)) = 3), `bracket_size = 8`, `num_byes = 2`
- Turno 1: 4 matchup (pos 0-3), di cui 2 bye (auto-completati)
- Turno 2: 2 matchup (pos 0-1), vuoti (aspettano vincitori turno 1)
- Turno 3 (finale): 1 matchup (pos 0), vuoto

**Avanzamento vincitore:**
- Matchup a posizione `p` nel turno `r` → vincitore va a turno `r+1`, posizione `p // 2`
- Se `p % 2 == 0` → vincitore va in `entry_1` del matchup successivo
- Se `p % 2 == 1` → vincitore va in `entry_2` del matchup successivo

### Vincoli e Attenzioni

1. **NON creare endpoint API in questa story** — gli endpoint bracket vanno nella Story 6.2 (`cs_clips/api/brackets/`)
2. **NON creare componenti frontend** — il frontend bracket va nella Story 6.3
3. **NON modificare Contest o video_views** — i due sistemi contest sono completamente separati
4. **Routing:** NON creare `bracket_urls.py` — il routing andrà in `cs_clips/urls.py` nella Story 6.2
5. **Test con PostgreSQL attivo** — i test richiedono Docker con DB attivo
6. **Notification integration** — NON aggiungere notifiche bracket in questa story. I tipi `bracket_invite` e `bracket_turn` nel modello Notification esistono già come choices, l'integrazione sarà nella Story 6.2 quando gli endpoint API saranno disponibili
7. **`User.groups` ha `blank=False`** — ogni utente nei test DEVE avere almeno un gruppo assegnato (pattern: `Group.objects.get_or_create(name="user")` + `user.groups.add(group)`)
8. **Custom User `related_name`** — `groups` ha `related_name="custom_user_set"`, NON usare `group.user_set`, usare `User.objects.filter(groups=group)`

### File da creare/modificare

**Nuovi file:**
- `backend/cs_clips/models/bracket.py` — modello Bracket
- `backend/cs_clips/models/contest_entry.py` — modello ContestEntry
- `backend/cs_clips/models/matchup.py` — modello Matchup
- `backend/cs_clips/utils/bracket_logic.py` — logica generazione bracket e avanzamento
- `backend/cs_clips/tests/test_brackets.py` — test

**File da modificare:**
- `backend/cs_clips/models/__init__.py` — aggiungere export Bracket, ContestEntry, Matchup
- `backend/cs_clips/admin.py` — aggiungere BracketAdmin, ContestEntryAdmin, MatchupAdmin

### Project Structure Notes

- I 3 nuovi modelli seguono la convenzione `cs_clips/models/{modello_singolare}.py`
- La logica di business (generate_bracket, advance_winner) va in `cs_clips/utils/bracket_logic.py` (convenzione: un file per funzionalità)
- I test vanno in `cs_clips/tests/test_brackets.py` (convenzione: `test_{modulo}.py`)
- **Nessun conflitto** con la struttura esistente — i modelli bracket sono un dominio completamente nuovo

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic 6, Story 6.1] — Acceptance criteria e user story
- [Source: _bmad-output/planning-artifacts/architecture.md#D2] — Decisione modelli separati da Contest
- [Source: _bmad-output/planning-artifacts/architecture.md#Structure Patterns] — Checklist creazione nuovo modello
- [Source: _bmad-output/planning-artifacts/architecture.md#Sistema 2: Champions League Bracket] — Specifica modelli e logica
- [Source: _bmad-output/project-context.md#Struttura Backend Modulare] — Pattern file e import
- [Source: _bmad-output/project-context.md#Custom User Model] — get_user_model() obbligatorio
- [Source: _bmad-output/project-context.md#Anti-Pattern da Evitare] — Vincoli da rispettare
- [Source: backend/cs_clips/models/notification.py] — Pattern modello con FK esplicite e TextChoices
- [Source: backend/cs_clips/models/video_like.py] — Pattern modello con unique_together
- [Source: backend/cs_clips/admin.py] — Pattern registrazione admin

## Dev Agent Record

### Agent Model Used
Claude Opus 4.6

### Debug Log References
- Admin action test falliva per mancanza di MessageMiddleware su RequestFactory — risolto con FallbackStorage manuale
- ruff format richiedeva riformattazione di 2 file — applicata con `ruff format`

### Completion Notes List
- Creati 3 modelli: Bracket (con Status TextChoices), ContestEntry (unique_together bracket+user), Matchup (unique_together bracket+round+position)
- Tutti i modelli usano `settings.AUTH_USER_MODEL` per FK a User, `help_text` in italiano, `related_name` su ogni FK
- Logica bracket in `bracket_logic.py`: `generate_bracket()` (generazione matchup con bye), `advance_winner()` (propagazione vincitore), `close_matchup()` (chiusura matchup)
- Admin: BracketAdmin con action "Avvia torneo", ContestEntryAdmin, MatchupAdmin con list_display/list_filter/autocomplete_fields
- 17 nuovi test in `test_brackets.py` — tutti passano
- 257 test totali: 256 pass, 1 fail pre-esistente (`test_registration_assigns_toconfirm_group`)
- ruff check + format: 0 errori, frontend build OK

### Change Log
- 2026-03-08: Implementata Story 6.1 — 3 modelli bracket (Bracket, ContestEntry, Matchup), logica eliminazione diretta con bye, admin con action, 17 test
- 2026-03-08: Code Review fix — H1: transaction.atomic() in generate_bracket/close_matchup; M1: validazione max_participants; M2: validazione winner in close_matchup; M3: current_round progressione automatica; M4: error handling admin action; +4 nuovi test (21 totali)

### File List
**Nuovi:**
- `backend/cs_clips/models/bracket.py`
- `backend/cs_clips/models/contest_entry.py`
- `backend/cs_clips/models/matchup.py`
- `backend/cs_clips/utils/bracket_logic.py`
- `backend/cs_clips/tests/test_brackets.py`
- `backend/cs_clips/migrations/0010_bracket_contestentry_matchup.py`

**Modificati:**
- `backend/cs_clips/models/__init__.py`
- `backend/cs_clips/admin.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
