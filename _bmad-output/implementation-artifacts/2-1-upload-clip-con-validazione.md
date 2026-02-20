# Story 2.1: Upload Clip con Validazione

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utente registrato,
I want caricare una clip video dalla mia galleria con titolo, tag e opzione download,
so that possa condividere i miei momenti di gioco con la community dopo che il sistema ha validato formato, durata e dimensione del file.

## Acceptance Criteria

1. **AC1 — Upload con metadati e progress bar**
   Given: un utente autenticato sulla pagina `/carica`
   When: seleziona un file video e compila titolo (max 100 char), tag tipo (clutch/funny/fail) e opzione allow_download
   Then: il file viene inviato direttamente a Django via upload CORS con progress bar in tempo reale (gradiente viola→ciano)

2. **AC2 — Validazione durata (10s – 1min)**
   Given: un file video con durata compresa tra 10s e 1min
   When: il backend riceve il file e calcola la durata via moviepy
   Then: la validazione passa e il processing continua

   Given: un file video con durata fuori range (< 10s o > 1min)
   When: il backend valida il file
   Then: viene restituito errore 400 con messaggio "Il video deve durare tra 10 secondi e 1 minuto" e il record Video viene eliminato (rollback)

3. **AC3 — Validazione formato (whitelist)**
   Given: un file video in formato nella whitelist (MP4, MOV, AVI, MKV, WebM)
   When: il backend riceve il file
   Then: la validazione formato passa

   Given: un file in formato non supportato
   When: il backend valida il file
   Then: viene restituito errore 400 con messaggio "Formato non supportato. Formati accettati: MP4, MOV, AVI, MKV, WebM"

4. **AC4 — Validazione dimensione (max 500MB)**
   Given: un file che supera 500MB
   When: il backend valida il file
   Then: viene restituito errore 400 con messaggio "Il file supera la dimensione massima di 500MB"

5. **AC5 — Campo allow_download nel form**
   Given: un utente sul form di upload
   When: compila i metadati della clip
   Then: può impostare allow_download (checkbox, default attivo) che viene salvato nel modello Video

## Tasks / Subtasks

> **NOTA:** Questa story tocca sia backend (validazione, settings) sia frontend (form allow_download, validazione client-side, UX error messages). Il grosso del lavoro è backend validation + Django settings per file grandi.

### Codice esistente (già implementato)

- [x] Modello `Video` in `backend/cs_clips/models.py` — ha `title`, `file`, `tag`, `duration`, `allow_download`, `uploader`. Campo `allow_download` BooleanField(default=True) già presente (migration 0015)
- [x] `VideoSerializer` in `backend/cs_clips/serializers.py` — `create()` calcola durata automaticamente via moviepy. Include `allow_download` nei fields. Se moviepy fallisce, fa rollback (delete record)
- [x] `VideoViewSet` in `backend/cs_clips/views.py` — endpoint `POST /api/videos/` già funzionante. `perform_create()` associa `contest` via `get_or_create_current_contest(tag)`
- [x] Pagina `/carica` in `frontend/src/app/(main)/carica/page.tsx` — flow 4 step (dropzone → metadata → uploading → done). Progress bar, toast errore, redirect post-upload
- [x] `videosApi.upload()` in `frontend/src/lib/api/videos.ts` — POST multipart con `onUploadProgress` callback
- [x] `useUploadVideo()` in `frontend/src/lib/hooks/use-videos.ts` — React Query mutation, invalida `queryKeys.videos.all` on success
- [x] Tipo `Video` in `frontend/src/types/video.ts` — interfaccia TypeScript (MANCA `allow_download`)
- [x] API client Axios in `frontend/src/lib/api/client.ts` — interceptors JWT, refresh mutex, CORS headers

### Gap identificati (lavoro da completare)

- [x] Task 1: Configurare Django per upload file grandi (AC: #1, #4)
  - [x] 1.1 — In `backend/project_clip/settings.py` aggiungere:
    ```python
    # Upload file grandi (video fino a 500MB)
    FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB — file più grandi vanno su disco temporaneo
    DATA_UPLOAD_MAX_MEMORY_SIZE = 524288000  # 500MB — limite corpo richiesta
    ```
  - [x] 1.2 — Verificare che `MEDIA_ROOT` e `upload_to='videos/'` siano corretti per i file temporanei

- [x] Task 2: Aggiungere validazione backend nel serializer (AC: #2, #3, #4)
  - [x] 2.1 — In `VideoSerializer` aggiungere metodo `validate_file(self, value)`:
    - Controllare dimensione: `value.size > 500 * 1024 * 1024` → `ValidationError("Il file supera la dimensione massima di 500MB")`
    - Controllare estensione: verificare che l'estensione sia in `{'.mp4', '.mov', '.avi', '.mkv', '.webm'}` (case-insensitive) → `ValidationError("Formato non supportato. Formati accettati: MP4, MOV, AVI, MKV, WebM")`
    - Controllare content-type: verificare che `value.content_type` inizi con `video/` → `ValidationError("Il file selezionato non è un video")`
  - [x] 2.2 — In `VideoSerializer.create()` wrappare TUTTO il blocco salvataggio+moviepy in `transaction.atomic()` e aggiungere validazione durata DOPO il calcolo moviepy:
    - Wrappare con `from django.db import transaction` → `with transaction.atomic():`
    - Se `duration < 10`: eliminare record, raise `ValidationError("Il video deve durare tra 10 secondi e 1 minuto")`
    - Se `duration > 60`: eliminare record, raise `ValidationError("Il video deve durare tra 10 secondi e 1 minuto")`
    - Wrappare il rollback (delete) in `try/except` per safety
    - **BUG FIX (project-context):** il `create()` attuale fa rollback SENZA `transaction.atomic()` — rischio record orfani se il delete fallisce
  - [x] 2.3 — Assicurarsi che `handle_exception_with_serializer()` nel ViewSet mappi `ValidationError → 400` con formato `{"code": "ValidationError", "detail": "..."}`

- [x] Task 3: Aggiornare frontend — tipo Video e form allow_download (AC: #5)
  - [x] 3.1 — In `frontend/src/types/video.ts` aggiungere `allow_download: boolean` all'interfaccia `Video`
  - [x] 3.2 — In `frontend/src/types/video.ts` aggiungere `allow_download?: boolean` all'interfaccia `VideoUploadData`
  - [x] 3.3 — In `frontend/src/app/(main)/carica/page.tsx`:
    - Aggiungere state `const [allowDownload, setAllowDownload] = useState(true)`
    - Aggiungere checkbox nel form metadata step: `<label>` + `<input type="checkbox">` oppure componente Shadcn `<Switch>` con label "Consenti il download"
    - Nel FormData: `formData.append("allow_download", String(allowDownload))`
  - [x] 3.4 — Verificare che il `VideoSerializer` accetti `allow_download` come campo writable (non in `read_only_fields`)

- [x] Task 4: Aggiornare validazione frontend (AC: #3, #4)
  - [x] 4.1 — In `frontend/src/app/(main)/carica/page.tsx` aggiornare `handleFileSelect`:
    - Cambiare limite dimensione da 100MB a 500MB: `selectedFile.size > 500 * 1024 * 1024`
    - Aggiungere validazione estensione: controllare che il nome file termini con `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm` (case-insensitive)
    - Messaggi errore specifici in italiano:
      - Formato: "Formato non supportato. Formati accettati: MP4, MOV, AVI, MKV, WebM"
      - Dimensione: "Il file supera la dimensione massima di 500MB"
  - [x] 4.2 — Aggiornare l'attributo `accept` del file input/dropzone per accettare solo i formati whitelist: `accept="video/mp4,video/quicktime,video/x-msvideo,video/x-matroska,video/webm,.mp4,.mov,.avi,.mkv,.webm"`

- [x] Task 5: Migliorare UX errori upload (AC: #2, #3, #4)
  - [x] 5.1 — Assicurarsi che errori di validazione backend (400) siano presentati all'utente con il messaggio specifico dal campo `detail` della response, non un generico "Errore durante il caricamento"
  - [x] 5.2 — Il form deve mantenere i dati compilati (titolo, tag, allow_download, file selezionato) dopo un errore di validazione backend — l'utente torna allo step "metadata" senza perdere nulla
  - [x] 5.3 — Accessibilità: `aria-label` sulla progress bar, `role="alert"` sui messaggi di errore, label esplicita sulla checkbox allow_download
  - [x] 5.4 — UX gaming identity: placeholder del campo titolo deve usare linguaggio gaming (es. "Clutch impossibile a Valorant" invece di "Inserisci titolo"). Toast successo: "La tua clip è live!" (non generico)

- [x] Task 6: Scrivere test backend per validazione upload (AC: #2, #3, #4)
  - [x] 6.1 — Creare `backend/cs_clips/tests/test_video_upload.py` con `APITestCase`:
    - Test upload con file valido (MP4, 30s, < 500MB) → 201
    - Test upload con durata troppo corta (< 10s) → 400 con messaggio specifico
    - Test upload con durata troppo lunga (> 1min) → 400 con messaggio specifico
    - Test upload con formato non supportato (.txt, .pdf) → 400 con messaggio specifico
    - Test upload con file troppo grande (mock size > 500MB) → 400 con messaggio specifico
    - Test upload senza autenticazione → 401
    - Test upload con utente toconfirm → 403 (read-only)
    - Test upload con campo allow_download=false → verificare che il campo sia salvato
  - [x] 6.2 — Per creare file video di test: usare `SimpleUploadedFile` con header MP4 valido oppure creare un breve video con moviepy in setUp
  - [x] 6.3 — Eseguire `python manage.py test cs_clips.tests.test_video_upload` da `backend/` — 0 fallimenti

- [x] Task 7: Verifica finale
  - [x] 7.1 — `npm run build` da `frontend/` — 0 errori TypeScript
  - [x] 7.2 — `python manage.py test` da `backend/` — tutti i test passano (94/94)
  - [ ] 7.3 — Verificare manualmente: upload MP4 valido → success con progress bar
  - [ ] 7.4 — Verificare manualmente: upload file non video → errore specifico formato
  - [ ] 7.5 — Verificare manualmente: campo allow_download salvato correttamente

## Dev Notes

### Analisi architetturale — stato attuale upload

Il sistema di upload è **già parzialmente implementato** ma manca di validazione rigorosa. L'attuale flow:

```
Frontend (/carica)                    Backend (POST /api/videos/)
┌─────────────────┐                  ┌──────────────────────────┐
│ 1. File drop     │ ──multipart──→  │ 1. FileField salva file  │
│ 2. Title + Tag   │                 │ 2. perform_create() →    │
│ 3. Progress bar  │                 │    get_or_create_contest  │
│ 4. Toast result  │  ←──JSON────  │ 3. moviepy → duration    │
└─────────────────┘                  │ 4. Se moviepy fallisce → │
                                     │    delete record         │
                                     └──────────────────────────┘
```

**Gap critici da colmare:**
| Gap | Rischio senza fix | Priorità |
|-----|-------------------|----------|
| Django default 2.5MB body limit | Upload > 2.5MB fallisce con 413 | CRITICO |
| Nessuna validazione durata | Video di 2 ore vengono accettati | ALTO |
| Nessuna validazione formato | File .exe rinominati in .mp4 vengono processati | ALTO |
| allow_download non nel form frontend | Campo esiste in DB ma l'utente non può impostarlo | MEDIO |
| Frontend limite 100MB hardcoded | PRD richiede 500MB | MEDIO |

### moviepy 2.x — API per validazione

```python
# Import v2 (NON v1)
from moviepy import VideoFileClip  # NON from moviepy.editor import VideoFileClip

# Pattern calcolo durata (già nel serializer)
with VideoFileClip(file_path) as clip:
    duration = int(clip.duration)
```

**Attenzione:** moviepy richiede `imageio-ffmpeg` che include un binario ffmpeg. Già installato (`imageio-ffmpeg==0.6.0`). Se il file non è un video valido, moviepy solleva un'eccezione che il serializer già cattura e fa rollback.

### Django settings per file grandi — spiegazione

| Setting | Default | Necessario per 500MB |
|---------|---------|---------------------|
| `FILE_UPLOAD_MAX_MEMORY_SIZE` | 2.5MB | 10MB (oltre questa soglia Django scrive su disco tmp) |
| `DATA_UPLOAD_MAX_MEMORY_SIZE` | 2.5MB | 524288000 (500MB) oppure `None` per disabilitare |

**Nota:** `FILE_UPLOAD_MAX_MEMORY_SIZE` NON è un limite di dimensione — è la soglia dopo la quale Django usa `TemporaryUploadedFile` invece di `InMemoryUploadedFile`. Un valore di 10MB significa che file > 10MB vengono streamati su disco, il che è desiderabile per video grandi.

`DATA_UPLOAD_MAX_MEMORY_SIZE` invece è un vero limite sulla dimensione del body della richiesta (escluso i file). Per upload video il body è piccolo (solo i campi title/tag/allow_download), ma Django può confondere multipart e body in certi casi. Impostare a 500MB o `None`.

### Strategia di validazione — backend

La validazione avviene in **due fasi** nel serializer:

```
Fase 1: validate_file() — PRIMA del salvataggio
├── Controllo dimensione (< 500MB)
├── Controllo estensione (.mp4, .mov, .avi, .mkv, .webm)
└── Controllo content-type (video/*)

Fase 2: create() — DOPO il salvataggio + calcolo moviepy
├── Calcolo durata via moviepy
├── Se durata < 10s o > 60s → delete record + ValidationError
└── Se moviepy fallisce → delete record (già implementato)
```

**Perché due fasi?** La durata può essere calcolata solo dopo che il file è stato scritto su disco e processato da moviepy. Formato e dimensione si possono controllare subito dal field in memoria.

### Validazione formato — approccio pragmatico

Per la validazione formato, l'approccio più semplice e robusto è:

1. **Estensione file** (check rapido) — controlla che `.name.lower()` termini con estensione valida
2. **Content-Type header** (check MIME) — controlla che `content_type` inizi con `video/`
3. **moviepy come validatore finale** — se il file non è un video valido, moviepy solleva eccezione (già gestita)

**NON aggiungere `python-magic`** come dipendenza — è overkill per questo caso e aggiunge una dipendenza C (`libmagic`). Il triplo check estensione + content-type + moviepy è sufficiente.

### Costanti di validazione

Definire le costanti in un posto centralizzato nel backend:

```python
# In serializers.py o in un file constants.py
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
ALLOWED_VIDEO_CONTENT_TYPES = {
    'video/mp4', 'video/quicktime', 'video/x-msvideo',
    'video/x-matroska', 'video/webm'
}
MAX_VIDEO_FILE_SIZE = 500 * 1024 * 1024  # 500MB
MIN_VIDEO_DURATION = 10   # secondi
MAX_VIDEO_DURATION = 60   # secondi
```

### Frontend — componente Switch per allow_download

Usare il componente Shadcn `<Switch>` (già disponibile nel progetto) con label in italiano:

```tsx
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

<div className="flex items-center space-x-2">
  <Switch
    id="allow-download"
    checked={allowDownload}
    onCheckedChange={setAllowDownload}
    aria-label="Consenti il download della clip"
  />
  <Label htmlFor="allow-download">Consenti il download</Label>
</div>
```

### Frontend — progress bar con gradiente Visual DNA

La progress bar attuale potrebbe usare un colore generico. Deve usare il gradiente del brand:

```tsx
<div className="h-2 rounded-full bg-muted overflow-hidden">
  <div
    className="h-full rounded-full gradient-bg transition-all duration-300"
    style={{ width: `${progress}%` }}
  />
</div>
```

La classe `gradient-bg` è già definita in `globals.css` (viola→ciano).

### Componenti da RIUTILIZZARE (NON ricreare)

| Componente | File | Riuso |
|-----------|------|-------|
| `Switch` | `components/ui/switch.tsx` | Per toggle allow_download |
| `Label` | `components/ui/label.tsx` | Per label del toggle |
| `toast` | Sonner (già integrato) | Per messaggi errore/successo |
| `GradientSpinner` | `components/shared/gradient-spinner.tsx` | Per loading states se necessario |
| `.gradient-bg` | `globals.css` | Per progress bar con gradiente |
| `videosApi.upload()` | `lib/api/videos.ts` | API upload già implementata |
| `useUploadVideo()` | `lib/hooks/use-videos.ts` | Hook React Query già implementato |
| `ErrorMessage` | `components/shared/error-message.tsx` | Per errori visuali (se esiste) |

### Lezioni dalla Story 1-8 e retro Epic 1 (da applicare)

- **Error handling obbligatorio**: ogni pagina deve gestire `isError` + messaggio specifico (retro Epic 1: 5+ story con error handling mancante)
- **a11y al primo commit**: `aria-label`, `role`, keyboard nav su ogni elemento interattivo (retro Epic 1: 4+ story con a11y retrofittata)
- **Named exports**: tutti i componenti usano `export function ComponentName()`, MAI default export (tranne pagine Next.js)
- **Import Framer Motion**: da `"framer-motion"` (NON `"motion/react"` — pacchetto `motion` non installato)
- **Lingua**: messaggi utente in italiano, codice/variabili in inglese
- **Dark mode**: usare Tailwind semantic tokens (`bg-background`, `text-foreground`, `bg-muted`)

### Git intelligence — pattern dai commit precedenti

Ultimi commit rilevanti (Epic 1):
- `2b65ab6` — docs: retrospettiva Epic 1
- `0ba5968` — fix: code review Story 1-8
- `b24a359` — feat: transizione post-login
- `0860534` — feat: Story 1-7 + 1-8

Pattern stabiliti:
- Commit message format: `feat:` / `fix:` / `docs:` + descrizione in italiano
- Client Component con `"use client"` per tutto ciò che usa hooks
- Componenti condivisi in `components/shared/`, layout in `components/layout/`
- Test backend in `backend/cs_clips/tests/` con `APITestCase`
- `Count()` annotation con `distinct=True` per query ottimizzate (retro Epic 1)

### Web Research — informazioni tecniche aggiornate

**Django 5.1 — Upload file grandi:**
- `FILE_UPLOAD_MAX_MEMORY_SIZE` controlla la soglia memoria/disco (default 2.5MB)
- `DATA_UPLOAD_MAX_MEMORY_SIZE` controlla il limite corpo richiesta (default 2.5MB)
- Per 500MB: impostare `DATA_UPLOAD_MAX_MEMORY_SIZE = 524288000`
- [Ref: Django docs File Uploads](https://docs.djangoproject.com/en/5.1/ref/files/uploads/)
- [Ref: Medium — Handling Large File Uploads in Django](https://medium.com/@ewho.ruth2014/handling-large-file-uploads-in-django-e86da6bde982)

**moviepy 2.2.1:**
- Import v2: `from moviepy import VideoFileClip` (NON `from moviepy.editor`)
- Supporta: MP4, MOV, AVI, MKV, WebM (tutti i formati nella whitelist)
- La validazione durata è già nel serializer ma manca il check range 10s-60s
- [Ref: moviepy PyPI](https://pypi.org/project/moviepy/)

**Validazione formato file:**
- `python-magic` richiede `libmagic` (dipendenza C) — NON aggiungere
- Approccio pragmatico: estensione + content-type + moviepy come safety net
- [Ref: filetype PyPI](https://pypi.org/project/filetype/)

### Debito tecnico Epic 1 (contesto — non in scope)

La retrospettiva Epic 1 ha identificato debito tecnico da integrare in Epic 2:
- **Middleware deprecation**: `next/server` middleware potrebbe necessitare aggiornamento
- **_retry typing**: tipo `AxiosRequestConfig` con `_retry` nel response interceptor
- **AuthProvider race**: potenziale race condition su mount/unmount rapido

Questi NON sono bloccanti per Story 2-1 ma vanno affrontati in una story dedicata dell'Epic 2.

### Project Structure Notes

| File | Ruolo | Azione |
|------|-------|--------|
| `backend/project_clip/settings.py` | Settings Django | **MODIFICARE** — aggiungere FILE_UPLOAD_MAX_MEMORY_SIZE, DATA_UPLOAD_MAX_MEMORY_SIZE |
| `backend/cs_clips/serializers.py` | Serializer Video | **MODIFICARE** — aggiungere validate_file(), validazione durata in create() |
| `frontend/src/app/(main)/carica/page.tsx` | Pagina upload | **MODIFICARE** — aggiungere allow_download, aggiornare validazione, migliorare UX errori |
| `frontend/src/types/video.ts` | Tipi TypeScript | **MODIFICARE** — aggiungere allow_download a Video e VideoUploadData |
| `backend/cs_clips/tests/test_video_upload.py` | Test upload | **CREARE** — test validazione formato, durata, dimensione, permessi |

**File NON da toccare:**
- `backend/cs_clips/models.py` — il modello Video ha già tutti i campi necessari (allow_download, duration, tag)
- `backend/cs_clips/views.py` — il ViewSet è già configurato correttamente per l'upload
- `backend/cs_clips/urls.py` — nessun nuovo endpoint necessario
- `frontend/src/lib/api/videos.ts` — l'API upload è già implementata
- `frontend/src/lib/hooks/use-videos.ts` — il hook è già funzionante
- `frontend/src/lib/api/client.ts` — nessuna modifica necessaria

### Stack tecnologico rilevante

- **Backend:** Python 3.x + Django 5.1.6 + DRF 3.15.1
- **Media:** moviepy 2.2.1 + imageio-ffmpeg 0.6.0
- **DB:** PostgreSQL 16 (Docker), psycopg 3.2.4
- **Frontend:** Next.js 16.1.6, React 19, TypeScript 5
- **UI:** TailwindCSS 4, Shadcn (Switch, Label), Sonner (toast)
- **State/Data:** React Query 5, Axios 1.13.5
- **Auth:** SimpleJWT 5.3.1 (access 12h, refresh 1d)

### Vincoli critici per lo sviluppatore

1. **SETTINGS DJANGO OBBLIGATORI**: Senza `DATA_UPLOAD_MAX_MEMORY_SIZE >= 500MB`, OGNI upload video fallirà con 413 Payload Too Large. Questo è il primo task da completare
2. **VALIDAZIONE IN DUE FASI**: formato/dimensione in `validate_file()` (pre-save), durata in `create()` (post-save + moviepy). NON invertire l'ordine
3. **TRANSACTION ATOMIC + ROLLBACK**: wrappare `create()` in `transaction.atomic()`. Quando la validazione durata fallisce, il record Video è GIÀ salvato in DB — fare `instance.delete()` esplicito dentro la transazione. Il pattern rollback è già nel serializer ma MANCA `atomic()` (bug noto da project-context)
4. **IMPORT moviepy v2**: usare `from moviepy import VideoFileClip` — il vecchio import `from moviepy.editor` è deprecato in v2
5. **LINGUA MESSAGGI**: tutti i messaggi di errore/validazione DEVONO essere in italiano (es. "Il video deve durare tra 10 secondi e 1 minuto", NON "Video must be between 10 seconds and 1 minute")
6. **ALLOW_DOWNLOAD DEFAULT True**: il campo è default True sia nel modello Django che nel frontend (checkbox pre-selezionata)
7. **NON AGGIUNGERE DIPENDENZE**: nessun nuovo pacchetto pip/npm necessario. moviepy + imageio-ffmpeg sono già installati
8. **CONTENT-TYPE MULTIPART**: l'header `Content-Type: multipart/form-data` è già gestito da Axios — non impostarlo manualmente (Axios calcola il boundary)
9. **TEST CON DB DOCKER**: i test necessitano PostgreSQL attivo via Docker Compose. Eseguire `docker compose up -d` prima di `python manage.py test`
10. **CUSTOM USER MODEL**: usare `get_user_model()`, MAI importare `User` da `django.contrib.auth.models`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-2.1]
- [Source: _bmad-output/planning-artifacts/architecture.md#Upload-Pattern]
- [Source: _bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Effortless-Interactions]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Critical-Success-Moments]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Visual-DNA-con-gradiente]
- [Source: _bmad-output/project-context.md#Regole-Specifiche-Python-Django]
- [Source: _bmad-output/project-context.md#Gestione-File-Media]
- [Source: _bmad-output/project-context.md#Regole-di-Testing]
- [Source: _bmad-output/implementation-artifacts/1-8-spinner-animato-del-brand-e-transizione-post-login.md#Dev-Notes]
- [Source: _bmad-output/implementation-artifacts/sprint-status.yaml]
- [Source: backend/cs_clips/models.py — Video model con allow_download, duration, tag]
- [Source: backend/cs_clips/serializers.py — VideoSerializer con calcolo durata moviepy]
- [Source: backend/cs_clips/views.py — VideoViewSet con upload endpoint]
- [Source: backend/cs_clips/permissions.py — RoleBasedPermission per upload]
- [Source: backend/project_clip/settings.py — CORS, media config, JWT]
- [Source: frontend/src/app/(main)/carica/page.tsx — pagina upload attuale]
- [Source: frontend/src/lib/api/videos.ts — API upload con progress]
- [Source: frontend/src/lib/hooks/use-videos.ts — hook useUploadVideo]
- [Source: frontend/src/types/video.ts — tipi Video/VideoUploadData]
- [Source: Web Research — Django 5.1 file upload settings per file grandi]
- [Source: Web Research — moviepy 2.2.1 supporto formati e API durata]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Test run 1: 6/9 pass — 3 failure dovuti a error handler che itera su ErrorDetail stringa (chars separati). Fix: raise ValidationError con lista `['msg']` per compatibilità con `handle_exception_with_serializer()`. Fix test oversized: patch costante `MAX_VIDEO_FILE_SIZE` anziché mock `.size` (non funziona con multipart parsing).
- Test run 2: 9/9 pass — tutti i test upload OK
- Build frontend: 0 errori TypeScript, compilato con successo
- Test suite completa: 94/94 pass, 0 regressioni

### Completion Notes List

- ✅ Task 1: Django settings `FILE_UPLOAD_MAX_MEMORY_SIZE` (10MB) e `DATA_UPLOAD_MAX_MEMORY_SIZE` (500MB) aggiunti
- ✅ Task 2: `validate_file()` con check dimensione/estensione/content-type + `create()` wrappato in `transaction.atomic()` con validazione durata 10s-60s + rollback sicuro (bug fix da project-context)
- ✅ Task 3: `allow_download: boolean` aggiunto a interfaccia `Video`, `allow_download?: boolean` a `VideoUploadData`, checkbox nel form upload con label "Consenti il download"
- ✅ Task 4: Limite frontend aggiornato da 100MB a 500MB, validazione estensione whitelist, attributo `accept` con formati specifici
- ✅ Task 5: Errori backend specifici estratti da `detail`/`file[]`, dati form preservati dopo errore, `role="alert"` errori, `role="progressbar"` + `aria-label` progress bar, placeholder gaming "Clutch impossibile a Valorant", toast successo "La tua clip è live!", progress bar con gradiente `gradient-bg`
- ✅ Task 6: 9 test in `test_video_upload.py` — upload valido, durata corta/lunga, formato non supportato, file oversized, unauthenticated, toconfirm, allow_download=false
- ✅ Task 7: `npm run build` 0 errori, `python manage.py test` 94/94 pass. Subtask manuali (7.3-7.5) rimangono per verifica utente
- Costanti di validazione centralizzate in `serializers.py`: `ALLOWED_VIDEO_EXTENSIONS`, `MAX_VIDEO_FILE_SIZE`, `MIN_VIDEO_DURATION`, `MAX_VIDEO_DURATION`
- Componente Switch non installato (richiede `@radix-ui/react-switch` non presente) → usato checkbox HTML nativo con styling accessibile

### File List

- `backend/project_clip/settings.py` — MODIFICATO: aggiunto FILE_UPLOAD_MAX_MEMORY_SIZE e DATA_UPLOAD_MAX_MEMORY_SIZE
- `backend/cs_clips/serializers.py` — MODIFICATO: aggiunto validate_file(), costanti validazione, transaction.atomic() in create(), validazione durata 10s-60s
- `frontend/src/types/video.ts` — MODIFICATO: aggiunto allow_download a Video e VideoUploadData
- `frontend/src/app/(main)/carica/page.tsx` — MODIFICATO: checkbox allow_download, validazione 500MB + estensione, accept formati, UX errori specifici, a11y, gaming placeholder, progress bar gradient
- `backend/cs_clips/tests/test_video_upload.py` — CREATO: 9 test APITestCase per validazione upload

### Change Log

- 2026-02-21: Implementata Story 2-1 — validazione upload video backend (dimensione, formato, durata) + frontend (allow_download, validazione client-side, UX errori gaming, a11y). 9 nuovi test, 94/94 suite completa.

## Status

review
