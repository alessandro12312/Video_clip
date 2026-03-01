# Story 1.2: Registrazione Utente

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utente non registrato,
I want creare un account con username, email e password,
so that possa accedere alla piattaforma e interagire con la community.

## Acceptance Criteria

1. **AC1 — Registrazione con successo e autenticazione JWT**
   Given: un utente non registrato sulla pagina `/registrati`
   When: compila username, email e password e invia il form
   Then: l'account viene creato e l'utente viene autenticato con JWT
   AND: l'utente viene reindirizzato alla Home (`/home`)

2. **AC2 — Errore duplicato username/email**
   Given: un utente che inserisce un username o email già esistente
   When: invia il form di registrazione
   Then: viene mostrato un errore specifico ("Username già in uso" o "Email già registrata")

3. **AC3 — Validazione password debole**
   Given: un utente che inserisce una password troppo corta o debole
   When: invia il form
   Then: viene mostrato un errore di validazione con requisiti minimi

## Tasks / Subtasks

> **NOTA:** Il codice di registrazione esiste già nel codebase (backend + frontend).
> Questa story documenta lo stato attuale, identifica gap rispetto agli AC,
> e definisce il lavoro residuo necessario per la review formale.

### Codice esistente (già implementato)

- [x] Backend: `UserRegistrationSerializer` in `backend/cs_clips/serializers.py` (AC: #1)
- [x] Backend: `UserViewSet.create()` con `AllowAny` in `backend/cs_clips/views.py` (AC: #1)
- [x] Backend: Assegnazione automatica gruppo utente in `perform_create()` (AC: #1)
- [x] Backend: JWT tokens via SimpleJWT (`/api/token/`, `/api/token/refresh/`) (AC: #1)
- [x] Frontend: Pagina registrazione `frontend/src/app/(auth)/registrati/page.tsx` (AC: #1)
- [x] Frontend: `authApi.register()` in `frontend/src/lib/api/auth.ts` (AC: #1)
- [x] Frontend: `AuthProvider.register()` con auto-login post-registrazione (AC: #1)
- [x] Frontend: Gestione errori AxiosError con messaggi specifici (AC: #2)
- [x] Frontend: Redirect a `/home` dopo registrazione riuscita (AC: #1)

### Lavoro residuo da completare

- [x] Task 1: Verificare e correggere il gruppo assegnato ai nuovi utenti (AC: #1)
  - [x] 1.1 — Controllare se `perform_create()` assegna `'user'` o `'toconfirm'` e allineare con il project-context (regola: nuovi utenti → `toconfirm`)
  - [x] 1.2 — Se necessario, aggiornare `perform_create()` per assegnare `'toconfirm'` invece di `'user'`
- [x] Task 2: Migliorare la validazione e i messaggi di errore backend (AC: #2, #3)
  - [x] 2.1 — Verificare che errori duplicato username/email restituiscano messaggi italiani specifici (non generici Django)
  - [x] 2.2 — Aggiungere validazione password nel serializer con messaggio italiano per requisiti minimi
  - [x] 2.3 — Verificare che `handle_exception()` sia implementato nel `UserViewSet` (pattern progetto)
- [x] Task 3: Migliorare il form frontend (AC: #3)
  - [x] 3.1 — Aggiungere indicazione requisiti minimi password visibile nel form (es. "Minimo 8 caratteri")
  - [x] 3.2 — Verificare accessibilità WCAG 2.1 AA: label, aria-describedby, focus management
  - [x] 3.3 — Verificare che il `GradientSpinner` sia usato durante il caricamento (design system)
- [x] Task 4: Scrivere test dedicati per la registrazione (AC: #1, #2, #3)
  - [x] 4.1 — Test registrazione con successo: crea utente, assegna gruppo, restituisce 201
  - [x] 4.2 — Test duplicato username: restituisce 400 con messaggio specifico
  - [x] 4.3 — Test duplicato email: restituisce 400 con messaggio specifico
  - [x] 4.4 — Test password debole: restituisce 400 con requisiti minimi
  - [x] 4.5 — Test campi mancanti: restituisce 400 per ciascun campo obbligatorio
- [x] Task 5: Verificare integrazione end-to-end (AC: #1)
  - [x] 5.1 — Verificare flusso completo: form → API → JWT → redirect `/home`
  - [x] 5.2 — Verificare che il token refresh funzioni dopo registrazione

## Dev Notes

### Stato attuale del codice

Il flusso di registrazione è funzionante end-to-end:
1. Frontend: form 3 campi (username, email, password) → `authApi.register()`
2. Backend: `POST /api/users/` → crea utente, assegna gruppo
3. Frontend: auto-login via `POST /api/token/` → salva JWT tokens
4. Frontend: redirect a `/home`

### Pattern architetturali da rispettare

| Pattern | Dettaglio | Source |
|---------|-----------|--------|
| Error handling | `handle_exception_with_serializer(exc)` in ogni ViewSet | [Source: project-context.md#Error-Handling-Centralizzato] |
| User model | `get_user_model()`, MAI import diretto | [Source: project-context.md#Custom-User-Model] |
| Lingua messaggi | Italiano per messaggi utente/help_text, inglese per codice | [Source: project-context.md#Lingua] |
| Validazione business | Nel serializer `validate()`, NON nella view | [Source: project-context.md#Pattern-Serializer] |
| Gruppi utente | Via migration, NON solo `get_or_create()` runtime | [Source: project-context.md#Anti-Pattern] |
| Password | `create_user()` per hash, MAI password in chiaro | [Source: project-context.md#Sicurezza] |
| Test API | `APITestCase` + `APIClient`, `force_authenticate()` per JWT | [Source: project-context.md#Regole-Testing] |

### Discrepanza critica: gruppo utente assegnato

Il `project-context.md` specifica:
> "Nuovi utenti → gruppo `toconfirm` automaticamente in `perform_create()`"

Ma il codice attuale in `views.py` assegna il gruppo `'user'`:
```python
group, created = Group.objects.get_or_create(name='user')
user.groups.add(group)
```

**Decisione necessaria:** Verificare se questa discrepanza è intenzionale (story 1-1 potrebbe averla cambiata deliberatamente) o se va corretta.

### File coinvolti

| File | Ruolo | Stato |
|------|-------|-------|
| `backend/cs_clips/serializers.py` | `UserRegistrationSerializer` | Esistente — verificare validazione password |
| `backend/cs_clips/views.py` | `UserViewSet.perform_create()` | Esistente — verificare gruppo assegnato |
| `frontend/src/app/(auth)/registrati/page.tsx` | Pagina registrazione | Esistente — verificare UX/accessibilità |
| `frontend/src/lib/api/auth.ts` | `authApi.register()` | Esistente — OK |
| `frontend/src/providers/auth-provider.tsx` | `register()` con auto-login | Esistente — OK |
| `backend/cs_clips/tests/test_views.py` | Test registrazione | **DA CREARE** |

### Stack tecnologico rilevante

- **Backend:** Django 5.1.6, DRF 3.15.1, SimpleJWT 5.3.1
- **Frontend:** Next.js 16.1.6, React 19, TypeScript 5, Axios
- **UI:** TailwindCSS 4, shadcn/ui (Radix), Framer Motion 12, Lucide React
- **Database:** PostgreSQL 16 (Docker), psycopg 3.2.4
- **Auth:** JWT (access 12h memory-only, refresh 1d localStorage, rotate=True)

### Lezioni dalla Story 1-1

- 34 test creati (14 model + 20 endpoint) — usare stesso pattern per test registrazione
- `handle_exception()` deve delegare a `handle_exception_with_serializer(exc)`
- Verificare che ogni ViewSet abbia `permission_classes` esplicito
- `related_name` sempre specificato nelle ForeignKey
- Pattern naming: help_text/messaggi in italiano, codice in inglese

### Validazione password Django configurata

`AUTH_PASSWORD_VALIDATORS` in `settings.py`:
- `UserAttributeSimilarityValidator` — password troppo simile a username/email
- `MinimumLengthValidator` — minimo 8 caratteri (default Django)
- `CommonPasswordValidator` — password troppo comune
- `NumericPasswordValidator` — password interamente numerica

Questi validator sono attivi lato backend ma il frontend non mostra i requisiti all'utente prima dell'invio.

### Design requirements (UX)

- Dark mode come default
- Form semplice: max 3 campi (username, email, password)
- Messaggi errore specifici, MAI generici
- Accessibilità: WCAG 2.1 AA, label su form, focus management
- Emotion target: velocità + familiarità ("Facile come Instagram")
- `GradientSpinner` durante loading

### Project Structure Notes

- La struttura del codice è conforme all'architettura documentata
- Route auth: `app/(auth)/registrati/page.tsx` — corretto
- API client: `lib/api/auth.ts` + `lib/api/client.ts` — corretto
- Provider: `providers/auth-provider.tsx` — corretto
- Nessun conflitto o varianza rilevata

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic-1-Story-1.2]
- [Source: _bmad-output/planning-artifacts/prd.md#FR1]
- [Source: _bmad-output/planning-artifacts/architecture.md#Authentication-Flow]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Form-Design]
- [Source: _bmad-output/project-context.md#Autenticazione-JWT]
- [Source: _bmad-output/implementation-artifacts/1-1-evoluzione-backend-migration-prd-alignment.md#Dev-Notes]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Prima esecuzione test: 7/10 falliti per incompatibilità con `handle_exception_with_serializer()` che trasforma le risposte di validazione in formato `{code, detail}` anziché il formato standard DRF `{field: [errors]}`. Risolto adattando le asserzioni dei test al formato progetto.
- `UniqueValidator` auto-generato da `ModelSerializer` intercettava duplicati prima dei custom `validate_*()` con messaggi in inglese. Risolto dichiarando esplicitamente i campi `username` e `email` con `UniqueValidator` custom e `lookup='iexact'`.

### Completion Notes List

- ✅ Task 1: Corretto `perform_create()` — gruppo assegnato cambiato da `'user'` a `'toconfirm'` come da project-context
- ✅ Task 2: `UserRegistrationSerializer` migliorato con `UniqueValidator` per username (case-insensitive) e email con messaggi italiani, validazione password via `django.contrib.auth.password_validation`. `handle_exception()` già presente nel `UserViewSet` (riga 173)
- ✅ Task 3: Aggiunto hint requisiti password (`aria-describedby` + testo), `role="alert"` sul messaggio errore. `GradientSpinner` già usato, `Label` con `htmlFor` già corretti
- ✅ Task 4: 12 test creati (10 unit + 2 integrazione): registrazione successo con gruppo, duplicato username/email, password debole/numerica, campi mancanti, password non in risposta, case-insensitive, flusso JWT completo, token refresh
- ✅ Task 5: Test integrazione verificano flusso end-to-end: registrazione → login JWT → accesso autenticato → refresh token

### Change Log

- 2026-02-15: Implementazione Story 1-2 — Corretta assegnazione gruppo utente (toconfirm), migliorata validazione registrazione con messaggi italiani e validazione password Django, migliorato form frontend con hint password e accessibilità WCAG, 12 test aggiunti (50 totali, 0 regressioni)
- 2026-02-15: Code Review (AI) — 4 fix applicati: (H1) frontend error handler ora usa `data.detail` invece di esporre codice interno, (H2) `validate_password` spostato in `validate()` con user temporaneo per abilitare `UserAttributeSimilarityValidator`, (M1) aggiunto test email duplicata case-insensitive, (M2) hint password aggiornato con "non troppo comune". 51 test totali, 0 regressioni

### File List

- `backend/cs_clips/views.py` — Modificato: `perform_create()` assegna `'toconfirm'` invece di `'user'`
- `backend/cs_clips/serializers.py` — Modificato: `UserRegistrationSerializer` con UniqueValidator italiano, validazione password, import UniqueValidator
- `backend/cs_clips/tests/test_views.py` — Modificato: aggiunte classi `UserRegistrationEndpointTest` (10 test) e `UserRegistrationIntegrationTest` (2 test)
- `frontend/src/app/(auth)/registrati/page.tsx` — Modificato: hint requisiti password con `aria-describedby`, `role="alert"` su errore
