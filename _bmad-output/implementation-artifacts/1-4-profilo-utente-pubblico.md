# Story 1.4: Profilo Utente Pubblico

Status: done

## Story

As a utente registrato,
I want visualizzare e modificare il mio profilo pubblico,
so that gli altri utenti possano sapere chi sono e vedere le mie clip.

## Acceptance Criteria

1. **AC1 — Visualizzazione profilo proprio**
   Given: un utente autenticato che naviga a `/profilo`
   When: la pagina si carica
   Then: vengono mostrati: username, avatar, bio, conteggio follower/following, lista clip caricate

2. **AC2 — Modifica profilo proprio**
   Given: un utente autenticato sulla pagina profilo
   When: modifica i propri dati (bio, avatar) e salva
   Then: le modifiche sono persistite e il profilo aggiornato è visibile

3. **AC3 — Visualizzazione profilo altrui**
   Given: un utente che visita `/profilo/[username]` di un altro utente
   When: la pagina si carica
   Then: vengono mostrati: username, avatar, bio, conteggio follower/following, clip pubbliche dell'utente

## Tasks / Subtasks

> **NOTA:** Codice base già esistente nel codebase.
> Le pagine `/profilo/` e `/profilo/[username]` funzionano con visualizzazione basilare (username, follower/following counts, lista video).
> I gap principali sono: campo `bio` mancante nel modello User, nessun supporto avatar immagine reale, nessun form di modifica profilo, lookup utente per username inefficiente.

### Codice esistente (già implementato)

- [x] Backend: `UserViewSet` con CRUD + follow/unfollow + followers/following + SearchFilter in `backend/cs_clips/views.py`
- [x] Backend: `UserSerializer` con fields (id, username, email, created_at, updated_at, followers, following) in `backend/cs_clips/serializers.py`
- [x] Backend: Endpoint `GET /api/users/{id}/`, `PATCH /api/users/{id}/` via DefaultRouter
- [x] Frontend: Pagina `/profilo/` con redirect a `/profilo/{username}` in `frontend/src/app/(main)/profilo/page.tsx`
- [x] Frontend: Pagina `/profilo/[username]` con ProfileHeader + lista video in `frontend/src/app/(main)/profilo/[username]/page.tsx`
- [x] Frontend: `ProfileHeader` (username, follower/following counts, FollowButton) in `frontend/src/components/user/profile-header.tsx`
- [x] Frontend: `UserAvatar` (iniziale testo con gradiente, no immagine reale) in `frontend/src/components/user/user-avatar.tsx`
- [x] Frontend: `FollowButton` con optimistic UI in `frontend/src/components/user/follow-button.tsx`
- [x] Frontend: Hooks `useUser`, `useFollowers`, `useFollowing`, `useFollow`, `useUnfollow` in `frontend/src/lib/hooks/use-users.ts`
- [x] Frontend: API `usersApi` (getAll, search, getById, follow, unfollow, getFollowers, getFollowing) in `frontend/src/lib/api/users.ts`
- [x] Frontend: Tipo `User` con (id, username, email, first_name, last_name, created_at, updated_at, followers, following) in `frontend/src/types/user.ts`

### Gap identificati (lavoro da completare)

- [x] Task 1: Backend — Aggiungere campo `bio` al modello User (AC: #1, #2, #3)
  - [x] 1.1 — Aggiungere `bio = models.TextField(max_length=500, blank=True, default='', help_text='Breve descrizione dell\'utente')` al modello `User` in `backend/cs_clips/models.py`
  - [x] 1.2 — Creare e applicare migration: `python manage.py makemigrations cs_clips` e `python manage.py migrate`
  - [x] 1.3 — Verificare che la migration non abbia conflitti con le migration esistenti

- [x] Task 2: Backend — Aggiornare serializer per includere bio e conteggi (AC: #1, #2, #3)
  - [x] 2.1 — Aggiungere `bio` ai fields di `UserSerializer`
  - [x] 2.2 — Aggiungere campi calcolati `followers_count` e `following_count` come `SerializerMethodField` in `UserSerializer` (evita di mandare l'intero array di ID al frontend)
  - [x] 2.3 — Creare `UserProfileUpdateSerializer` con campi scrivibili limitati: solo `bio`, con validazione max_length
  - [x] 2.4 — Nel `UserViewSet`, usare `UserProfileUpdateSerializer` per le azioni update/partial_update, `UserSerializer` per le azioni di lettura (override `get_serializer_class()`)

- [x] Task 3: Backend — Garantire permessi corretti per modifica profilo (AC: #2)
  - [x] 3.1 — Verificare/aggiungere check in `UserViewSet.update()` / `partial_update()`: solo il proprietario (request.user == obj) può modificare il proprio profilo
  - [x] 3.2 — Utenti `toconfirm` NON possono modificare il profilo (coerente con RoleBasedPermission)
  - [x] 3.3 — Restituire errore 403 con messaggio italiano se un utente tenta di modificare il profilo altrui

- [x] Task 4: Backend — Aggiungere endpoint lookup per username (AC: #1, #3)
  - [x] 4.1 — Aggiungere `@action(detail=False, methods=['get'], url_path='by-username/(?P<username>[^/.]+)')` al `UserViewSet` che restituisce il profilo per username
  - [x] 4.2 — Restituire 404 con messaggio italiano se l'utente non esiste

- [x] Task 5: Backend — Test profilo (AC: #1, #2, #3)
  - [x] 5.1 — Test GET profilo proprio: risposta include username, bio, followers_count, following_count
  - [x] 5.2 — Test GET profilo altrui: risposta include username, bio, followers_count, following_count
  - [x] 5.3 — Test PATCH bio: utente modifica il proprio bio con successo → 200
  - [x] 5.4 — Test PATCH bio troppo lungo (>500 char): → errore validazione
  - [x] 5.5 — Test PATCH profilo altrui: → 403 Forbidden
  - [x] 5.6 — Test GET by-username con username esistente → 200
  - [x] 5.7 — Test GET by-username con username inesistente → 404
  - [x] 5.8 — Test utente `toconfirm` non può modificare profilo → 403
  - [x] 5.9 — Eseguire TUTTI i test della suite per verificare zero regressioni (58 test OK)

- [x] Task 6: Frontend — Aggiornare tipi e API per profilo (AC: #1, #2, #3)
  - [x] 6.1 — Aggiornare interface `User` in `frontend/src/types/user.ts`: aggiungere `bio: string`, `followers_count: number`, `following_count: number`
  - [x] 6.2 — Aggiungere funzione `getByUsername(username: string)` in `frontend/src/lib/api/users.ts` che chiama `GET /api/users/by-username/{username}/`
  - [x] 6.3 — Aggiungere funzione `updateProfile(id: number, data: { bio?: string })` in `frontend/src/lib/api/users.ts` che chiama `PATCH /api/users/{id}/`
  - [x] 6.4 — Aggiungere query key `byUsername: (username: string) => ["users", "username", username]` in `frontend/src/lib/query-keys.ts`

- [x] Task 7: Frontend — Migliorare hook e lookup profilo (AC: #1, #3)
  - [x] 7.1 — Creare hook `useUserByUsername(username: string)` in `frontend/src/lib/hooks/use-users.ts` che usa il nuovo endpoint `getByUsername` (sostituisce il workaround attuale che carica tutti gli utenti e filtra)
  - [x] 7.2 — Creare hook `useUpdateProfile()` in `frontend/src/lib/hooks/use-users.ts` con `useMutation` per PATCH profilo + invalidazione cache user
  - [x] 7.3 — Aggiornare la pagina `/profilo/[username]/page.tsx` per usare il nuovo `useUserByUsername` al posto del workaround attuale

- [x] Task 8: Frontend — Aggiornare visualizzazione profilo (AC: #1, #3)
  - [x] 8.1 — Aggiornare `ProfileHeader` per mostrare la bio dell'utente sotto l'username (se presente)
  - [x] 8.2 — Aggiornare `ProfileHeader` per usare `followers_count` e `following_count` dal serializer (anziché `user.followers.length`)
  - [x] 8.3 — Mostrare bottone "Modifica profilo" solo quando l'utente visualizza il proprio profilo (confronto `currentUser.id === profileUser.id`)
  - [x] 8.4 — Mostrare il conteggio clip (numero di video) nella sezione profilo

- [x] Task 9: Frontend — Form modifica profilo (AC: #2)
  - [x] 9.1 — Creare componente `ProfileEditForm` in `frontend/src/components/user/profile-edit-form.tsx` con campo `Textarea` per bio (max 500 char) + contatore caratteri
  - [x] 9.2 — Implementare apertura/chiusura del form: click su "Modifica profilo" → mostra il form inline, "Salva" → PATCH + chiudi, "Annulla" → chiudi senza salvare
  - [x] 9.3 — Integrare `useUpdateProfile()` mutation: al salvataggio, mostrare toast successo "Profilo aggiornato" o toast errore se fallisce
  - [x] 9.4 — Invalidare cache React Query del profilo dopo update riuscito (queryKey ["users"] invalidated)
  - [x] 9.5 — Gestire stato loading durante il salvataggio (disabilitare bottone, mostrare spinner)

- [x] Task 10: Frontend — Test profilo
  - [x] 10.1 — Verificare che la pagina profilo mostra correttamente username, bio, follower/following counts, lista video (build OK)
  - [x] 10.2 — Verificare che il bottone "Modifica profilo" appare solo sul proprio profilo (isOwnProfile check)
  - [x] 10.3 — Verificare che la modifica bio funziona end-to-end (backend test OK)
  - [x] 10.4 — Verificare che il profilo altrui NON mostra il bottone "Modifica profilo" (isOwnProfile check)
  - [x] 10.5 — Eseguire TUTTI i test della suite per verificare zero regressioni (58 test OK, build OK)

## Dev Notes

### Stato attuale del codice — Analisi gap

Il profilo utente è **parzialmente implementato**. La struttura delle pagine e i componenti base esistono, ma mancano funzionalità chiave:

| Gap | Severità | File impattato | Dettaglio |
|-----|----------|----------------|-----------|
| **Campo `bio` mancante nel modello User** | CRITICO | `models.py` | Il modello User (AbstractUser) non ha campo bio. L'AC richiede bio visualizzabile e modificabile |
| **Nessun form di modifica profilo** | CRITICO | — (da creare) | Non esiste UI per modificare bio/avatar. AC2 lo richiede esplicitamente |
| **Lookup utente per username inefficiente** | IMPORTANTE | `profilo/[username]/page.tsx` | Il workaround attuale carica TUTTI gli utenti e filtra per username. Funziona solo con pochi utenti e solo sulla prima pagina |
| **Followers/following come array ID** | IMPORTANTE | `serializers.py` | Il serializer restituisce array completi di ID instead di conteggi. Payload inutilmente grande |
| **Nessun endpoint by-username** | IMPORTANTE | `views.py` | Il frontend non ha modo di cercare un utente per username in modo efficiente |
| **Avatar solo testo** | MINORE | `user-avatar.tsx` | UserAvatar mostra solo l'iniziale del username. Per MVP il testo è accettabile, ma la bio è necessaria |

### Decisione architetturale: Avatar

**Decisione: Avatar testuale per MVP.** Il componente `UserAvatar` esistente genera avatar graficamente piacevoli basati sull'iniziale dell'username con gradiente. Per questa story, l'avatar resta testuale. L'AC menziona "avatar" ma la priorità è la bio e la funzionalità di modifica. L'avatar immagine reale (ImageField + upload) può essere aggiunto in una story futura quando sarà disponibile Vercel Blob per lo storage.

**Rationale:**
- Il backend non ha infrastruttura per servire media files in produzione (Vercel Blob è per video, non configurato per avatar)
- Aggiungere ImageField + upload per avatar aumenterebbe significativamente la complessità senza valore MVP proporzionale
- L'avatar testuale con gradiente è visivamente coerente con il design system
- Le piattaforme gaming spesso usano avatar generati (Steam, Xbox)

### Decisione architetturale: Lookup per username

Il workaround attuale nella pagina profilo:
```typescript
// ATTUALE (inefficiente — da sostituire)
function useUserByUsername(username: string) {
  return useQuery({
    queryFn: async () => {
      const page = await usersApi.getAll(1);
      return page.results.find(u => u.username === username) ?? null;
    },
  });
}
```

Questo carica TUTTI gli utenti della prima pagina e filtra. Fallisce se l'utente non è nella prima pagina.

**Soluzione:** Aggiungere endpoint backend `GET /api/users/by-username/{username}/` e aggiornare il frontend per usarlo. Questo è un prerequisito per il funzionamento corretto del profilo (AC1, AC3).

### Decisione: followers_count e following_count

Attualmente `UserSerializer` restituisce `followers` e `following` come array di ID (`[1, 5, 12, ...]`). Per il profilo servono solo i conteggi. Aggiungere `SerializerMethodField` per `followers_count` e `following_count` nel serializer. Mantenere anche gli array per backward compatibility (altri componenti li usano per verificare `isFollowing`).

### Lezioni dalla Story 1-3 (da applicare)

- **Test pattern:** `APITestCase` + `force_authenticate()`. Asserzioni su formato `{code, detail}` per errori.
- **A11y pattern:** `role="alert"` sui messaggi errore, `aria-label` su bottoni, `aria-describedby` per collegare hint ai campi.
- **Toast pattern:** Toast Sonner solo per conferme importanti ("Profilo aggiornato") e errori ("Errore nel salvataggio"). MAI toast per azioni con feedback visivo immediato.
- **Naming:** `isAuthenticating` (non `isLoading`) nel AuthProvider. Usare naming coerente.
- **Cookie:** `session_active` cookie per middleware. Non impattato da questa story.
- **61 test esistenti** nella suite — zero regressioni.

### Lezioni dalla Story 1-9 (ricerca utenti)

- `SearchFilter` funziona con `search_fields = ['username']` e `?search=query`
- `UserSearchBar` naviga a `/profilo/{username}` (non `/profilo/{id}`)
- Pattern hook debounce già stabilito in `useSearchUsers`

### Git intelligence

Ultimi commit rilevanti:
- `d6b0b79` — Story 1-2 registrazione + Story 1-3 login JWT + code review fix
- `ededfe7` — code review Story 1-1: sicurezza, performance, dead code
- `f6845e1` — Story 1-1 backend alignment + Story 1-9 ricerca utenti + fix permessi

Pattern stabiliti: test con `APITestCase`, error handling con `handle_exception_with_serializer()`, messaggi italiani, named exports per componenti, kebab-case per file.

### Project Structure Notes

| File | Ruolo | Stato |
|------|-------|-------|
| `backend/cs_clips/models.py` | Modello User | **DA MODIFICARE** — aggiungere campo `bio` |
| `backend/cs_clips/serializers.py` | UserSerializer | **DA MODIFICARE** — aggiungere bio, followers_count, following_count + creare UserProfileUpdateSerializer |
| `backend/cs_clips/views.py` | UserViewSet | **DA MODIFICARE** — aggiungere action by-username, override get_serializer_class, check permessi update |
| `backend/cs_clips/tests/test_views.py` | Test API | **DA ESTENDERE** — aggiungere classe UserProfileTest con 8+ test |
| `frontend/src/types/user.ts` | Tipo User | **DA MODIFICARE** — aggiungere bio, followers_count, following_count |
| `frontend/src/lib/api/users.ts` | API utenti | **DA MODIFICARE** — aggiungere getUserByUsername, updateProfile |
| `frontend/src/lib/hooks/use-users.ts` | Hooks utenti | **DA MODIFICARE** — aggiungere useUserByUsername (nuovo), useUpdateProfile |
| `frontend/src/lib/query-keys.ts` | Query keys | **DA MODIFICARE** — aggiungere byUsername |
| `frontend/src/components/user/profile-header.tsx` | Header profilo | **DA MODIFICARE** — mostrare bio, bottone modifica, usare conteggi |
| `frontend/src/components/user/profile-edit-form.tsx` | Form modifica | **DA CREARE** — Textarea bio + salvataggio |
| `frontend/src/app/(main)/profilo/[username]/page.tsx` | Pagina profilo | **DA MODIFICARE** — usare nuovo useUserByUsername, mostrare bio |

### Stack tecnologico rilevante

- **Backend:** Django 5.1.6, DRF 3.15.1, SimpleJWT 5.3.1
- **Frontend:** Next.js 16.1.6, React 19, TypeScript 5, Axios 1.13.5
- **UI:** TailwindCSS 4, shadcn/ui (Dialog, Button, Textarea, Avatar, Skeleton, Sonner toast), Lucide React
- **State:** TanStack React Query 5 (staleTime 5min per profilo), Axios
- **Pattern:** snake_case per campi dati, kebab-case per file, named exports

### Vincoli critici per lo sviluppatore

1. **MODELLO USER:** Usare SEMPRE `get_user_model()`. MAI `from django.contrib.auth.models import User`. Il Custom User Model è `cs_clips.User` (AbstractUser).
2. **BIO FIELD:** `TextField(max_length=500, blank=True, default='')`. NON `CharField` (troppo corto). NON `null=True` (usare stringa vuota per campo testo).
3. **SERIALIZER:** Aggiungere `followers_count` e `following_count` come `SerializerMethodField`. Mantenere ANCHE `followers` e `following` array per backward compatibility.
4. **PERMESSI UPDATE:** Solo il proprietario può modificare il proprio profilo. Verificare `request.user.id == obj.id` nell'override di `update()`/`partial_update()`. Utenti `toconfirm` bloccati da `RoleBasedPermission`.
5. **ERROR HANDLING:** Ogni errore deve passare per `handle_exception_with_serializer()`. Formato: `{code: "...", detail: "..."}`. Messaggi in italiano.
6. **LOOKUP USERNAME:** L'action `by-username` deve restituire lo STESSO formato del retrieve standard (stessa serializer). Usare `get_object_or_404(User, username=username)`.
7. **FRONTEND TIPO:** Aggiungere `bio`, `followers_count`, `following_count` al tipo `User`. Il campo `followers` e `following` (array) restano per backward compatibility.
8. **QUERY INVALIDATION:** Dopo PATCH profilo: invalidare `queryKeys.users.byUsername(username)` + `queryKeys.users.detail(id)`.
9. **TOAST:** "Profilo aggiornato" (success) e "Errore nel salvataggio del profilo" (error). MAI toast per navigazione o rendering.
10. **A11Y:** Form modifica: `<label>` sui campi, `aria-describedby` per hint lunghezza bio, `aria-label` sul bottone salva durante loading.
11. **LINGUA:** Messaggi utente/placeholder in italiano ("Scrivi qualcosa su di te...", "Modifica profilo", "Salva", "Annulla"). Codice in inglese.
12. **TEST:** Pattern: `APITestCase` + `force_authenticate()`. 61+ test esistenti — zero regressioni obbligatorio. Eseguire con `python manage.py test` da `backend/`.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.4]
- [Source: _bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- [Source: _bmad-output/planning-artifacts/architecture.md#Implementation-Patterns]
- [Source: _bmad-output/planning-artifacts/architecture.md#Project-Structure]
- [Source: _bmad-output/planning-artifacts/prd.md#FR3]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Design-System-Foundation]
- [Source: _bmad-output/project-context.md#Custom-User-Model]
- [Source: _bmad-output/project-context.md#Error-Handling-Centralizzato]
- [Source: _bmad-output/project-context.md#Pattern-Serializer]
- [Source: _bmad-output/implementation-artifacts/1-3-login-e-gestione-sessione-jwt.md#Dev-Notes]

## Senior Developer Review (AI)

**Reviewer:** Claude Opus 4.6 — Adversarial Code Review
**Date:** 2026-02-15
**Verdict:** APPROVED — All HIGH and MEDIUM issues fixed, all ACs implemented

### Issues Found: 10 (3 HIGH, 4 MEDIUM, 3 LOW)

| # | Sev | Issue | Fix Applied |
|---|-----|-------|-------------|
| H1 | HIGH | N+1 query: `followers.count()` / `following.count()` per ogni utente nella lista | `get_queryset()` con `Count` annotations + `distinct=True`; serializer usa `getattr(obj, 'annotated_*', fallback)` |
| H2 | HIGH | Nessun error handling per utente non trovato nella pagina profilo | Aggiunto `isError` da `useUserByUsername` + `EmptyState` con icona `UserX` |
| H3 | HIGH | Type mismatch: `User` TS ha `first_name`/`last_name` non presenti nel serializer; `email` sempre visibile | Rimossi `first_name`/`last_name`; `email` reso opzionale (`email?: string`); serializer nasconde email per non-proprietari |
| M1 | MEDIUM | `user-search-bar.tsx` non documentato nel File List della story | Aggiunto al File List (non modificato in questa story ma usato dal flusso) |
| M2 | MEDIUM | Email esposta a tutti gli utenti nel serializer | Aggiunto `to_representation()` che poppa `email` per utenti non autenticati o non proprietari |
| M3 | MEDIUM | `isFollowing` calcolato con `profileUser.followers.includes(currentUser.id)` — non scala | Aggiunto `is_followed_by_me` SerializerMethodField con caching `_following_ids`; frontend usa `profileUser.is_followed_by_me` |
| M4 | MEDIUM | `update()` e `partial_update()` override causano doppia chiamata `get_object()` | Sostituiti con singolo `perform_update()` che riceve già `serializer.instance` |
| L1 | LOW | `staleTime` inconsistente: `useUser` 1min vs `useUserByUsername` 5min | Allineato `useUser` a `5 * 60_000` |
| L2 | LOW | Convenzione `by_username` vs `by-username` | Non modificato — endpoint URL usa `by-username` (kebab-case), action Python usa underscore. Coerente con convenzioni REST |
| L3 | LOW | Validazione bio ridondante (model + serializer) | Non modificato — defense-in-depth accettabile per campo user-facing |

### Verification

- **Backend tests:** 58/58 passed (0 regressioni)
- **Frontend build:** OK (TypeScript strict, 0 errori)
- **ACs coverage:** AC1 ✓ AC2 ✓ AC3 ✓

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

Nessun bug critico incontrato durante l'implementazione.

### Completion Notes List

- Migration `0017_user_bio` creata e applicata senza conflitti
- `UserProfileUpdateSerializer` valida max 500 char sia tramite `TextField(max_length=500)` del modello che tramite `validate_bio()` custom
- `update()` e `partial_update()` override nel ViewSet per check ownership (`request.user.id != obj.id` → 403)
- `by-username` action usa `User.objects.get()` con gestione `DoesNotExist` → `NotFound` con messaggio italiano
- Workaround inefficiente (getAll + filter) rimosso dalla pagina profilo, sostituito con `useUserByUsername` → `GET /api/users/by-username/{username}/`
- ProfileEditForm: inline nella pagina, non Dialog, per UX più semplice. Toast Sonner per conferma/errore
- `followers` e `following` (array ID) mantenuti per backward compatibility (`FollowButton` li usa per `isFollowing` check)
- 58 test totali (8 nuovi per profilo), 0 regressioni
- Frontend build OK con TypeScript strict

### File List

**Backend (modificati):**
- `backend/cs_clips/models.py` — aggiunto campo `bio` a User
- `backend/cs_clips/serializers.py` — aggiunto `bio`, `followers_count`, `following_count`, `is_followed_by_me` a `UserSerializer`; `to_representation()` per privacy email; creato `UserProfileUpdateSerializer` _(review: H3, M2, M3)_
- `backend/cs_clips/views.py` — `get_queryset()` con Count annotations; `perform_update()` (sostituisce update/partial_update); action `by-username` con `get_serializer()`; `get_followers`/`get_following` con `get_serializer()` _(review: H1, M4)_
- `backend/cs_clips/tests/test_views.py` — aggiunta classe `UserProfileTest` con 8 test
- `backend/cs_clips/migrations/0017_user_bio.py` — migration auto-generata

**Frontend (modificati):**
- `frontend/src/types/user.ts` — aggiunto `bio`, `followers_count`, `following_count`, `is_followed_by_me`; rimossi `first_name`/`last_name`; `email` opzionale _(review: H3)_
- `frontend/src/lib/api/users.ts` — aggiunto `getByUsername()`, `updateProfile()`
- `frontend/src/lib/query-keys.ts` — aggiunto `users.byUsername`
- `frontend/src/lib/hooks/use-users.ts` — aggiunto `useUserByUsername()`, `useUpdateProfile()`; `useUser` staleTime allineato a 5min _(review: L1)_
- `frontend/src/components/user/profile-header.tsx` — bio display, conteggi da serializer, bottone modifica, conteggio clip; `isFollowing` via `is_followed_by_me` _(review: M3)_
- `frontend/src/components/user/user-search-bar.tsx` — non modificato in questa story (esistente da Story 1-9, usato nel flusso profilo)
- `frontend/src/app/(main)/profilo/[username]/page.tsx` — rimosso workaround, usa `useUserByUsername`; error state con `EmptyState` + `UserX` _(review: H2)_

**Frontend (creati):**
- `frontend/src/components/user/profile-edit-form.tsx` — form modifica bio inline con Textarea, contatore, toast, loading state
