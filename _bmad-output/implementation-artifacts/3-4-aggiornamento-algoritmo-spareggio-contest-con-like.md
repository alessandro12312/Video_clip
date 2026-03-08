# Story 3.4: Aggiornamento Algoritmo Spareggio Contest con Like

Status: done

## Story

As a sistema,
I want che l'algoritmo di spareggio contest usi i like reali invece dei commenti come fallback,
So that la classifica contest riflette il reale engagement della community.

## Acceptance Criteria

1. **Given** l'algoritmo di spareggio in `desempate.py`
   **When** calcola il vincitore in caso di parimerito
   **Then** usa il peso 20% basato su `VideoLike.count` per video (non più commenti come fallback) (FR42a)
   **And** i pesi restano: 50% numero voti, 30% visualizzazioni, 20% like

2. **Given** un video senza like
   **When** il sistema calcola lo spareggio
   **Then** il peso like contribuisce 0 senza errori

## Tasks / Subtasks

- [x] Task 1: Aggiornare `desempate_ponderato()` in `desempate.py` (AC: #1, #2)
  - [x] 1.1 Sostituire `num_comments = [v.comments.count() for v in videos]` con `num_likes = [v.likes.count() for v in videos]`
  - [x] 1.2 Rinominare chiave weights da `"comments"` a `"likes"` (peso 0.2 invariato)
  - [x] 1.3 Aggiornare variabili: `n_comments_norm` → `n_likes_norm`
  - [x] 1.4 Aggiornare docstring: rimuovere "commenti", aggiungere "like"
- [x] Task 2: Aggiornare management command `test_spareggio.py` (AC: #1)
  - [x] 2.1 Creare VideoLike al posto dei commenti nel setup test
  - [x] 2.2 Aggiornare output atteso
- [x] Task 3: Aggiornare/creare test automatici per spareggio con like (AC: #1, #2)
  - [x] 3.1 Test: vincitore corretto con dati noti (video con più like vince a parità di voti/views)
  - [x] 3.2 Test: video con 0 like non causa errori, contribuisce 0 al punteggio
  - [x] 3.3 Test: tutti i video con stesso numero like → `normalize()` ritorna tutti 1
  - [x] 3.4 Test: integrazione `EndContestView` con like reali (spareggio chiama algoritmo aggiornato)
  - [x] 3.5 Test: integrazione `close_contests` management command con like reali
- [x] Task 4: Verifica qualità (AC: #1, #2)
  - [x] 4.1 `python manage.py test` — tutti passanti, nessuna regressione
  - [x] 4.2 `ruff check backend/` — 0 errori
  - [x] 4.3 Nessun commento `.count()` rimasto nell'algoritmo di spareggio

## Dev Notes

### Cosa cambia

Modifica **chirurgica**: sostituire `comments.count()` con `likes.count()` nell'algoritmo di spareggio. Il modello `VideoLike` è già implementato (Story 3.1) con `related_name="likes"` su Video.

### File da modificare

| File | Modifica |
|------|----------|
| `backend/cs_clips/utils/desempate.py` | `comments.count()` → `likes.count()`, rinominare variabili e chiave peso |
| `backend/cs_clips/management/commands/test_spareggio.py` | Setup: creare `VideoLike` al posto di `Comment` |
| `backend/cs_clips/tests/test_contest.py` (o nuovo file) | Aggiungere test spareggio con like |

### File da NON toccare

- `contest_views.py` — chiama `desempate_ponderato(top_videos)` senza cambiamenti, i video passati hanno già la relazione `likes`
- `close_contests.py` — stessa situazione, chiama `desempate_ponderato()` che internamente ora userà `likes`
- Modelli — nessuna migrazione necessaria
- Frontend — nessuna modifica (story solo backend)

### Algoritmo attuale vs target

**Attuale** (`desempate.py`):
```python
num_comments = [v.comments.count() for v in videos]
weights = {"ratings": 0.5, "comments": 0.2, "views": 0.3}
```

**Target**:
```python
num_likes = [v.likes.count() for v in videos]
weights = {"ratings": 0.5, "likes": 0.2, "views": 0.3}
```

### Dipendenza critica: VideoLike.related_name

`VideoLike` model (da Story 3.1) ha `related_name="likes"` su Video:
```python
class VideoLike(models.Model):
    video = models.ForeignKey("Video", on_delete=models.CASCADE, related_name="likes")
```
Quindi `video.likes.count()` ritorna il numero di like. Nessun import aggiuntivo necessario in `desempate.py` (il modulo non importa modelli, lavora sugli oggetti Video passati).

### Edge case: normalize() con tutti 0

La funzione `normalize()` gestisce già il caso `max == min`:
```python
def normalize(arr):
    arr = np.array(arr)
    if arr.max() == arr.min():
        return np.ones(len(arr))
    return (arr - arr.min()) / (arr.max() - arr.min())
```
Se tutti i video hanno 0 like → `max == min == 0` → ritorna `[1, 1, ...]` → tutti contribuiscono ugualmente, spareggio deciso dagli altri pesi. Nessuna divisione per zero.

### Pattern test da seguire

- **Framework**: `django.test.TestCase` + `APITestCase`
- **Naming**: `test_{action}_{scenario}_{expected}`
- **Fixture**: usare `conftest.py` helpers: `create_authenticated_user()`, `create_api_client_authenticated()`
- **Assertion**: status code + formato risposta + contenuto specifico
- **VideoLike creation**: `VideoLike.objects.create(user=user, video=video)` — unique_together(user, video)
- **Import**: `from cs_clips.models.video_like import VideoLike`

### Test spareggio nella architecture.md

Requisito architetturale critico #5:
> `desempate.py` con dati noti produce vincitore atteso, gestisce parità, gestisce contest senza video

I test devono coprire:
1. Dati noti → vincitore atteso (con like al posto di commenti)
2. Parità totale (tutti uguali) → `np.argmax` ritorna primo (deterministico)
3. Video senza like → contribuisce 0, no errori
4. Integrazione end-to-end con `EndContestView`

### Intelligence da Story 3.3

- `PopupComments` endpoint usa `like_count` annotazione con `Count("likes", distinct=True)` — pattern consistente
- Cache invalidation pattern per like: invalidare query keys dopo mutazione
- 186 test backend baseline (185 pass, 1 pre-existing fail `test_registration_assigns_toconfirm_group`)
- Ruff 0 errori come baseline

### Git commit recenti

- `da01a68` — feat: Story 3.1 (modelli VideoLike/CommentLike + endpoint like/unlike)
- Prefix: `feat:` per feature story
- Pattern suggerito: `feat: Story 3.4 — aggiornamento algoritmo spareggio con like reali`

### Project Structure Notes

- `backend/cs_clips/utils/desempate.py` — algoritmo spareggio (unico file utils)
- `backend/cs_clips/management/commands/test_spareggio.py` — demo/test manuale (non test automatico)
- `backend/cs_clips/management/commands/close_contests.py` — chiusura automatica contest
- `backend/cs_clips/api/contests/contest_views.py` — `EndContestView` + `ContestWinnersView`
- `backend/cs_clips/models/video_like.py` — modello VideoLike (related_name="likes")
- Nessun conflitto con project structure

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 3.4] — AC e requisiti FR42a
- [Source: _bmad-output/planning-artifacts/architecture.md#Strategia Testing Risk-Based] — test critico #5 spareggio
- [Source: backend/cs_clips/utils/desempate.py] — algoritmo attuale
- [Source: backend/cs_clips/api/contests/contest_views.py] — flow chiusura contest
- [Source: backend/cs_clips/management/commands/close_contests.py] — auto-close
- [Source: backend/cs_clips/models/video_like.py] — modello VideoLike con related_name="likes"

## Dev Agent Record

### Agent Model Used
Claude Opus 4.6

### Debug Log References
- RED phase: 4 test falliti correttamente (algoritmo usava ancora comments)
- GREEN phase: tutti 6 test passanti dopo sostituzione comments → likes
- Ruff: 1 import inutilizzato (numpy in test file) corretto

### Completion Notes List
- Sostituito `v.comments.count()` con `v.likes.count()` in `desempate_ponderato()` (pesi invariati: 50% ratings, 30% views, 20% likes)
- Aggiornate variabili (`num_comments` → `num_likes`, `n_comments_norm` → `n_likes_norm`), chiave peso (`"comments"` → `"likes"`), docstring
- Management command `test_spareggio.py`: sostituiti Comment con VideoLike nel setup, aggiornato output (`n_commenti` → `n_like`)
- Creato `test_desempate.py` con 6 test: 4 unitari (vincitore con like, zero like, parità like, likes vs comments) + 1 integrazione EndContestView + 1 integrazione close_contests command
- 193 test totali: 192 pass, 1 fail pre-esistente (test_registration_assigns_toconfirm_group — bug noto non legato a questa story)
- Ruff 0 errori

### File List
- `backend/cs_clips/utils/desempate.py` — modificato (comments → likes, guard clause lista vuota/singola)
- `backend/cs_clips/management/commands/test_spareggio.py` — modificato (Comment → VideoLike)
- `backend/cs_clips/tests/test_desempate.py` — nuovo (8 test per spareggio con like)

## Senior Developer Review (AI)

**Reviewer:** AcchippameQuisso — 2026-03-08
**Outcome:** Approved with fixes applied

### Fix applicati (3 MEDIUM, 2 LOW):
- **M1** (FIXED): Rimosso `tempfile.NamedTemporaryFile().name` fragile su Windows → sostituito con stringhe statiche `"test_video_*.mp4"`
- **M2** (FIXED): Aggiunta guard clause in `desempate_ponderato()` per lista vuota (`return None`) e singola (`return videos[0]`) + 2 nuovi test edge case
- **M3** (FIXED): Assertion `assertIsNotNone(finalists)` → verifica `len(finalists) == 2` + titoli specifici
- **L1** (FIXED): Import `Comment` spostato da body del test al top-level del modulo
- **L2** (FIXED): Input validation aggiunta in `desempate_ponderato()` (guard clause)

### Test post-review: 8/8 pass, ruff 0 errori

## Change Log
- 2026-03-08: Story 3.4 — Algoritmo spareggio aggiornato da commenti a like reali (FR42a). 6 nuovi test, 0 regressioni.
- 2026-03-08: Code review — 5 fix applicati (3M+2L), 2 test edge case aggiunti, guard clause in desempate_ponderato(). 8 test totali.
