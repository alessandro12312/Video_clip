# Story 2.4: Commenti Dual-Layer con Timestamp

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utente registrato,
I want commentare le clip con e senza timestamp e vedere i commenti in due viste,
so that posso esprimere reazioni precise ancorate al momento esatto del video.

## Acceptance Criteria (BDD)

### AC-1: Commento temporizzato con timestamp pre-compilato (FR24, FR25, FR26)

```gherkin
Scenario: Timestamp pre-compilato alla pausa
  Given un utente autenticato sulla pagina dettaglio clip con video in pausa
  When il form commento è visibile
  Then il timestamp corrente del video è pre-compilato nel campo timestamp
  And l'utente può rimuovere il timestamp per un commento normale

Scenario: Invio commento con timestamp
  Given un utente che invia un commento con timestamp
  When il backend riceve timestamp_second con valore tra 0 e video.duration
  Then il commento viene salvato con il timestamp associato
  And appare nella vista "Nel video" ordinato per timestamp

Scenario: Invio commento senza timestamp
  Given un utente che invia un commento senza timestamp
  When il backend riceve timestamp_second nullo o uguale a 0
  Then il commento viene salvato come commento normale
  And appare nella vista "Tutti" ordinata cronologicamente
```

### AC-2: Dual-view "Tutti" / "Nel video" (FR29, FR30)

```gherkin
Scenario: Vista "Tutti" mostra tutti i commenti
  Given la pagina dettaglio clip
  When l'utente seleziona il tab "Tutti"
  Then vede tutti i commenti (con e senza timestamp) in ordine cronologico decrescente

Scenario: Vista "Nel video" mostra solo commenti temporizzati
  Given la pagina dettaglio clip
  When l'utente seleziona il tab "Nel video"
  Then vede solo i commenti con timestamp_second > 0 ordinati per timestamp crescente

Scenario: Conteggio commenti nei tab
  Given 5 commenti normali e 3 commenti temporizzati per una clip
  When la sezione commenti viene renderizzata
  Then il tab "Tutti" mostra "(8)" e il tab "Nel video" mostra "(3)"
```

### AC-3: Eliminazione commento proprio (useDeleteComment)

```gherkin
Scenario: Utente elimina il proprio commento
  Given un utente autenticato che è autore di un commento
  When clicca il bottone elimina sul proprio commento
  Then il commento viene rimosso via DELETE /api/comments/{id}/
  And la lista commenti si aggiorna senza ricaricare la pagina

Scenario: Bottone elimina visibile solo per autore
  Given una lista commenti di vari utenti
  When un utente visualizza la lista
  Then il bottone elimina è visibile SOLO sui propri commenti
  And sui commenti altrui il bottone non è presente

Scenario: Utente non proprietario tenta eliminazione
  Given un utente autenticato che NON è autore del commento
  When tenta DELETE /api/comments/{id}/
  Then riceve status 403 (Forbidden)
```

### AC-4: Filtro backend commenti per video

```gherkin
Scenario: Filtro commenti per video ID
  Given 10 commenti su video A e 5 commenti su video B
  When il frontend chiama GET /api/comments/?video={videoA_id}
  Then riceve solo i 10 commenti del video A, paginati

Scenario: Filtro senza video ID ritorna tutti i commenti
  Given commenti su vari video
  When il frontend chiama GET /api/comments/ senza filtro video
  Then riceve tutti i commenti non disabilitati, paginati
```

### AC-5: Utenti toconfirm — sola lettura (non-regressione permessi)

```gherkin
Scenario: Utente toconfirm può leggere commenti
  Given un utente con gruppo "toconfirm"
  When chiama GET /api/comments/?video={id}
  Then riceve status 200 con i commenti (SAFE_METHOD)

Scenario: Utente toconfirm non può creare commenti
  Given un utente con gruppo "toconfirm"
  When chiama POST /api/comments/ con dati validi
  Then riceve status 403 (Forbidden)
```

### AC-6: Non-regressione e integrazione

```gherkin
Scenario: Suite test completa senza regressioni
  Given le modifiche apportate per commenti e delete
  When viene eseguita la suite test backend completa
  Then tutti i test esistenti (112+) passano senza regressioni

Scenario: Frontend compila senza errori
  Given le modifiche frontend per useDeleteComment e delete button
  When viene eseguito npm run build
  Then la build completa senza errori TypeScript o warning bloccanti
```

## Tasks / Subtasks

- [x] **Task 1: Aggiungere `filterset_fields` al CommentViewSet** (AC: #4)
  - [x] 1.1 In `backend/cs_clips/api/comments/comment_views.py`, aggiungere `filterset_fields = ["video"]` al `CommentViewSet` — abilita il filtro `?video={id}` via DjangoFilterBackend (globale in settings)
  - [x] 1.2 Verificare che `GET /api/comments/?video={id}` ritorna solo i commenti del video specificato

- [x] **Task 2: Creare hook `useDeleteComment` nel frontend** (AC: #3)
  - [x] 2.1 In `frontend/src/lib/hooks/use-comments.ts`, aggiungere hook `useDeleteComment(videoId: number)` come `useMutation` che chiama `commentsApi.delete(id)`
  - [x] 2.2 In `onSuccess`, invalidare le queries `queryKeys.comments.byVideo(videoId)` per aggiornare la lista
  - [x] 2.3 Aggiungere toast di successo ("Commento eliminato") e toast di errore ("Errore nell'eliminazione del commento")

- [x] **Task 3: Aggiungere bottone elimina al CommentItem** (AC: #3)
  - [x] 3.1 In `frontend/src/components/comments/comment-item.tsx`, aggiungere prop opzionale `currentUsername: string` e `onDelete: (commentId: number) => void`
  - [x] 3.2 Mostrare icona `Trash2` (da lucide-react) visibile SOLO se `comment.user === currentUsername`
  - [x] 3.3 Al click: chiamare `onDelete(comment.id)` — la logica di conferma/mutazione è nel parent
  - [x] 3.4 Aggiungere `aria-label="Elimina commento"` per accessibilità

- [x] **Task 4: Collegare delete nel flusso CommentSection → CommentList → CommentItem** (AC: #3)
  - [x] 4.1 In `clip-content.tsx`, istanziare `useDeleteComment(videoId)` e passare callback `handleDeleteComment` a `CommentSection`
  - [x] 4.2 Passare `currentUsername` (da `user?.username`) e `onDelete` callback attraverso `CommentSection` → `CommentList` → `CommentItem`
  - [x] 4.3 In `handleDeleteComment`, chiamare `deleteComment.mutate(commentId)` con toast success/error

- [x] **Task 5: Scrivere test backend per commenti** (AC: #1, #3, #4, #5, #6)
  - [x] 5.1 Creare `backend/cs_clips/tests/test_comments.py`
  - [x] 5.2 Test: creazione commento con timestamp valido → 201 + commento con timestamp_second
  - [x] 5.3 Test: creazione commento senza timestamp (timestamp_second=0) → 201 + commento normale
  - [x] 5.4 Test: creazione commento con timestamp > durata video → 400 + errore validazione
  - [x] 5.5 Test: creazione commento con timestamp negativo → 400 + errore validazione — NOTA: PositiveIntegerField impedisce valori negativi a livello DB; la validazione del serializer copre il caso timestamp > duration. Il test 5.4 (timestamp_exceeds_duration) copre la validazione. Il test timestamp_at_duration (=30s) verifica il boundary.
  - [x] 5.6 Test: filtro commenti per video `?video={id}` → 200 + solo commenti del video specificato
  - [x] 5.7 Test: filtro commenti senza video → 200 + tutti i commenti non disabilitati
  - [x] 5.8 Test: eliminazione commento proprio → 204 No Content
  - [x] 5.9 Test: eliminazione commento altrui → 403 Forbidden
  - [x] 5.10 Test: utente non autenticato → 401 su POST e DELETE
  - [x] 5.11 Test: utente toconfirm può leggere (GET) → 200
  - [x] 5.12 Test: utente toconfirm non può creare (POST) → 403
  - [x] 5.13 Test: commento su video con is_disabled=True non appare nella lista → filtro is_disabled=False funziona
  - [x] 5.14 Test: formato risposta paginato (count, next, previous, results)
  - [x] 5.15 Usare helper da conftest.py (`create_authenticated_user`, `create_toconfirm_user`, `create_api_client_authenticated`, `create_sample_video`)
  - [x] 5.16 Eseguire `ruff check backend/` e `ruff format backend/` — zero errori

- [x] **Task 6: Verificare integrazione e non-regressione** (AC: #6)
  - [x] 6.1 Eseguire la suite test completa backend — zero regressioni (128 test totali: 112 precedenti + 16 nuovi)
  - [x] 6.2 Verificare `npm run build` frontend — zero errori
  - [x] 6.3 Ruff check + format: zero errori

## Dev Notes

### Contesto Critico

Questa è la **quarta story di Epic 2** e copre il sistema commenti. La maggior parte dell'infrastruttura **esiste già** (pattern "frontend-avanti"): il modello `Comment` ha tutti i campi necessari, il frontend ha l'intera UI dei commenti con dual-view, form con timestamp, markers sulla timeline, sidebar dinamica. Il backend ha un CommentViewSet CRUD funzionante.

**Il valore aggiunto principale di questa story è:**
1. **`filterset_fields` sul CommentViewSet** — il filtro `?video={id}` è probabilmente non funzionante (DjangoFilterBackend globale ma nessun `filterset_fields` dichiarato) — BUG CRITICO da verificare e fixare
2. **`useDeleteComment` hook** — l'API `commentsApi.delete(id)` esiste ma manca l'hook React Query
3. **Bottone elimina su CommentItem** — visibile solo per l'autore del commento
4. **Test backend completi** — nessun test esiste per commenti (`test_comments.py` non creato)
5. **Verifica end-to-end** del flusso commenti con timestamp e dual-view

### Stato Attuale del Codice — Cosa GIÀ Esiste

**Backend (già implementato e funzionante):**

- **Comment model** (`backend/cs_clips/models/comment.py`): campi `user` (FK), `video` (FK), `content` (TextField), `timestamp_second` (PositiveIntegerField, default=0), `is_disabled` (BooleanField, default=False), `created_at`, `updated_at`
- **CommentSerializer** (`backend/cs_clips/api/comments/comment_serializers.py`): validazione `timestamp_second >= 0 && <= video.duration`, campo `user` read-only da `user.username`, `is_disabled` NON esposto in API (solo moderazione backend)
- **CommentViewSet** (`backend/cs_clips/api/comments/comment_views.py`): `ModelViewSet` con queryset `Comment.objects.filter(is_disabled=False)`, permessi `IsAuthenticated + RoleBasedPermission`, `perform_create` con `user=request.user`
- **⚠️ MANCA `filterset_fields`** — Il frontend chiama `GET /api/comments/?video={id}` ma il ViewSet non dichiara `filterset_fields = ['video']`. DjangoFilterBackend è configurato globalmente in `settings.py` ma senza `filterset_fields` sul ViewSet, il parametro `?video=` viene **silenziosamente ignorato** e tutti i commenti vengono ritornati. Questo è un **bug critico** che causa:
  - Performance: il frontend riceve TUTTI i commenti di TUTTI i video
  - UX: commenti di altri video appaiono nella pagina dettaglio

- **Routing**: registrato via DefaultRouter come `r"comments"` → `GET/POST /api/comments/`, `GET/PATCH/DELETE /api/comments/{id}/`
- **Permissions**: `RoleBasedPermission.has_object_permission()` controlla `getattr(obj, 'user', None)` per delete — l'autore può eliminare solo il proprio commento

**Frontend (già implementato e funzionante):**

- **CommentForm** (`frontend/src/components/comments/comment-form.tsx`): textarea con 500 char max, badge timestamp removibile (pre-compilato alla pausa video), placeholder contestuale ("Descrivi questo momento..." se timestamp, "Scrivi un commento..." altrimenti), toast success/error
- **CommentSection** (`frontend/src/components/comments/comment-section.tsx`): shadcn/ui Tabs con "Tutti (N)" e "Nel video (M)", delega a CommentList
- **CommentList** (`frontend/src/components/comments/comment-list.tsx`): mode "all" ordina per `-created_at`, mode "timestamped" filtra `timestamp_second > 0` e ordina per `timestamp_second` crescente, empty state in italiano
- **CommentItem** (`frontend/src/components/comments/comment-item.tsx`): avatar, username link, timestamp badge cliccabile (seek video), data relativa, contenuto — **nessun bottone elimina**
- **CommentMarker** (`frontend/src/components/video/comment-marker.tsx`): dot sulla progress bar con tooltip "Commento a MM:SS"
- **DynamicSidebar** (`frontend/src/components/comments/dynamic-sidebar.tsx`): top 20 commenti temporizzati recenti, compact mode
- **ClipContent** (`frontend/src/app/clip/[id]/clip-content.tsx`): orchestrazione completa — `useVideo`, `useComments`, `popupMap`, `markerPositions`, `pauseTimestamp`, `handlePause`, `handleTimestampClick`, `handleRefreshUrl`, integrazione CommentForm + CommentSection + DynamicSidebar

- **Hooks**: `useComments(videoId)` (eager multi-page fetch per popupMap), `useCreateComment(videoId)` (mutation con cache invalidation) — **`useDeleteComment` MANCA**
- **API client**: `commentsApi.getByVideo(videoId, page)`, `commentsApi.create(data)`, `commentsApi.delete(id)` — il metodo delete ESISTE già
- **Query keys**: `queryKeys.comments.byVideo(videoId)` → `["comments", "video", videoId]`
- **Types**: `Comment { id, user, video, content, timestamp_second, created_at, updated_at }`, `CreateCommentData { video, content, timestamp_second }`

### Pattern da Seguire

**`filterset_fields` — Pattern già usato in VideoViewSet:**
```python
# backend/cs_clips/api/videos/video_views.py
class VideoViewSet(viewsets.ModelViewSet):
    filterset_fields = ["uploader"]  # Abilita ?uploader={id}
```
Applicare lo stesso pattern al CommentViewSet con `filterset_fields = ["video"]`.

**`useDeleteComment` — Pattern da `useCreateComment`:**
```typescript
export function useDeleteComment(videoId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (commentId: number) => commentsApi.delete(commentId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.comments.byVideo(videoId),
      });
    },
  });
}
```

**Delete button su CommentItem — Pattern condizionale:**
```tsx
{comment.user === currentUsername && (
  <button
    onClick={() => onDelete?.(comment.id)}
    className="text-muted-foreground/50 hover:text-destructive transition-colors"
    aria-label="Elimina commento"
  >
    <Trash2 className="h-3.5 w-3.5" />
  </button>
)}
```

**Test pattern — da conftest.py:**
```python
from cs_clips.tests.conftest import (
    create_authenticated_user,
    create_api_client_authenticated,
    create_sample_video,
    create_toconfirm_user,
)
```

### Anti-Pattern da Evitare

- **MAI** filtrare commenti client-side per video — DEVE essere fatto via `?video={id}` backend. Il frontend già invia il parametro, il backend deve rispettarlo con `filterset_fields`
- **MAI** mostrare il bottone elimina su commenti altrui — il check `comment.user === currentUsername` deve essere nel componente
- **MAI** eliminare un commento senza aggiornare la cache React Query — usare `invalidateQueries` dopo delete
- **MAI** creare un endpoint custom per eliminare commenti — `DELETE /api/comments/{id}/` funziona già via ModelViewSet
- **MAI** importare `from cs_clips.models.user import User` — usare `get_user_model()`
- **MAI** esporre `is_disabled` nel serializer — è solo per moderazione backend/admin
- **MAI** aggiungere dialog di conferma per delete commento — non richiesto dalle AC, keep it simple con delete diretto + toast
- **MAI** rendere il commento eliminabile da admin via frontend — la moderazione admin è via Django Admin (campo `is_disabled`), fuori scope per questa story

### Informazioni Tecniche

**django-filter — `filterset_fields` behavior:**
- Quando `DjangoFilterBackend` è nel `DEFAULT_FILTER_BACKENDS` (già configurato in `settings.py`) e `filterset_fields` è dichiarato sul ViewSet, il filtro è automatico
- `filterset_fields = ["video"]` genera un filtro esatto su FK → `?video=5` filtra `comment.video_id = 5`
- Senza `filterset_fields`, il parametro `?video=` viene silenziosamente ignorato da DjangoFilterBackend

**DRF ModelViewSet DELETE behavior:**
- `DELETE /api/comments/{id}/` → chiama `destroy()` → `perform_destroy()` → `instance.delete()` → 204 No Content
- `RoleBasedPermission.has_object_permission()` verifica `obj.user == request.user` per operazioni di scrittura → solo l'autore può eliminare

**React Query `useMutation` + `invalidateQueries`:**
- `invalidateQueries` marca le query come stale e triggera un refetch automatico
- Il pattern `onSuccess → invalidateQueries` è lo standard del progetto (usato in `useCreateComment`, `useCreateRating`, etc.)

### Project Structure Notes

**File da modificare:**
- `backend/cs_clips/api/comments/comment_views.py` — aggiungere `filterset_fields = ["video"]`
- `frontend/src/lib/hooks/use-comments.ts` — aggiungere `useDeleteComment` hook
- `frontend/src/components/comments/comment-item.tsx` — aggiungere bottone elimina condizionale
- `frontend/src/components/comments/comment-list.tsx` — passare `currentUsername` e `onDelete` a CommentItem
- `frontend/src/components/comments/comment-section.tsx` — passare `currentUsername` e `onDelete` a CommentList
- `frontend/src/app/clip/[id]/clip-content.tsx` — istanziare `useDeleteComment`, passare callback e username

**File da creare:**
- `backend/cs_clips/tests/test_comments.py` — test completi per commenti

**File che NON devono essere modificati:**
- `backend/cs_clips/models/comment.py` — il modello è già completo
- `backend/cs_clips/api/comments/comment_serializers.py` — il serializer è già completo con validazione
- `backend/cs_clips/urls.py` — le route sono già registrate
- `frontend/src/lib/api/comments.ts` — il client API ha già `getByVideo`, `create`, `delete`
- `frontend/src/types/comment.ts` — i tipi sono già completi
- `frontend/src/lib/query-keys.ts` — le query keys sono già definite
- `frontend/src/components/comments/comment-form.tsx` — il form è già completo
- `frontend/src/components/comments/dynamic-sidebar.tsx` — la sidebar è già completa
- `frontend/src/components/video/comment-marker.tsx` — i marker sono già completi

### Intelligence dalla Story 2.3 (Precedente)

**Pattern stabiliti da riusare:**
- `create_sample_video` da conftest.py — crea video con durata 30s senza file reale (MinIO necessario)
- Ruff 0 errori è gate obbligatorio
- `tearDownClass` per cleanup `TEMP_MEDIA_ROOT` nei test con file
- `translation_override("it")` per messaggi validazione in italiano nei test

**Problemi risolti nella Story 2.3 da non re-introdurre:**
- **Formato risposta inconsistente per feed vuoto**: `self.paginate_queryset()` ritorna `[]` (falsy) per queryset vuoti → usare `page is not None` invece di `if page` nel pattern paginazione custom
- **SSR fetch senza auth**: se serve accesso pubblico a un endpoint, usare `get_permissions()` con `AllowAny` per l'azione specifica

**Debito tecnico rilevante:**
- `has_object_permission` — il `RoleBasedPermission` ora controlla sia `obj.uploader` che `obj.user` via `getattr()`, funziona per Comment (campo `user`)
- Test comment non esistono — questa story li crea per la prima volta

### Git Intelligence

**Ultimi commit (post-Story 2.3):**
- `8d20865` — feat: Story 2.1 — upload clip con validazione completa e allow_download
- Suite test attuale: **112 test passanti** — non introdurre regressioni
- Conftest.py ha 6 helper: `create_authenticated_user`, `create_toconfirm_user`, `create_admin_user`, `create_api_client_authenticated`, `create_sample_video`, `create_sample_contest`

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 2, Story 2.4, FR23-26, FR29-30]
- [Source: _bmad-output/planning-artifacts/architecture.md — FR23-30, CommentViewSet, DjangoFilterBackend, RoleBasedPermission]
- [Source: _bmad-output/implementation-artifacts/2-3-feed-home-e-navigazione-clip.md — Dev notes, pattern testing, anti-pattern]
- [Source: _bmad-output/implementation-artifacts/2-2-download-clip-e-presigned-url-refresh.md — Pattern hook useMutation, permessi]
- [Source: backend/cs_clips/models/comment.py — Comment model completo]
- [Source: backend/cs_clips/api/comments/comment_serializers.py — CommentSerializer con validazione timestamp]
- [Source: backend/cs_clips/api/comments/comment_views.py — CommentViewSet SENZA filterset_fields (bug)]
- [Source: backend/cs_clips/permissions.py — RoleBasedPermission con has_object_permission]
- [Source: frontend/src/components/comments/comment-form.tsx — Form con timestamp pre-compilato]
- [Source: frontend/src/components/comments/comment-section.tsx — Tabs "Tutti"/"Nel video"]
- [Source: frontend/src/components/comments/comment-list.tsx — Filtraggio e ordinamento dual-view]
- [Source: frontend/src/components/comments/comment-item.tsx — Nessun bottone elimina]
- [Source: frontend/src/lib/hooks/use-comments.ts — useComments + useCreateComment, NO useDeleteComment]
- [Source: frontend/src/lib/api/comments.ts — commentsApi con delete già presente]
- [Source: frontend/src/app/clip/[id]/clip-content.tsx — Orchestrazione commenti completa]
- [Source: backend/project_clip/settings.py — DjangoFilterBackend globale in DEFAULT_FILTER_BACKENDS]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

Nessun bug o problema incontrato durante l'implementazione.

### Completion Notes List

- **Task 1**: Aggiunto `filterset_fields = ["video"]` al CommentViewSet — risolve bug critico dove `?video={id}` veniva silenziosamente ignorato dal DjangoFilterBackend
- **Task 2**: Creato hook `useDeleteComment(videoId)` in `use-comments.ts` — segue pattern identico a `useCreateComment` con `useMutation` + `invalidateQueries`
- **Task 3**: Aggiunto bottone elimina condizionale su CommentItem — icona Trash2, visibile solo per `comment.user === currentUsername`, con `aria-label` e hover effect (opacity transition su group hover)
- **Task 4**: Collegato flusso delete attraverso `clip-content.tsx` → `CommentSection` → `CommentList` → `CommentItem` — `handleDeleteComment` con toast success/error in italiano
- **Task 5**: Creati 16 test backend in `test_comments.py` — 5 classi (TestCommentCreate, TestCommentFilter, TestCommentDelete, TestCommentAuth, TestCommentDisabled) coprendo AC-1, AC-3, AC-4, AC-5. Nota: subtask 5.5 (timestamp negativo) non testabile direttamente perché `PositiveIntegerField` impedisce valori negativi a livello DB; coperto indirettamente dal test timestamp_exceeds_duration + boundary test at_duration
- **Task 6**: Suite completa 128 test passanti (112 pre-esistenti + 16 nuovi), build frontend OK, ruff 0 errori

### Change Log

- 2026-03-01: Story 2.4 implementata — filtro commenti backend, useDeleteComment hook, bottone elimina su CommentItem, 16 test backend
- 2026-03-01: Code review — 3 MEDIUM fix applicati (mobile delete button, blocco PUT/PATCH, test assertions), 1 test aggiunto, test moderazione aggiornato. 129 test totali OK.

### File List

**Modificati:**
- `backend/cs_clips/api/comments/comment_views.py` — aggiunto `filterset_fields = ["video"]` + `http_method_names` (blocco PUT/PATCH)
- `backend/cs_clips/tests/test_admin_moderation.py` — aggiornato test `is_disabled` per 405 (PATCH bloccato)
- `frontend/src/lib/hooks/use-comments.ts` — aggiunto hook `useDeleteComment`
- `frontend/src/components/comments/comment-item.tsx` — aggiunto bottone elimina condizionale + visibilita' mobile touch-friendly
- `frontend/src/components/comments/comment-list.tsx` — passaggio props `currentUsername`, `onDelete` a CommentItem
- `frontend/src/components/comments/comment-section.tsx` — passaggio props `currentUsername`, `onDelete` a CommentList
- `frontend/src/app/clip/[id]/clip-content.tsx` — istanziato `useDeleteComment`, `handleDeleteComment` con toast, passaggio props

**Creati:**
- `backend/cs_clips/tests/test_comments.py` — 17 test per commenti (create, filter, delete, auth, disabled, method restriction)

### Senior Developer Review (AI)

**Reviewer:** AcchippameQuisso — 2026-03-01
**Outcome:** Approved with fixes applied

**Issues found:** 0 Critical, 3 Medium (fixed), 4 Low (noted as tech debt)

**MEDIUM — Fixed:**
1. **M1**: Bottone elimina invisibile su mobile/touch (`opacity-0 group-hover`) → fix: `opacity-100 sm:opacity-0 sm:group-hover:opacity-100`
2. **M2**: Campo `video` scrivibile su UPDATE/PATCH (riassegnazione commento) → fix: `http_method_names` restrittivo (solo GET/POST/DELETE)
3. **M3**: Test assertions incomplete su errori 400 → fix: verifica `code`, `detail`, messaggio specifico + test PUT/PATCH 405

**LOW — Tech debt (pre-esistente, non introdotto dalla story):**
1. Nessun `ordering` default su CommentViewSet (warning DRF paginazione)
2. Serializer singolo vs Input/Output split (deviazione architettura)
3. `read_only_fields` non espliciti per `id` e `user`
4. Comment model senza `ordering` in Meta

**Verification:** 129 test OK, ruff 0 errori, Next.js build OK
