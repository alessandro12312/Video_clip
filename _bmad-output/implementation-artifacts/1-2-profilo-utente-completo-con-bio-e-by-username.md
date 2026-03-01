# Story 1.2: Profilo Utente Completo con Bio e By-Username

Status: done

<!-- Validation: opzionale. Esegui validate-create-story per quality check prima di dev-story. -->

## Story

As a utente registrato,
I want visualizzare e modificare il mio profilo con bio, e visitare profili altrui via username,
so that la mia identità sulla piattaforma è completa e posso scoprire altri utenti.

## Acceptance Criteria (BDD)

### AC-1: Endpoint by-username con campi calcolati (FR53, FR3)

```gherkin
Scenario: Recupero profilo per username esistente
  Given un utente autenticato
  When chiama GET /api/users/by-username/{username}/
  Then riceve status 200 con il profilo dell'utente
  And la risposta contiene: id, username, email, bio, created_at, updated_at
  And la risposta contiene followers_count (intero, annotation Count distinct)
  And la risposta contiene following_count (intero, annotation Count distinct)
  And la risposta contiene is_followed_by_me (booleano, True se request.user segue questo utente)
  And la risposta contiene followers (array di ID) e following (array di ID)

Scenario: Username inesistente
  Given un utente autenticato
  When chiama GET /api/users/by-username/{username_inesistente}/
  Then riceve errore 404 con formato {code, detail}

Scenario: Utente non autenticato accede a by-username
  Given un utente non autenticato
  When chiama GET /api/users/by-username/{username}/
  Then riceve errore 401
```

### AC-2: Campo bio nel modello User (FR3)

```gherkin
Scenario: Migrazione campo bio
  Given il modello User senza campo bio
  When viene eseguita la migrazione
  Then il campo bio è un TextField opzionale (blank=True, default='')
  And il campo ha help_text in italiano
  And la max_length NON è nel modello (TextField non la supporta a DB level) — la validazione è nel serializer

Scenario: Modifica bio dal proprio profilo
  Given un utente autenticato con gruppo "user"
  When invia PATCH /api/users/{proprio_id}/ con {bio: "Ciao, amo i video!"}
  Then il campo bio viene aggiornato
  And la risposta contiene il profilo aggiornato con bio
  And i campi calcolati (followers_count, following_count, is_followed_by_me) sono presenti

Scenario: Bio troppo lunga
  Given un utente autenticato
  When invia PATCH /api/users/{id}/ con bio di 501+ caratteri
  Then riceve errore 400 con messaggio di validazione in italiano

Scenario: Bio vuota (reset)
  Given un utente con bio esistente
  When invia PATCH /api/users/{id}/ con {bio: ""}
  Then il campo bio viene svuotato
```

### AC-3: Campi calcolati nel UserSerializer (FR3, FR53)

```gherkin
Scenario: GET /api/users/{id}/ include campi calcolati
  Given un utente autenticato
  When chiama GET /api/users/{id}/
  Then la risposta include followers_count, following_count, is_followed_by_me, bio
  And i contatori sono calcolati via Count() annotation con distinct=True (no N+1)
  And is_followed_by_me è calcolato via Exists() subquery (no N+1)

Scenario: is_followed_by_me corretto per utente che seguo
  Given utente A segue utente B
  When utente A chiama GET /api/users/{B.id}/
  Then is_followed_by_me è True

Scenario: is_followed_by_me corretto per utente che NON seguo
  Given utente A NON segue utente C
  When utente A chiama GET /api/users/{C.id}/
  Then is_followed_by_me è False

Scenario: is_followed_by_me per il proprio profilo
  Given utente A
  When utente A chiama GET /api/users/{A.id}/
  Then is_followed_by_me è False (non puoi seguire te stesso)
```

### AC-4: Permessi PATCH profilo

```gherkin
Scenario: Utente modifica il proprio profilo
  Given un utente con gruppo "user" e id=5
  When invia PATCH /api/users/5/ con {bio: "Nuova bio"}
  Then riceve status 200 con profilo aggiornato

Scenario: Utente tenta di modificare profilo altrui
  Given un utente con gruppo "user" e id=5
  When invia PATCH /api/users/10/ con {bio: "Hacked"}
  Then riceve errore 403 (RoleBasedPermission.has_object_permission blocca)

Scenario: Utente toconfirm tenta di modificare il profilo
  Given un utente con gruppo "toconfirm"
  When invia PATCH /api/users/{proprio_id}/ con {bio: "Test"}
  Then riceve errore 403 (toconfirm = solo SAFE_METHODS)
```

## Tasks / Subtasks

- [x] **Task 1: Aggiungere campo `bio` al modello User** (AC: #2)
  - [x] 1.1 In `backend/cs_clips/models/user.py`, aggiungere `bio = models.TextField(blank=True, default="", help_text="Biografia dell'utente")`
  - [x] 1.2 Eseguire `python manage.py makemigrations cs_clips`
  - [x] 1.3 Eseguire `python manage.py migrate`
  - [x] 1.4 Verificare che la migrazione non alteri campi esistenti

- [x] **Task 2: Aggiornare UserSerializer con bio e campi calcolati** (AC: #1, #3)
  - [x] 2.1 Aggiungere `bio` ai fields del `UserSerializer`
  - [x] 2.2 Aggiungere `followers_count = serializers.IntegerField(read_only=True)` — verrà da annotation
  - [x] 2.3 Aggiungere `following_count = serializers.IntegerField(read_only=True)` — verrà da annotation
  - [x] 2.4 Aggiungere `is_followed_by_me = serializers.BooleanField(read_only=True)` — verrà da annotation
  - [x] 2.5 Aggiungere validazione `bio` nel serializer: `MaxLengthValidator(500)` con messaggio in italiano
  - [x] 2.6 NON rimuovere `followers` e `following` (array ID) — il frontend li usa ancora in `User.followers: number[]`

- [x] **Task 3: Annotare queryset nel UserViewSet** (AC: #3)
  - [x] 3.1 Sovrascrivere `get_queryset()` nel `UserViewSet`
  - [x] 3.2 Annotare `followers_count=Count('followers', distinct=True)`
  - [x] 3.3 Annotare `following_count=Count('following', distinct=True)`
  - [x] 3.4 Annotare `is_followed_by_me` con `Exists(User.objects.filter(id=request.user.id, following=OuterRef('pk')))` — attenzione: `request.user` è anonimo per utenti non autenticati, gestire con `Value(False)` se anonimo
  - [x] 3.5 Verificare che le annotation funzionino con la paginazione globale (PageNumberPagination)

- [x] **Task 4: Creare endpoint by-username** (AC: #1)
  - [x] 4.1 Aggiungere `@action(detail=False, methods=['get'], url_path='by-username/(?P<username>[^/.]+)')` al `UserViewSet`
  - [x] 4.2 Implementare `get_by_username(self, request, username=None)`: lookup `get_object_or_404(self.get_queryset(), username=username)`
  - [x] 4.3 Serializzare con `UserSerializer` e ritornare la risposta
  - [x] 4.4 Permessi: `IsAuthenticated` (ereditato dal ViewSet) — NON `AllowAny`

- [x] **Task 5: Fix has_object_permission per PATCH profilo** (AC: #4)
  - [x] 5.1 In `RoleBasedPermission.has_object_permission()`, aggiungere caso per PATCH/PUT: l'utente `user` può modificare solo il proprio oggetto User (`obj == request.user`)
  - [x] 5.2 Il check attuale gestisce solo DELETE — estendere a tutte le operazioni di scrittura non-safe
  - [x] 5.3 **Attenzione**: il modello User NON ha campo `uploader` né `user` — il check `getattr(obj, 'uploader', None) or getattr(obj, 'user', None)` ritorna None per User. Serve `obj == request.user` specifico per istanze User

- [x] **Task 6: Scrivere test per profilo e by-username** (AC: #1, #2, #3, #4)
  - [x] 6.1 Creare `backend/cs_clips/tests/test_profile.py`
  - [x] 6.2 Test GET by-username con username valido → 200, contiene bio, followers_count, following_count, is_followed_by_me
  - [x] 6.3 Test GET by-username con username inesistente → 404
  - [x] 6.4 Test PATCH bio con valore valido → 200, bio aggiornata
  - [x] 6.5 Test PATCH bio troppo lunga → 400, messaggio in italiano
  - [x] 6.6 Test PATCH bio vuota → 200, bio svuotata
  - [x] 6.7 Test PATCH profilo altrui → 403
  - [x] 6.8 Test PATCH come toconfirm → 403
  - [x] 6.9 Test is_followed_by_me = True quando seguo l'utente
  - [x] 6.10 Test is_followed_by_me = False quando NON seguo l'utente
  - [x] 6.11 Test followers_count e following_count corretti dopo follow/unfollow
  - [x] 6.12 Ogni test crea i propri dati in `setUp()` — usare helper da `conftest.py`
  - [x] 6.13 Eseguire `ruff check backend/` e `ruff format backend/` — zero errori

- [x] **Task 7: Verificare integrazione frontend→backend** (AC: #1, #2, #3)
  - [x] 7.1 Verificare che `GET /api/users/by-username/{username}/` risponda con la shape attesa dal frontend: `User` type in `frontend/src/types/user.ts`
  - [x] 7.2 Verificare che `PATCH /api/users/{id}/` con `{bio}` funzioni per il `useUpdateProfile` hook
  - [x] 7.3 Verificare che i campi `followers_count`, `following_count`, `is_followed_by_me` siano presenti sia in `/api/users/{id}/` che in `/api/users/by-username/{username}/`
  - [x] 7.4 Verificare che la paginazione `GET /api/users/{id}/followers/` e `/following/` funzioni ancora correttamente (non deve rompersi)

## Dev Notes

### Contesto Critico

Questa story implementa il **profilo utente completo** — l'anello mancante tra il frontend (già completamente costruito) e il backend. Il frontend ha pagine profilo (`/profilo/[username]/`), form di modifica bio, contatori follower/following, e pulsante follow/unfollow che dipendono tutti da endpoint e campi che **non esistono ancora nel backend**.

Il frontend è la **specifica vivente**: ogni hook che chiama un endpoint inesistente è un requisito implicito. In particolare:
- `usersApi.getByUsername(username)` → chiama `/api/users/by-username/{username}/` che dà 404
- `profileUser.bio` → campo non presente nel serializer né nel modello
- `profileUser.followers_count` / `following_count` → non annotati, il serializer ritorna solo array ID
- `profileUser.is_followed_by_me` → non calcolato

### Stato Attuale del Codice

**Backend — Funziona già:**
- `UserViewSet` con CRUD base (list, create, retrieve, update, partial_update, destroy)
- `follow/unfollow` actions con messaggi in italiano
- `get_followers/get_following` actions (ma ritornano array piatti, NON paginati — fix sarà in Story 1.3)
- `UserSerializer` con fields: id, username, email, created_at, updated_at, followers, following
- `UserRegistrationSerializer` con validazione password + traduzione italiana
- `RoleBasedPermission` con check gruppi (toconfirm=read-only, user=CRUD, admin=tutto)
- Auth JWT completo (Story 1.1): token blacklist, refresh rotation, errori in italiano

**Backend — Da aggiungere (questa story):**
- Campo `bio` nel modello User (migrazione)
- `bio` nel `UserSerializer` con validazione max 500 caratteri
- `followers_count`, `following_count`, `is_followed_by_me` come campi annotati
- Endpoint `by-username` come `@action` nel ViewSet
- Fix `has_object_permission` per PATCH profilo utente
- Test profilo completi

**Frontend — Già pronto (NON modificare):**
- `ProfileHeader` mostra bio, followers_count, following_count, is_followed_by_me, pulsante follow
- `ProfileEditForm` permette editing bio con submit via `useUpdateProfile()`
- `ProfiloPage` (`/profilo/[username]/`) usa `useUserByUsername(username)` + `useUserVideos(username)`
- `useFollow`/`useUnfollow` con optimistic updates su `is_followed_by_me` e `followers_count`
- React Query keys: `["users", "username", username]` per by-username, `["users", id]` per detail

### Pattern da Seguire

**Annotation queryset (CRITICO — lezione Epic 1 N+1):**
```python
from django.db.models import Count, Exists, OuterRef, Value

def get_queryset(self):
    qs = User.objects.all().order_by("id")
    qs = qs.annotate(
        followers_count=Count('followers', distinct=True),
        following_count=Count('following', distinct=True),
    )
    if self.request.user.is_authenticated:
        qs = qs.annotate(
            is_followed_by_me=Exists(
                User.objects.filter(
                    id=self.request.user.id,
                    following=OuterRef('pk')
                )
            )
        )
    else:
        qs = qs.annotate(is_followed_by_me=Value(False))
    return qs
```

**Endpoint by-username:**
```python
@action(detail=False, methods=['get'], url_path='by-username/(?P<username>[^/.]+)')
def get_by_username(self, request, username=None):
    user = get_object_or_404(self.get_queryset(), username=username)
    serializer = self.get_serializer(user)
    return Response(serializer.data)
```

**Validazione bio nel serializer:**
```python
# In UserSerializer — NON usare MaxLengthValidator su TextField a livello modello
bio = serializers.CharField(required=False, allow_blank=True, max_length=500)
# Oppure validazione custom con messaggio italiano nel validate_bio()
```

**has_object_permission fix per User PATCH:**
```python
def has_object_permission(self, request, view, obj):
    if request.user.is_superuser:
        return True
    if request.user.groups.filter(name="user").exists():
        if request.method == "DELETE":
            owner = getattr(obj, "uploader", None) or getattr(obj, "user", None)
            return owner == request.user
        if request.method in ("PUT", "PATCH"):
            # Per modello User: l'oggetto È l'utente stesso
            if isinstance(obj, User):
                return obj == request.user
            owner = getattr(obj, "uploader", None) or getattr(obj, "user", None)
            return owner == request.user
    if request.user.groups.filter(name="toconfirm").exists():
        return request.method in SAFE_METHODS
    return False
```

**Test — usare helper da conftest.py:**
```python
from cs_clips.tests.conftest import create_authenticated_user, create_api_client_authenticated

class TestProfile(APITestCase):
    def setUp(self):
        self.user = create_authenticated_user(username="mario")
        self.client = create_api_client_authenticated(self.user)
        self.other = create_authenticated_user(username="luigi")
```

### Anti-Pattern da Evitare

- **MAI** usare `SerializerMethodField` per contatori che possono essere annotati — `Count()` è una singola query SQL, `SerializerMethodField` causa N+1
- **MAI** usare `len(user.followers.all())` — SEMPRE `Count()` annotation
- **MAI** dimenticare `distinct=True` nelle `Count()` annotation con M2M — senza distinct il count è gonfiato dai join
- **MAI** importare `from cs_clips.models.user import User` direttamente — usare `get_user_model()`
- **MAI** creare test utenti senza assegnare un gruppo — `User.groups` ha `blank=False` per policy
- **MAI** toccare il frontend — è già funzionante e aspetta questi cambiamenti
- **MAI** modificare la logica follow/unfollow — è scope della Story 1.3
- **MAI** paginare followers/following in questa story — la paginazione è scope della Story 1.3
- **MAI** rimuovere `followers` e `following` (array ID) dal serializer — il frontend li usa ancora
- **MAI** ritornare messaggi utente in inglese — regola progetto: italiano

### Bug Noti (Fuori Scope)

- `get_followers` e `get_following` ritornano array piatti (non paginati) — fix in Story 1.3
- `useUserVideos` filtra client-side — fix in Story 1.4
- `RoleBasedPermission.has_object_permission` per operazioni non-DELETE su modelli non-User — il fix in Task 5 copre solo il caso User PATCH, non il caso generico

### Informazioni Tecniche Aggiornate

- **Django 5.1.6**: `Count()` con `distinct=True` supportato su `ManyToManyField` self-referenziale. `Exists()` con `OuterRef()` è il pattern raccomandato per subquery booleane.
- **DRF 3.15.1**: `@action(detail=False, url_path='...')` supporta regex nel path. `get_object_or_404` funziona con queryset annotati.
- **Pattern annotazione**: l'annotation viene eseguita una sola volta a livello queryset — tutti gli utenti nella risposta hanno i contatori calcolati in una singola query SQL. Nessun overhead per paginazione.
- **TextField vs CharField per bio**: Django `TextField` non ha `max_length` enforcement a livello database (PostgreSQL `text` type). La validazione lunghezza è gestita nel serializer DRF con `max_length=500`. Questo è il pattern Django standard per campi testo lungo con limiti applicativi.
- **`get_user_model()` vs import diretto**: per le annotation con `Exists` + `OuterRef`, si usa `User.objects.filter(...)` dove `User = get_user_model()` all'inizio del file. Questo è coerente con il pattern già stabilito nel codebase.

### Project Structure Notes

- **Allineamento**: tutti i file toccati seguono la struttura modulare `cs_clips/api/users/`
- **File modificati**: `cs_clips/models/user.py`, `cs_clips/api/users/user_serializers.py`, `cs_clips/api/users/user_views.py`, `cs_clips/permissions.py`
- **File nuovi**: `cs_clips/tests/test_profile.py`, 1 migrazione auto-generata
- **Nessun file frontend toccato**

### Frontend Integration (Riferimento — NON Modificare)

Il frontend aspetta esattamente questa shape dall'API (da `frontend/src/types/user.ts`):
```typescript
interface User {
  id: number;
  username: string;
  email?: string;
  bio: string;
  created_at: string;
  updated_at: string;
  followers: number[];
  following: number[];
  followers_count: number;
  following_count: number;
  is_followed_by_me: boolean;
}
```

**Endpoint chiamati dal frontend:**
- `GET /api/users/by-username/{username}/` → `usersApi.getByUsername()` — **DA CREARE**
- `PATCH /api/users/{id}/` con `{bio?: string}` → `usersApi.updateProfile()` — **DA AGGIORNARE (aggiungere bio)**
- `GET /api/users/{id}/` → `usersApi.getById()` — **DA AGGIORNARE (aggiungere campi calcolati)**

**React Query keys usati:**
- `["users", "username", username]` per by-username
- `["users", userId]` per detail by ID
- `["users", userId, "followers"]` per followers list
- `["users", userId, "following"]` per following list

**Optimistic updates (useFollow/useUnfollow):**
- Aggiornano `is_followed_by_me` e `followers_count` su entrambi i query keys (byUsername e detail)
- OnSettled invalida entrambi i keys + followers list + following list dell'utente corrente

### Intelligence dalla Story 1.1 (Precedente)

**Pattern stabiliti da riusare:**
- `get_user_model()` ovunque — MAI import diretto
- `translation_override("it")` per messaggi validazione in italiano
- `run_validation()` override per forzare locale italiano su TUTTI i messaggi (non solo custom)
- Test con `APITestCase`, `force_authenticate`, helper da `conftest.py`
- Formato errori: `{code, detail}` dal global exception handler

**Problemi incontrati e risolti:**
- `AuthenticationFailed` vs `serializers.ValidationError`: usare `AuthenticationFailed` per errori auth (mantiene 401), `ValidationError` per validazione input (400)
- Test con asserzioni precise: `assertEqual(status, 401)` non `assertGreaterEqual(status, 400)`
- Test messaggio in italiano: `assertIn("keyword_italiano", response.data["detail"])`

**Code review feedback applicato:**
- Tutti i messaggi di validazione devono essere in italiano (non solo i custom)
- Test devono asserire sul contenuto del messaggio, non solo sullo status code
- `get_user_model()` ovunque, mai import diretto

### Git Intelligence

**Ultimi commit (pattern recenti):**
- `4f42b36` — Epic 0 retrospettiva
- `ca75ed4` — Story 0-3 + Story 0-4: testing baseline, CI/CD, Django Admin
- `f68fa2c` — Story 0-2: linting, formatting, developer tools
- `b2bfa77` — Story 0-1: bug fix settings, permissions, pulizia dipendenze

**Insight rilevanti:**
- `b2bfa77` ha fixato `RoleBasedPermission.has_object_permission` aggiungendo `getattr(obj, 'uploader', None) or getattr(obj, 'user', None)` — ma il fix non copre il caso PATCH su User (dove obj È l'utente)
- `ca75ed4` ha creato `conftest.py` con 5 helper functions — riusarle nei test
- Ruff è configurato e attivo — eseguire `ruff check` e `ruff format` prima del commit

### References

- [Source: _bmad-output/planning-artifacts/epics.md — Epic 1, Story 1.2]
- [Source: _bmad-output/planning-artifacts/architecture.md — Gap Backend, Cross-Cutting Concerns 1-4, 13]
- [Source: _bmad-output/implementation-artifacts/1-1-registrazione-e-login-end-to-end.md — Pattern e anti-pattern]
- [Source: backend/cs_clips/models/user.py — User model (missing bio)]
- [Source: backend/cs_clips/api/users/user_serializers.py — UserSerializer, UserRegistrationSerializer]
- [Source: backend/cs_clips/api/users/user_views.py — UserViewSet, follow/unfollow actions]
- [Source: backend/cs_clips/permissions.py — RoleBasedPermission, has_object_permission]
- [Source: backend/cs_clips/tests/conftest.py — Helper functions]
- [Source: frontend/src/types/user.ts — User interface (shape attesa)]
- [Source: frontend/src/lib/api/users.ts — usersApi.getByUsername, updateProfile]
- [Source: frontend/src/lib/hooks/use-users.ts — useUserByUsername, useFollow, useUnfollow, useUpdateProfile]
- [Source: frontend/src/components/user/profile-header.tsx — ProfileHeader (consuma bio, followers_count, is_followed_by_me)]
- [Source: frontend/src/app/(main)/profilo/[username]/page.tsx — ProfiloPage (usa useUserByUsername)]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Migrazione `0004_add_bio_to_user`: la colonna `bio` esisteva già nel DB (tentativo precedente), risolta con `--fake`
- Fix preventivo su `get_followers`/`get_following`: le actions usavano queryset raw senza annotazioni → aggiornate per usare `self.get_queryset()` filtrato, evitando errori di serializzazione sui nuovi campi calcolati

### Completion Notes List

- ✅ Task 1: Campo `bio` aggiunto al modello User con migrazione `0004_add_bio_to_user`
- ✅ Task 2: `UserSerializer` aggiornato con `bio` (CharField max_length=500), `followers_count`, `following_count`, `is_followed_by_me` come campi read-only, e `run_validation()` con traduzione italiana
- ✅ Task 3: `get_queryset()` in UserViewSet con annotazioni `Count('followers', distinct=True)`, `Count('following', distinct=True)`, `Exists()` subquery per `is_followed_by_me`, gestione utente anonimo con `Value(False)`
- ✅ Task 4: Endpoint `GET /api/users/by-username/{username}/` creato come `@action(detail=False)` con `get_object_or_404` su queryset annotato
- ✅ Task 5: `RoleBasedPermission.has_object_permission()` riscritto: utenti `user` hanno accesso SAFE + ownership check per scrittura, con `isinstance(obj, User)` per il caso specifico PATCH profilo
- ✅ Task 6: 14 test creati in `test_profile.py` — by-username (3 test), bio CRUD (3 test), permessi (3 test), is_followed_by_me (3 test), contatori (2 test). Tutti passano. Ruff: zero errori
- ✅ Task 7: Shape API verificata contro frontend `User` type — 100% compatibile. Fix preventivo su `get_followers`/`get_following` per usare queryset annotato

### Change Log

- 2026-03-01: Implementazione completa Story 1.2 — profilo utente con bio, endpoint by-username, campi calcolati, permessi PATCH, 14 test
- 2026-03-01: **Code Review (AI)** — 7 issue trovati (2H, 3M, 2L), tutti fixati:
  - H1: `following`/`username`/`email` scrivibili via PATCH → aggiunti a read_only_fields
  - H2: test bio troppo lunga non verificava messaggio italiano → aggiunta assertion
  - M1: 3 file non documentati (scope Story 1.1) → aggiunti al File List
  - M2: test non usavano helper conftest.py → refactored
  - M3: test 404 non verificava formato {code, detail} → aggiunta assertion
  - L1: @extend_schema misleading su get_followers/get_following → rimossi
  - L2: campi annotati senza default → aggiunti default=0/False

### File List

- `backend/cs_clips/models/user.py` — aggiunto campo `bio`
- `backend/cs_clips/api/users/user_serializers.py` — aggiornato UserSerializer con bio, followers_count, following_count, is_followed_by_me, run_validation italiano, read_only_fields per sicurezza
- `backend/cs_clips/api/users/user_views.py` — aggiunto `get_queryset()` con annotazioni, endpoint `get_by_username`, fix `get_followers`/`get_following` per usare queryset annotato, rimosso @extend_schema misleading
- `backend/cs_clips/permissions.py` — riscritto `has_object_permission()` per supportare SAFE_METHODS, PATCH/PUT/DELETE su User e altri modelli
- `backend/cs_clips/migrations/0004_add_bio_to_user.py` — migrazione AddField bio
- `backend/cs_clips/tests/test_profile.py` — **NUOVO** — 14 test per profilo, by-username, bio, permessi, campi calcolati (usa helper conftest.py)
- `backend/cs_clips/tests/test_auth.py` — **RISCRITTO** (scope Story 1.1) — da 3 a 13 test, copertura AC completa auth flow
- `backend/project_clip/settings.py` — **MODIFICATO** (scope Story 1.1) — token_blacklist, BLACKLIST_AFTER_ROTATION
- `backend/project_clip/urls.py` — **MODIFICATO** (scope Story 1.1) — CustomTokenRefreshView
