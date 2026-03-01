# Story 1.4: Filtro Video per Uploader Backend

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utente registrato,
I want che il mio profilo carichi solo i miei video dal backend,
so that la pagina profilo è performante anche con molti video sulla piattaforma.

## Acceptance Criteria (BDD)

### AC-1: Filtro video per uploader via query param (FR49)

```gherkin
Scenario: Filtro video per uploader ID
  Given un utente autenticato
  When chiama GET /api/videos/?uploader={id}
  Then il backend ritorna solo i video di quell'uploader
  And la risposta è paginata nel formato standard {count, next, previous, results}
  And i risultati sono ordinati per -created_at (più recenti prima)

Scenario: Filtro con uploader senza video
  Given un uploader senza video caricati
  When chiama GET /api/videos/?uploader={id}
  Then riceve risposta paginata vuota {count: 0, next: null, previous: null, results: []}

Scenario: Filtro con uploader inesistente
  Given un ID uploader che non esiste nel database
  When chiama GET /api/videos/?uploader=99999
  Then riceve risposta paginata vuota {count: 0, next: null, previous: null, results: []}
  And NON un errore 404 (filtro vuoto, non risorsa mancante)
```

### AC-2: Paginazione corretta con filtro (FR49)

```gherkin
Scenario: Paginazione con filtro uploader
  Given un uploader con 15 video (page_size=10)
  When chiama GET /api/videos/?uploader={id}
  Then riceve {count: 15, next: "...?uploader={id}&page=2", results: [10 video]}

Scenario: Pagina 2 con filtro uploader
  Given un uploader con 15 video
  When chiama GET /api/videos/?uploader={id}&page=2
  Then riceve {count: 15, previous: "...?uploader={id}", results: [5 video]}
  And il parametro uploader è preservato nei link next/previous
```

### AC-3: Endpoint video senza filtro invariato (non-regressione)

```gherkin
Scenario: GET /api/videos/ senza filtro (invariato)
  Given un utente autenticato
  When chiama GET /api/videos/ senza query param uploader
  Then riceve tutti i video paginati come prima
  And il comportamento è identico a prima dell'implementazione del filtro

Scenario: Le custom actions esistenti non sono impattate
  Given un utente autenticato
  When chiama GET /api/videos/following/ o GET /api/videos/top-rated/
  Then il comportamento è identico a prima
```

### AC-4: Frontend usa filtro server-side (fix useUserVideos)

```gherkin
Scenario: useUserVideos usa il filtro backend
  Given un utente che visita il profilo di un altro utente
  When il frontend carica i video dell'utente
  Then chiama GET /api/videos/?uploader={id}&page=N (filtro server-side)
  And NON scarica tutti i video per poi filtrare client-side
  And la paginazione funziona correttamente (next page carica solo video dell'utente)
```

## Tasks / Subtasks

- [x] **Task 1: Installare e configurare django-filter** (AC: #1, #3)
  - [x] 1.1 Installare django-filter: `pip install django-filter` nel venv
  - [x] 1.2 Aggiungere `django-filter` a `backend/requirements.txt`
  - [x] 1.3 Aggiungere `"django_filters"` a `INSTALLED_APPS` in `backend/project_clip/settings.py` (NOTA: underscore, non trattino)
  - [x] 1.4 Aggiungere `"django_filters.rest_framework.DjangoFilterBackend"` a `DEFAULT_FILTER_BACKENDS` in `REST_FRAMEWORK` settings

- [x] **Task 2: Aggiungere filterset_fields al VideoViewSet** (AC: #1, #2)
  - [x] 2.1 In `backend/cs_clips/api/videos/video_views.py`, aggiungere `filterset_class = VideoFilter` con `NumberFilter` alla classe `VideoViewSet`
  - [x] 2.2 Verificare che il queryset base `Video.objects.all().order_by("-created_at")` funzioni correttamente con il filtro (l'ordine viene preservato)

- [x] **Task 3: Aggiornare il frontend per usare il filtro server-side** (AC: #4)
  - [x] 3.1 In `frontend/src/lib/api/videos.ts`, aggiungere metodo `getByUploader`:
    ```typescript
    getByUploader: (uploaderId: number, page = 1) =>
      apiClient
        .get<PaginatedResponse<Video>>("/videos/", { params: { uploader: uploaderId, page } })
        .then((r) => normalizePaginated(r.data)),
    ```
  - [x] 3.2 In `frontend/src/lib/hooks/use-videos.ts`, modificare `useUserVideos` per accettare `userId: number` e usare `videosApi.getByUploader(userId, pageParam)` — rimuovere il `select` con filtro client-side
  - [x] 3.3 In `frontend/src/app/(main)/profilo/[username]/page.tsx`, aggiornare la chiamata a `useUserVideos(profileUser?.id ?? 0)` — passare l'ID utente (già disponibile da `useUserByUsername`)
  - [x] 3.4 Aggiornare `queryKeys.videos.byUser` per riflettere il cambio da `username: string` a `userId: number`

- [x] **Task 4: Scrivere test backend** (AC: #1, #2, #3)
  - [x] 4.1 Creare test in `backend/cs_clips/tests/test_video_filter.py`
  - [x] 4.2 Test filtro per uploader → 200, solo video dell'uploader specificato nei results
  - [x] 4.3 Test filtro con uploader senza video → 200, `{count: 0, results: []}`
  - [x] 4.4 Test filtro con uploader inesistente → 200, risposta paginata vuota (non 404)
  - [x] 4.5 Test paginazione con filtro → con >10 video per un uploader, page=2 funziona
  - [x] 4.6 Test GET /api/videos/ senza filtro → comportamento invariato (non-regressione)
  - [x] 4.7 Test ordinamento con filtro → i video filtrati mantengono ordine `-created_at`
  - [x] 4.8 Usare helper da `conftest.py` (`create_authenticated_user`, `create_api_client_authenticated`)
  - [x] 4.9 Eseguire `ruff check backend/` e `ruff format backend/` — zero errori

- [x] **Task 5: Verificare integrazione frontend↔backend** (AC: #1, #4)
  - [x] 5.1 Verificare che `GET /api/videos/?uploader={id}` risponda con `PaginatedResponse<Video>` — stessa shape di `GET /api/videos/`
  - [x] 5.2 Verificare che il campo `uploader` nei results sia la stringa username (non l'ID) — `VideoOutputSerializer` serializza `uploader` come `source="uploader.username"`
  - [x] 5.3 Verificare che le custom actions (`/following/`, `/top-rated/`) non siano impattate
  - [x] 5.4 Verificare che `npm run build` frontend compili senza errori dopo le modifiche

## Dev Notes

### Contesto Critico

Questa story risolve un **problema di performance**: il hook `useUserVideos` attualmente scarica TUTTI i video dalla piattaforma e li filtra client-side per username. Con la crescita dei contenuti, la performance degrada linearmente — su 1000 video, ogni pagina profilo scarica tutte le 100 pagine da 10 per trovare i video dell'utente.

**Il fix è in due parti:**
1. **Backend**: abilitare il filtro `?uploader=` nel `VideoViewSet` via `django-filter` e `filterset_fields`
2. **Frontend**: aggiornare `useUserVideos` per chiamare `GET /api/videos/?uploader={id}` invece di scaricare tutto

### Stato Attuale del Codice

**Backend — VideoViewSet (`backend/cs_clips/api/videos/video_views.py`):**
```python
class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all().order_by("-created_at")
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
```
- Nessun filtro configurato
- `django-filter` NON è installato (nonostante il project-context.md lo elenchi come parte dello stack)
- Nessun `DEFAULT_FILTER_BACKENDS` in settings

**Backend — Video model (`backend/cs_clips/models/video.py`):**
```python
uploader = models.ForeignKey(
    User, on_delete=models.CASCADE, related_name="uploaded_videos"
)
```
- `uploader` è FK a User — `filterset_fields = ["uploader"]` filtrerà per `uploader_id` (intero)

**Backend — VideoOutputSerializer:**
```python
uploader = serializers.ReadOnlyField(source="uploader.username")
```
- Il campo `uploader` nella risposta API è la **stringa username**, non l'ID
- Il filtro `?uploader=` accetta l'**ID numerico** (FK), non lo username
- Questa asimmetria è intenzionale: si filtra per ID (performante, FK diretto) ma si mostra lo username (UX leggibile)

**Frontend — useUserVideos (`frontend/src/lib/hooks/use-videos.ts`):**
```typescript
export function useUserVideos(username: string) {
  return useInfiniteQuery({
    queryKey: queryKeys.videos.byUser(username),
    queryFn: ({ pageParam = 1 }) => videosApi.getAll(pageParam),  // ← scarica TUTTO
    getNextPageParam: (lastPage) => extractPageFromUrl(lastPage.next),
    initialPageParam: 1,
    select: (data) => ({
      ...data,
      pages: data.pages.map((page) => ({
        ...page,
        results: page.results.filter((v) => v.uploader === username),  // ← filtra client-side
      })),
    }),
  });
}
```
- **BUG**: chiama `videosApi.getAll()` (endpoint generico senza filtro) e filtra in `select`
- La paginazione è rotta: `getNextPageParam` punta alla pagina successiva di TUTTI i video, non solo quelli dell'utente
- Il `count` nel risultato è il totale di tutti i video, non solo quelli dell'uploader

**Frontend — Pagina profilo (`frontend/src/app/(main)/profilo/[username]/page.tsx`):**
```typescript
const { data: profileUser } = useUserByUsername(username);  // ← ha profileUser.id
const { data: userVideosData } = useUserVideos(username);   // ← passa username
```
- `profileUser` ha già l'ID numerico dall'API — può essere passato a `useUserVideos`

**Frontend — Query Keys (`frontend/src/lib/query-keys.ts`):**
```typescript
byUser: (username: string) => ["videos", "user", username] as const,
```
- La key usa username — valutare se cambiare a userId per coerenza con il filtro backend

### Pattern da Seguire

**Configurazione django-filter in settings.py:**
```python
# In INSTALLED_APPS — aggiungere DOPO django_extensions se presente
INSTALLED_APPS = [
    ...
    "django_filters",  # NOTA: underscore, non trattino
    ...
]

# In REST_FRAMEWORK — aggiungere la chiave DEFAULT_FILTER_BACKENDS
REST_FRAMEWORK = {
    ...
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    ...
}
```

**filterset_class con NumberFilter nel VideoViewSet:**
```python
class VideoFilter(django_filters.FilterSet):
    """NumberFilter su uploader_id: evita validazione FK, ID inesistenti → 200 vuoto."""
    uploader = django_filters.NumberFilter(field_name="uploader_id")

    class Meta:
        model = Video
        fields = ["uploader"]

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all().order_by("-created_at")
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    filterset_class = VideoFilter
```
- **NON usare** `filterset_fields = ["uploader"]` — valida la FK e ritorna 400 per ID inesistenti
- `NumberFilter(field_name="uploader_id")` tratta il campo come intero semplice: ID inesistenti → risposta vuota 200
- DjangoFilterBackend si integra automaticamente con la paginazione DRF — i link `next`/`previous` preservano i query param del filtro

**Frontend — Nuovo metodo API e hook aggiornato:**
```typescript
// In videos.ts — aggiungere metodo
getByUploader: (uploaderId: number, page = 1) =>
  apiClient
    .get<PaginatedResponse<Video>>("/videos/", { params: { uploader: uploaderId, page } })
    .then((r) => normalizePaginated(r.data)),

// In use-videos.ts — modificare useUserVideos
export function useUserVideos(userId: number) {
  return useInfiniteQuery({
    queryKey: queryKeys.videos.byUser(userId),
    queryFn: ({ pageParam = 1 }) => videosApi.getByUploader(userId, pageParam),
    getNextPageParam: (lastPage) => extractPageFromUrl(lastPage.next),
    initialPageParam: 1,
    enabled: userId > 0,
  });
}
```
- Rimuovere completamente il `select` con filtro client-side — il backend restituisce già solo i video dell'uploader
- Aggiungere `enabled: userId > 0` per evitare chiamate con userId=0 (profilo non ancora caricato)

**Test — Pattern da conftest.py:**
```python
from cs_clips.tests.conftest import create_authenticated_user, create_api_client_authenticated

class TestVideoFilter(APITestCase):
    def setUp(self):
        self.user_a = create_authenticated_user(username="alice")
        self.user_b = create_authenticated_user(username="bob")
        self.client_a = create_api_client_authenticated(self.user_a)
        # Creare video per ciascun utente (senza file reale — mockare lo storage)
```

### Anti-Pattern da Evitare

- **MAI** filtrare client-side quando il backend può farlo — è il bug che questa story corregge
- **MAI** usare `filter()` Python/JS su dati paginati — la paginazione conta il totale pre-filtro, rendendo `count` e `next` errati
- **MAI** confondere il filtro `?uploader=<id>` (accetta ID numerico) con il campo `uploader` nelle risposte API (stringa username) — sono due cose diverse
- **MAI** creare un endpoint custom `/api/videos/by-uploader/{id}/` — usare il pattern standard `django-filter` con query param
- **MAI** aggiungere `"django-filter"` con trattino in INSTALLED_APPS — il nome del package Python è `"django_filters"` con underscore e `s` finale
- **MAI** aggiungere `filterset_fields` senza configurare `DEFAULT_FILTER_BACKENDS` in settings — il filtro non funzionerebbe
- **MAI** importare `from cs_clips.models.user import User` — usare `get_user_model()`
- **MAI** creare test utenti senza assegnare un gruppo — usare helper da conftest.py

### Informazioni Tecniche Aggiornate

- **django-filter 25.2** (versione più recente, 2025): compatibile con Django 5.1+ e DRF 3.15+. Il progetto attualmente non lo ha installato nonostante il project-context.md lo elenchi come "24.3" — installare la versione più recente.
- **`DjangoFilterBackend`**: quando configurato globalmente in `DEFAULT_FILTER_BACKENDS`, si applica a tutti i ViewSet. Ogni ViewSet con `filterset_fields` abilita automaticamente il filtraggio. ViewSet senza `filterset_fields` non sono impattati.
- **Integrazione automatica paginazione**: `DjangoFilterBackend` si integra con `PageNumberPagination` — i query param del filtro (`?uploader=1`) vengono preservati nei link `next`/`previous` generati da DRF. Non serve codice aggiuntivo.
- **drf-spectacular**: `DjangoFilterBackend` è supportato nativamente da drf-spectacular 0.28+ — i parametri filtro appaiono automaticamente nella documentazione OpenAPI (`/api/docs/`).

### Project Structure Notes

- **Allineamento**: tutti i file toccati seguono la struttura modulare stabilita
- **File backend modificati**: `project_clip/settings.py` (INSTALLED_APPS + DEFAULT_FILTER_BACKENDS), `cs_clips/api/videos/video_views.py` (+1 riga)
- **File backend nuovi**: `cs_clips/tests/test_video_filter.py`
- **File frontend modificati**: `src/lib/api/videos.ts` (+1 metodo), `src/lib/hooks/use-videos.ts` (useUserVideos), `src/app/(main)/profilo/[username]/page.tsx` (passaggio userId), possibile `src/lib/query-keys.ts` (tipo parametro byUser)
- **Dipendenza nuova**: `django-filter` in `requirements.txt`
- **Nessun nuovo modello, nessuna migrazione necessaria**

### Frontend Integration

**Pagina profilo — flusso attuale (BUG):**
1. `useUserByUsername(username)` → ottiene `profileUser` con `id`
2. `useUserVideos(username)` → chiama `GET /api/videos/?page=1` (TUTTI i video)
3. `select` filtra `v.uploader === username` → ritorna subset scorretto con count/next errati

**Pagina profilo — flusso corretto (dopo fix):**
1. `useUserByUsername(username)` → ottiene `profileUser` con `id`
2. `useUserVideos(profileUser.id)` → chiama `GET /api/videos/?uploader={id}&page=1` (solo video dell'utente)
3. Nessun filtro client-side — backend ritorna dati corretti con count/next precisi

**NOTA CRITICA — Timing di `enabled`:**
- `profileUser` arriva dall'hook `useUserByUsername` che è asincrono
- `useUserVideos(profileUser?.id)` potrebbe ricevere `undefined` prima che il profilo sia caricato
- Usare `enabled: userId > 0` nel hook, oppure gestire la condizione nella pagina profilo:
  ```typescript
  const { data: userVideosData } = useUserVideos(profileUser?.id ?? 0);
  ```

**Query Keys — Cambio tipo:**
- Attuale: `byUser: (username: string) => ["videos", "user", username]`
- Nuovo: `byUser: (userId: number) => ["videos", "user", userId]`
- Questo cambio di tipo è sicuro perché la key era legata al filtro client-side — nessun altro componente la usa direttamente

### Intelligence dalla Story 1.3 (Precedente)

**Pattern stabiliti da riusare:**
- `get_user_model()` ovunque — MAI import diretto
- Test con `APITestCase`, `force_authenticate`, helper da `conftest.py`
- Formato errori: `{code, detail}` dal global exception handler
- Ruff check + format obbligatori prima di ogni commit
- Test devono asserire sul contenuto della risposta, non solo sullo status code
- Code review 1.3: test 403/404 devono verificare body `{code, detail}`, usare helper conftest.py

**Problemi risolti in story precedenti:**
- N+1 queries: risolto con annotazioni queryset in Story 1.2
- Paginazione custom actions: risolto con `self.paginate_queryset()` in Story 1.3
- `self.get_serializer()` vs `Serializer()` diretto: usare sempre `self.get_serializer()` (fix H2 review 1.3)

### Git Intelligence

**Ultimi commit (pattern recenti):**
- `859f0a8` — Story 1.1 + Story 1.2: auth end-to-end e profilo utente con bio (14 test profile)
- `4f42b36` — Epic 0 retrospettiva completata
- `ca75ed4` — Story 0-3 + Story 0-4: testing baseline, CI/CD, Django Admin
- Pattern commit: `feat: Story X.Y — descrizione breve`

**Insight rilevanti:**
- django-filter era pianificato fin dall'architettura (project-context.md lo elenca) ma non è mai stato installato
- Le dipendenze backend sono in `backend/requirements.txt` (non pyproject.toml)
- La suite test attuale ha 63 test passanti — non introdurre regressioni
- Story 1.3 ha introdotto `create_toconfirm_user()` in conftest.py

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 1, Story 1.4]
- [Source: _bmad-output/planning-artifacts/architecture.md — FR49, useUserVideos client-side, filterset_fields pattern]
- [Source: _bmad-output/planning-artifacts/prd.md — FR49: lista video filtrata per uploader]
- [Source: _bmad-output/project-context.md — django-filter 24.3 (da aggiornare a 25.2), filterset_fields, DEFAULT_FILTER_BACKENDS]
- [Source: backend/cs_clips/api/videos/video_views.py — VideoViewSet senza filtri]
- [Source: backend/cs_clips/api/videos/video_serializers.py — VideoOutputSerializer con uploader=username string]
- [Source: backend/cs_clips/models/video.py — Video.uploader FK a User]
- [Source: backend/project_clip/settings.py — REST_FRAMEWORK senza DEFAULT_FILTER_BACKENDS]
- [Source: frontend/src/lib/hooks/use-videos.ts — useUserVideos con filtro client-side]
- [Source: frontend/src/lib/api/videos.ts — videosApi senza metodo getByUploader]
- [Source: frontend/src/lib/query-keys.ts — queryKeys.videos.byUser(username)]
- [Source: frontend/src/app/(main)/profilo/[username]/page.tsx — ProfiloPage con useUserVideos(username)]
- [Source: frontend/src/types/video.ts — Video interface con uploader: string]
- [Source: backend/cs_clips/tests/conftest.py — Helper functions (create_authenticated_user, etc.)]
- [Source: _bmad-output/implementation-artifacts/1-3-follow-unfollow-e-liste-paginate.md — pattern test, anti-pattern, code review feedback]

## Senior Developer Review (AI)

**Reviewer:** Claude Opus 4.6 — Adversarial Code Review
**Date:** 2026-03-01
**Verdict:** APPROVED — All HIGH and MEDIUM issues fixed, all ACs implemented

### Issues Found: 9 (2 HIGH, 4 MEDIUM, 3 LOW)

| # | Sev | Issue | Fix Applied |
|---|-----|-------|-------------|
| H1 | HIGH | `videoCount={videos.length}` mostra count client-side (max 10) invece del totale server | Aggiunto `totalVideoCount = userVideosData?.pages[0]?.count ?? 0`; ProfileHeader usa `totalVideoCount` |
| H2 | HIGH | Nessun error handling per fallimento caricamento video nel profilo | Aggiunto `isError: videosError` + `EmptyState` con `AlertTriangle` prima del loading/empty check |
| M1 | MEDIUM | Test non-regressione AC-3 troppo superficiali (solo status 200) | `test_following_action_not_impacted`: verifica struttura dict paginated; `test_top_rated`: verifica `count` corretto |
| M2 | MEDIUM | Nessun test per `?uploader=abc` (valore non numerico) | Aggiunto `test_filter_uploader_non_numeric_returns_error` → 400 |
| M3 | MEDIUM | N+1 query `get_average_rating`: 3 query/video amplificata dal nuovo filtro | `get_queryset()` con `Avg("ratings__value")` annotation; serializer con fallback `hasattr(obj, "avg_rating")` |
| M4 | MEDIUM | Dev Notes "Pattern da Seguire" mostra `filterset_fields` (approccio rifiutato) | Aggiornato per mostrare `filterset_class` + `NumberFilter` con spiegazione del motivo |
| L1 | LOW | `django-filter==24.3` invece di 25.2 raccomandato nei Dev Notes | Non corretto — 24.3 compatibile e pre-installato |
| L2 | LOW | Codice commentato in `videos_from_following` (dead code pre-esistente) | Non corretto — pre-esistente, fuori scope |
| L3 | LOW | f-string in chiamate logger (anti-pattern pre-esistente) | Non corretto — pre-esistente, fuori scope |

### Verification

- **ACs coverage:** AC-1 ✓ AC-2 ✓ AC-3 ✓ AC-4 ✓
- **Test count:** 14 (12 originali + 2 da review: M1 migliorati, M2 aggiunto)
- **File List aggiornato** con file toccati dalla review

## Change Log

- 2026-03-01: Implementazione completa Story 1.4 — filtro video per uploader backend + fix frontend useUserVideos
- 2026-03-01: Code Review — 2 HIGH, 4 MEDIUM, 3 LOW trovati. Fix applicati: videoCount server-side, error handling video, test non-regressione migliorati, test edge case non-numerico, N+1 avg_rating con annotazione Avg, Dev Notes pattern aggiornato

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- django-filter con FK `filterset_fields = ["uploader"]` valida l'esistenza dell'FK e ritorna 400 per ID inesistenti. Risolto con `VideoFilter` custom che usa `NumberFilter(field_name="uploader_id")` per trattare il campo come intero semplice, permettendo ID inesistenti di restituire risultati vuoti (200) invece di errori (400).
- Action `/following/` ritorna array vuoto `[]` (non paginato) quando l'utente non segue nessuno — bug pre-esistente nel codice di `videos_from_following`, non introdotto da questa story.

### Completion Notes List

- ✅ Task 1: django-filter 24.3 era gia' installato nel venv ma non configurato. Aggiunto a requirements.txt, INSTALLED_APPS e DEFAULT_FILTER_BACKENDS.
- ✅ Task 2: Usato `filterset_class = VideoFilter` con `NumberFilter` invece di `filterset_fields` per gestire correttamente ID uploader inesistenti (AC-1 scenario 3).
- ✅ Task 3: Frontend aggiornato — `useUserVideos` ora accetta `userId: number`, chiama `getByUploader(userId, page)`, rimosso filtro client-side `select`. Query key cambiata da `string` a `number`. Pagina profilo passa `profileUser?.id ?? 0` con `enabled: userId > 0`.
- ✅ Task 4: 12 test scritti in 3 classi (TestVideoFilterByUploader, TestVideoFilterPagination, TestVideoListWithoutFilter). Coprono tutti gli AC: filtro, paginazione, uploader vuoto/inesistente, ordinamento, non-regressione.
- ✅ Task 5: Integrazione verificata — shape risposta identica, uploader come stringa username, custom actions invariate, frontend build OK.
- ✅ Suite regressione: 75 test passanti (63 pre-esistenti + 12 nuovi), zero regressioni.
- ✅ ruff check + format: zero errori.

#### Code Review Fix (2026-03-01)

- 🔧 H1: `videoCount` usa `userVideosData.pages[0].count` (server-side) invece di `videos.length` (client-side)
- 🔧 H2: Aggiunto error handling (`isError` + `EmptyState` con `AlertTriangle`) per fallimento caricamento video nel profilo
- 🔧 M1: Test non-regressione migliorati — `test_following_action_not_impacted` verifica struttura paginated, `test_top_rated_action_not_impacted` verifica `count` corretto
- 🔧 M2: Aggiunto `test_filter_uploader_non_numeric_returns_error` per edge case `?uploader=abc` → 400
- 🔧 M3: N+1 query `average_rating` risolta con `get_queryset()` + `Avg("ratings__value")` annotation nel ViewSet, serializer con fallback `hasattr(obj, "avg_rating")`
- 🔧 M4: Dev Notes "Pattern da Seguire" aggiornato per riflettere `filterset_class` + `NumberFilter` (non `filterset_fields`)

### File List

- `backend/requirements.txt` — aggiunto `django-filter==24.3`
- `backend/project_clip/settings.py` — aggiunto `"django_filters"` a INSTALLED_APPS, `DEFAULT_FILTER_BACKENDS` a REST_FRAMEWORK
- `backend/cs_clips/api/videos/video_views.py` — aggiunta classe `VideoFilter` (NumberFilter), `filterset_class = VideoFilter`, `get_queryset()` con Avg annotation _(review: M3)_
- `backend/cs_clips/api/videos/video_serializers.py` — `get_average_rating` usa annotazione `avg_rating` con fallback _(review: M3)_
- `backend/cs_clips/tests/test_video_filter.py` — **NUOVO** — 14 test per filtro video per uploader _(review: M1, M2 — +2 test)_
- `frontend/src/lib/api/videos.ts` — aggiunto metodo `getByUploader`
- `frontend/src/lib/hooks/use-videos.ts` — `useUserVideos` cambiato da `username: string` a `userId: number`, rimosso filtro client-side
- `frontend/src/lib/query-keys.ts` — `byUser` cambiato da `username: string` a `userId: number`
- `frontend/src/app/(main)/profilo/[username]/page.tsx` — `useUserVideos(profileUser?.id ?? 0)`, `totalVideoCount` da server, error state video _(review: H1, H2)_
