# Story 2.5: Delete Video e Operazioni CRUD Mancanti

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utente registrato,
I want eliminare le mie clip e modificare i miei voti,
so that ho pieno controllo sui miei contenuti e interazioni.

## Acceptance Criteria (BDD)

### AC-1: Eliminazione video proprio (FR46, useDeleteVideo)

```gherkin
Scenario: Utente proprietario elimina il proprio video
  Given un utente autenticato proprietario di un video
  When clicca il bottone "Elimina" sulla pagina dettaglio clip
  Then appare un dialog di conferma "Sei sicuro di voler eliminare questa clip?"
  And confermando, il video viene rimosso via DELETE /api/videos/{id}/
  And il file su MinIO viene rimosso automaticamente (django-cleanup)
  And tutti i commenti e rating associati vengono eliminati a cascata
  And l'utente viene reindirizzato al proprio profilo
  And un toast conferma "Clip eliminata"

Scenario: Eliminazione aggiorna la lista video nel profilo
  Given un utente che ha appena eliminato un proprio video
  When la navigazione va al profilo
  Then la cache React Query per i video dell'utente viene invalidata
  And la lista video nel profilo non contiene più il video eliminato

Scenario: Bottone elimina visibile solo per il proprietario
  Given la pagina dettaglio di un video
  When un utente autenticato visualizza un video di un ALTRO utente
  Then il bottone "Elimina" NON è visibile
  And solo DownloadButton e StarRating sono disponibili
```

### AC-2: Tentativo eliminazione video altrui — 403 (RoleBasedPermission)

```gherkin
Scenario: Non-proprietario tenta di eliminare un video
  Given un utente autenticato che NON è il proprietario del video
  When chiama DELETE /api/videos/{id}/
  Then riceve status 403 (Forbidden)
  And il video resta intatto

Scenario: Utente toconfirm non può eliminare video
  Given un utente con gruppo "toconfirm"
  When chiama DELETE /api/videos/{id}/
  Then riceve status 403 (Forbidden)

Scenario: Utente non autenticato non può eliminare video
  Given un utente non autenticato
  When chiama DELETE /api/videos/{id}/
  Then riceve status 401 (Unauthorized)
```

### AC-3: Modifica voto (rating) esistente (useUpdateRating, PATCH)

```gherkin
Scenario: Utente modifica il proprio voto su una clip
  Given un utente autenticato che ha già votato una clip con valore 3
  When clicca su una stella diversa (es. 5)
  Then il rating viene aggiornato via PATCH /api/ratings/{id}/ con { value: 5 }
  And le stelle riflettono il nuovo valore
  And il toast conferma "Voto aggiornato!"
  And la media rating (average_rating) del video viene ricalcolata

Scenario: Primo voto usa POST, voti successivi usano PATCH
  Given un utente autenticato che NON ha ancora votato una clip
  When clicca su una stella
  Then il rating viene creato via POST /api/ratings/ (useCreateRating, già implementato)
  And il toast conferma "Voto registrato!"

Scenario: Pre-compilazione stelle con voto proprio
  Given un utente autenticato che ha già votato una clip con valore 4
  When carica la pagina dettaglio clip
  Then le stelle mostrano il valore 4 pre-compilato (dal campo my_rating_value)
  And il colore delle stelle indica che è il voto dell'utente
```

### AC-4: Annotazione backend my_rating per il voto dell'utente corrente

```gherkin
Scenario: VideoOutputSerializer include my_rating per utente autenticato
  Given un utente autenticato che ha votato un video con valore 4
  When chiama GET /api/videos/{id}/
  Then la risposta include my_rating_id (intero) e my_rating_value (4)

Scenario: my_rating null per utente che non ha votato
  Given un utente autenticato che NON ha votato un video
  When chiama GET /api/videos/{id}/
  Then my_rating_id è null e my_rating_value è null

Scenario: my_rating null per utente non autenticato
  Given un utente non autenticato
  When chiama GET /api/videos/{id}/ (retrieve è pubblico per SSR)
  Then my_rating_id è null e my_rating_value è null
```

### AC-5: Restrizione metodi HTTP su RatingViewSet (sicurezza)

```gherkin
Scenario: PATCH su rating aggiorna solo value
  Given un utente autenticato proprietario di un rating
  When chiama PATCH /api/ratings/{id}/ con { value: 5 }
  Then il rating viene aggiornato con valore 5
  And il campo video NON può essere cambiato

Scenario: PUT su rating non è permesso
  Given un utente autenticato
  When chiama PUT /api/ratings/{id}/
  Then riceve status 405 Method Not Allowed

Scenario: DELETE su rating non è permesso (fuori scope)
  Given un utente autenticato
  When chiama DELETE /api/ratings/{id}/
  Then riceve status 405 Method Not Allowed
```

### AC-6: Non-regressione e integrazione

```gherkin
Scenario: Suite test completa senza regressioni
  Given le modifiche apportate per delete video e update rating
  When viene eseguita la suite test backend completa
  Then tutti i test esistenti (129+) passano senza regressioni

Scenario: Frontend compila senza errori
  Given le modifiche frontend per useDeleteVideo, useUpdateRating e delete button
  When viene eseguito npm run build
  Then la build completa senza errori TypeScript o warning bloccanti
```

## Tasks / Subtasks

- [x] **Task 1: Aggiungere annotazione `my_rating` al VideoViewSet/Serializer** (AC: #4)
  - [x] 1.1 In `backend/cs_clips/api/videos/video_views.py`, nel metodo `get_queryset()`, aggiungere annotazione condizionale: se `self.request.user.is_authenticated`, annotare `my_rating_id` e `my_rating_value` tramite `Subquery` su Rating filtrato per `video=OuterRef('pk'), user=self.request.user`; altrimenti usare `Value(None)` per entrambi
  - [x] 1.2 In `backend/cs_clips/api/videos/video_serializers.py`, aggiungere al `VideoOutputSerializer` i campi `my_rating_id = serializers.IntegerField(read_only=True, allow_null=True, default=None)` e `my_rating_value = serializers.IntegerField(read_only=True, allow_null=True, default=None)` + aggiungerli a `read_only_fields`
  - [x] 1.3 Refactorare l'action `top_rated()` in `video_views.py` affinché usi `self.get_queryset()` come base (come fa `videos_from_following()`) invece di `Video.objects.all()` — altrimenti le annotazioni `my_rating_id`/`my_rating_value` saranno assenti nelle risposte di `/api/videos/top-rated/`, causando `undefined` nel frontend
  - [x] 1.4 In `frontend/src/types/video.ts`, aggiungere `my_rating_id: number | null` e `my_rating_value: number | null` all'interfaccia `Video`

- [x] **Task 2: Restrizione metodi HTTP su VideoViewSet e RatingViewSet** (AC: #2, #5)
  - [x] 2.1 In `backend/cs_clips/api/videos/video_views.py`, aggiungere `http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]` — esplicita i metodi permessi (stessa lezione M2 di Story 2.4). NOTA: `VideoUpdateSerializer` già limita i campi scrivibili (`title`, `tag`, `allow_download`), quindi `uploader` FK non è riassegnabile via PATCH/PUT. L'esplicitazione serve come guardrail documentativo e previene future regressioni se il serializer cambia
  - [x] 2.2 In `backend/cs_clips/api/ratings/rating_views.py`, aggiungere `http_method_names = ["get", "post", "patch", "head", "options"]` — blocca PUT e DELETE
  - [x] 2.3 In `backend/cs_clips/api/ratings/rating_serializers.py`, aggiungere `RatingUpdateSerializer` con `fields = ("value",)` — impedisce riassegnazione `video` FK su PATCH
  - [x] 2.4 Aggiungere `get_serializer_class()` al RatingViewSet: `partial_update` → `RatingUpdateSerializer`, default → `RatingSerializer`
  - [x] 2.5 Correggere `read_only_fields` in `RatingSerializer`: rimuovere `"timestamp"` (campo inesistente, bug), sostituire con `("id", "user", "created_at", "updated_at")`

- [x] **Task 3: Creare hook `useDeleteVideo` nel frontend** (AC: #1)
  - [x] 3.1 In `frontend/src/lib/hooks/use-videos.ts`, aggiungere hook `useDeleteVideo()` come `useMutation` che chiama `videosApi.delete(videoId)`
  - [x] 3.2 In `onSuccess`, invalidare `queryKeys.videos.all` (invalida tutte le query video: profilo, feed, top-rated)
  - [x] 3.3 Ritornare la mutation per uso con toast e redirect nel componente chiamante

- [x] **Task 4: Creare hook `useUpdateRating` nel frontend** (AC: #3)
  - [x] 4.1 In `frontend/src/lib/hooks/use-ratings.ts`, aggiungere hook `useUpdateRating(videoId: number)` come `useMutation` che chiama `ratingsApi.update(ratingId, value)`
  - [x] 4.2 In `onSuccess`, invalidare `queryKeys.videos.detail(videoId)` per ricalcolare `average_rating` e `my_rating_value`

- [x] **Task 5: Aggiungere bottone elimina e logica rating smart in clip-content** (AC: #1, #3)
  - [x] 5.0 Verificare che shadcn `AlertDialog` sia installato: `ls frontend/src/components/ui/alert-dialog.tsx`. Se manca → `cd frontend && npx shadcn@latest add alert-dialog`
  - [x] 5.1 In `frontend/src/app/clip/[id]/clip-content.tsx`, importare `useDeleteVideo` e `useUpdateRating`, `useRouter` da `next/navigation`
  - [x] 5.2 Aggiungere bottone elimina (icona `Trash2`) visibile SOLO se `user?.username === video.uploader` — posizionato accanto a `DownloadButton` nella riga stats
  - [x] 5.3 Al click del bottone elimina: mostrare dialog di conferma (shadcn `AlertDialog`) con "Sei sicuro di voler eliminare questa clip? L'azione è irreversibile." → confermando, chiamare `deleteVideo.mutate(video.id)` con toast success ("Clip eliminata") → redirect a `/profilo/${user.username}` via `router.replace()` (NON `router.push()` — evita che il tasto "Back" riporti a una pagina 404 del video eliminato)
  - [x] 5.4 Modificare `handleRate`: se `video.my_rating_id` esiste → usare `updateRating.mutate({ ratingId: video.my_rating_id, value })` con toast "Voto aggiornato!"; altrimenti → usare `createRating` (logica attuale) con toast "Voto registrato!"
  - [x] 5.5 Pre-compilare `StarRating`: se `video.my_rating_value` esiste → passare come `value` (voto personale, stelle piene interattive); se null → passare 0 (stelle vuote) per consentire il primo voto. Media mostrata nel testo sottostante. NOTA: non conflazionare voto personale e media — sono semanticamente diversi

- [x] **Task 6: Scrivere test backend** (AC: #1, #2, #4, #5, #6)
  - [x] 6.1 Creare `backend/cs_clips/tests/test_delete_video.py` con classi:
    - `TestVideoDeleteOwner` — proprietario elimina il proprio video → 204, video non esiste più in DB
    - `TestVideoDeleteCascade` — commenti e rating associati vengono eliminati a cascata
    - `TestVideoDeleteNonOwner` — non-proprietario → 403
    - `TestVideoDeleteToconfirm` — utente toconfirm → 403
    - `TestVideoDeleteUnauthenticated` — non autenticato → 401
  - [x] 6.2 Creare `backend/cs_clips/tests/test_rating_update.py` con classi:
    - `TestRatingPatch` — PATCH value → 200, valore aggiornato
    - `TestRatingPatchNonOwner` — PATCH rating altrui → 403
    - `TestRatingMethodRestriction` — PUT → 405, DELETE → 405
    - `TestMyRatingAnnotation` — GET video include my_rating_id e my_rating_value corretti (autenticato, non votato, non autenticato)
  - [x] 6.3 Usare helper da conftest.py (`create_authenticated_user`, `create_api_client_authenticated`, `create_sample_video`, `create_toconfirm_user`)
  - [x] 6.4 Eseguire `ruff check backend/` e `ruff format backend/` — zero errori

- [x] **Task 7: Verificare integrazione e non-regressione** (AC: #6)
  - [x] 7.1 Eseguire la suite test completa backend — zero regressioni (129 precedenti + 21 nuovi = 150 totali)
  - [x] 7.2 Verificare `npm run build` frontend — zero errori
  - [x] 7.3 Ruff check + format: zero errori

## Dev Notes

### Contesto Critico

Questa è la **quinta e ultima story di Epic 2**. Chiude il ciclo CRUD per video e rating, aggiungendo le operazioni mancanti (delete video, update rating) con i relativi hook frontend.

**Il backend è quasi tutto pronto** — `ModelViewSet.destroy()` e `partial_update()` sono ereditati e funzionanti. Il lavoro principale è:
1. **Annotazione `my_rating`** — per sapere se l'utente ha già votato e con quale valore/ID
2. **Restrizione metodi HTTP** su RatingViewSet (pattern M2 da Story 2.4)
3. **Hook frontend** `useDeleteVideo` e `useUpdateRating`
4. **UI**: bottone elimina con dialog conferma, logica rating smart (create vs update)
5. **Test backend** per delete video e rating update

### Stato Attuale del Codice — Cosa GIÀ Esiste

**Backend (già implementato e funzionante):**

- **Video model** (`backend/cs_clips/models/video.py`): campi `id`, `title`, `file`, `uploader` (FK User, CASCADE), `created_at`, `updated_at`, `contest` (FK Contest, SET_NULL), `views`, `tag`, `duration`, `allow_download`, `thumbnail`
- **VideoViewSet** (`backend/cs_clips/api/videos/video_views.py`): `ModelViewSet` completo con CRUD. `destroy()` ereditato e funzionante (DELETE → 204). Nessun `http_method_names` esplicito (da aggiungere). Permessi: `[IsAuthenticated, RoleBasedPermission]` con `retrieve` pubblico (AllowAny per SSR). **ATTENZIONE**: l'action `top_rated()` (riga 238) crea il proprio queryset da `Video.objects.all()` senza passare per `get_queryset()` — va refactorato per ereditare le annotazioni `my_rating`
- **VideoOutputSerializer** (`backend/cs_clips/api/videos/video_serializers.py`): serializza `id, title, file_url, uploader, average_rating, views, tag, duration, thumbnail_url, allow_download, contest, created_at, updated_at`. Il campo `average_rating` usa l'annotazione `avg_rating` da `get_queryset()`. **Mancano** `my_rating_id` e `my_rating_value`
- **Rating model** (`backend/cs_clips/models/rating.py`): campi `id`, `user` (FK User, CASCADE), `video` (FK Video, CASCADE), `value` (1-5, validators), `created_at`, `updated_at`. Vincolo `unique_together = ('user', 'video')`
- **RatingViewSet** (`backend/cs_clips/api/ratings/rating_views.py`): `ModelViewSet` con tutti i metodi (incluso `partial_update` PATCH). Nessun `http_method_names` → permette PUT e DELETE (da restringere)
- **RatingSerializer** (`backend/cs_clips/api/ratings/rating_serializers.py`): `fields = ("id", "user", "video", "value", "created_at", "updated_at")`, `read_only_fields = ("timestamp", "created_at", "updated_at")` — **BUG: "timestamp" non esiste nel model, va rimosso**. `video` è scrivibile → **rischio riassegnazione su PATCH** (M2 pattern)
- **RoleBasedPermission** (`backend/cs_clips/permissions.py`): `has_object_permission` controlla `getattr(obj, "uploader", None) or getattr(obj, "user", None) == request.user` — funziona per Video (campo `uploader`) e Rating (campo `user`)
- **django-cleanup**: configurato in `INSTALLED_APPS` → rimuove automaticamente il file MinIO quando il Video model viene eliminato (signal `post_delete`)
- **Cascade**: `Video.uploader` è `CASCADE` → eliminando un Video, Django elimina automaticamente tutti i Comment e Rating associati (FK con CASCADE)

**Frontend (già implementato e funzionante):**

- **videosApi** (`frontend/src/lib/api/videos.ts`): metodo `delete(id)` **ESISTE** → `apiClient.delete(\`/videos/${id}/\`)` — manca solo l'hook wrapper
- **ratingsApi** (`frontend/src/lib/api/ratings.ts`): metodo `update(id, value)` **ESISTE** → `apiClient.patch(\`/ratings/${id}/\`, { value })` — manca solo l'hook wrapper
- **useCreateRating** (`frontend/src/lib/hooks/use-ratings.ts`): hook mutation per POST, invalida `queryKeys.videos.detail(videoId)` on success
- **StarRating** (`frontend/src/components/rating/star-rating.tsx`): componente con `value`, `onChange`, `readonly`, `size` — supporta hover, click, e pre-filling
- **ClipContent** (`frontend/src/app/clip/[id]/clip-content.tsx`): orchestrazione completa. `handleRate` attualmente usa **solo** `createRating` (POST) → se l'utente ha già votato, il POST fallisce con 409 (IntegrityError) e l'utente vede "Errore nel salvataggio del voto". Questo è il **bug da risolvere**
- **FeedGrid + ClipCard** per la lista video profilo — attualmente nessun bottone elimina su card
- **DownloadButton** (`frontend/src/components/video/download-button.tsx`): bottone condizionale già posizionato nella riga stats di clip-content
- **Video type** (`frontend/src/types/video.ts`): interfaccia con 14 campi — **mancano** `my_rating_id` e `my_rating_value`
- **Query keys**: `queryKeys.videos.all`, `queryKeys.videos.detail(id)`, `queryKeys.videos.byUser(userId)`, `queryKeys.ratings.byVideo(videoId)`
- **shadcn AlertDialog**: componente dialog disponibile (verificare se installato, altrimenti `npx shadcn@latest add alert-dialog`)

### Pattern da Seguire

**Annotazione `my_rating` — Pattern Subquery (come `avg_rating`):**
```python
from django.db.models import Subquery, OuterRef, Value, IntegerField

def get_queryset(self):
    qs = Video.objects.annotate(avg_rating=Avg("ratings__value")).order_by("-created_at")
    if self.request.user.is_authenticated:
        my_rating_qs = Rating.objects.filter(
            video=OuterRef('pk'), user=self.request.user
        )
        qs = qs.annotate(
            my_rating_id=Subquery(my_rating_qs.values('id')[:1]),
            my_rating_value=Subquery(my_rating_qs.values('value')[:1]),
        )
    else:
        qs = qs.annotate(
            my_rating_id=Value(None, output_field=IntegerField()),
            my_rating_value=Value(None, output_field=IntegerField()),
        )
    return qs
```

**`http_method_names` restrittivo — Pattern da CommentViewSet (Story 2.4 M2 fix):**
```python
class RatingViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "head", "options"]
    # Blocca PUT (sovrascrittura totale) e DELETE (no cancellazione voto)
```

**`RatingUpdateSerializer` — Pattern da VideoUpdateSerializer:**
```python
class RatingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ("value",)
```

**`useDeleteVideo` — Pattern da `useDeleteComment` (Story 2.4):**
```typescript
export function useDeleteVideo() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (videoId: number) => videosApi.delete(videoId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.videos.all });
    },
  });
}
```

**`useUpdateRating` — Pattern da `useCreateRating`:**
```typescript
export function useUpdateRating(videoId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ ratingId, value }: { ratingId: number; value: number }) =>
      ratingsApi.update(ratingId, value),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.videos.detail(videoId),
      });
    },
  });
}
```

**Delete button condizionale con AlertDialog:**
```tsx
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { Trash2 } from "lucide-react";

{user?.username === video.uploader && (
  <AlertDialog>
    <AlertDialogTrigger asChild>
      <button className="text-muted-foreground/50 hover:text-destructive transition-colors" aria-label="Elimina clip">
        <Trash2 className="h-3.5 w-3.5" />
      </button>
    </AlertDialogTrigger>
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>Eliminare questa clip?</AlertDialogTitle>
        <AlertDialogDescription>L'azione è irreversibile. La clip, i commenti e i voti associati verranno eliminati permanentemente.</AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel>Annulla</AlertDialogCancel>
        <AlertDialogAction onClick={handleDeleteVideo} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">Elimina</AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
)}
```

**Smart rating handler (create vs update):**
```typescript
const handleRate = useCallback(
  (value: number) => {
    if (video.my_rating_id) {
      updateRating.mutate(
        { ratingId: video.my_rating_id, value },
        {
          onSuccess: () => toast.success("Voto aggiornato!"),
          onError: () => toast.error("Errore nell'aggiornamento del voto."),
        }
      );
    } else {
      createRating(
        { video: videoId, value },
        {
          onSuccess: () => toast.success("Voto registrato!"),
          onError: () => toast.error("Errore nel salvataggio del voto."),
        }
      );
    }
  },
  [video.my_rating_id, createRating, updateRating, videoId]
);
```

### Anti-Pattern da Evitare

- **MAI** eliminare un video senza dialog di conferma — l'azione è irreversibile, django-cleanup elimina il file da MinIO immediatamente
- **MAI** mostrare il bottone elimina su video di altri utenti — check `user?.username === video.uploader` obbligatorio
- **MAI** fare redirect prima che la mutation completi — usare `onSuccess` per il redirect dopo eliminazione
- **MAI** permettere PUT su RatingViewSet — consentirebbe sovrascrittura completa dell'oggetto inclusa la FK `video`
- **MAI** permettere DELETE su RatingViewSet — fuori scope, un voto dato resta. Solo il valore è modificabile
- **MAI** usare `SerializerMethodField` per `my_rating` — causa N+1 queries. Usare `Subquery` annotazione in `get_queryset()`
- **MAI** importare `from cs_clips.models.user import User` — usare `get_user_model()` o import da `cs_clips.models`
- **MAI** tentare POST se l'utente ha già votato — controllare `video.my_rating_id` e usare PATCH
- **MAI** invalidare solo `queryKeys.videos.detail` dopo delete video — invalidare `queryKeys.videos.all` per pulire tutte le cache (feed, profilo, top-rated)
- **MAI** pre-compilare StarRating con `average_rating` quando `my_rating_value` esiste — mostrare `my_rating_value` (voto personale) come valore precompilato
- **MAI** creare queryset custom in action senza passare per `get_queryset()` — tutte le annotazioni (avg_rating, my_rating) devono essere ereditate. L'action `top_rated()` va refactorata per usare `self.get_queryset()` come base
- **MAI** usare `router.push()` dopo eliminazione di una risorsa — usare `router.replace()` per evitare che "Back" riporti a una pagina 404

### Informazioni Tecniche

**DRF ModelViewSet.destroy() — Comportamento standard:**
- `DELETE /api/videos/{id}/` → chiama `destroy()` → `perform_destroy()` → `instance.delete()` → 204 No Content
- `RoleBasedPermission.has_object_permission()` verifica `obj.uploader == request.user`
- Django cascade: tutti i `Comment` e `Rating` con FK verso il Video vengono eliminati automaticamente
- django-cleanup (signal `post_delete`): rimuove il file fisico da MinIO storage

**Subquery annotation pattern:**
- `Subquery(qs.values('field')[:1])` ritorna il valore del primo match o `None`
- Nessun N+1: tutto in una singola query SQL con subselect
- Per utenti non autenticati: `Value(None, output_field=IntegerField())` ritorna colonna costante NULL

**RatingSerializer bug `read_only_fields = ("timestamp", ...)`:**
- Il campo `"timestamp"` non esiste nel model `Rating` — è probabilmente un errore di copia dal model Comment
- DRF ignora silenziosamente campi in `read_only_fields` non presenti in `fields` — nessun crash, ma da correggere per chiarezza
- Correggere con: `read_only_fields = ("id", "user", "created_at", "updated_at")`

**shadcn AlertDialog:**
- Verificare se installato: `ls frontend/src/components/ui/alert-dialog.tsx`
- Se manca: `cd frontend && npx shadcn@latest add alert-dialog`

### Project Structure Notes

**File da modificare:**
- `backend/cs_clips/api/videos/video_views.py` — aggiungere annotazione `my_rating_id`, `my_rating_value` in `get_queryset()`, refactorare `top_rated()` per usare `get_queryset()`, aggiungere `http_method_names` esplicito
- `backend/cs_clips/api/videos/video_serializers.py` — aggiungere campi `my_rating_id`, `my_rating_value` al `VideoOutputSerializer`
- `backend/cs_clips/api/ratings/rating_views.py` — aggiungere `http_method_names`, `get_serializer_class()`
- `backend/cs_clips/api/ratings/rating_serializers.py` — fix `read_only_fields`, aggiungere `RatingUpdateSerializer`
- `frontend/src/types/video.ts` — aggiungere `my_rating_id`, `my_rating_value`
- `frontend/src/lib/hooks/use-videos.ts` — aggiungere `useDeleteVideo` hook
- `frontend/src/lib/hooks/use-ratings.ts` — aggiungere `useUpdateRating` hook
- `frontend/src/app/clip/[id]/clip-content.tsx` — aggiungere bottone elimina, logica rating smart

**File da creare:**
- `backend/cs_clips/tests/test_delete_video.py` — test eliminazione video
- `backend/cs_clips/tests/test_rating_update.py` — test aggiornamento rating

**File che NON devono essere modificati:**
- `backend/cs_clips/models/video.py` — il modello è già completo
- `backend/cs_clips/models/rating.py` — il modello è già completo
- `backend/cs_clips/permissions.py` — `RoleBasedPermission` già gestisce video (campo `uploader`) e rating (campo `user`)
- `backend/cs_clips/urls.py` — le route sono già registrate
- `frontend/src/lib/api/videos.ts` — `videosApi.delete(id)` già esiste
- `frontend/src/lib/api/ratings.ts` — `ratingsApi.update(id, value)` già esiste
- `frontend/src/lib/query-keys.ts` — le query keys sono già definite
- `frontend/src/components/rating/star-rating.tsx` — il componente è già completo (supporta `value` e `onChange`)
- `frontend/src/components/video/download-button.tsx` — nessuna modifica necessaria
- `frontend/src/app/(main)/profilo/[username]/page.tsx` — la cache viene invalidata automaticamente via `queryKeys.videos.all`

### Intelligence dalla Story 2.4 (Precedente)

**Pattern stabiliti da riusare:**
- `create_sample_video` da conftest.py — crea video con durata 30s senza file reale
- `http_method_names` restrittivo per bloccare metodi non necessari (M2 fix)
- Toast in italiano per success/error
- `ruff check + format` zero errori come gate obbligatorio
- `translation_override("it")` per messaggi validazione in italiano nei test

**Problemi risolti nella Story 2.4 da non re-introdurre:**
- **M2**: Campo FK (`video`) scrivibile su PATCH → usare serializer separato per update che espone solo `value`
- **M3**: Test assertions incomplete su errori → verificare `code`, `detail`, messaggio specifico
- **Formato risposta paginato**: `page is not None` (non `if page`) per gestire pagine vuote

**Debito tecnico rilevante (pre-esistente, non da risolvere in questa story):**
- Nessun `ordering` default su CommentViewSet e RatingViewSet
- Serializer singolo vs Input/Output split su Comment
- CI mai testata end-to-end

### Git Intelligence

**Ultimi commit (post-Story 2.4):**
- `8d20865` — feat: Story 2.1 — upload clip con validazione completa e allow_download
- Suite test attuale: **129 test passanti** — non introdurre regressioni
- Conftest.py ha 6 helper: `create_authenticated_user`, `create_toconfirm_user`, `create_admin_user`, `create_api_client_authenticated`, `create_sample_video`, `create_sample_contest`

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 2, Story 2.5, FR46]
- [Source: _bmad-output/planning-artifacts/architecture.md — RoleBasedPermission, django-cleanup, Subquery annotation]
- [Source: _bmad-output/implementation-artifacts/2-4-commenti-dual-layer-con-timestamp.md — M2 http_method_names fix, test pattern, anti-pattern]
- [Source: backend/cs_clips/api/videos/video_views.py — VideoViewSet destroy() ereditato, get_queryset() con annotazione avg_rating]
- [Source: backend/cs_clips/api/videos/video_serializers.py — VideoOutputSerializer senza my_rating]
- [Source: backend/cs_clips/api/ratings/rating_views.py — RatingViewSet senza http_method_names]
- [Source: backend/cs_clips/api/ratings/rating_serializers.py — RatingSerializer con bug timestamp]
- [Source: backend/cs_clips/permissions.py — RoleBasedPermission con getattr uploader/user]
- [Source: frontend/src/lib/api/videos.ts — videosApi.delete(id) già presente]
- [Source: frontend/src/lib/api/ratings.ts — ratingsApi.update(id, value) già presente]
- [Source: frontend/src/lib/hooks/use-videos.ts — manca useDeleteVideo]
- [Source: frontend/src/lib/hooks/use-ratings.ts — manca useUpdateRating, solo useCreateRating]
- [Source: frontend/src/app/clip/[id]/clip-content.tsx — handleRate usa solo createRating (bug per utenti che hanno già votato)]
- [Source: frontend/src/types/video.ts — Video interface senza my_rating_id/my_rating_value]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Fix campo `text` → `content` nel test cascade (Comment model usa `content`)
- Fix test `test_response_shape_all_frontend_fields` che non includeva i nuovi campi `my_rating_id`/`my_rating_value`
- Task 5.5: non usato `readonly` su StarRating (avrebbe bloccato il primo voto), mostrato `my_rating_value ?? 0` con media nel testo sottostante

### Completion Notes List

- **Task 1**: Annotazione `my_rating_id`/`my_rating_value` via `Subquery` in `get_queryset()`, campi aggiunti a `VideoOutputSerializer` e tipo TypeScript `Video`. Action `top_rated()` refactorata per usare `self.get_queryset()` (eredita tutte le annotazioni).
- **Task 2**: `http_method_names` esplicito su VideoViewSet (tutti i metodi) e RatingViewSet (blocca PUT/DELETE). `RatingUpdateSerializer` con solo `value`. Fix bug `read_only_fields` con campo `"timestamp"` inesistente.
- **Task 3**: Hook `useDeleteVideo` con invalidazione `queryKeys.videos.all`.
- **Task 4**: Hook `useUpdateRating(videoId)` con invalidazione `queryKeys.videos.detail(videoId)`.
- **Task 5**: Bottone elimina con `AlertDialog` (visibile solo al proprietario), `handleRate` smart (create vs update in base a `my_rating_id`), pre-compilazione StarRating con voto personale, testo info sotto le stelle (voto personale + media).
- **Task 6**: 21 nuovi test: 10 per delete video (owner/cascade/non-owner/toconfirm/unauth), 11 per rating update (PATCH/non-owner/method restriction/my_rating annotation su retrieve/list/top-rated).
- **Task 7**: 150 test backend passati (0 regressioni), build frontend OK, ruff zero errori.
- **Code Review (AI)**: 7 findings (1H, 4M, 2L). 5 fix applicati: (1) bug paginazione `top_rated()` — `page or queryset` → `page if page is not None`; (2) disabled state su delete button durante mutation; (3) guard double-click su StarRating con `isPending`; (4) 4 test per validazione valore rating fuori range; (5) 1 test per PATCH rating non autenticato → 401. Suite post-review: 155 test (0 regressioni), build OK, ruff OK.

### File List

**Modificati:**
- `backend/cs_clips/api/videos/video_views.py` — annotazione my_rating, refactor top_rated(), http_method_names
- `backend/cs_clips/api/videos/video_serializers.py` — campi my_rating_id, my_rating_value in VideoOutputSerializer
- `backend/cs_clips/api/ratings/rating_views.py` — http_method_names, get_serializer_class()
- `backend/cs_clips/api/ratings/rating_serializers.py` — fix read_only_fields, RatingUpdateSerializer
- `backend/cs_clips/tests/test_upload_validation.py` — aggiornato expected_fields con my_rating_id/my_rating_value
- `frontend/src/types/video.ts` — my_rating_id, my_rating_value nell'interfaccia Video
- `frontend/src/lib/hooks/use-videos.ts` — hook useDeleteVideo
- `frontend/src/lib/hooks/use-ratings.ts` — hook useUpdateRating
- `frontend/src/app/clip/[id]/clip-content.tsx` — bottone elimina, handleRate smart, StarRating pre-compilazione

**Creati:**
- `backend/cs_clips/tests/test_delete_video.py` — 10 test eliminazione video
- `backend/cs_clips/tests/test_rating_update.py` — 11 test rating update e annotazione
- `frontend/src/components/ui/alert-dialog.tsx` — componente shadcn AlertDialog (installato via npx)

## Change Log

- **2026-03-01**: Story 2.5 implementata — delete video con dialog conferma, update rating via PATCH, annotazione my_rating (Subquery), restrizione metodi HTTP su RatingViewSet, fix bug RatingSerializer read_only_fields, 21 nuovi test backend, build frontend OK
- **2026-03-01**: Code review (AI) — 5 fix applicati: bug paginazione top_rated(), disabled state delete button, guard double-click StarRating, 5 nuovi test (validazione rating + unauth PATCH). Suite: 155 test, 0 regressioni. Status → done
