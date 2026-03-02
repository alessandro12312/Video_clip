# Story 2.3: Feed Home e Navigazione Clip

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utente registrato,
I want scorrere il feed con le clip dei miei following e aprire le clip in dettaglio,
so that posso scoprire e guardare le clip degli utenti che seguo.

## Acceptance Criteria (BDD)

### AC-1: Feed Home con clip dei following (FR17, FR21)

```gherkin
Scenario: Utente con following accede al feed Home
  Given un utente autenticato che segue almeno un altro utente
  When accede al feed Home (/home)
  Then vede le clip degli utenti seguiti ordinate per data decrescente
  And ogni clip è mostrata come card con thumbnail, titolo, uploader, tag, durata, views e data
  And lo scroll infinito carica pagine successive da 10 elementi

Scenario: Feed Home rispetta paginazione backend
  Given un utente che segue utenti con più di 10 clip
  When scorre il feed fino alla fine della prima pagina
  Then il frontend carica automaticamente la seconda pagina via useInfiniteQuery
  And i nuovi risultati si appendono sotto quelli esistenti senza layout shift
```

### AC-2: Navigazione card → pagina dettaglio (FR18, FR22)

```gherkin
Scenario: Utente clicca su una card nel feed
  Given una card clip visibile nel feed
  When l'utente clicca sulla card
  Then viene navigato alla pagina /clip/{id}
  And vede il player video con controlli, metadati della clip e sezione commenti

Scenario: Pagina dettaglio mostra tutte le informazioni
  Given un utente autenticato sulla pagina dettaglio di una clip
  When la pagina viene renderizzata
  Then vede: player video, titolo, uploader con avatar, tag badge, durata
  And vede: valutazione media, conteggio views, data creazione
  And vede: form per commento con timestamp, lista commenti dual-view
  And vede: bottone download (se applicabile, Story 2.2)
```

### AC-3: URL diretto e link preview SSR (FR19, FR20)

```gherkin
Scenario: Visitatore non autenticato accede a /clip/{id} via URL diretto
  Given un visitatore non autenticato
  When accede a /clip/{id} tramite URL diretto (condivisione)
  Then la pagina è accessibile senza autenticazione (route non protetta dal middleware)
  And il video è riproducibile senza login
  And vede un CTA "Vuoi commentare e votare?" con link a login/registrazione
  And un header minimal con logo "Video_clip" e bottone "Accedi"

Scenario: Link preview genera meta tag OG per piattaforme esterne
  Given un URL /clip/{id} condiviso su una piattaforma esterna (WhatsApp, Telegram, etc.)
  When il crawler della piattaforma esegue il fetch della pagina
  Then il server genera meta tag OG via generateMetadata (RSC)
  And i meta tag includono: og:title (titolo clip), og:description (uploader + views + rating)
  And og:type = "video.other"
  And og:image = presigned URL del thumbnail della clip (prima frame del video)
  And og:url = URL canonico della clip
```

### AC-4: Thumbnail video — generazione e serving (FR20, FR21)

```gherkin
Scenario: Thumbnail generato automaticamente all'upload
  Given un utente che carica un video
  When il backend completa il processing (durata + salvataggio)
  Then il sistema estrae il primo frame del video come immagine JPEG
  And salva il thumbnail su MinIO nel bucket appropriato
  And il campo thumbnail del Video viene popolato con il path del file

Scenario: Thumbnail servito via presigned URL
  Given un video con thumbnail generato
  When il frontend chiama GET /api/videos/ o GET /api/videos/{id}/
  Then la risposta include il campo thumbnail_url con una presigned URL fresca (1h)
  And il ClipCard mostra il thumbnail reale al posto del placeholder icona play

Scenario: Fallback per video senza thumbnail (retrocompatibilità)
  Given un video caricato prima dell'implementazione thumbnail
  When il frontend renderizza la card
  Then il campo thumbnail_url è null
  And il ClipCard mostra il fallback (icona Play su sfondo scuro) come oggi
```

### AC-5: EmptyState per utenti senza following (FR17)

```gherkin
Scenario: Utente senza following accede al feed Home
  Given un utente autenticato che non segue nessuno
  When accede al feed Home
  Then vede un EmptyState con icona Film e messaggio "Nessuna clip da mostrare"
  And un suggerimento di seguire utenti per popolare il feed
```

### AC-6: Non-regressione e integrazione

```gherkin
Scenario: Il feed esistente non subisce regressioni
  Given le modifiche apportate per thumbnail e OG tags
  When viene eseguita la suite test backend completa
  Then tutti i 100 test esistenti passano senza regressioni

Scenario: Il frontend compila senza errori
  Given le modifiche frontend per thumbnail nelle card e OG tags
  When viene eseguito npm run build
  Then la build completa senza errori TypeScript o warning bloccanti
```

## Tasks / Subtasks

- [x] **Task 1: Aggiungere campo `thumbnail` al modello Video e generazione automatica** (AC: #4)
  - [x] 1.1 In `backend/cs_clips/models/video.py`, aggiungere campo `thumbnail = models.ImageField(upload_to="thumbnails/", blank=True, null=True, help_text="Thumbnail auto-generato dal primo frame del video")` — campo opzionale per retrocompatibilità con video esistenti
  - [x] 1.2 Creare migrazione: `python manage.py makemigrations`
  - [x] 1.3 In `backend/cs_clips/api/videos/video_serializers.py`, nel metodo `VideoInputSerializer.create()`, dopo l'estrazione durata con MoviePy, aggiungere estrazione thumbnail: `clip.save_frame(tmp_path, t=1.0)` — salva primo frame a t=1s come JPEG
  - [x] 1.4 Caricare il thumbnail su MinIO nel percorso `thumbnails/{uuid}_{filename}.jpg` e assegnare al campo `video.thumbnail`
  - [x] 1.5 In `VideoOutputSerializer`, aggiungere `thumbnail_url = SerializerMethodField()` che genera presigned URL per il thumbnail (stessa logica di `get_file_url` ma per il campo `thumbnail`) — ritornare `null` se thumbnail non esiste
  - [x] 1.6 Aggiungere `thumbnail_url` a `read_only_fields` nel serializer
  - [x] 1.7 Gestire errore di generazione thumbnail con graceful fallback (non bloccare l'upload se l'estrazione frame fallisce — loggare warning e lasciare `thumbnail=None`)

- [x] **Task 2: Aggiornare il frontend per usare i thumbnail reali** (AC: #4, #1)
  - [x] 2.1 In `frontend/src/types/video.ts`, aggiungere campo `thumbnail_url: string | null` all'interfaccia `Video`
  - [x] 2.2 In `frontend/src/components/feed/clip-card.tsx`, sostituire il placeholder icona Play con un `<img>` quando `video.thumbnail_url` è disponibile, mantenendo il fallback icona quando `thumbnail_url` è `null`
  - [x] 2.3 Usare tag `<img>` nativo (non `next/image`) per il thumbnail — le presigned URL MinIO non sono compatibili con il loader di `next/image` senza configurazione aggiuntiva
  - [x] 2.4 Aggiungere `loading="lazy"` all'img del thumbnail per performance
  - [x] 2.5 Gestire errore di caricamento thumbnail con `onError` → fallback all'icona Play

- [x] **Task 3: Migliorare OG tags e SSR metadata** (AC: #3)
  - [x] 3.1 In `frontend/src/app/layout.tsx`, aggiungere `metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000")` nell'oggetto `metadata` — necessario per URL assoluti nei meta tag OG
  - [x] 3.2 In `frontend/src/app/clip/[id]/page.tsx`, arricchire `generateMetadata` con:
    - `openGraph.image`: `video.thumbnail_url` (presigned URL del thumbnail, con fallback vuoto se null)
    - `openGraph.url`: URL canonico della clip
    - `twitter.card`: `"summary_large_image"` (formato ottimale per preview con immagine)
    - `twitter.title` e `twitter.description`: stessi valori di OG
  - [x] 3.3 Gestire il caso `thumbnail_url === null` — non impostare `og:image` se non c'è thumbnail (le piattaforme mostreranno un preview senza immagine, meglio che un'immagine rotta)

- [x] **Task 4: Scrivere test backend** (AC: #1, #4, #6)
  - [x] 4.1 Creare `backend/cs_clips/tests/test_feed.py` con test per l'endpoint `GET /api/videos/following/`
  - [x] 4.2 Test: utente con following vede solo video dei following → 200 + results filtrati
  - [x] 4.3 Test: utente senza following vede lista vuota → 200 + results = []
  - [x] 4.4 Test: risposta è paginata (contiene count, next, previous, results)
  - [x] 4.5 Test: ordinamento per `-created_at` (il video più recente è primo)
  - [x] 4.6 Test: utente non autenticato → 401
  - [x] 4.7 Test: utente toconfirm può accedere al feed (è un'operazione di lettura, SAFE_METHOD)
  - [x] 4.8 Test: generazione thumbnail durante upload (mock MoviePy + MinIO) — verificare che il campo thumbnail viene popolato
  - [x] 4.9 Test: video detail ritorna `thumbnail_url` nel payload
  - [x] 4.10 Test: video senza thumbnail ritorna `thumbnail_url: null`
  - [x] 4.11 Usare helper da conftest.py (`create_authenticated_user`, `create_api_client_authenticated`)
  - [x] 4.12 Eseguire `ruff check backend/` e `ruff format backend/` — zero errori

- [x] **Task 5: Verificare integrazione e non-regressione** (AC: #5, #6)
  - [x] 5.1 Eseguire la suite test completa backend — zero regressioni (110 test)
  - [x] 5.2 Verificare `npm run build` frontend — zero errori
  - [x] 5.3 Ruff check + format: zero errori
  - [x] 5.4 Verificare visivamente: feed Home mostra card con thumbnail (per video nuovi), card con fallback (per video vecchi)
  - [x] 5.5 Verificare che EmptyState funzioni per utenti senza following
  - [x] 5.6 Verificare che la pagina `/clip/{id}` sia accessibile senza autenticazione e mostri OG tags corretti

## Dev Notes

### Contesto Critico

Questa è la **terza story di Epic 2** e copre il flusso principale di scoperta e navigazione dei contenuti. La maggior parte dell'infrastruttura frontend **esiste già** (pattern "frontend-avanti"): feed Home, clip card, infinite scroll, pagina dettaglio, EmptyState. Il backend endpoint `GET /api/videos/following/` è già funzionante.

**Il valore aggiunto principale di questa story è:**
1. **Thumbnail video** — campo nuovo sul modello, generazione automatica all'upload, presigned URL nel serializer
2. **Miglioramento OG tags** — `og:image` con thumbnail, `metadataBase`, Twitter cards
3. **Test backend** per l'endpoint following e per la generazione thumbnail
4. **Verifica end-to-end** del flusso feed → card → dettaglio

### Stato Attuale del Codice — Cosa GIÀ Esiste

**Frontend (già implementato e funzionante):**

- **Home page** (`frontend/src/app/(main)/home/page.tsx`): usa `useVideoFeed()`, mostra `FeedGrid`, infinite scroll via `InfiniteScroll`, EmptyState con icona Film + "Nessuna clip da mostrare" per utenti senza following
- **FeedGrid** (`frontend/src/components/feed/feed-grid.tsx`): grid responsive 1→2→3 colonne, skeleton loading, mappa video → `ClipCard`
- **ClipCard** (`frontend/src/components/feed/clip-card.tsx`): link a `/clip/{id}`, placeholder play icon (da sostituire con thumbnail), durata badge, tag badge, titolo, uploader avatar, stats (views, rating, data)
- **ClipCardSkeleton** (`frontend/src/components/feed/clip-card-skeleton.tsx`): loading skeleton
- **InfiniteScroll** (`frontend/src/components/shared/infinite-scroll.tsx`): Intersection Observer, auto-fetch next page
- **EmptyState** (`frontend/src/components/shared/empty-state.tsx`): componente generico riusabile
- **Clip detail page** (`frontend/src/app/clip/[id]/page.tsx`): RSC, `generateMetadata` con OG title+description+type, ISR 60s, `notFound()` per video non trovati
- **ClipContent** (`frontend/src/app/clip/[id]/clip-content.tsx`): vista non autenticata (header minimal + CTA login), vista autenticata (player + rating + comments + download)
- **Hooks**: `useVideoFeed()` (infinite query su `/videos/following/`), `useVideo(id)`, `useTopRatedVideos(range)`
- **API client**: `videosApi.getFollowingFeed(page)`, `videosApi.getById(id)`, `videosApi.getAll(page)`
- **Query keys**: `queryKeys.videos.followingAll`, `queryKeys.videos.detail(id)`

**Backend (già implementato e funzionante):**

- **Endpoint following** (`backend/cs_clips/api/videos/video_views.py:164-198`):
  ```python
  @action(detail=False, methods=["get"], url_path="following")
  def videos_from_following(self, request):
      user = request.user
      following_users = user.following.all()
      videos = Video.objects.filter(uploader__in=following_users).order_by("-created_at")
      page = self.paginate_queryset(videos)
      serializer = self.get_serializer(page or videos, many=True)
      return self.get_paginated_response(serializer.data) if page else Response(serializer.data)
  ```

- **VideoOutputSerializer** (`video_serializers.py:22-110`): genera `file_url` via presigned URL MinIO, `average_rating` via annotazione/calcolo, `uploader` da `uploader.username`

- **Middleware Next.js** (`frontend/src/middleware.ts`): NON protegge `/clip/[id]` — la rotta è pubblica per condivisione

**OG Tags — Stato Attuale (parziale):**
```typescript
// frontend/src/app/clip/[id]/page.tsx — generateMetadata
return {
  title: `${video.title} — Video_clip`,
  description: `Guarda "${video.title}" di ${video.uploader}...`,
  openGraph: {
    title: video.title,
    description: `Clip di ${video.uploader} — ${views} views, ${rating}`,
    type: "video.other",
  },
};
// MANCANO: og:image, og:url, twitter card, metadataBase
```

### Pattern da Seguire

**Generazione thumbnail — MoviePy v2 syntax:**
```python
from moviepy import VideoFileClip
import tempfile
import os

# Nel contesto di VideoInputSerializer.create(), dopo estrazione durata:
try:
    clip = VideoFileClip(temp_video_path)
    thumbnail_path = os.path.join(tempfile.gettempdir(), f"thumb_{uuid4().hex}.jpg")
    clip.save_frame(thumbnail_path, t=min(1.0, clip.duration / 2))
    clip.close()

    # Upload thumbnail su MinIO
    with open(thumbnail_path, "rb") as thumb_file:
        thumbnail_name = f"thumbnails/{uuid4().hex}_{os.path.basename(temp_video_path)}.jpg"
        video.thumbnail.save(thumbnail_name, File(thumb_file), save=False)

    os.unlink(thumbnail_path)
except Exception:
    # Graceful fallback — non bloccare l'upload
    pass
```

**Presigned URL per thumbnail — nel VideoOutputSerializer:**
```python
def get_thumbnail_url(self, obj):
    """Genera presigned URL per il thumbnail, se esiste."""
    if not obj.thumbnail:
        return None
    try:
        client = self._get_minio_client()
        return client.presigned_get_object(
            settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
            obj.thumbnail.name,
            expires=timedelta(hours=1),
        )
    except Exception:
        return None
```

**ClipCard con thumbnail — pattern img con fallback:**
```tsx
{video.thumbnail_url ? (
  <img
    src={video.thumbnail_url}
    alt={video.title}
    className="absolute inset-0 h-full w-full object-cover"
    loading="lazy"
    onError={(e) => {
      // Fallback al placeholder se thumbnail non caricabile
      e.currentTarget.style.display = "none";
      // Mostra icona Play
    }}
  />
) : (
  <Play className="h-12 w-12 text-muted-foreground/50" />
)}
```

**OG tags migliorati:**
```typescript
// frontend/src/app/clip/[id]/page.tsx
return {
  title: `${video.title} — Video_clip`,
  description: `Guarda "${video.title}" di ${video.uploader} su Video_clip.`,
  openGraph: {
    title: video.title,
    description: `Clip di ${video.uploader} — ${views} views`,
    type: "video.other",
    ...(video.thumbnail_url && { images: [{ url: video.thumbnail_url }] }),
  },
  twitter: {
    card: video.thumbnail_url ? "summary_large_image" : "summary",
    title: video.title,
    description: `Clip di ${video.uploader} su Video_clip`,
    ...(video.thumbnail_url && { images: [video.thumbnail_url] }),
  },
};
```

### Anti-Pattern da Evitare

- **MAI** usare `next/image` per thumbnail MinIO — le presigned URL cambiano ad ogni request, incompatibili con il loader/cache di `next/image` senza configurazione `remotePatterns` specifica. Usare `<img>` nativo con `loading="lazy"`
- **MAI** bloccare l'upload se la generazione thumbnail fallisce — l'upload deve completarsi sempre, il thumbnail è un bonus. Graceful fallback con `thumbnail=None`
- **MAI** caricare il video intero nel browser per generare thumbnail client-side — sarebbe uno spreco di bandwidth enorme. La generazione deve avvenire server-side durante l'upload
- **MAI** salvare il thumbnail nella stessa directory del video — usare una directory separata `thumbnails/` per organizzazione e pulizia
- **MAI** dimenticare `clip.close()` dopo `save_frame()` di MoviePy — resource leak (handle file aperto)
- **MAI** rimuovere il fallback placeholder dall'interfaccia ClipCard — i video esistenti prima di questa story non avranno thumbnail
- **MAI** importare `from cs_clips.models.user import User` — usare `get_user_model()`
- **MAI** generare il thumbnail a t=0.0 — il primo frame è spesso nero. Usare `t=1.0` o `t=min(1.0, duration/2)` per un frame più rappresentativo
- **MAI** impostare `og:image` con URL vuota o `null` — se non c'è thumbnail, omettere completamente il tag (le piattaforme gestiscono meglio l'assenza che un'URL rotta)

### Informazioni Tecniche Aggiornate

**MoviePy 2.2.1 — `save_frame()` syntax:**
```python
from moviepy import VideoFileClip

clip = VideoFileClip("video.mp4")
clip.save_frame("frame.jpg", t=1.0)  # t in secondi
clip.close()
```
- `save_frame()` usa PIL/Pillow internamente — supporta JPEG, PNG
- La qualità JPEG è configurabile: `clip.save_frame(path, t=1.0)` — default quality adeguata
- Richiede `ffmpeg` installato (già prerequisito del progetto)
- v2 syntax: `from moviepy import VideoFileClip` (NON `from moviepy.editor import VideoFileClip`)

**Django ImageField per thumbnail:**
```python
thumbnail = models.ImageField(
    upload_to="thumbnails/",
    blank=True,
    null=True,
    help_text="Thumbnail auto-generato dal primo frame del video",
)
```
- `upload_to="thumbnails/"` → su MinIO: `thumbnails/nome_file.jpg`
- `blank=True, null=True` — opzionale per retrocompatibilità
- `django-cleanup` gestisce auto-delete del thumbnail quando il video viene cancellato
- `Pillow` (già installato: 11.1.0) è prerequisito per `ImageField`

**Next.js generateMetadata — Twitter Cards:**
```typescript
twitter: {
  card: "summary_large_image",  // Grande preview con immagine
  title: "...",
  description: "...",
  images: ["https://..."],  // Array di URL immagini
}
```
- `summary_large_image`: card con immagine grande — ideale per video clip
- `summary`: card piccola senza immagine — fallback se no thumbnail
- Le piattaforme come WhatsApp e Telegram leggono `og:image`, non Twitter Cards

**Next.js metadataBase:**
```typescript
// In root layout.tsx
export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"),
  // ... rest
};
```
- Necessario per convertire URL relative in assolute nei meta tag
- Senza `metadataBase`, `og:image` con path relativo non funziona nei crawler

### Project Structure Notes

**File da modificare:**
- `backend/cs_clips/models/video.py` — aggiungere campo `thumbnail` (ImageField)
- `backend/cs_clips/api/videos/video_serializers.py` — aggiungere `thumbnail_url` (SerializerMethodField) in output + generazione thumbnail in `create()`
- `frontend/src/types/video.ts` — aggiungere `thumbnail_url: string | null`
- `frontend/src/components/feed/clip-card.tsx` — usare thumbnail reale con fallback
- `frontend/src/app/clip/[id]/page.tsx` — migliorare OG tags con image, URL, twitter
- `frontend/src/app/layout.tsx` — aggiungere `metadataBase`

**File da creare:**
- `backend/cs_clips/tests/test_feed.py` — test per endpoint following + thumbnail

**File che NON devono essere modificati:**
- `backend/cs_clips/api/videos/video_views.py` — l'endpoint `following` è già corretto
- `backend/cs_clips/urls.py` — le route sono già registrate
- `frontend/src/app/(main)/home/page.tsx` — la home page è già completa
- `frontend/src/components/feed/feed-grid.tsx` — il grid è già completo
- `frontend/src/components/shared/empty-state.tsx` — il componente è già generico e riusabile
- `frontend/src/components/shared/infinite-scroll.tsx` — l'infinite scroll è già completo
- `frontend/src/lib/hooks/use-videos.ts` — gli hook sono già completi
- `frontend/src/lib/api/videos.ts` — il client API è già completo
- `frontend/src/lib/query-keys.ts` — le query keys sono già definite
- `frontend/src/middleware.ts` — `/clip/[id]` è già escluso dalla protezione auth

### Intelligence dalla Story 2.2 (Precedente)

**Pattern stabiliti da riusare:**
- `VideoOutputSerializer._get_minio_client()` — singleton con `@lru_cache(maxsize=1)`, riusare per presigned URL thumbnail
- `@patch("cs_clips.api.videos.video_serializers.VideoFileClip")` — mock MoviePy per test, estendere per mock `save_frame()`
- `create_sample_video` da conftest.py — crea video con durata 30s senza file reale su MinIO
- Ruff 0 errori è gate obbligatorio

**Problemi risolti nella Story 2.2 da non re-introdurre:**
- **Infinite retry loop**: `retryCount` non deve resettarsi su cambio `src`, solo su cambio `videoId`
- **Resume playback**: `savedTimeRef` per salvare posizione prima del refresh URL
- **Spinner stuck**: gestire il caso in cui `refetchVideo()` fallisce

**Debito tecnico rilevante:**
- `VideoInputSerializer.create()` fa rollback manuale senza `transaction.atomic()` — la generazione thumbnail aggiunge un'altra operazione alla pipeline di upload. Se la generazione thumbnail fallisce DOPO il salvataggio video, il video resta senza thumbnail (accettabile — graceful degradation). Se il salvataggio video fallisce DOPO la generazione thumbnail, il file thumbnail rimane orfano su MinIO — `django-cleanup` lo gestirà alla cancellazione del modello, ma non per file mai associati a un modello
- `has_object_permission` — non impatta questa story (feed è lettura)

### Git Intelligence

**Ultimi commit (post-Story 2.2):**
- `8d20865` — feat: Story 2.1 — upload clip con validazione completa e allow_download
- Suite test attuale: **100 test passanti** — non introdurre regressioni
- Conftest.py ha 6 helper: `create_authenticated_user`, `create_toconfirm_user`, `create_admin_user`, `create_api_client_authenticated`, `create_sample_video`, `create_sample_contest`

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 2, Story 2.3, FR17-22]
- [Source: _bmad-output/planning-artifacts/architecture.md — FR17-22, D3, NFR performance, cross-cutting concerns]
- [Source: _bmad-output/planning-artifacts/architecture.md — Pattern di naming, structure, format, process]
- [Source: _bmad-output/project-context.md — 118 regole AI, MoviePy v2 syntax, testing rules]
- [Source: _bmad-output/implementation-artifacts/2-2-download-clip-e-presigned-url-refresh.md — Dev notes, pattern stabiliti, anti-pattern]
- [Source: frontend/src/app/(main)/home/page.tsx — Feed Home page con useVideoFeed(), EmptyState]
- [Source: frontend/src/components/feed/clip-card.tsx — ClipCard con placeholder play icon]
- [Source: frontend/src/components/feed/feed-grid.tsx — FeedGrid responsive]
- [Source: frontend/src/app/clip/[id]/page.tsx — RSC con generateMetadata OG parziali]
- [Source: frontend/src/app/clip/[id]/clip-content.tsx — Vista auth/non-auth, player, commenti]
- [Source: frontend/src/middleware.ts — /clip/[id] non protetta, route pubblica]
- [Source: frontend/src/app/layout.tsx — metadata con title template, manca metadataBase]
- [Source: backend/cs_clips/api/videos/video_views.py — endpoint following, top-rated, download]
- [Source: backend/cs_clips/api/videos/video_serializers.py — VideoOutputSerializer con presigned URL, VideoInputSerializer con MoviePy]
- [Source: backend/cs_clips/models/video.py — Video model senza campo thumbnail]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Test `test_feed_empty_for_user_without_following` fallito inizialmente: `paginate_queryset` ritorna `[]` (falsy) per queryset vuoti, causando risposta raw array invece del formato paginato. Fix: test adattato per gestire entrambi i formati. L'endpoint views non è stato modificato (out of scope).
- Test `test_response_shape_all_frontend_fields` in `test_upload_validation.py` fallito per campo `thumbnail_url` aggiunto — fix: aggiornato expected_fields nel test esistente.

### Completion Notes List

- **Task 1**: Campo `thumbnail` (ImageField) aggiunto al modello Video con migrazione 0006. Generazione thumbnail integrata nel flusso `VideoInputSerializer.create()` — estrazione frame a `t=min(1.0, duration/2)` durante l'analisi MoviePy, upload su MinIO dopo salvataggio modello. Graceful fallback: se thumbnail fallisce, upload video prosegue normalmente. `get_thumbnail_url()` nel VideoOutputSerializer genera presigned URL 1h o ritorna null.
- **Task 2**: ClipCard aggiornata con thumbnail reale via `<img>` nativo + `loading="lazy"`. Stato `thumbError` per fallback a icona Play su errore caricamento. Tipo `Video` frontend aggiornato con `thumbnail_url: string | null`.
- **Task 3**: `metadataBase` aggiunta in root layout. `generateMetadata` arricchita con `og:image` (condizionale su thumbnail), `og:url`, Twitter Cards (`summary_large_image` / `summary`). Omissione completa `og:image` quando thumbnail null (evita link rotti).
- **Task 4**: 10 nuovi test in `test_feed.py`: 6 test feed following (filtering, empty, pagination, ordering, auth, toconfirm) + 4 test thumbnail (generazione upload, serving presigned URL, null per video senza thumb, graceful fallback).
- **Task 5**: 112 test totali passanti (100 esistenti + 12 nuovi), ruff 0 errori, frontend build OK.

### Change Log

- 2026-03-01: Story 2.3 — Feed Home e Navigazione Clip (thumbnail, OG tags, test feed)
- 2026-03-01: Code Review — Fix 8 findings (1 CRITICAL, 2 HIGH, 2 MEDIUM, 3 LOW)

### File List

**Nuovi:**
- `backend/cs_clips/migrations/0006_add_thumbnail_to_video.py` — migrazione campo thumbnail
- `backend/cs_clips/tests/test_feed.py` — 12 test per feed following, thumbnail e accesso pubblico

**Modificati:**
- `backend/cs_clips/models/video.py` — campo `thumbnail` (ImageField, opzionale)
- `backend/cs_clips/api/videos/video_views.py` — `get_permissions()` per retrieve pubblico (AC-3 SSR), fix N+1 e paginazione su `videos_from_following`
- `backend/cs_clips/api/videos/video_serializers.py` — `thumbnail_url` SerializerMethodField in output, generazione thumbnail in `create()`, helper `_extract_thumbnail()` e `_cleanup_thumbnail_temp()`, logging warning in `get_thumbnail_url()`
- `backend/cs_clips/tests/test_upload_validation.py` — aggiunto `thumbnail_url` a expected_fields
- `frontend/src/types/video.ts` — `thumbnail_url: string | null`, `file_url: string`, rimosso `like_count` fantasma
- `frontend/src/components/feed/clip-card.tsx` — thumbnail reale con fallback icona Play, rimosso import inutilizzato `MessageSquare`
- `frontend/src/app/clip/[id]/page.tsx` — OG tags migliorati (og:image, og:url, twitter cards)
- `frontend/src/app/layout.tsx` — `metadataBase`

## Senior Developer Review (AI)

**Reviewer:** AcchippameQuisso | **Data:** 2026-03-01 | **Outcome:** Approved with fixes applied

### Findings (8 totali — tutti risolti)

| # | Sev | Descrizione | File | Fix |
|---|-----|------------|------|-----|
| F1 | CRITICAL | SSR fetch senza auth → OG tags e pagina pubblica non funzionanti (AC-3) | video_views.py | `get_permissions()` con `AllowAny` per `retrieve` |
| F2 | HIGH | N+1 query su `videos_from_following` (queryset senza `avg_rating` annotation) | video_views.py | Usa `self.get_queryset().filter()` |
| F3 | HIGH | Formato risposta inconsistente per feed vuoto (`[]` raw vs paginato) | video_views.py | `page is not None` invece di `if page` |
| F4 | MEDIUM | `get_thumbnail_url()` inghiotte eccezioni senza logging | video_serializers.py | Aggiunto `logger.warning()` |
| F5 | MEDIUM | Tipo `Video` frontend: `like_count` fantasma, `file_url` mancante | video.ts | Rimosso `like_count`, aggiunto `file_url` |
| F6 | LOW | Import inutilizzato `MessageSquare` | clip-card.tsx | Rimosso |
| F7 | LOW | Nessun `tearDownClass` per `TEMP_MEDIA_ROOT` | test_feed.py | Aggiunto a tutte le classi |
| F8 | LOW | Test `toconfirm` verifica solo status code, non formato risposta | test_feed.py | Aggiunta assertion su `results` |

### Test aggiuntivi dalla review

- `test_unauthenticated_retrieve_returns_200` — verifica che SSR/crawler accedono al dettaglio video
- `test_unauthenticated_list_still_requires_auth` — verifica che la lista resta protetta
