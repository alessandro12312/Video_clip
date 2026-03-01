# Story 2.1: Upload Clip con Validazione Completa

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utente registrato,
I want caricare clip con validazione automatica di durata e formato,
so that ricevo feedback immediato se il video non è accettabile.

## Acceptance Criteria (BDD)

### AC-1: Upload video valido con campo allow_download (FR7, FR11, FR12, FR15)

```gherkin
Scenario: Upload video con tutti i campi validi
  Given un utente autenticato con gruppo "user"
  When carica un video con durata tra 10s e 60s, formato MP4, dimensione < 500MB
  And imposta title="Ace con Jett", tag="clutch", allow_download=true
  Then il video viene salvato su MinIO con durata estratta via MoviePy
  And la risposta contiene il video con presigned URL, allow_download=true
  And il video è associato automaticamente al contest corrente per quel tag
  And lo status è 201 Created

Scenario: Upload video con allow_download=false
  Given un utente autenticato
  When carica un video con allow_download=false
  Then il campo allow_download viene salvato come False nel modello
  And la risposta contiene allow_download=false

Scenario: Upload video senza allow_download (default true)
  Given un utente autenticato
  When carica un video senza specificare allow_download
  Then il campo allow_download è True (valore default del modello)
```

### AC-2: Validazione durata — reject automatico (FR8, FR54)

```gherkin
Scenario: Video troppo corto (< 10 secondi)
  Given un utente autenticato
  When carica un video con durata di 5 secondi
  Then il video viene rifiutato con status 400
  And il messaggio è: "La durata del video deve essere tra 10 secondi e 1 minuto"
  And il file NON viene salvato su MinIO

Scenario: Video troppo lungo (> 60 secondi)
  Given un utente autenticato
  When carica un video con durata di 90 secondi
  Then il video viene rifiutato con status 400
  And il messaggio è: "La durata del video deve essere tra 10 secondi e 1 minuto"
  And il file NON viene salvato su MinIO

Scenario: Video con durata esattamente 10 secondi (limite inferiore)
  Given un utente autenticato
  When carica un video con durata di 10 secondi
  Then il video viene accettato (status 201)

Scenario: Video con durata esattamente 60 secondi (limite superiore)
  Given un utente autenticato
  When carica un video con durata di 60 secondi
  Then il video viene accettato (status 201)
```

### AC-3: Validazione formato — reject automatico (FR9)

```gherkin
Scenario: File con formato non supportato
  Given un utente autenticato
  When carica un file con estensione .gif
  Then il file viene rifiutato con status 400
  And il messaggio è: "Formato non supportato. Formati accettati: MP4, MOV, AVI, MKV, WebM"

Scenario: File con content-type non video
  Given un utente autenticato
  When carica un file con content_type="image/png" (rinominato .mp4)
  Then il file viene rifiutato con status 400
  And il messaggio contiene "Formato non supportato"
```

### AC-4: Validazione dimensione file (FR9)

```gherkin
Scenario: File troppo grande (> 500MB)
  Given un utente autenticato
  When carica un file di 600MB
  Then il file viene rifiutato con status 400
  And il messaggio è: "Il file supera la dimensione massima di 500MB"
```

### AC-5: File corrotto o codec non supportato (edge case MoviePy)

```gherkin
Scenario: File corrotto — MoviePy non riesce a leggere i metadati
  Given un utente autenticato
  When carica un file video corrotto che MoviePy non riesce ad aprire
  Then il video viene rifiutato con status 400
  And il messaggio è: "Impossibile leggere i metadati del video. Verifica che il file non sia corrotto"
  And il file temporaneo viene pulito (nessun leak)
```

### AC-6: Permessi — solo utenti confermati possono caricare (non-regressione)

```gherkin
Scenario: Utente toconfirm tenta upload
  Given un utente con gruppo "toconfirm"
  When tenta di caricare un video (POST /api/videos/)
  Then riceve status 403 (Forbidden)
  And il messaggio indica permessi insufficienti

Scenario: Utente non autenticato tenta upload
  Given un utente non autenticato
  When tenta di caricare un video
  Then riceve status 401 (Unauthorized)
```

### AC-7: Frontend mostra errori backend specifici (FR16)

```gherkin
Scenario: Frontend mostra errore di validazione backend
  Given un utente sulla pagina di upload (/carica)
  When il backend rifiuta il video per durata/formato/dimensione
  Then la modale di errore mostra il messaggio specifico dal campo "detail" della risposta
  And il bottone "Riprova" torna allo step del form per correggere

Scenario: Frontend mostra errore di rete
  Given un utente che sta caricando un video
  When la connessione si interrompe durante l'upload
  Then appare un messaggio di errore generico
  And il bottone "Riprova" permette di ri-tentare l'upload
```

### AC-8: Serializer output include tutti i campi attesi dal frontend

```gherkin
Scenario: Risposta upload contiene tutti i campi del tipo Video frontend
  Given un upload completato con successo
  When il backend risponde con 201
  Then la risposta contiene: id, title, file, file_url, uploader (username string),
       average_rating, views, tag, duration, allow_download, contest, created_at, updated_at
  And allow_download è booleano
  And views è intero (default 0 per video nuovo)
  And average_rating è float (default 0.0 per video nuovo)
```

## Tasks / Subtasks

- [x] **Task 1: Aggiungere campo `allow_download` al modello Video** (AC: #1, #8)
  - [x]1.1 In `backend/cs_clips/models/video.py`, aggiungere `allow_download = models.BooleanField(default=True, help_text="Consenti il download della clip ad altri utenti")`
  - [x]1.2 Creare e applicare la migrazione: `python manage.py makemigrations cs_clips && python manage.py migrate`
  - [x]1.3 Aggiornare `VideoAdmin` se necessario per mostrare il nuovo campo

- [x] **Task 2: Aggiungere validazione durata nel serializer** (AC: #2, #5)
  - [x]2.1 In `VideoInputSerializer.create()`, dopo l'estrazione durata con MoviePy, aggiungere validazione:
    ```python
    if duration < 10 or duration > 60:
        raise serializers.ValidationError(
            "La durata del video deve essere tra 10 secondi e 1 minuto"
        )
    ```
  - [x]2.2 Assicurarsi che il file temporaneo venga pulito anche in caso di ValidationError (il `finally` block è già presente)
  - [x]2.3 Verificare che il file NON venga salvato su MinIO se la validazione fallisce (la ValidationError viene lanciata prima di `super().create()`)

- [x] **Task 3: Aggiungere validazione formato e dimensione** (AC: #3, #4)
  - [x]3.1 In `VideoInputSerializer`, aggiungere metodo `validate_file(self, value)`:
    ```python
    ALLOWED_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
    ALLOWED_CONTENT_TYPES = {'video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/webm'}
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    ```
  - [x]3.2 Validare estensione file (case-insensitive) e content_type
  - [x]3.3 Validare dimensione file (`value.size > MAX_FILE_SIZE`)
  - [x]3.4 Messaggi di errore in italiano come da AC

- [x] **Task 4: Aggiornare i serializer per includere allow_download e views** (AC: #1, #8)
  - [x]4.1 In `VideoInputSerializer`: aggiungere `allow_download` ai `fields` (opzionale, con default dal modello)
  - [x]4.2 In `VideoOutputSerializer`: aggiungere `allow_download` e `views` ai `fields` e a `read_only_fields`
  - [x]4.3 In `VideoUpdateSerializer`: aggiungere `allow_download` ai `fields` (l'utente può cambiarlo dopo l'upload)
  - [x]4.4 Verificare che `duration`, `uploader`, `contest`, `views`, `average_rating`, `file_url` siano tutti in `read_only_fields` nel serializer di output

- [x] **Task 5: Scrivere test backend** (AC: #1-#6)
  - [x]5.1 Creare `backend/cs_clips/tests/test_upload_validation.py`
  - [x]5.2 Test upload con video valido → 201, risposta contiene allow_download, views, duration
  - [x]5.3 Test allow_download=false → campo salvato correttamente
  - [x]5.4 Test allow_download default → true quando non specificato
  - [x]5.5 Test durata < 10s → 400 con messaggio specifico
  - [x]5.6 Test durata > 60s → 400 con messaggio specifico
  - [x]5.7 Test durata esattamente 10s → 201 (boundary)
  - [x]5.8 Test durata esattamente 60s → 201 (boundary)
  - [x]5.9 Test formato non supportato (estensione) → 400 con messaggio specifico
  - [x]5.10 Test content-type non video → 400 con messaggio specifico
  - [x]5.11 Test file > 500MB → 400 con messaggio specifico
  - [x]5.12 Test file corrotto (MoviePy exception) → 400 con messaggio specifico
  - [x]5.13 Test utente toconfirm → 403
  - [x]5.14 Test utente non autenticato → 401
  - [x]5.15 Test shape risposta → tutti i campi presenti nel tipo Video frontend
  - [x]5.16 Usare helper da conftest.py (`create_authenticated_user`, `create_toconfirm_user`, `create_api_client_authenticated`)
  - [x]5.17 Per test di durata: mockare `MoviePy VideoFileClip` per controllare durata senza file reali
  - [x]5.18 Eseguire `ruff check backend/` e `ruff format backend/` — zero errori

- [x] **Task 6: Verificare integrazione frontend↔backend** (AC: #7, #8)
  - [x]6.1 Verificare che il `FormData` inviato dal frontend (`allow_download` come stringa "true"/"false") sia correttamente interpretato dal serializer Django (BooleanField DRF gestisce stringhe)
  - [x]6.2 Verificare che la risposta di errore 400 contenga `{detail: "..."}` compatibile con `error.response?.data?.detail` nel frontend
  - [x]6.3 Verificare che la pagina `/carica` mostri correttamente il messaggio di errore backend
  - [x]6.4 Verificare che `npm run build` frontend compili senza errori
  - [x]6.5 Eseguire la suite test completa backend e verificare zero regressioni

## Dev Notes

### Contesto Critico

Questa è la **prima story di Epic 2** e la prima che tocca la pipeline di upload video. Il backend ha già un meccanismo di upload funzionante (MoviePy per durata, MinIO per storage) ma con lacune critiche:

1. **Nessuna validazione durata** — MoviePy estrae la durata ma non la valida (< 10s o > 60s passano)
2. **Nessuna validazione formato** — qualsiasi file passa, il frontend valida solo l'estensione lato client
3. **Nessuna validazione dimensione** — nessun controllo server-side (il frontend limita a 500MB ma il backend accetta tutto)
4. **Campo `allow_download` mancante** — il frontend lo invia nel FormData ma il backend lo ignora
5. **Campo `views` non serializzato** — il modello ha il campo ma il serializer non lo include nella risposta

### Stato Attuale del Codice

**Pipeline di upload attuale (`VideoInputSerializer.create()`):**

```python
def create(self, validated_data):
    uploaded_file = validated_data.get("file")
    if not uploaded_file:
        raise serializers.ValidationError("Il file video è obbligatorio.")

    try:
        # TemporaryUploadedFile → usa temporary_file_path()
        # InMemoryUploadedFile → scrive su temp file, poi usa VideoFileClip
        clip = VideoFileClip(path)
        duration = int(clip.duration)
        clip.close()
        validated_data["duration"] = duration
    except Exception:
        raise serializers.ValidationError("Impossibile leggere i metadati del video.")
    finally:
        # Pulizia temp file

    return super().create(validated_data)
```

**Il punto di intervento è PRIMA di `super().create()`**: la validazione della durata va dopo l'estrazione MoviePy e prima del salvataggio. La validazione formato/dimensione va in `validate_file()` che DRF chiama prima di `create()`.

**Frontend — Pagina upload (`/carica`):**
- File: `frontend/src/app/(main)/carica/page.tsx`
- Già implementato con: dropzone, metadata form (title, tag, allow_download checkbox), progress bar, error display
- `FormData` include: `file`, `title`, `tag`, `allow_download` (come stringa)
- Error handling: cattura `error.response?.data?.detail` e mostra in alert

### Pattern da Seguire

**Validazione nel serializer (non nella view):**
La logica di validazione va nel serializer per coerenza con il pattern Django REST Framework:
- `validate_file(self, value)` → formato ed dimensione (campo-level validation)
- Durata → in `create()` dopo estrazione MoviePy (cross-field, dipende dall'analisi del file)

**Messaggio ValidationError:**
```python
raise serializers.ValidationError({"detail": "messaggio"})
# OPPURE, se il global exception handler gestisce già:
raise serializers.ValidationError("messaggio")
```
Verificare che il global exception handler converta ValidationError in formato `{code: "validation_error", detail: "messaggio"}` — il frontend si aspetta `error.response.data.detail`.

**Migrazione `allow_download`:**
```python
# In models/video.py
allow_download = models.BooleanField(
    default=True,
    help_text="Consenti il download della clip ad altri utenti"
)
```

**Test con mock MoviePy (per controllare durata senza file reali):**
```python
from unittest.mock import patch, MagicMock

@patch("cs_clips.api.videos.video_serializers.VideoFileClip")
def test_duration_too_short(self, mock_vfc):
    mock_clip = MagicMock()
    mock_clip.duration = 5  # 5 secondi — troppo corto
    mock_clip.close = MagicMock()
    mock_vfc.return_value = mock_clip

    response = self.client.post("/api/videos/", data=form_data, format="multipart")
    self.assertEqual(response.status_code, 400)
    self.assertIn("durata", response.data["detail"].lower())
```

**Test con file SimpleUploadedFile (per validazione formato):**
```python
from django.core.files.uploadedfile import SimpleUploadedFile

# File con estensione non supportata
fake_file = SimpleUploadedFile("test.gif", b"fake content", content_type="image/gif")
```

### Anti-Pattern da Evitare

- **MAI** validare la durata nella view — deve stare nel serializer (coerenza pattern DRF)
- **MAI** salvare il file su MinIO prima della validazione — se la durata è fuori range, il file non deve essere salvato
- **MAI** usare `filter()` o logica condizionale complessa per `allow_download` — è un semplice BooleanField con default
- **MAI** dimenticare `read_only_fields` per campi calcolati (`views`, `duration`, `average_rating`, `file_url`, `uploader`) — lezione Epic 1 (sicurezza H1)
- **MAI** importare `from cs_clips.models.user import User` — usare `get_user_model()`
- **MAI** creare test utenti senza assegnare un gruppo — usare helper da conftest.py
- **MAI** ignorare la pulizia del file temporaneo in caso di ValidationError — il `finally` block è fondamentale
- **MAI** testare solo lo status code — ogni test deve verificare anche il body/messaggio della risposta (lezione Epic 1)

### Informazioni Tecniche Aggiornate

- **MoviePy (imageio-ffmpeg)** — Usato per estrazione durata. `VideoFileClip(path)` → `clip.duration` (float, secondi). Non supporta tutti i codec — file con codec esotici possono fallire. Sempre chiudere `clip.close()` per rilasciare file handle.
- **MinIO storage** — `django-minio-storage` gestisce upload automatico su `model.save()`. Il file viene salvato solo quando `super().create()` viene chiamato nel serializer. Se la ValidationError viene lanciata prima, il file non viene mai salvato su MinIO.
- **DRF BooleanField da FormData** — Django REST Framework gestisce automaticamente stringhe `"true"`/`"false"` da FormData e le converte in booleani Python. Il frontend invia `String(allowDownload)` che diventa `"true"` o `"false"` — DRF lo converte correttamente.
- **TemporaryUploadedFile vs InMemoryUploadedFile** — Django usa `TemporaryUploadedFile` per file > 2.5MB (configurabile con `FILE_UPLOAD_MAX_MEMORY_SIZE`). Per file piccoli usa `InMemoryUploadedFile`. Il serializer gestisce entrambi i casi.
- **django-filter 24.3** — Già installato e configurato (Story 1-4). Non necessita modifiche per questa story.
- **ruff** — Linter+formatter configurato. Zero errori è requisito gate per ogni commit.

### Project Structure Notes

**File da modificare:**
- `backend/cs_clips/models/video.py` — aggiungere `allow_download` BooleanField
- `backend/cs_clips/api/videos/video_serializers.py` — validazione formato/dimensione, validazione durata, aggiornare fields/read_only_fields
- `backend/cs_clips/api/videos/video_views.py` — nessuna modifica necessaria (la logica è nel serializer)

**File da creare:**
- `backend/cs_clips/tests/test_upload_validation.py` — test per tutte le validazioni
- Migrazione Django (auto-generata)

**File frontend — nessuna modifica necessaria:**
- La pagina upload (`/carica`) è già completa e gestisce `allow_download`, errori backend e retry
- I tipi TypeScript (`Video`, `VideoUploadData`) includono già `allow_download`
- L'unico requisito è che la risposta backend matchi la shape `Video` del frontend

### Intelligence dalla Story 1.4 (Precedente)

**Pattern stabiliti da riusare:**
- `get_user_model()` ovunque — MAI import diretto
- Test con `APITestCase`, `force_authenticate`, helper da `conftest.py`
- Formato errori: `{code, detail}` dal global exception handler
- Ruff check + format obbligatori prima di ogni commit
- Test devono asserire sul contenuto della risposta, non solo sullo status code
- `read_only_fields` espliciti per tutti i campi calcolati/identità (lezione H1 Story 1-2)
- Error handling frontend: `isError` + `ErrorMessage` obbligatorio (lezione H2 Story 1-4)
- `self.get_serializer()` invece di `Serializer()` diretto
- Annotazione queryset per evitare N+1 (già in `get_queryset()` con `Avg`)

**Problemi risolti in story precedenti:**
- N+1 queries: annotazioni queryset (Story 1-2, 1-4)
- Paginazione custom actions: `self.paginate_queryset()` (Story 1-3)
- NumberFilter per FK: evita 400 per ID inesistenti (Story 1-4)
- `has_object_permission`: ora gestisce sia `obj.uploader` che `obj.user` (Story 1-2)

**Debito tecnico rilevante per questa story:**
- `has_object_permission` — Fixato per User PATCH in Story 1-2, ma verificare che funzioni per DELETE Video (debito T1 della retro Epic 1)
- Action `/following/` ritorna array vuoto non paginato — bug pre-esistente, non da fixare in questa story

### Git Intelligence

**Ultimi commit (pattern recenti):**
- `a97a544` — Story 1.3 + Story 1.4: follow paginato, filtro video server-side, retro Epic 1
- `859f0a8` — Story 1.1 + Story 1.2: auth end-to-end e profilo utente con bio
- Pattern commit: `feat: Story X.Y — descrizione breve`

**Insight rilevanti:**
- La suite test attuale ha 77 test passanti — non introdurre regressioni
- `conftest.py` ha 6 helper: `create_authenticated_user`, `create_toconfirm_user`, `create_admin_user`, `create_api_client_authenticated`, `create_sample_video`, `create_sample_contest`
- `create_sample_video` bypassa MoviePy e usa `Video.objects.create()` con durata hardcoded a 30s — utile per test che non riguardano la validazione upload
- Per test di validazione upload servono mock di MoviePy (non file reali) — pattern `@patch`

### Preparazione necessaria dalla Retro Epic 1

| # | Task pre-requisito | Status | Impatto su questa story |
|---|---------------------|--------|-------------------------|
| T1 | Verificare `has_object_permission` per DELETE Video | DA FARE | Necessario per AC-6 (permessi) |
| T3 | Configurare test con MinIO (almeno fixture locale) | ESISTENTE | `create_sample_video` bypassa già MinIO per test di base |

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 2, Story 2.1]
- [Source: _bmad-output/planning-artifacts/architecture.md — FR7-9, FR11-12, FR15-16, FR54]
- [Source: _bmad-output/planning-artifacts/prd.md — Upload validation, Video Processing]
- [Source: backend/cs_clips/models/video.py — Video model senza allow_download]
- [Source: backend/cs_clips/api/videos/video_serializers.py — VideoInputSerializer con MoviePy, senza validazione durata/formato]
- [Source: backend/cs_clips/api/videos/video_views.py — VideoViewSet con perform_create, throttle upload]
- [Source: backend/cs_clips/permissions.py — RoleBasedPermission con has_object_permission]
- [Source: backend/cs_clips/tests/conftest.py — 6 helper functions]
- [Source: frontend/src/app/(main)/carica/page.tsx — Upload page con dropzone, metadata, progress, error handling]
- [Source: frontend/src/types/video.ts — Video interface con allow_download: boolean]
- [Source: frontend/src/lib/api/videos.ts — videosApi.upload() con FormData e onProgress]
- [Source: _bmad-output/implementation-artifacts/1-4-filtro-video-per-uploader-backend.md — pattern test, anti-pattern, learnings]
- [Source: _bmad-output/implementation-artifacts/epic-1-retro-2026-03-01.md — action items, debito tecnico, preparazione Epic 2]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Fix DRF BooleanField.initial=False: campo assente in multipart veniva trattato come False — aggiunto `allow_download = serializers.BooleanField(default=True, required=False)` esplicito
- Fix view create: `super().create()` usava `VideoInputSerializer` per la risposta — modificato per restituire `VideoOutputSerializer` (AC-8)
- Fix except chain: `except serializers.ValidationError: raise` aggiunto prima del generico `except Exception` per evitare rewrapping dei messaggi di validazione
- Test file size: `SimpleUploadedFile.size` override non funziona con API test client (parser ricrea il file) — risolto con `@patch` su `MAX_FILE_SIZE`

### Completion Notes List

- ✅ Task 1: Campo `allow_download = BooleanField(default=True)` aggiunto al modello Video, migrazione 0005 creata e applicata, VideoAdmin aggiornato
- ✅ Task 2: Validazione durata 10s–60s aggiunta in `create()` dopo estrazione MoviePy, prima di `super().create()`. Messaggio errore file corrotto aggiornato per AC-5
- ✅ Task 3: Metodo `validate_file()` aggiunto con validazione estensione (5 formati), content_type e dimensione (500MB). Messaggi in italiano
- ✅ Task 4: Serializer aggiornati — `VideoOutputSerializer` include `allow_download` e `views` nei fields e read_only_fields; `VideoInputSerializer` include `allow_download` con default esplicito; `VideoUpdateSerializer` include `allow_download`; view `create()` restituisce `VideoOutputSerializer` per AC-8
- ✅ Task 5: 14 test scritti in `test_upload_validation.py` — coprono AC-1 (3 test allow_download), AC-2 (4 test durata con boundary), AC-3 (2 test formato), AC-4 (1 test dimensione), AC-5 (1 test corrotto), AC-6 (2 test permessi), AC-8 (1 test shape). Ruff 0 errori
- ✅ Task 6: Integrazione verificata — FormData con `String(allowDownload)` compatibile con DRF BooleanField, errori 400 con `{detail: "..."}` compatibili con frontend, `npm run build` OK, 90 test passanti (0 regressioni)

### File List

**Modificati:**
- `backend/cs_clips/models/video.py` — aggiunto campo `allow_download`
- `backend/cs_clips/api/videos/video_serializers.py` — validazione formato/dimensione/durata spostata in `create()` (fix prefisso errore), `allow_download` esplicito, aggiornamento fields/read_only_fields
- `backend/cs_clips/api/videos/video_views.py` — `create()` restituisce `VideoOutputSerializer`, OpenAPI schema con `allow_download`, cleanup `perform_create`
- `backend/cs_clips/admin.py` — `allow_download` in `VideoAdmin.list_display`

**Creati:**
- `backend/cs_clips/tests/test_upload_validation.py` — 14 test per validazione upload
- `backend/cs_clips/migrations/0005_add_allow_download_to_video.py` — migrazione campo `allow_download`

**Non modificati (frontend):**
- Nessuna modifica frontend necessaria — la pagina `/carica` è già compatibile

## Change Log

| Data | Descrizione |
|------|-------------|
| 2026-03-01 | Implementazione Story 2.1: campo allow_download, validazione durata/formato/dimensione, 14 test, aggiornamento serializer e view per AC-8 |
| 2026-03-01 | Code review: 6 fix applicati (H1: messaggi errore senza prefisso "Campo 'file':", H2: test contest auto-associazione, M1: OpenAPI allow_download, M2: cleanup temp dir test, M3: assertEqual per messaggi errore, M4: cleanup perform_create). 91 test OK, ruff 0 errori |
