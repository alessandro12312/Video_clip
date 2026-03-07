# Story 2.2: Download Clip e Presigned URL Refresh

Status: done

## Story

As a utente registrato,
I want scaricare le mie clip e quelle di altri utenti (se permesso), e guardare video senza interruzioni,
so that posso salvare le clip e non subisco errori per URL scadute.

## Acceptance Criteria (BDD)

### AC-1: Download della propria clip (FR13)

```gherkin
Scenario: Utente scarica la propria clip
  Given un utente autenticato proprietario di un video
  When chiama GET /api/videos/{id}/download/
  Then riceve status 200 con payload {"download_url": "<presigned_url>"}
  And la presigned URL ha Content-Disposition: attachment con il titolo del video come filename
  And il frontend apre la URL in una nuova tab per avviare il download

Scenario: Utente scarica la propria clip con allow_download=False
  Given un utente autenticato proprietario di un video con allow_download=False
  When chiama GET /api/videos/{id}/download/
  Then riceve comunque status 200 con la presigned URL
  And il proprietario può SEMPRE scaricare i propri video, indipendentemente da allow_download
```

### AC-2: Download della clip altrui con allow_download abilitato (FR14)

```gherkin
Scenario: Utente scarica clip altrui con download abilitato
  Given un utente autenticato
  And un video di un altro utente con allow_download=True
  When chiama GET /api/videos/{id}/download/
  Then riceve status 200 con payload {"download_url": "<presigned_url>"}

Scenario: Utente tenta download di clip altrui con download disabilitato
  Given un utente autenticato
  And un video di un altro utente con allow_download=False
  When chiama GET /api/videos/{id}/download/
  Then riceve status 403 con detail: "Il download non è abilitato per questa clip"
```

### AC-3: Permessi download — utenti non autenticati e toconfirm

```gherkin
Scenario: Utente non autenticato tenta download
  Given un utente non autenticato
  When chiama GET /api/videos/{id}/download/
  Then riceve status 401 (Unauthorized)

Scenario: Utente toconfirm tenta download
  Given un utente con gruppo "toconfirm"
  When chiama GET /api/videos/{id}/download/
  Then riceve status 403 (Forbidden) — toconfirm è read-only, download è un'azione privilegiata
```

### AC-4: Presigned URL refresh automatico — lazy re-fetch (D3)

```gherkin
Scenario: Video in riproduzione con presigned URL scaduta
  Given un video in riproduzione da più di 1 ora (URL scaduta)
  When il <video> genera un evento onerror (MediaError.MEDIA_ERR_NETWORK o MEDIA_ERR_SRC_NOT_SUPPORTED)
  Then il player mostra un mini-spinner (lo stesso del caricamento iniziale)
  And il player chiama refetch() su useVideo(id) per ottenere una nuova presigned URL
  And il playback riprende automaticamente con la nuova URL
  And l'utente NON vede mai un messaggio di errore durante il re-fetch

Scenario: Presigned URL refresh fallisce dopo 2 tentativi
  Given un video il cui re-fetch della presigned URL fallisce
  When il player ha già tentato 2 re-fetch senza successo
  Then mostra il messaggio "Video non disponibile, ricarica la pagina"
  And il mini-spinner viene sostituito dal messaggio di fallback

Scenario: Errore video non legato a URL scaduta (es. codec non supportato)
  Given un video con MediaError.MEDIA_ERR_DECODE (code 3)
  When il <video> genera onerror
  Then il player NON tenta il re-fetch (solo MEDIA_ERR_NETWORK e MEDIA_ERR_SRC_NOT_SUPPORTED triggherano retry)
  And mostra direttamente "Impossibile riprodurre il video"
```

### AC-5: UI bottone download nella pagina dettaglio clip

```gherkin
Scenario: Bottone download visibile per il proprietario
  Given un utente autenticato sulla pagina dettaglio di un proprio video
  When la pagina viene renderizzata
  Then il bottone download è visibile indipendentemente da allow_download

Scenario: Bottone download visibile per altri utenti (allow_download=True)
  Given un utente autenticato sulla pagina dettaglio di un video altrui con allow_download=True
  When la pagina viene renderizzata
  Then il bottone download è visibile

Scenario: Bottone download nascosto per altri utenti (allow_download=False)
  Given un utente autenticato sulla pagina dettaglio di un video altrui con allow_download=False
  When la pagina viene renderizzata
  Then il bottone download NON è visibile

Scenario: Click su bottone download
  Given il bottone download visibile
  When l'utente clicca il bottone
  Then il frontend chiama GET /api/videos/{id}/download/
  And apre la download_url ricevuta in una nuova tab (o trigghera download via anchor tag con download attribute)
  And durante il fetch mostra un mini-spinner sul bottone
```

### AC-6: Serializer output — verifica campo file_url fresco (non-regressione)

```gherkin
Scenario: Ogni chiamata a GET /api/videos/{id}/ genera una presigned URL fresca
  Given un video esistente
  When il frontend chiama GET /api/videos/{id}/ due volte a distanza di tempo
  Then ciascuna risposta contiene un file_url con presigned URL diversa (nuova firma)
  And il @lru_cache(maxsize=1) sul client MinIO NON causa URL stantie (il cache è sul client, non sull'URL)
```

## Tasks / Subtasks

- [x] **Task 1: Creare endpoint download su VideoViewSet** (AC: #1, #2, #3)
  - [x] 1.1 In `backend/cs_clips/api/videos/video_views.py`, aggiungere `@action(detail=True, methods=['get'], url_path='download')` su `VideoViewSet`
  - [x] 1.2 Logica permessi: se `request.user == video.uploader` → sempre consentito; altrimenti verificare `video.allow_download == True`
  - [x] 1.3 Generare presigned URL con `response_headers={"response-content-disposition": f'attachment; filename="{safe_filename}"'}` dove `safe_filename` è il titolo del video sanitizzato + estensione originale
  - [x] 1.4 Risposta: `{"download_url": "<presigned_url>"}` con status 200
  - [x] 1.5 Errore 403: `{"detail": "Il download non è abilitato per questa clip"}` se `allow_download=False` e non è il proprietario
  - [x] 1.6 Aggiungere `@extend_schema` con documentazione OpenAPI

- [x] **Task 2: Implementare presigned URL refresh nel video player** (AC: #4)
  - [x] 2.1 In `frontend/src/components/video/video-player.tsx`, aggiungere handler `onError` all'elemento `<video>`
  - [x] 2.2 Logica di retry: controllare `videoEl.error.code` — solo `MEDIA_ERR_NETWORK` (2) e `MEDIA_ERR_SRC_NOT_SUPPORTED` (4) triggherano retry; `MEDIA_ERR_DECODE` (3) mostra errore diretto
  - [x] 2.3 Stato locale: `retryCount` (useRef, max 2), `isRefreshing` (useState, per spinner)
  - [x] 2.4 Al trigger: impostare `isRefreshing=true` → mostrare mini-spinner → chiamare `onRefreshUrl()` callback (passata dal parent)
  - [x] 2.5 Dopo max 2 retry falliti: mostrare overlay "Video non disponibile, ricarica la pagina"
  - [x] 2.6 Reset `retryCount` quando la sorgente video cambia (nuovo video) — `useEffect` su `src`

- [x] **Task 3: Collegare refresh URL nel componente ClipContent** (AC: #4)
  - [x] 3.1 In `frontend/src/app/(main)/clip/[id]/clip-content.tsx`, passare callback `onRefreshUrl` al `VideoPlayer`
  - [x] 3.2 La callback chiama `refetch()` dal hook `useVideo(videoId)` e ritorna la nuova `file_url`
  - [x] 3.3 Il `VideoPlayer` riceve la nuova `src` via prop e aggiorna `<video>.src` per riprendere il playback

- [x] **Task 4: Aggiungere bottone download alla pagina dettaglio** (AC: #5)
  - [x] 4.1 Creare componente `DownloadButton` (in `frontend/src/components/video/download-button.tsx`)
  - [x] 4.2 Props: `videoId: number`, `isOwner: boolean`, `allowDownload: boolean`
  - [x] 4.3 Visibilità: visibile se `isOwner || allowDownload`
  - [x] 4.4 Icona: `Download` da `lucide-react`
  - [x] 4.5 On click: chiama `videosApi.download(id)` → apre `download_url` per il download
  - [x] 4.6 Loading state: spinner nell'icona durante la fetch
  - [x] 4.7 Error handling: toast con messaggio se 403 o errore di rete

- [x] **Task 5: Aggiungere API download e hook frontend** (AC: #5)
  - [x] 5.1 In `frontend/src/lib/api/videos.ts`, aggiungere metodo `download(id: number)` che chiama `GET /api/videos/{id}/download/` e ritorna `{ download_url: string }`
  - [x] 5.2 In `frontend/src/lib/hooks/use-videos.ts`, aggiungere hook `useDownloadVideo()` come `useMutation` che chiama `videosApi.download(id)` e apre la URL ricevuta
  - [x] 5.3 Aggiungere tipo `DownloadResponse` in `frontend/src/types/video.ts`: `{ download_url: string }`

- [x] **Task 6: Scrivere test backend** (AC: #1, #2, #3, #6)
  - [x] 6.1 Creare `backend/cs_clips/tests/test_download.py`
  - [x] 6.2 Test download propria clip → 200 + download_url presente
  - [x] 6.3 Test download propria clip con allow_download=False → 200 (proprietario bypassa)
  - [x] 6.4 Test download clip altrui con allow_download=True → 200
  - [x] 6.5 Test download clip altrui con allow_download=False → 403 con messaggio specifico
  - [x] 6.6 Test download utente non autenticato → 401
  - [x] 6.7 Test download utente toconfirm → 403
  - [x] 6.8 Test download video inesistente → 404
  - [x] 6.9 Test che presigned URL contiene response-content-disposition (se possibile verificare parametro URL)
  - [x] 6.10 Test non-regressione: GET /api/videos/{id}/ ritorna file_url valida
  - [x] 6.11 Usare helper da conftest.py (`create_authenticated_user`, `create_toconfirm_user`, `create_api_client_authenticated`)
  - [x] 6.12 Eseguire `ruff check backend/` e `ruff format backend/` — zero errori

- [x] **Task 7: Verificare integrazione e non-regressione** (AC: #4, #5, #6)
  - [x] 7.1 Eseguire la suite test completa backend — zero regressioni
  - [x] 7.2 Verificare `npm run build` frontend — zero errori
  - [x] 7.3 Verificare che il componente `VideoPlayer` non rompa le pagine esistenti (feed, profilo)
  - [x] 7.4 Verificare visivamente che il bottone download appaia solo quando appropriato
  - [x] 7.5 Ruff check + format: zero errori

## Dev Notes

### Contesto Critico

Questa è la **seconda story di Epic 2** e introduce due funzionalità distinte ma correlate:

1. **Download clip** — endpoint backend `GET /api/videos/{id}/download/` + UI bottone download
2. **Presigned URL refresh** — meccanismo di recovery automatico quando le presigned URL MinIO scadono (TTL 1h)

Entrambe ruotano attorno alla presigned URL MinIO. Il download genera una presigned URL con `Content-Disposition: attachment` per forzare il download. Il refresh rigenera la presigned URL standard per riprendere il playback.

### Stato Attuale del Codice

**Backend — Presigned URL Generation (`video_serializers.py` linee 71-110):**

```python
@staticmethod
@lru_cache(maxsize=1)
def _get_minio_client():
    """Client MinIO singleton (cached)."""
    return Minio(
        settings.MINIO_STORAGE_ENDPOINT,
        access_key=settings.MINIO_STORAGE_ACCESS_KEY,
        secret_key=settings.MINIO_STORAGE_SECRET_KEY,
        secure=False,
    )

def get_file_url(self, obj):
    """Genera presigned URL valida 1 ora."""
    client = self._get_minio_client()
    return client.presigned_get_object(
        bucket_name, object_name, expires=timedelta(hours=1)
    )
```

**PUNTO CRITICO**: `@lru_cache(maxsize=1)` è sul **client MinIO** (singleton), NON sull'URL. Ogni chiamata a `get_file_url()` genera un URL fresco con nuova firma. Il re-fetch via `useVideo(id)` ottiene sempre un URL valido. **Nessuna modifica necessaria** al meccanismo di generazione URL.

**Frontend — Video Player (`video-player.tsx`):**
- Riceve `src: string` come prop → passa a `<video src={src}>`
- **Nessun handler `onError`** sull'elemento `<video>` — il player ignora gli errori di playback
- Ha già: tracking views (5s delay), popup overlay, controlli base (play/pause/volume/fullscreen/seek)
- Ha progress bar con comment markers

**Frontend — ClipContent (`clip-content.tsx`):**
- Usa `useVideo(videoId)` → riceve oggetto `Video` con `file_url` (presigned)
- Costruisce `videoSrc`: `video.file.startsWith("http") ? video.file : ${API_BASE_URL}${video.file}`
- Ha `ErrorMessage` per errori di fetch, ma **non** per errori di playback
- **Nota**: il campo usato per la sorgente video è `video.file`, non `video.file_url` — verificare quale campo contiene la presigned URL

**Frontend — Video types (`video.ts`):**
```typescript
export interface Video {
  id: number;
  title: string;
  file: string;            // Presigned URL dal backend
  uploader: string;
  average_rating: number;
  like_count: number;
  views: number;
  tag: VideoTag;
  duration: number;
  allow_download: boolean;
  contest: number | null;
  created_at: string;
  updated_at: string;
}
```

**Frontend — useVideo hook (`use-videos.ts`):**
```typescript
export function useVideo(id: number) {
  return useQuery({
    queryKey: queryKeys.videos.detail(id),
    queryFn: () => videosApi.getById(id),
  });
}
```
- `refetch()` disponibile dal return di `useQuery` — usare per refresh URL

### Pattern da Seguire

**Endpoint download — Pattern @action con permessi custom inline:**
```python
@extend_schema(
    summary="Download clip",
    description="Genera presigned URL per il download della clip",
    responses={200: {"type": "object", "properties": {"download_url": {"type": "string"}}}},
)
@action(detail=True, methods=['get'], url_path='download')
def download(self, request, pk=None):
    video = self.get_object()

    # Il proprietario può SEMPRE scaricare
    if video.uploader != request.user and not video.allow_download:
        return Response(
            {"detail": "Il download non è abilitato per questa clip"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Genera presigned URL con Content-Disposition: attachment
    safe_filename = self._sanitize_filename(video.title, video.file.name)
    client = VideoOutputSerializer._get_minio_client()
    download_url = client.presigned_get_object(
        settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
        video.file.name,
        expires=timedelta(hours=1),
        response_headers={
            "response-content-disposition": f'attachment; filename="{safe_filename}"'
        },
    )

    return Response({"download_url": download_url})
```

**Presigned URL refresh — Pattern nel VideoPlayer:**
```tsx
// Stato per retry
const retryCountRef = useRef(0);
const [isRefreshing, setIsRefreshing] = useState(false);
const MAX_RETRIES = 2;

// Reset retry count quando cambia src
useEffect(() => { retryCountRef.current = 0; }, [src]);

const handleVideoError = useCallback(() => {
  const video = videoRef.current;
  if (!video?.error) return;

  const code = video.error.code;

  // Solo MEDIA_ERR_NETWORK (2) e MEDIA_ERR_SRC_NOT_SUPPORTED (4) triggherano retry
  if (code !== 2 && code !== 4) {
    setErrorMessage("Impossibile riprodurre il video");
    return;
  }

  if (retryCountRef.current >= MAX_RETRIES) {
    setErrorMessage("Video non disponibile, ricarica la pagina");
    return;
  }

  retryCountRef.current += 1;
  setIsRefreshing(true);
  onRefreshUrl?.();
}, [onRefreshUrl]);
```

**Download button — useMutation pattern:**
```tsx
export function useDownloadVideo() {
  return useMutation({
    mutationFn: (videoId: number) => videosApi.download(videoId),
    onSuccess: (data) => {
      // Apri URL per download — usa anchor con download attribute
      const a = document.createElement("a");
      a.href = data.download_url;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    },
  });
}
```

**Sanitizzazione filename per Content-Disposition:**
```python
import re
from pathlib import PurePosixPath

def _sanitize_filename(title: str, original_path: str) -> str:
    """Sanitizza il titolo per uso in Content-Disposition header."""
    ext = PurePosixPath(original_path).suffix or ".mp4"
    # Rimuovi caratteri non sicuri per header HTTP
    safe_title = re.sub(r'[^\w\s\-.]', '', title).strip()
    if not safe_title:
        safe_title = "clip"
    return f"{safe_title}{ext}"
```

### Anti-Pattern da Evitare

- **MAI** fare redirect 302 alla presigned URL dal backend — il frontend deve ricevere l'URL e gestire il download. Un redirect non permette di mostrare loading state o gestire errori
- **MAI** usare `window.open()` per download — non funziona bene in tutti i browser con presigned URL. Usare anchor tag con `download` attribute
- **MAI** tentare retry su `MEDIA_ERR_DECODE` (code 3) — indica un problema col file, non con l'URL
- **MAI** mostrare un messaggio di errore all'utente durante il re-fetch — l'UX deve essere trasparente con solo spinner
- **MAI** resettare `retryCount` ad ogni re-fetch riuscito — il contatore è per sessione di riproduzione del singolo video
- **MAI** invalidare cache React Query per `videos.list` dopo un download — il download non modifica i dati
- **MAI** creare un endpoint separato solo per refreshare la presigned URL — `GET /api/videos/{id}/` già genera un URL fresco ad ogni chiamata (il @lru_cache è sul client, non sull'URL)
- **MAI** importare `from cs_clips.models.user import User` — usare `get_user_model()`
- **MAI** dimenticare `@extend_schema` sull'action download

### Informazioni Tecniche Aggiornate

**MinIO Python SDK 7.2.15 — `presigned_get_object()` signature:**
```python
presigned_get_object(
    bucket_name: str,
    object_name: str,
    expires: timedelta = timedelta(days=7),
    response_headers: dict | None = None,    # Per Content-Disposition
    request_date: datetime | None = None,
    version_id: str | None = None,
    extra_query_params: dict | None = None,
) -> str
```
- `response_headers` accetta `{"response-content-disposition": "attachment; filename=\"nome.mp4\""}` — il prefisso `response-` è obbligatorio (S3 convention)
- Il filename nel Content-Disposition deve essere sanitizzato (no caratteri speciali, no path traversal)
- La URL generata include i response headers come query parameter firmati — il download forzato avviene lato MinIO senza intermediari

**HTML5 MediaError codes:**
- `MEDIA_ERR_ABORTED` (1) — utente ha interrotto, NON triggherare retry
- `MEDIA_ERR_NETWORK` (2) — errore rete / URL scaduta → triggherare retry
- `MEDIA_ERR_DECODE` (3) — file corrotto / codec non supportato → mostrare errore
- `MEDIA_ERR_SRC_NOT_SUPPORTED` (4) — sorgente non caricabile (include URL 403/404 da presigned scaduta) → triggherare retry

**DRF `@action` routing:**
```python
@action(detail=True, methods=['get'], url_path='download')
```
- Genera route: `GET /api/videos/{id}/download/`
- `detail=True` → richiede PK nell'URL, `self.get_object()` recupera l'istanza
- Il `permission_classes` del ViewSet si applica anche alle action — `IsAuthenticated` + `RoleBasedPermission` proteggono già l'endpoint

### Project Structure Notes

**File da modificare:**
- `backend/cs_clips/api/videos/video_views.py` — aggiungere action `download`
- `frontend/src/components/video/video-player.tsx` — aggiungere handler `onError` + spinner + retry logic
- `frontend/src/app/(main)/clip/[id]/clip-content.tsx` — passare `onRefreshUrl` callback al player, aggiungere `DownloadButton`
- `frontend/src/lib/api/videos.ts` — aggiungere metodo `download(id)`
- `frontend/src/lib/hooks/use-videos.ts` — aggiungere hook `useDownloadVideo()`
- `frontend/src/types/video.ts` — aggiungere tipo `DownloadResponse`

**File da creare:**
- `backend/cs_clips/tests/test_download.py` — test per endpoint download
- `frontend/src/components/video/download-button.tsx` — componente bottone download

**File che NON devono essere modificati:**
- `backend/cs_clips/api/videos/video_serializers.py` — la generazione presigned URL è già corretta
- `backend/cs_clips/models/video.py` — `allow_download` esiste già
- `backend/cs_clips/urls.py` — il DefaultRouter registra automaticamente le nuove @action

### Intelligence dalla Story 2.1 (Precedente)

**Pattern stabiliti da riusare:**
- `VideoOutputSerializer` per leggere `file_url` — genera presigned URL fresca ad ogni serializzazione
- Test con `@patch("cs_clips.api.videos.video_serializers.VideoFileClip")` per mock MoviePy
- `create_sample_video` da conftest.py crea video con durata 30s senza file reale su MinIO — utile per test logica download, ma per test presigned URL servono mock MinIO
- `SimpleUploadedFile` per file test
- Ruff 0 errori è gate obbligatorio

**Problemi risolti nella Story 2.1 da non re-introdurre:**
- DRF BooleanField.initial=False: gestito con `serializers.BooleanField(default=True, required=False)` esplicito
- View create: restituisce `VideoOutputSerializer` per shape corretta
- Except chain: `except serializers.ValidationError: raise` prima del generico `except Exception`

**Debito tecnico rilevante:**
- `has_object_permission` — Il check di ownership per l'action download è diverso: non è un'operazione di scrittura ma di lettura privilegiata. `RoleBasedPermission.has_object_permission()` controlla ownership solo per metodi non-safe (PUT, PATCH, DELETE). Per download (GET), il check ownership è custom nell'action stessa (non nel permission class)

### Git Intelligence

**Ultimi commit (post-Story 2.1):**
- `8d20865` — feat: Story 2.1 — upload clip con validazione completa e allow_download
- Suite test attuale: **91 test passanti** — non introdurre regressioni
- Conftest.py ha 6 helper: `create_authenticated_user`, `create_toconfirm_user`, `create_admin_user`, `create_api_client_authenticated`, `create_sample_video`, `create_sample_contest`

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 2, Story 2.2]
- [Source: _bmad-output/planning-artifacts/architecture.md — D3 (Presigned URL Refresh), FR13, FR14]
- [Source: _bmad-output/implementation-artifacts/2-1-upload-clip-con-validazione-completa.md — Dev notes, pattern stabiliti]
- [Source: backend/cs_clips/api/videos/video_serializers.py — VideoOutputSerializer.get_file_url(), @lru_cache su client]
- [Source: backend/cs_clips/api/videos/video_views.py — VideoViewSet con 6 azioni, nessun download]
- [Source: backend/cs_clips/models/video.py — Video model con allow_download=True]
- [Source: backend/cs_clips/permissions.py — RoleBasedPermission con has_object_permission]
- [Source: frontend/src/components/video/video-player.tsx — Nessun handler onError su <video>]
- [Source: frontend/src/app/(main)/clip/[id]/clip-content.tsx — useVideo hook, costruzione videoSrc]
- [Source: frontend/src/lib/hooks/use-videos.ts — useVideo con refetch disponibile]
- [Source: frontend/src/lib/api/videos.ts — videosApi senza metodo download]
- [Source: frontend/src/types/video.ts — Video interface con allow_download ma senza DownloadResponse]
- [Source: .venv MinIO SDK 7.2.15 — presigned_get_object con response_headers per Content-Disposition]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

- Nessun bug bloccante riscontrato durante l'implementazione
- Rilevato che `RoleBasedPermission` permette GET per toconfirm (SAFE_METHOD) → risolto aggiungendo `OnlyUsersPermission` sull'action download per bloccare toconfirm come da AC-3

### Completion Notes List

- **Task 1**: Endpoint `GET /api/videos/{id}/download/` con @action, permessi owner/allow_download, presigned URL con Content-Disposition attachment, sanitizzazione filename, @extend_schema OpenAPI. Aggiunto `OnlyUsersPermission` per bloccare toconfirm.
- **Task 2**: Handler `onError` su `<video>` con retry logic (max 2) per MEDIA_ERR_NETWORK e MEDIA_ERR_SRC_NOT_SUPPORTED. Mini-spinner durante refresh, overlay errore dopo 2 fallimenti. Reset retryCount su cambio src.
- **Task 3**: Callback `onRefreshUrl` passata da ClipContent al VideoPlayer. Chiama `refetchVideo()` da useVideo per ottenere presigned URL fresca.
- **Task 4**: Componente `DownloadButton` con visibilita condizionale (isOwner || allowDownload), icona Download, loading spinner, error toast. Integrato in ClipContent nella sezione stats.
- **Task 5**: Metodo `videosApi.download(id)`, hook `useDownloadVideo()` con useMutation e anchor tag per trigger download, tipo `DownloadResponse` esportato.
- **Task 6**: 9 test backend: owner 200, owner allow_download=False 200, other allow=True 200, other allow=False 403, unauth 401, toconfirm 403, 404, Content-Disposition verification, non-regressione file_url. Tutti passanti.
- **Task 7**: 100 test backend (91 esistenti + 9 nuovi) tutti passanti, `npm run build` zero errori, ruff check + format zero errori.

### File List

**File modificati:**
- `backend/cs_clips/api/videos/video_views.py` — aggiunta action `download`, import `OnlyUsersPermission`, `re`, `PurePosixPath`, `settings`
- `frontend/src/components/video/video-player.tsx` — aggiunto handler onError, retry logic, spinner, errorMessage overlay, prop onRefreshUrl
- `frontend/src/app/clip/[id]/clip-content.tsx` — aggiunto refetchVideo, handleRefreshUrl, DownloadButton integration
- `frontend/src/lib/api/videos.ts` — aggiunto metodo `download(id)`, import `DownloadResponse`
- `frontend/src/lib/hooks/use-videos.ts` — aggiunto hook `useDownloadVideo()`
- `frontend/src/types/video.ts` — aggiunto tipo `DownloadResponse`
- `frontend/src/types/index.ts` — aggiunto export `DownloadResponse`
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — status 2-2 aggiornato

**File creati:**
- `backend/cs_clips/tests/test_download.py` — 9 test per endpoint download
- `frontend/src/components/video/download-button.tsx` — componente DownloadButton

## Senior Developer Review (AI)

**Reviewer:** AcchippameQuisso (2026-03-01)
**Findings:** 2 HIGH, 2 MEDIUM, 6 LOW → **4 fixati automaticamente**, 6 LOW accettati

### Fix Applicati
- **[H1] Infinite retry loop**: `retryCount` si resettava su cambio `src` (incluso refresh URL), creando loop infinito. Fix: reset solo su cambio `videoId` (navigazione a video diverso).
- **[H2] Resume playback mancante**: AC-4 richiede ripresa automatica dopo refresh URL. Aggiunto `savedTimeRef` per salvare posizione, `onLoadedData` per seek + play dopo caricamento nuova sorgente.
- **[M1] Spinner bloccato se refetch fallisce**: Se `refetchVideo()` falliva, `isRefreshing` restava true per sempre. Fix: `handleRefreshUrl` ora è async e propaga errori, `handleVideoError` li cattura con try/catch e mostra fallback.
- **[M2] Sanitizzazione filename con newline**: `_sanitize_filename` usava `\s` (include `\r\n`). Fix: sostituito con spazio letterale ` `.

### LOW Accettati (non fixati)
- L1: `from project_clip import settings` → stile non convenzionale
- L2: Risposta 403 download senza campo `code`
- L3: Accoppiamento `VideoOutputSerializer._get_minio_client()` nella view
- L4: `tempfile.mkdtemp()` a livello modulo nei test
- L5: `_sanitize_filename` non testato in isolamento
- L6: Import dentro `setUp` nel file test

### Verifica Post-Fix
- 100 test backend passanti (0 regressioni)
- `npm run build` frontend: 0 errori
- `ruff check`: 0 errori

## Change Log

- **2026-03-01**: Implementata Story 2.2 — endpoint download clip con permessi owner/allow_download, presigned URL refresh automatico nel player (retry max 2, discriminazione MediaError codes), bottone download nella pagina dettaglio, 9 test backend. Suite completa: 100 test passanti, 0 regressioni.
- **2026-03-01**: Code review — 4 fix (2 HIGH retry/resume player, 1 MEDIUM spinner stuck, 1 MEDIUM sanitize filename). 100 test passanti post-fix.
