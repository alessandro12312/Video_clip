# Story 1.5: Follow e Unfollow

Status: done

## Story

As a utente registrato,
I want seguire e smettere di seguire altri utenti,
so that possa costruire il mio feed personalizzato con le clip che mi interessano.

## Acceptance Criteria

1. **AC1 — Follow con feedback visivo immediato**
   Given: un utente autenticato che visualizza il profilo di un altro utente
   When: clicca il bottone "Segui"
   Then: inizia a seguire l'utente con feedback visivo immediato (optimistic UI)
   And: il conteggio follower/following si aggiorna

2. **AC2 — Unfollow con feedback visivo immediato**
   Given: un utente che già segue un altro utente
   When: clicca il bottone "Smetti di seguire"
   Then: smette di seguire l'utente con feedback visivo immediato
   And: il conteggio si aggiorna

3. **AC3 — Rollback su errore con toast**
   Given: un errore durante l'operazione di follow/unfollow
   When: la chiamata API fallisce
   Then: l'UI fa rollback allo stato precedente e mostra un toast di errore

## Tasks / Subtasks

> **NOTA:** La funzionalità follow/unfollow è parzialmente implementata.
> Il backend ha gli endpoint `follow`/`unfollow` funzionanti e il frontend ha un `FollowButton` con hooks base.
> I gap principali sono: nessun test backend, nessuna optimistic UI con rollback, nessun toast di errore, testo bottone errato ("Segui già" invece di "Smetti di seguire"), cache invalidation troppo ampia, risposta API senza stato aggiornato.

### Codice esistente (già implementato)

- [x] Backend: `User.following` ManyToManyField (symmetrical=False, related_name='followers') in `backend/cs_clips/models.py`
- [x] Backend: `follow()` action in `UserViewSet` — `POST /api/users/{id}/follow/` con check self-follow in `backend/cs_clips/views.py`
- [x] Backend: `unfollow()` action in `UserViewSet` — `POST /api/users/{id}/unfollow/` in `backend/cs_clips/views.py`
- [x] Backend: `get_followers()` e `get_following()` actions — `GET /api/users/{id}/followers/`, `GET /api/users/{id}/following/`
- [x] Backend: `is_followed_by_me` SerializerMethodField in `UserSerializer` (aggiunto in Story 1-4)
- [x] Backend: `followers_count`, `following_count` SerializerMethodField + Count annotations nel queryset (Story 1-4)
- [x] Backend: `OnlyUsersPermission` su azioni follow/unfollow (utenti `toconfirm` bloccati)
- [x] Frontend: `FollowButton` componente in `frontend/src/components/user/follow-button.tsx`
- [x] Frontend: `useFollow()`, `useUnfollow()` hooks con `useMutation` in `frontend/src/lib/hooks/use-users.ts`
- [x] Frontend: `usersApi.follow(id)`, `usersApi.unfollow(id)` in `frontend/src/lib/api/users.ts`
- [x] Frontend: `ProfileHeader` integra `FollowButton` con `is_followed_by_me` in `frontend/src/components/user/profile-header.tsx`
- [x] Frontend: Tipo `User` con `is_followed_by_me: boolean` in `frontend/src/types/user.ts`

### Gap identificati (lavoro da completare)

- [x] Task 1: Backend — Migliorare risposta endpoint follow/unfollow (AC: #1, #2, #3)
  - [x] 1.1 — Modificare `follow()` action in `views.py`: restituire `{"detail": "...", "is_followed": true, "followers_count": <count>}` invece del solo `{"detail": "..."}`
  - [x] 1.2 — Modificare `unfollow()` action in `views.py`: restituire `{"detail": "...", "is_followed": false, "followers_count": <count>}` invece del solo `{"detail": "..."}`
  - [x] 1.3 — Gestire idempotenza su `follow()`: se l'utente segue già il target, restituire `200` con lo stato attuale (non creare relazione duplicata — M2M `.add()` è già idempotente, ma il messaggio deve riflettere lo stato reale)
  - [x] 1.4 — Gestire idempotenza su `unfollow()`: se l'utente NON segue il target, restituire `200` con lo stato attuale
  - [x] 1.5 — Verificare che `handle_exception_with_serializer()` copra l'errore su self-follow (400 con formato `{code, detail}`)

- [x] Task 2: Backend — Test completi follow/unfollow (AC: #1, #2, #3)
  - [x] 2.1 — Test POST `/api/users/{id}/follow/` con successo → 200, `is_followed: true`, `followers_count` incrementato
  - [x] 2.2 — Test POST `/api/users/{id}/unfollow/` con successo → 200, `is_followed: false`, `followers_count` decrementato
  - [x] 2.3 — Test self-follow → 400 con messaggio errore italiano
  - [x] 2.4 — Test double-follow (già segui) → 200 idempotente, nessun errore
  - [x] 2.5 — Test unfollow quando non segui → 200 idempotente, nessun errore
  - [x] 2.6 — Test GET `/api/users/{id}/followers/` → lista utenti follower
  - [x] 2.7 — Test GET `/api/users/{id}/following/` → lista utenti seguiti
  - [x] 2.8 — Test `is_followed_by_me` → `true` dopo follow, `false` dopo unfollow
  - [x] 2.9 — Test utente non autenticato → 401
  - [x] 2.10 — Test utente `toconfirm` → 403 su follow/unfollow
  - [x] 2.11 — Eseguire TUTTI i test della suite per verificare zero regressioni (84 test OK)

- [x] Task 3: Frontend — Implementare optimistic UI con rollback (AC: #1, #2, #3)
  - [x] 3.1 — Aggiornare `useFollow()` in `use-users.ts`: aggiungere callback `onMutate` che salva snapshot della query cache e aggiorna ottimisticamente `is_followed_by_me: true` e `followers_count + 1` nella cache React Query del profilo target
  - [x] 3.2 — Aggiornare `useFollow()`: aggiungere callback `onError` che ripristina lo snapshot salvato (rollback) e mostra toast Sonner errore: `"Errore nel seguire l'utente"`
  - [x] 3.3 — Aggiornare `useFollow()`: aggiungere callback `onSettled` con invalidazione cache precisa (vedi Task 5)
  - [x] 3.4 — Aggiornare `useUnfollow()` in `use-users.ts`: stessi pattern di `useFollow()` — `onMutate` (snapshot + set `is_followed_by_me: false`, `followers_count - 1`), `onError` (rollback + toast `"Errore nello smettere di seguire l'utente"`), `onSettled` (invalidazione)
  - [x] 3.5 — Passare `userId` come variabile ai mutation hooks per poter aggiornare la cache corretta (attualmente i hooks non ricevono il targetUserId nel contesto `onMutate`)

- [x] Task 4: Frontend — Fix testo bottone e stato loading (AC: #1, #2)
  - [x] 4.1 — Modificare `FollowButton` in `follow-button.tsx`: cambiare testo da `"Segui già"` a `"Smetti di seguire"` quando `isFollowing === true` (coerente con AC2 che dice "clicca il bottone Smetti di seguire")
  - [x] 4.2 — Aggiungere stato loading differenziato durante la mutation: mostrare testo `"Seguendo..."` durante follow e `"Rimuovendo..."` durante unfollow (invece di solo disabilitare il bottone)
  - [x] 4.3 — Verificare che il bottone sia nascosto quando l'utente visualizza il proprio profilo (già implementato, confermato)

- [x] Task 5: Frontend — Precisare cache invalidation (AC: #1, #2)
  - [x] 5.1 — Sostituire l'invalidazione broad `queryClient.invalidateQueries({ queryKey: ["users"] })` con invalidazione specifica:
    - `queryKeys.users.detail(targetUserId)` — profilo target aggiornato
    - `queryKeys.users.byUsername(targetUsername)` — profilo target via username
    - `queryKeys.users.followers(targetUserId)` — lista follower target
    - `queryKeys.users.following(currentUserId)` — lista following utente corrente
  - [x] 5.2 — Mantenere `queryKeys.videos.followingAll` (invalidazione feed home — già presente)
  - [x] 5.3 — Verificare che `queryKeys` in `query-keys.ts` abbia tutte le chiavi necessarie (followers, following per userId specifico); aggiungere se mancanti

- [x] Task 6: Verifica finale (AC: #1, #2, #3)
  - [x] 6.1 — Eseguire TUTTI i test backend: `python manage.py test` da `backend/` → 84 test (inclusi 12 nuovi) passano
  - [x] 6.2 — Eseguire frontend build: `npm run build` da `frontend/` → TypeScript strict, 0 errori
  - [ ] 6.3 — Verificare manualmente il flusso completo: visita profilo → click "Segui" → feedback immediato → conteggi aggiornati → click "Smetti di seguire" → rollback visivo → conteggi aggiornati

## Dev Notes

### Stato attuale del codice — Analisi gap

Il sistema follow/unfollow è **parzialmente implementato**. La struttura backend è completa e funzionante, ma il frontend manca di optimistic UI, error handling e toast — tutti requisiti espliciti degli AC.

| Gap | Severità | File impattato | Dettaglio |
|-----|----------|----------------|-----------|
| **Nessun test backend per follow/unfollow** | CRITICO | `tests/test_views.py` | 0 test per gli endpoint `follow`, `unfollow`, `followers`, `following`. I count sono testati solo indirettamente in `UserProfileTest` |
| **Nessuna optimistic UI** | CRITICO | `use-users.ts` | `useFollow`/`useUnfollow` non hanno `onMutate`. L'utente aspetta la risposta API prima di vedere il cambio bottone |
| **Nessun toast su errore** | CRITICO | `follow-button.tsx` | Se la chiamata API fallisce, l'utente non riceve alcun feedback. Nessun `onError` con toast Sonner |
| **Nessun rollback su errore** | CRITICO | `use-users.ts` | Senza `onMutate` snapshot non c'è nulla da ripristinare. Dopo errore l'UI resta in stato inconsistente fino al refetch |
| **Testo bottone errato** | IMPORTANTE | `follow-button.tsx` | "Segui già" dovrebbe essere "Smetti di seguire" (l'AC2 lo richiede esplicitamente) |
| **Cache invalidation troppo ampia** | IMPORTANTE | `use-users.ts` | `invalidateQueries({ queryKey: ["users"] })` invalida TUTTE le query utenti. Spreca risorse e causa refetch inutili |
| **Risposta API senza stato** | MEDIO | `views.py` | `follow()` restituisce solo `{detail: "Hai iniziato a seguire..."}`. Non restituisce `is_followed` né `followers_count` aggiornato |

### Pattern optimistic UI da implementare

Il pattern architetturale definito nel documento di architettura è:

```typescript
// Pattern: useMutation con onMutate → onError → onSettled
// Applicato a: commenti, like, follow/unfollow

const useFollow = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: number) => usersApi.follow(userId),
    onMutate: async (userId) => {
      // 1. Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: queryKeys.users.detail(userId) });
      // 2. Snapshot previous value
      const previousUser = queryClient.getQueryData(queryKeys.users.detail(userId));
      // 3. Optimistically update cache
      queryClient.setQueryData(queryKeys.users.detail(userId), (old) => ({
        ...old,
        is_followed_by_me: true,
        followers_count: (old?.followers_count ?? 0) + 1,
      }));
      return { previousUser };
    },
    onError: (_err, userId, context) => {
      // Rollback to snapshot
      queryClient.setQueryData(queryKeys.users.detail(userId), context?.previousUser);
      toast.error("Errore nel seguire l'utente");
    },
    onSettled: (_data, _err, userId) => {
      // Refetch per sincronizzare con server
      queryClient.invalidateQueries({ queryKey: queryKeys.users.detail(userId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.videos.followingAll });
    },
  });
};
```

**NOTA CRITICA:** La cache React Query potrebbe contenere il profilo sia sotto `queryKeys.users.detail(id)` che `queryKeys.users.byUsername(username)`. L'optimistic update deve aggiornare ENTRAMBE le chiavi, oppure il profilo visualizzato (che usa `useUserByUsername`) non mostrerebbe il cambio immediato. Verificare quale chiave è attiva nella pagina profilo e aggiornare quella.

### Decisione: Cache key per optimistic update

La pagina `/profilo/[username]` usa `useUserByUsername(username)` che ha queryKey `["users", "username", username]`. Quindi l'optimistic update deve aggiornare questa chiave, non solo `users.detail(id)`. Opzioni:

1. **Passare `username` come variabile aggiuntiva alla mutation** — più preciso
2. **Aggiornare tutte le query che matchano `["users"]`** — più semplice ma invalida troppo

**Scelta raccomandata:** Opzione 1. I mutation hooks devono ricevere `{ userId, username }` come variabili per aggiornare la cache corretta. Esempio:
```typescript
const followMutation = useFollow();
followMutation.mutate({ userId: profileUser.id, username: profileUser.username });
```

### Lezioni dalla Story 1-4 (da applicare)

- **Test pattern:** `APITestCase` + `force_authenticate()`. Asserzioni su formato `{code, detail}` per errori.
- **Toast pattern:** Toast Sonner solo per errori e conferme importanti. MAI toast per azioni con feedback visivo immediato (il follow ha già il cambio bottone, quindi: nessun toast su successo, toast solo su errore).
- **Naming:** kebab-case per file, named exports per componenti, snake_case per campi dati.
- **Serializer pattern:** `SerializerMethodField` per campi calcolati. `getattr(obj, 'annotated_*', fallback)` per count con annotation.
- **is_followed_by_me:** Aggiunto in Story 1-4 con caching `_following_ids`. Funziona correttamente. Il `FollowButton` riceve `isFollowing={profileUser.is_followed_by_me}` da `ProfileHeader`.
- **Permessi:** `OnlyUsersPermission` blocca utenti `toconfirm`. Già applicato a follow/unfollow actions.
- **Error handling centralizzato:** `handle_exception_with_serializer(exc)` nel ViewSet. Formato: `{code: "...", detail: "..."}`.
- **N+1 fix:** `get_queryset()` con `Count` annotations + `distinct=True` applicato in Story 1-4. Le action `get_followers`/`get_following` passano per `get_serializer()` ma NON per `get_queryset()` annotata — potenziale N+1 sulle liste.
- **58 test totali** — zero regressioni obbligatorio.

### Git intelligence

Ultimi commit rilevanti:
- `d6b0b79` — Story 1-2 registrazione + Story 1-3 login JWT + code review fix
- `ededfe7` — code review Story 1-1: sicurezza, performance, dead code
- `f6845e1` — Story 1-1 backend alignment + Story 1-9 ricerca utenti + fix permessi

Pattern stabiliti nei commit precedenti:
- Test con `APITestCase` + `force_authenticate()` in classe dedicata (es. `UserProfileTest`)
- Error handling con `handle_exception_with_serializer()` e messaggi italiani
- Named exports per componenti React
- kebab-case per file frontend
- Ogni story aggiunge test nella stessa `test_views.py` in classi separate

### Project Structure Notes

| File | Ruolo | Azione |
|------|-------|--------|
| `backend/cs_clips/views.py` | UserViewSet follow/unfollow actions | **DA MODIFICARE** — migliorare risposta con is_followed + followers_count |
| `backend/cs_clips/tests/test_views.py` | Test API | **DA ESTENDERE** — aggiungere classe `FollowUnfollowTest` con 10+ test |
| `frontend/src/lib/hooks/use-users.ts` | useFollow/useUnfollow hooks | **DA MODIFICARE** — aggiungere onMutate/onError/onSettled completi |
| `frontend/src/components/user/follow-button.tsx` | Bottone follow/unfollow | **DA MODIFICARE** — fix testo, loading state |
| `frontend/src/lib/query-keys.ts` | Query keys | **VERIFICARE** — assicurare che followers(id)/following(id) esistano |

**File NON da toccare (già corretti):**
- `backend/cs_clips/models.py` — User.following ManyToManyField OK
- `backend/cs_clips/serializers.py` — is_followed_by_me, followers_count, following_count OK
- `frontend/src/types/user.ts` — Tipo User con is_followed_by_me OK
- `frontend/src/lib/api/users.ts` — follow/unfollow API functions OK
- `frontend/src/components/user/profile-header.tsx` — Integrazione FollowButton OK

### Stack tecnologico rilevante

- **Backend:** Django 5.1.6, DRF 3.15.1, SimpleJWT 5.3.1
- **Frontend:** Next.js 16.1.6, React 19, TypeScript 5, Axios 1.13.5
- **UI:** TailwindCSS 4, shadcn/ui (Button, Sonner toast), Lucide React
- **State:** TanStack React Query 5 (useMutation + useQueryClient), Axios
- **Pattern:** snake_case per campi dati, kebab-case per file, named exports

### Vincoli critici per lo sviluppatore

1. **MODELLO USER:** Usare SEMPRE `get_user_model()`. MAI `from django.contrib.auth.models import User`. Il Custom User Model è `cs_clips.User` (AbstractUser).
2. **M2M FOLLOW:** `request.user.following.add(target_user)` è idempotente (non genera errore se la relazione esiste già). Lo stesso per `.remove()`. Sfruttare questa proprietà per gestire le chiamate duplicate.
3. **OPTIMISTIC UI:** Il pattern React Query è: `onMutate` (snapshot + update cache) → `onError` (restore snapshot + toast) → `onSettled` (invalidate queries). TUTTI e tre i callback sono obbligatori.
4. **CACHE KEY:** La pagina profilo usa `useUserByUsername(username)` con queryKey `["users", "username", username]`. L'optimistic update DEVE aggiornare questa chiave, non solo `users.detail(id)`.
5. **TOAST:** Usare Sonner. Toast solo su errore follow/unfollow, MAI su successo (il cambio bottone è feedback sufficiente). Import: `import { toast } from "sonner"`.
6. **TESTO BOTTONE:** "Segui" quando non segui, "Smetti di seguire" quando segui. NON "Segui già" (non è un'azione, è uno stato).
7. **ERROR HANDLING BACKEND:** Ogni errore deve passare per `handle_exception_with_serializer()`. Formato: `{code: "...", detail: "..."}`. Messaggi in italiano.
8. **QUERY INVALIDATION:** Dopo follow/unfollow invalidare: `users.detail(id)`, `users.byUsername(username)`, `users.followers(targetId)`, `users.following(currentUserId)`, `videos.followingAll`. NON invalidare tutto `["users"]`.
9. **PERMESSI:** `OnlyUsersPermission` è già applicato. Utenti `toconfirm` ricevono 403. NON aggiungere altri controlli permessi.
10. **LINGUA:** Messaggi utente/toast in italiano ("Errore nel seguire l'utente", "Smetti di seguire"). Codice in inglese.
11. **TEST:** Pattern: `APITestCase` + `force_authenticate()`. Classe `FollowUnfollowTest`. 58+ test esistenti — zero regressioni obbligatorio. Eseguire con `python manage.py test` da `backend/`.
12. **SELF-FOLLOW:** Il check `if target_user == request.user` è già implementato nel backend. Restituisce 400. Il frontend nasconde il bottone su profilo proprio. Non serve lavoro aggiuntivo.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.5]
- [Source: _bmad-output/planning-artifacts/architecture.md#Optimistic-UI-Pattern]
- [Source: _bmad-output/planning-artifacts/architecture.md#Error-Handling]
- [Source: _bmad-output/planning-artifacts/architecture.md#React-Query-Cache-Invalidation]
- [Source: _bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- [Source: _bmad-output/planning-artifacts/prd.md#FR4-FR5]
- [Source: _bmad-output/project-context.md#Custom-User-Model]
- [Source: _bmad-output/project-context.md#Error-Handling-Centralizzato]
- [Source: _bmad-output/project-context.md#Pattern-Serializer]
- [Source: _bmad-output/implementation-artifacts/1-4-profilo-utente-pubblico.md#Dev-Notes]
- [Source: _bmad-output/implementation-artifacts/1-4-profilo-utente-pubblico.md#Senior-Developer-Review]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

Nessun debug log necessario — implementazione fluida senza blocchi.

### Completion Notes List

- **Task 1:** Modificati endpoint `follow()` e `unfollow()` in `views.py` per restituire `{detail, is_followed, followers_count}`. Self-follow ora passa per `ValidationError` → `handle_exception_with_serializer()` → formato `{code, detail}`. Gestita idempotenza: double-follow e unfollow-when-not-following restituiscono 200 con stato attuale.
- **Task 2:** Aggiunta classe `FollowUnfollowTest` con 12 test: follow success, unfollow success, self-follow 400, double-follow idempotente, unfollow-not-following idempotente, GET followers/following, is_followed_by_me, 401 non autenticato, 403 toconfirm. Full regression suite: 84/84 OK.
- **Task 3:** Implementata optimistic UI completa su `useFollow()` e `useUnfollow()`: `onMutate` (cancel queries + snapshot + update cache `byUsername`), `onError` (rollback snapshot + toast Sonner), `onSettled` (invalidazione precisa). Mutation hooks ora ricevono `{userId, username}`.
- **Task 4:** Testo bottone corretto da "Segui già" a "Smetti di seguire". Aggiunto loading differenziato: "Seguendo..." durante follow, "Rimuovendo..." durante unfollow. Confermato: bottone nascosto su profilo proprio.
- **Task 5:** Cache invalidation precisa: `users.detail(id)`, `users.byUsername(username)`, `users.followers(targetId)`, `users.following(currentUserId)`, `videos.followingAll`. Rimossa invalidazione broad `["users"]`. Query keys verificate: tutte le chiavi necessarie già presenti in `query-keys.ts`.
- **Task 6:** Backend 84/84 test OK (12 nuovi follow/unfollow + 72 esistenti). Frontend build OK, TypeScript strict 0 errori. Verifica manuale: da effettuare dall'utente (subtask 6.3).

### File List

- `backend/cs_clips/views.py` — Modificato: follow() e unfollow() con risposta arricchita, idempotenza, ValidationError per self-follow. **Review fix:** get_followers/get_following con queryset annotato + paginazione
- `backend/cs_clips/tests/test_views.py` — Modificato: aggiunta classe FollowUnfollowTest (13 test). **Review fix:** assertion rafforzate, test paginazione, test 404 utente inesistente
- `frontend/src/lib/hooks/use-users.ts` — Modificato: useFollow/useUnfollow con optimistic UI, rollback, toast, cache invalidation precisa. **Review fix:** dual-key optimistic update (byUsername + detail), useUpdateProfile invalidazione specifica
- `frontend/src/components/user/follow-button.tsx` — Modificato: testo corretto, loading differenziato, prop username aggiunta
- `frontend/src/components/user/profile-header.tsx` — Modificato: passaggio prop username a FollowButton
- `frontend/src/lib/api/users.ts` — Modificato: tipo risposta follow/unfollow con is_followed e followers_count

## Senior Developer Review (AI)

**Reviewer:** Claude Opus 4.6 — Adversarial Code Review
**Data:** 2026-02-15
**Esito:** PASS — tutti i fix applicati automaticamente

### Issue trovati e risolti

| # | Sev | Titolo | Fix applicato |
|---|-----|--------|--------------|
| H1 | HIGH | N+1 queries in get_followers/get_following | Usato `self.get_queryset().filter(pk__in=...)` per passare dal queryset annotato |
| H2 | HIGH | Paginazione mancante su get_followers/get_following | Aggiunto `self.paginate_queryset()` + `self.get_paginated_response()` |
| M1 | MEDIUM | Test mancante per follow utente inesistente | Aggiunto `test_follow_nonexistent_user_returns_404` |
| M2 | MEDIUM | useUpdateProfile invalidazione troppo ampia | Sostituita invalidazione broad con `detail(id)` + `byUsername(username)` specifici |
| M3 | MEDIUM | Optimistic update solo su chiave byUsername | Aggiunto dual-key optimistic update su `byUsername` E `detail` |
| M4 | MEDIUM | Assertion debole in test_self_follow_returns_400 | Aggiunto `assertIn('Non puoi seguire te stesso', response.data['detail'])` |

### Issue non bloccanti (non corretti)

| # | Sev | Titolo | Motivo |
|---|-----|--------|--------|
| L1 | LOW | UserSerializer espone array M2M ID (followers/following) | Non bloccante — richiede decisione architetturale più ampia |
| L2 | LOW | Discrepanza conteggio test (84 dichiarati, 85 effettivi post-fix) | Corretto nel Change Log |

### Risultato test post-review

- Backend: **85/85 test OK** (13 FollowUnfollowTest + 72 esistenti) — zero regressioni
- Frontend: TypeScript strict — **0 errori**

## Change Log

- **2026-02-15:** Story 1-5 Follow e Unfollow — Implementazione completa: risposta API arricchita con is_followed/followers_count, idempotenza endpoint, 12 test backend (classe FollowUnfollowTest), optimistic UI con rollback e toast Sonner, fix testo bottone ("Smetti di seguire"), loading differenziato, cache invalidation precisa. 84 test backend OK, frontend build OK.
- **2026-02-15:** Senior Developer Review (AI) — 6 fix applicati: N+1 query fix (H1), paginazione followers/following (H2), test 404 utente inesistente (M1), useUpdateProfile invalidazione specifica (M2), dual-key optimistic update (M3), assertion rafforzata self-follow (M4). 85 test backend OK, 0 errori TypeScript.
