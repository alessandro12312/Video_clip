# Story 1.3: Follow, Unfollow e Liste Paginate

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utente registrato,
I want seguire e smettere di seguire altri utenti e vedere le liste follower/following,
so that posso costruire il mio network e scoprire chi mi segue.

## Acceptance Criteria (BDD)

### AC-1: Follow di un altro utente (FR4)

```gherkin
Scenario: Follow riuscito
  Given un utente autenticato con gruppo "user"
  When chiama POST /api/users/{id}/follow/
  Then l'utente target viene aggiunto ai following
  And la risposta status 200 contiene {detail: "Ora segui {username}.", is_followed: true, followers_count: <contatore aggiornato>}

Scenario: Follow con risposta arricchita per optimistic update
  Given il frontend esegue optimistic update su is_followed_by_me e followers_count
  When la risposta di follow arriva
  Then contiene is_followed (booleano) e followers_count (intero) per confermare/correggere lo stato ottimistico
```

### AC-2: Unfollow di un utente seguito (FR5)

```gherkin
Scenario: Unfollow riuscito
  Given un utente autenticato che segue un altro utente
  When chiama POST /api/users/{id}/unfollow/
  Then l'utente target viene rimosso dai following
  And la risposta status 200 contiene {detail: "Hai smesso di seguire {username}.", is_followed: false, followers_count: <contatore aggiornato>}

Scenario: Unfollow di utente non seguito
  Given un utente autenticato che NON segue l'utente target
  When chiama POST /api/users/{id}/unfollow/
  Then la rimozione è idempotente (M2M .remove() non genera errore)
  And la risposta contiene {detail: "Hai smesso di seguire {username}.", is_followed: false, followers_count: <contatore invariato>}
```

### AC-3: Liste followers e following paginate (FR6)

```gherkin
Scenario: Lista followers paginata
  Given un utente autenticato
  When chiama GET /api/users/{id}/followers/
  Then riceve risposta paginata {count, next, previous, results}
  And results contiene oggetti User completi (id, username, bio, followers_count, following_count, is_followed_by_me)
  And NON un array piatto (fix della paginazione attuale)
  And usa self.paginate_queryset() + self.get_paginated_response() nelle custom actions

Scenario: Lista following paginata
  Given un utente autenticato
  When chiama GET /api/users/{id}/following/
  Then riceve risposta paginata {count, next, previous, results}
  And results contiene oggetti User completi con campi calcolati

Scenario: Lista followers paginata con pagina 2
  Given un utente con 15 follower (page_size=10)
  When chiama GET /api/users/{id}/followers/?page=2
  Then riceve {count: 15, next: null, previous: "...?page=1", results: [5 utenti]}

Scenario: Lista followers vuota
  Given un utente senza follower
  When chiama GET /api/users/{id}/followers/
  Then riceve {count: 0, next: null, previous: null, results: []}

Scenario: Lista following vuota
  Given un utente che non segue nessuno
  When chiama GET /api/users/{id}/following/
  Then riceve {count: 0, next: null, previous: null, results: []}
```

### AC-4: Protezione self-follow (validazione)

```gherkin
Scenario: Utente tenta di seguire sé stesso
  Given un utente autenticato con id=5
  When chiama POST /api/users/5/follow/
  Then riceve errore 400 con {detail: "Non puoi seguire te stesso."}

Scenario: Permessi follow/unfollow
  Given un utente con gruppo "toconfirm"
  When tenta POST /api/users/{id}/follow/ o /unfollow/
  Then riceve errore 403 (OnlyUsersPermission blocca)
```

## Tasks / Subtasks

- [x] **Task 1: Fix risposta follow con campi arricchiti** (AC: #1)
  - [x] 1.1 In `backend/cs_clips/api/users/user_views.py`, modificare `follow()`: dopo `request.user.following.add(target_user)`, calcolare `followers_count` aggiornato dell'utente target via `target_user.followers.count()`
  - [x] 1.2 Aggiornare la risposta da `{detail}` a `{detail, is_followed: True, followers_count: <count>}`
  - [x] 1.3 Aggiornare il messaggio detail da "Hai iniziato a seguire" a "Ora segui" per allineamento con l'epics

- [x] **Task 2: Fix risposta unfollow con campi arricchiti** (AC: #2)
  - [x] 2.1 In `user_views.py`, modificare `unfollow()`: dopo `request.user.following.remove(target_user)`, calcolare `followers_count` aggiornato
  - [x] 2.2 Aggiornare la risposta da `{detail}` a `{detail, is_followed: False, followers_count: <count>}`

- [x] **Task 3: Paginare get_followers** (AC: #3)
  - [x] 3.1 In `user_views.py`, riscrivere `get_followers()`: sostituire `target_user.followers.values_list("pk", flat=True)` con query diretta `self.get_queryset().filter(following=target_user)` — filtra utenti che hanno `target_user` nel loro campo `following` (cioè i follower del target)
  - [x] 3.2 Aggiungere paginazione: `page = self.paginate_queryset(followers)` → `if page is not None: serializer = UserSerializer(page, many=True); return self.get_paginated_response(serializer.data)`
  - [x] 3.3 Il queryset passa per `get_queryset()` che include le annotazioni — `followers_count`, `following_count`, `is_followed_by_me` saranno presenti in ogni utente della lista

- [x] **Task 4: Paginare get_following** (AC: #3)
  - [x] 4.1 In `user_views.py`, riscrivere `get_following()`: sostituire con query diretta `self.get_queryset().filter(followers=target_user)` — filtra utenti che hanno `target_user` nel loro campo `followers` (cioè gli utenti seguiti dal target)
  - [x] 4.2 Aggiungere paginazione identica al Task 3
  - [x] 4.3 Verificare che le annotazioni funzionino correttamente sulla lista paginata

- [x] **Task 5: Scrivere test completi** (AC: #1, #2, #3, #4)
  - [x] 5.1 Creare `backend/cs_clips/tests/test_follow.py`
  - [x] 5.2 Test follow riuscito → 200, risposta contiene `detail`, `is_followed: True`, `followers_count` aggiornato
  - [x] 5.3 Test follow di sé stesso → 400, messaggio "Non puoi seguire te stesso."
  - [x] 5.4 Test follow come toconfirm → 403
  - [x] 5.5 Test follow utente inesistente → 404
  - [x] 5.6 Test unfollow riuscito → 200, risposta contiene `detail`, `is_followed: False`, `followers_count` decrementato
  - [x] 5.7 Test unfollow di utente non seguito → 200 (idempotente), `followers_count` invariato
  - [x] 5.8 Test GET followers paginato → 200, formato `{count, next, previous, results}`, results contengono User con bio, followers_count, following_count, is_followed_by_me
  - [x] 5.9 Test GET following paginato → 200, formato paginato corretto
  - [x] 5.10 Test GET followers pagina 2 (con >10 follower) → paginazione corretta
  - [x] 5.11 Test GET followers vuoti → `{count: 0, next: null, previous: null, results: []}`
  - [x] 5.12 Test GET following vuoti → risposta paginata vuota
  - [x] 5.13 Ogni test crea i propri dati in `setUp()` — usare helper da `conftest.py`
  - [x] 5.14 Eseguire `ruff check backend/` e `ruff format backend/` — zero errori

- [x] **Task 6: Verificare integrazione frontend→backend** (AC: #1, #2, #3)
  - [x] 6.1 Verificare che `POST /api/users/{id}/follow/` risponda con la shape attesa dal frontend: `{detail: string, is_followed: boolean, followers_count: number}` — corrisponde a `apiClient.post<{ detail: string; is_followed: boolean; followers_count: number }>`
  - [x] 6.2 Verificare che `GET /api/users/{id}/followers/?page=N` risponda con `PaginatedResponse<User>` — corrisponde a `{count, next, previous, results: User[]}`
  - [x] 6.3 Verificare che ogni `User` in results abbia: `id, username, bio, followers_count, following_count, is_followed_by_me` — consumati dal componente `UserListItem` che mostra avatar, username, bio troncata, e `FollowButton` (usa `is_followed_by_me`)
  - [x] 6.4 Verificare che React Query keys siano compatibili: `["users", id, "followers", page]` e `["users", id, "following", page]`
  - [x] 6.5 Verificare che la `PAGE_SIZE` frontend (10) corrisponda al `PAGE_SIZE` Django (10)

## Dev Notes

### Contesto Critico

Questa story risolve **due bug funzionali** nel backend: le risposte follow/unfollow incomplete (mancano `is_followed` e `followers_count`) e la mancanza di paginazione su `get_followers`/`get_following` (ritornano array piatti).

**Il frontend è già completamente implementato e funzionante** — pagine `/profilo/[username]/followers` e `/profilo/[username]/following` con paginazione, skeleton loading, empty state, error handling, e navigazione avanti/indietro. Il componente `UserListItem` mostra avatar, username, bio troncata, e un `FollowButton` che legge `is_followed_by_me` da ogni User nella lista.

**Le risposte attuali del backend sono insufficienti:**
- `follow()` e `unfollow()` ritornano solo `{detail: "..."}` — il frontend aspetta `{detail, is_followed, followers_count}` per confermare gli optimistic update
- `get_followers()` e `get_following()` ritornano `Response(serializer.data)` (array piatto) — il frontend aspetta `{count, next, previous, results}` (formato paginato Django)

### Stato Attuale del Codice

**Backend — Funziona già (NON modificare):**
- `UserViewSet` con CRUD, `get_queryset()` annotato con `Count('followers', distinct=True)`, `Count('following', distinct=True)`, `Exists()` per `is_followed_by_me`
- `follow` action: `@action(detail=True, methods=["post"])`, permission `OnlyUsersPermission`, check self-follow
- `unfollow` action: `@action(detail=True, methods=["post"])`, permission `OnlyUsersPermission`
- `UserSerializer` con `bio`, `followers_count`, `following_count`, `is_followed_by_me` come campi read-only
- `RoleBasedPermission` con check gruppi e ownership (riscritto in Story 1.2)
- Auth JWT completa (Story 1.1): token blacklist, refresh rotation

**Backend — Da modificare (questa story):**
- `follow()`: aggiungere `is_followed` e `followers_count` alla risposta, cambiare messaggio "Hai iniziato a seguire" → "Ora segui"
- `unfollow()`: aggiungere `is_followed` e `followers_count` alla risposta
- `get_followers()`: riscrivere query + aggiungere paginazione
- `get_following()`: riscrivere query + aggiungere paginazione
- Test: creare `test_follow.py` con copertura completa

**Frontend — Già pronto (NON modificare):**
- `FollowButton` (`follow-button.tsx`): chiama `useFollow()`/`useUnfollow()`, mostra "Segui"/"Smetti di seguire"/"Seguendo..."/"Rimuovendo..."
- `ProfileHeader` (`profile-header.tsx`): mostra contatori e link a followers/following pages
- `FollowersPage` (`profilo/[username]/followers/page.tsx`): `useFollowers(userId, page)`, paginazione con bottoni Precedente/Successivo, `UserListItem`, empty state, error handling
- `FollowingPage` (`profilo/[username]/following/page.tsx`): identica struttura con `useFollowing(userId, page)`
- `UserListItem` (`user-list-item.tsx`): mostra avatar, username, bio (troncata), `FollowButton` con `is_followed_by_me`
- `useFollowers(userId, page)`: `useQuery` con key `[...queryKeys.users.followers(userId), page]`, `enabled: userId > 0`, `staleTime: 5min`, `placeholderData: prev => prev`
- `useFollowing(userId, page)`: identica struttura
- `useFollow()`: optimistic update su `is_followed_by_me: true` e `followers_count + 1`, rollback on error, invalidate detail + byUsername + followers + following + followingAll
- `useUnfollow()`: optimistic update su `is_followed_by_me: false` e `followers_count - 1`, rollback, stesse invalidation

### Pattern da Seguire

**Paginazione nelle custom actions (CRITICO — regola project-context.md):**
```python
# In get_followers e get_following — usare SEMPRE il pattern paginato DRF
@action(detail=True, methods=["get"], url_path="followers")
def get_followers(self, request, pk=None):
    target_user = self.get_object()
    # Query diretta sulla reverse relation — NO values_list().filter()
    followers = self.get_queryset().filter(following=target_user)
    page = self.paginate_queryset(followers)
    if page is not None:
        serializer = UserSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    serializer = UserSerializer(followers, many=True)
    return Response(serializer.data)
```

**Risposta arricchita follow/unfollow:**
```python
@action(detail=True, methods=["post"], url_path="follow",
        permission_classes=[OnlyUsersPermission])
def follow(self, request, pk=None):
    target_user = self.get_object()
    if request.user == target_user:
        return Response(
            {"detail": "Non puoi seguire te stesso."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    request.user.following.add(target_user)
    return Response({
        "detail": f"Ora segui {target_user.username}.",
        "is_followed": True,
        "followers_count": target_user.followers.count(),
    })
```

**Query efficiente per followers (CRITICO — lezione N+1 da Epic 1):**
```python
# CORRETTO: query diretta sulla relazione M2M
# User.following è il campo ManyToMany con related_name='followers'
# "Chi segue target_user" = utenti che hanno target_user nel loro following
followers = self.get_queryset().filter(following=target_user)

# SBAGLIATO (N+1 — codice attuale da sostituire):
# followers = self.get_queryset().filter(
#     pk__in=target_user.followers.values_list("pk", flat=True)
# )
```

**Test — usare helper da conftest.py:**
```python
from cs_clips.tests.conftest import create_authenticated_user, create_api_client_authenticated

class TestFollow(APITestCase):
    def setUp(self):
        self.user_a = create_authenticated_user(username="alice")
        self.user_b = create_authenticated_user(username="bob")
        self.client_a = create_api_client_authenticated(self.user_a)
        self.client_b = create_api_client_authenticated(self.user_b)
```

### Anti-Pattern da Evitare

- **MAI** ritornare array piatto da get_followers/get_following — SEMPRE formato paginato Django `{count, next, previous, results}`
- **MAI** usare `target_user.followers.values_list("pk", flat=True)` per poi filtrare — usare query diretta `filter(following=target_user)`
- **MAI** usare `SerializerMethodField` o codice Python per contare followers — il queryset è già annotato con `Count()` nel `get_queryset()`
- **MAI** ritornare solo `{detail}` da follow/unfollow — il frontend aspetta anche `is_followed` e `followers_count`
- **MAI** importare `from cs_clips.models.user import User` direttamente — usare `get_user_model()`
- **MAI** creare test utenti senza assegnare un gruppo — `User.groups` ha `blank=False`
- **MAI** toccare il frontend — è già funzionante e aspetta questi cambiamenti backend
- **MAI** modificare la logica di `get_queryset()` (annotazioni) — è stata implementata e validata in Story 1.2
- **MAI** ritornare messaggi utente in inglese — regola progetto: italiano
- **MAI** modificare `UserSerializer` — i campi sono già corretti dalla Story 1.2 (bio, followers_count, following_count, is_followed_by_me, followers, following)

### Informazioni Tecniche Aggiornate

- **Django 5.1.6**: `PageNumberPagination` globale con `PAGE_SIZE=10`. Nelle custom actions di un `ModelViewSet`, `self.paginate_queryset()` usa la classe di paginazione del ViewSet. `self.get_paginated_response()` produce `{count, next, previous, results}`.
- **DRF 3.15.1**: `self.paginate_queryset(queryset)` ritorna `None` se la paginazione è disabilitata — gestire con `if page is not None`. In pratica con `PageNumberPagination` configurato globalmente, ritorna sempre una pagina.
- **ManyToMany self-referenziale**: `User.following = ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)`. Per trovare i follower di un utente X: `User.objects.filter(following=X)` (utenti il cui campo following contiene X). Per trovare chi un utente X segue: `User.objects.filter(followers=X)` (utenti il cui campo followers contiene X, equivalente a `X.following.all()`).
- **`target_user.followers.count()`**: per le risposte follow/unfollow, un singolo `COUNT(*)` SQL è accettabile — non serve l'annotazione queryset perché ritorniamo solo un intero, non un serializer User completo.
- **Idempotenza M2M**: `following.add(target)` non genera errore se la relazione esiste già, `following.remove(target)` non genera errore se la relazione non esiste. Entrambi sono idempotenti.

### Project Structure Notes

- **Allineamento**: tutti i file toccati seguono la struttura modulare `cs_clips/api/users/`
- **File modificati**: `cs_clips/api/users/user_views.py` (4 metodi: follow, unfollow, get_followers, get_following)
- **File nuovi**: `cs_clips/tests/test_follow.py`
- **Nessun file frontend toccato**
- **Nessun nuovo modello, nessuna migrazione necessaria**

### Frontend Integration (Riferimento — NON Modificare)

**Risposta follow/unfollow attesa dal frontend** (da `frontend/src/lib/api/users.ts`):
```typescript
apiClient.post<{ detail: string; is_followed: boolean; followers_count: number }>(
  `/users/${id}/follow/`
)
```

**Risposta followers/following attesa** (PaginatedResponse<User>):
```typescript
{
  count: number;
  next: string | null;
  previous: string | null;
  results: User[];  // User con id, username, bio, followers_count, following_count, is_followed_by_me
}
```

**Componenti che consumano i dati:**
- `UserListItem`: mostra `user.username`, `user.bio` (troncata), `FollowButton(isFollowing=user.is_followed_by_me)`
- `FollowersPage`/`FollowingPage`: usa `data.results.map(user => <UserListItem />)`, `data.count` per totale pagine, `data.next` per abilitare bottone "Successivo"
- `PAGE_SIZE` frontend = 10 = `PAGE_SIZE` Django = 10

**React Query keys:**
- `["users", userId, "followers", page]` per lista followers
- `["users", userId, "following", page]` per lista following
- Invalidati su onSettled di follow/unfollow (sia target followers che current user following)

### Intelligence dalla Story 1.2 (Precedente)

**Pattern stabiliti da riusare:**
- `get_user_model()` ovunque — MAI import diretto
- Test con `APITestCase`, `force_authenticate`, helper da `conftest.py` (`create_authenticated_user`, `create_api_client_authenticated`)
- Formato errori: `{code, detail}` dal global exception handler
- Annotazioni queryset: `Count('followers', distinct=True)`, `Exists()` subquery — già implementate in `get_queryset()`
- `UserSerializer` con `bio`, `followers_count`, `following_count`, `is_followed_by_me` come campi read-only — funziona correttamente con il queryset annotato

**Problemi incontrati e risolti in 1.2:**
- N+1 queries: risolto con `Count()` annotation e `distinct=True`
- `get_followers`/`get_following`: fixati per usare `self.get_queryset()` filtrato (ma senza paginazione — fix rimandato a questa story)
- `@extend_schema` misleading sui followers/following: rimossi in code review
- Test: devono asserire sul contenuto del messaggio, non solo sullo status code

**Code review feedback applicato in 1.2 da NON ripetere:**
- H1: campi scrivibili via PATCH — verificare che follow/unfollow non modifichino campi non autorizzati
- M2: test devono usare helper conftest.py (non creare utenti manualmente)
- M3: test 404 deve verificare formato `{code, detail}`

### Git Intelligence

**Ultimi commit (pattern recenti):**
- `859f0a8` — Story 1.1 + Story 1.2: auth end-to-end e profilo utente con bio
- `4f42b36` — Epic 0 retrospettiva
- `ca75ed4` — Story 0-3 + Story 0-4: testing baseline, CI/CD, Django Admin
- `f68fa2c` — Story 0-2: linting, formatting, developer tools
- `b2bfa77` — Story 0-1: bug fix settings, permissions, pulizia dipendenze

**Insight rilevanti:**
- `859f0a8` ha implementato le annotazioni queryset in UserViewSet, endpoint by-username, bio, permessi PATCH — il codice è fresco e stabile
- Le annotazioni `Count('followers', distinct=True)` e `Exists()` subquery sono già testate con 14 test in `test_profile.py`
- Il fix `get_followers`/`get_following` per usare `self.get_queryset()` è già stato applicato in Story 1.2 — rimane da aggiungere solo la paginazione
- Pattern commit: feature con formato `feat: Story X.Y — descrizione breve`

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 1, Story 1.3]
- [Source: _bmad-output/planning-artifacts/architecture.md — FR4-FR6, vincoli API paginazione]
- [Source: _bmad-output/planning-artifacts/prd.md — FR4 follow, FR5 unfollow, FR6 liste]
- [Source: _bmad-output/project-context.md — regole 106 (formato paginato), 135 (custom actions paginazione), 122 (FK proprietario), 232-233 (ruff)]
- [Source: _bmad-output/implementation-artifacts/1-2-profilo-utente-completo-con-bio-e-by-username.md — pattern queryset, anti-pattern, code review]
- [Source: backend/cs_clips/api/users/user_views.py — UserViewSet, follow/unfollow/get_followers/get_following]
- [Source: backend/cs_clips/api/users/user_serializers.py — UserSerializer con campi calcolati]
- [Source: backend/cs_clips/permissions.py — OnlyUsersPermission, RoleBasedPermission]
- [Source: backend/cs_clips/tests/conftest.py — Helper functions (5 helper)]
- [Source: backend/project_clip/settings.py — PAGE_SIZE=10, PageNumberPagination]
- [Source: frontend/src/lib/api/users.ts — follow/unfollow/getFollowers/getFollowing signatures]
- [Source: frontend/src/lib/hooks/use-users.ts — useFollow/useUnfollow (optimistic updates), useFollowers/useFollowing (paginated)]
- [Source: frontend/src/lib/query-keys.ts — queryKeys.users.followers/following]
- [Source: frontend/src/types/user.ts — User interface]
- [Source: frontend/src/components/user/follow-button.tsx — FollowButton (consuma is_followed_by_me)]
- [Source: frontend/src/components/user/user-list-item.tsx — UserListItem (consuma bio, username, is_followed_by_me)]
- [Source: frontend/src/app/(main)/profilo/[username]/followers/page.tsx — FollowersPage (paginated, uses PaginatedResponse<User>)]
- [Source: frontend/src/app/(main)/profilo/[username]/following/page.tsx — FollowingPage (paginated)]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

Nessun problema durante l'implementazione. Tutti i 16 test nuovi passati al primo tentativo. Suite completa 57 test — zero regressioni.

### Completion Notes List

- Task 1-2: Arricchite le risposte `follow()` e `unfollow()` con `is_followed` (boolean) e `followers_count` (intero). Messaggio follow aggiornato da "Hai iniziato a seguire" a "Ora segui".
- Task 3-4: Riscritta query `get_followers()` e `get_following()` con filtro diretto M2M (`filter(following=target_user)` e `filter(followers=target_user)`) — elimina il pattern N+1 `values_list("pk", flat=True)`. Aggiunta paginazione DRF completa con `self.paginate_queryset()` + `self.get_paginated_response()`.
- Task 5: Creati 16 test in `test_follow.py` coprendo: follow riuscito, self-follow 400, toconfirm 403, utente inesistente 404, follow idempotente, contatori multi-utente, unfollow riuscito, unfollow idempotente, unfollow decremento contatore, formato paginato followers/following, campi utente nei results, paginazione pagina 2 (>10 follower), liste vuote.
- Task 6: Verificata compatibilità completa frontend↔backend su tutti gli endpoint. Shape risposte, tipi TypeScript, query keys React Query, e PAGE_SIZE (10) — tutto allineato.
- Ruff check + format: zero errori su tutto il backend (47 file).

### Change Log

- 2026-03-01: Implementata Story 1.3 — follow/unfollow con risposte arricchite e liste paginate. 16 test aggiunti, 57 totali passanti.
- 2026-03-01: Code review (AI) — 7 finding (2H, 3M, 2L), tutti fixati. 6 test aggiunti (22 totali follow, 63 suite). Dettagli sotto.

### File List

- `backend/cs_clips/api/users/user_views.py` — Modificato: follow(), unfollow(), get_followers(), get_following()
- `backend/cs_clips/tests/test_follow.py` — Nuovo: 22 test per follow/unfollow/followers/following + accesso non autenticato
- `backend/cs_clips/tests/conftest.py` — Modificato: aggiunto helper `create_toconfirm_user()`
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — Modificato: status story 1-3 aggiornato

### Senior Developer Review (AI)

**Reviewer:** Claude Opus 4.6 — 2026-03-01
**Esito:** Approvato con fix applicati (7 finding, tutti risolti)

**Fix applicati:**

| ID | Sev. | Descrizione | Fix |
|----|------|-------------|-----|
| H1 | HIGH | Test 403/404 non verificano body `{code, detail}` (ripete errore review 1.2) | Aggiunte assertion `assertIn("detail", response.data)` |
| H2 | HIGH | `get_followers/get_following` usano `UserSerializer()` diretto, no context | Sostituito con `self.get_serializer()` (pattern DRF standard) |
| M1 | MED | Test `is_followed_by_me` verifica solo presenza, non valore | Aggiunti `assertFalse`/`assertTrue` con valori attesi |
| M2 | MED | Nessun test accesso non autenticato (401) | Aggiunta classe `TestFollowUnauthenticated` con 4 test |
| M3 | MED | Nessun test GET followers/following su utente inesistente (404) | Aggiunti `test_followers_nonexistent_user_returns_404` e `test_following_nonexistent_user_returns_404` |
| L1 | LOW | `status=400` raw integer in follow() | Import `from rest_framework import status`, usato `status.HTTP_400_BAD_REQUEST` |
| L2 | LOW | Creazione manuale utente toconfirm nel test | Aggiunto `create_toconfirm_user()` in conftest.py e usato nel test |

**Verifica finale:** 63 test passanti, ruff check + format zero errori (47 file).
