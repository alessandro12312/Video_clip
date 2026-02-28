# Story 0.2: Linting, Formatting e Developer Tools

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a sviluppatore,
I want linting automatico e strumenti di debug configurati,
so that il codice è consistente e posso identificare problemi (N+1 queries, cache issues) rapidamente.

## Acceptance Criteria

1. **AC-1 (D5 — ruff config):** `pyproject.toml` nella directory `backend/` contiene configurazione ruff allineata alle regole di `project-context.md` — line-length 88, target Python 3.10, rule sets E/F/I/DJ/UP, quote-style double, indent-style space, isort con `known-third-party` per Django/DRF.
2. **AC-2 (D5 — ruff clean):** `ruff check backend/` e `ruff format --check backend/` passano con **0 errori** su tutto il codebase backend. Tutti i file Python esistenti sono stati corretti (auto-fix dove possibile, manuale dove necessario).
3. **AC-3 (.editorconfig):** `.editorconfig` alla root del progetto definisce: `indent_style = space`, `indent_size = 4` per Python, `indent_size = 2` per JS/TS/JSON/YAML, `end_of_line = lf`, `charset = utf-8`, `trim_trailing_whitespace = true`, `insert_final_newline = true`.
4. **AC-4 (Debug Toolbar):** `django-debug-toolbar` e' installato in `requirements.txt` e attivo SOLO quando `DEBUG=True` — aggiunto a `INSTALLED_APPS`, `MIDDLEWARE`, `INTERNAL_IPS`, e URL pattern `__debug__/` in `urls.py`. Visibilita' su query SQL, N+1 detection, cache hits.
5. **AC-5 (React Query DevTools):** `ReactQueryDevtools` e' importato e renderizzato nel `QueryProvider` (`query-provider.tsx`). La dipendenza `@tanstack/react-query-devtools` e' gia' inclusa nel pacchetto `@tanstack/react-query` — serve solo l'import e il componente.
6. **AC-6 (D6 — Rate Limiting):** `REST_FRAMEWORK` in `settings.py` include `DEFAULT_THROTTLE_CLASSES` e `DEFAULT_THROTTLE_RATES`: `anon: 100/hour`, `user: 2000/hour`. Un `ScopedRateThrottle` con scope `upload` a `10/hour` e' applicato su `VideoViewSet` per l'azione di upload.

## Tasks / Subtasks

- [x] Task 1 — Configurazione ruff in `pyproject.toml` (AC: 1)
  - [x] 1.1 Creare `backend/pyproject.toml` con sezioni `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.ruff.format]`, `[tool.ruff.lint.isort]`
  - [x] 1.2 Aggiungere `ruff` a `backend/requirements.txt`
  - [x] 1.3 Installare ruff nel venv: `pip install ruff`
- [x] Task 2 — Fix linting e formatting su tutto il backend (AC: 2)
  - [x] 2.1 Eseguire `ruff check backend/ --fix` per auto-fix errori risolvibili
  - [x] 2.2 Eseguire `ruff format backend/` per formattare tutto il codice
  - [x] 2.3 Risolvere manualmente eventuali errori residui (unused imports, undefined names, Django-specific)
  - [x] 2.4 Verificare: `ruff check backend/` e `ruff format --check backend/` con 0 errori
- [x] Task 3 — Creare `.editorconfig` alla root (AC: 3)
  - [x] 3.1 Creare `.editorconfig` con sezioni per `[*]`, `[*.py]`, `[*.{js,jsx,ts,tsx,json,yaml,yml,css}]`, `[*.md]`, `[Makefile]`
- [x] Task 4 — Installare e configurare Django Debug Toolbar (AC: 4)
  - [x] 4.1 Aggiungere `django-debug-toolbar` a `requirements.txt`
  - [x] 4.2 Installare: `pip install django-debug-toolbar`
  - [x] 4.3 In `settings.py`: aggiungere `'debug_toolbar'` a `INSTALLED_APPS` (condizionato a `DEBUG`)
  - [x] 4.4 In `settings.py`: aggiungere `'debug_toolbar.middleware.DebugToolbarMiddleware'` a `MIDDLEWARE` (condizionato a `DEBUG`)
  - [x] 4.5 In `settings.py`: aggiungere `INTERNAL_IPS = ['127.0.0.1']`
  - [x] 4.6 In `urls.py`: aggiungere `path('__debug__/', include('debug_toolbar.urls'))` condizionato a `settings.DEBUG`
- [x] Task 5 — Aggiungere React Query DevTools al QueryProvider (AC: 5)
  - [x] 5.1 Verificare che `@tanstack/react-query-devtools` sia disponibile come dipendenza
  - [x] 5.2 Importare `ReactQueryDevtools` da `@tanstack/react-query-devtools`
  - [x] 5.3 Renderizzare `<ReactQueryDevtools initialIsOpen={false} />` dentro `QueryClientProvider`
- [x] Task 6 — Configurare Rate Limiting DRF (AC: 6)
  - [x] 6.1 In `settings.py` `REST_FRAMEWORK`: aggiungere `DEFAULT_THROTTLE_CLASSES` con `AnonRateThrottle` e `UserRateThrottle`
  - [x] 6.2 In `settings.py` `REST_FRAMEWORK`: aggiungere `DEFAULT_THROTTLE_RATES` con `anon: 100/hour`, `user: 2000/hour`, `upload: 10/hour`
  - [x] 6.3 In `VideoViewSet`: aggiungere `throttle_scope = 'upload'` e `ScopedRateThrottle` a `throttle_classes` per l'azione `create`
- [x] Task 7 — Verifica finale (AC: 1-6)
  - [x] 7.1 `ruff check backend/` — 0 errori
  - [x] 7.2 `ruff format --check backend/` — 0 errori
  - [x] 7.3 `python manage.py check` — 0 errori
  - [x] 7.4 `python manage.py test` — tutti i test passano (inclusi i 5 test di Story 0.1)
  - [x] 7.5 `npm run build` — 0 errori TypeScript
  - [x] 7.6 Avviare `npm run dev` e verificare Debug Toolbar visibile su pagine Django (es. `/api/docs/`) — verificato via Playwright MCP: pannello DJDT visibile con SQL, Cache, Templates, Settings
  - [x] 7.7 Verificare React Query DevTools visibile nel browser (icona flottante) — verificato via Playwright MCP: bottone "Open Tanstack query devtools" presente sulla pagina login

## Dev Notes

### Stato Attuale (Pre-Implementazione)

**Nessun linter/formatter configurato:**
- Nessun `pyproject.toml` nel backend
- Nessun `ruff` nei requirements ne' installato
- Nessun `.editorconfig` alla root
- Codice Python formattato in modo inconsistente (vari stili di quote, import non ordinati)

**Nessun debug tool configurato:**
- Django Debug Toolbar: non installato, non in INSTALLED_APPS
- React Query DevTools: dipendenza disponibile (`@tanstack/react-query` include devtools) ma non importata ne' renderizzata
- Nessun rate limiting: `REST_FRAMEWORK` in settings.py ha solo auth, permissions, schema, pagination, exception handler

**Settings.py REST_FRAMEWORK attuale (riga 122-133):**
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'EXCEPTION_HANDLER': 'cs_clips.exceptions.error_handler.handle_exception_with_serializer',
}
```

### Dettaglio Tecnico: Configurazione ruff (D5)

**Versione:** ruff 0.15.4 (ultima stabile febbraio 2026)

**Configurazione `backend/pyproject.toml`:**
```toml
[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "DJ", "UP"]
# E = pycodestyle errors
# F = pyflakes (undefined names, unused imports)
# I = isort (import sorting)
# DJ = django-specific best practices
# UP = pyupgrade (modern Python syntax)

[tool.ruff.lint.isort]
known-third-party = ["django", "rest_framework", "drf_spectacular", "minio_storage", "minio"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"
```

**Strategia di fix:**
1. `ruff check backend/ --fix` — auto-fix import sorting, unused imports, pyupgrade
2. `ruff format backend/` — formatta tutto il codice (quote, indentazione, line length)
3. Fix manuali per errori residui (es. variabili non usate, Django-specific)

**ATTENZIONE:** ruff potrebbe segnalare errori in file come `test_spareggio.py` (management command con ImportError pre-esistente — NON e' un test Django). Valutare se ignorare con `# noqa` o fixare l'import.

### Dettaglio Tecnico: Django Debug Toolbar

**Versione:** django-debug-toolbar 6.2.0 (compatibile Django 5.1.6)

**Configurazione CONDIZIONATA a DEBUG:**
```python
# settings.py — dopo INSTALLED_APPS e MIDDLEWARE esistenti
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(2, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    # Dopo CorsMiddleware (posizione 1), prima di SessionMiddleware

INTERNAL_IPS = ['127.0.0.1']
```

```python
# urls.py — import condizionato
from django.conf import settings

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
```

**Nota:** `APP_DIRS: True` e' gia' impostato nei TEMPLATES — prerequisito soddisfatto. `django.contrib.staticfiles` e' gia' in INSTALLED_APPS — prerequisito soddisfatto.

### Dettaglio Tecnico: React Query DevTools

**Nessuna installazione aggiuntiva necessaria.** Il pacchetto `@tanstack/react-query-devtools` e' un modulo separato ma tipicamente gia' disponibile con l'installazione di `@tanstack/react-query`. Verificare con `ls frontend/node_modules/@tanstack/react-query-devtools/`.

**Modifica a `frontend/src/providers/query-provider.tsx`:**
```tsx
"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { useState, type ReactNode } from "react";

export function QueryProvider({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

**Nota:** `ReactQueryDevtools` si auto-disabilita in production build — nessun tree-shaking manuale necessario.

### Dettaglio Tecnico: Rate Limiting DRF (D6)

**Nessuna dipendenza aggiuntiva** — il throttling e' built-in in Django REST Framework.

**Configurazione `settings.py`:**
```python
REST_FRAMEWORK = {
    # ... config esistente ...
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '2000/hour',
        'upload': '10/hour',
    },
}
```

**Throttle scope per upload su `VideoViewSet`:**
```python
from rest_framework.throttling import ScopedRateThrottle

class VideoViewSet(ModelViewSet):
    # ... config esistente ...

    def get_throttles(self):
        if self.action == 'create':
            return [ScopedRateThrottle()]
        return super().get_throttles()

    throttle_scope = 'upload'
```

**ATTENZIONE al rate `user: 2000/hour`:** Il valore originale in D6 era 1000/hour, ma e' stato alzato a 2000/hour nell'architettura (validation party mode) per accomodare il polling notifiche 15s (240 req/hour solo per polling) + navigazione normale (~200 req/hour). Margine adeguato.

### Dettaglio Tecnico: .editorconfig

```ini
# EditorConfig — https://editorconfig.org
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 4

[*.py]
indent_size = 4

[*.{js,jsx,ts,tsx,json,yaml,yml,css}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
```

**Nota Windows:** `end_of_line = lf` e' critico perche' il progetto si sviluppa su Windows 11 ma i container Docker e le CI usano Linux. Forza LF evita problemi di line ending misti.

### Project Structure Notes

- **File NUOVI da creare:** `backend/pyproject.toml`, `.editorconfig`
- **File da MODIFICARE:** `backend/requirements.txt`, `backend/project_clip/settings.py`, `backend/project_clip/urls.py`, `frontend/src/providers/query-provider.tsx`
- **File Python da RIFORMATTARE:** tutti i file `.py` in `backend/` verranno toccati da `ruff format` — questo e' intenzionale e atteso
- **VideoViewSet location:** `backend/cs_clips/api/videos/video_views.py` — aggiungere throttle scope qui
- Allineamento con struttura modulare: nessun nuovo modulo, solo configurazione infrastrutturale

### Previous Story Intelligence (Story 0.1)

**Learnings dalla Story 0.1:**
- `requirements.txt` e' ora in UTF-8 (convertito da UTF-16 LE nella story 0.1) — safe per aggiungere nuove dipendenze
- `backend/cs_clips/tests/__init__.py` esiste gia' — creato nella story 0.1
- 5 test in `test_permissions.py` devono continuare a passare dopo ruff format
- `test_spareggio.py` e' un management command, NON un test Django — ha un `ImportError` pre-esistente (`VideoSerializer` da modulo sbagliato), non correlato a questa story
- Code review della story 0.1 ha identificato `handle_exception` ridondante in alcuni ViewSet — pre-esistente, non in scope
- Pattern commit: `fix:` / `feat:` prefix + story reference

**Definition of Done della story precedente (eccezioni):**
- Story 0.1 era esente da ruff check (ruff non ancora configurato). **Questa story ATTIVA il requisito ruff** nella DoD per tutte le story successive.

### Git Intelligence — Commit Recenti

```
b2bfa77 fix: Story 0-1 — bug fix settings, permissions e pulizia dipendenze
87e8304 Frontend / backend ALIGNMENT
79e7e84 fix: code review Story 2-1 — a11y, error messages, dead code, tipi
d893f75 feat: Story 2-1 upload clip con validazione frontend + backend
```

**Pattern rilevanti per questa story:**
- Il commit piu' recente (b2bfa77) e' la Story 0.1 completata — base pulita per iniziare
- Commit message style: `fix:` / `feat:` prefix + story reference
- Il backend e' stato recentemente resettato (87e8304) — il codice Python potrebbe avere stili inconsistenti dal repo originale

### Ricerca Tecnologica — Versioni Aggiornate

| Tool | Versione | Note |
|------|----------|------|
| ruff | 0.15.4 | Ultima stabile (feb 2026). Supporta Django rules (DJ), pyupgrade (UP) |
| django-debug-toolbar | 6.2.0 | Compatibile Django 5.1.6. Richiede Python 3.10+ |
| @tanstack/react-query-devtools | (bundled) | Incluso con @tanstack/react-query 5.90 |
| DRF Throttling | built-in | Nessuna dipendenza extra |

**Breaking changes ruff dal 0.4.x:**
- v0.5.0: E999 (syntax errors) non piu' ignorabile; deprecated settings rimossi
- v0.6.0: isort cerca `src/` di default; Jupyter support stabile
- v0.15.4: 2026 style guide; miglioramenti lambda formatting

### References

- [Source: epics.md — Story 0.2 AC] `_bmad-output/planning-artifacts/epics.md#Story 0.2`
- [Source: architecture.md — D5 Linter Backend ruff] `_bmad-output/planning-artifacts/architecture.md#D5`
- [Source: architecture.md — D6 Rate Limiting API] `_bmad-output/planning-artifacts/architecture.md#D6`
- [Source: architecture.md — Debug Tools] `_bmad-output/planning-artifacts/architecture.md#Debug Tools`
- [Source: architecture.md — .editorconfig] `_bmad-output/planning-artifacts/architecture.md#Editor Configuration`
- [Source: project-context.md — Qualita' Codice e Stile] `_bmad-output/project-context.md#Qualita' Codice e Stile`
- [Source: project-context.md — Nessun linter configurato] `_bmad-output/project-context.md#Pattern di Qualita' Impliciti`
- [Source: architecture.md — Throttle Rates Validation] `_bmad-output/planning-artifacts/architecture.md#Validation Issues Addressed`
- [Source: Story 0.1 — Completion Notes] `_bmad-output/implementation-artifacts/0-1-bug-fix-configurazione-settings-e-verifica-ambiente.md`

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- ruff auto-fix: 36 file riformattati, fix manuali per 39 errori residui (E501 linee lunghe, F821 VideoSerializer undefined)
- `test_spareggio.py`: fixato import pre-esistente `VideoSerializer` → `VideoOutputSerializer` (bug dal repo originale)
- `models/__init__.py`: aggiunto `__all__` per re-export esplicito (fix F401)
- `pyproject.toml`: aggiunto `extend-exclude = ["migrations"]` per escludere file auto-generati Django
- `@tanstack/react-query-devtools`: non era bundled con react-query, installato come dipendenza separata
- AUTH_PASSWORD_VALIDATORS e EXCEPTION_HANDLER: spezzati con string concatenation implicita per rispettare line-length 88

### Completion Notes List

- **AC-1 ✅** `backend/pyproject.toml` creato con configurazione ruff completa (line-length 88, py310, E/F/I/DJ/UP, isort known-third-party, double quotes, extend-exclude migrations)
- **AC-2 ✅** `ruff check backend/` e `ruff format --check backend/` passano con 0 errori. 36 file riformattati, 39+ fix manuali per linee lunghe, import errati, barrel export
- **AC-3 ✅** `.editorconfig` creato alla root con indent 4 per Python, indent 2 per JS/TS/JSON/YAML, LF line endings, trim whitespace
- **AC-4 ✅** `django-debug-toolbar==6.2.0` installato e configurato: INSTALLED_APPS + MIDDLEWARE condizionati a DEBUG, INTERNAL_IPS, URL pattern `__debug__/`
- **AC-5 ✅** `ReactQueryDevtools` importato e renderizzato in `query-provider.tsx` con `initialIsOpen={false}`. Dipendenza `@tanstack/react-query-devtools` installata
- **AC-6 ✅** Rate limiting configurato: AnonRateThrottle 100/hour, UserRateThrottle 2000/hour, ScopedRateThrottle upload 10/hour su VideoViewSet.create
- **Verifica ✅** ruff 0 errori, Django check 0 issues, 5/5 test passano, npm build 0 errori TypeScript
- **Nota:** Task 7.6 e 7.7 (verifica visiva Debug Toolbar e React Query DevTools) richiedono avvio runtime manuale — non automatizzabili in CI

### Change Log

- 2026-02-28: Story 0.2 implementata — linting ruff, .editorconfig, Django Debug Toolbar, React Query DevTools, rate limiting DRF
- 2026-02-28: Code review (AI) — H1: revertate migrazioni riformattate da ruff; M1: File List completata (+6 file mancanti); M2: project-context.md aggiornato (ruff configurato); M3: throttle_scope spostato a livello di action in VideoViewSet

### File List

**File nuovi:**
- `backend/pyproject.toml`
- `.editorconfig`

**File modificati (configurazione):**
- `backend/requirements.txt` (aggiunto ruff, django-debug-toolbar)
- `backend/project_clip/settings.py` (debug toolbar condizionato, INTERNAL_IPS, throttle classes/rates)
- `backend/project_clip/urls.py` (debug toolbar URL pattern condizionato)
- `frontend/src/providers/query-provider.tsx` (ReactQueryDevtools import e render)
- `frontend/package.json` (aggiunto @tanstack/react-query-devtools)
- `frontend/package-lock.json` (lockfile aggiornato)

**File modificati (ruff format + fix manuali):**
- `backend/cs_clips/admin.py`
- `backend/cs_clips/apps.py`
- `backend/cs_clips/permissions.py`
- `backend/cs_clips/scheduler.py`
- `backend/cs_clips/urls.py`
- `backend/cs_clips/models/__init__.py`
- `backend/cs_clips/models/comment.py`
- `backend/cs_clips/models/contest.py`
- `backend/cs_clips/models/rating.py`
- `backend/cs_clips/models/user.py`
- `backend/cs_clips/models/video.py`
- `backend/cs_clips/api/comments/comment_serializers.py`
- `backend/cs_clips/api/comments/comment_urls.py`
- `backend/cs_clips/api/comments/comment_views.py`
- `backend/cs_clips/api/contests/contest_serializers.py`
- `backend/cs_clips/api/contests/contest_urls.py`
- `backend/cs_clips/api/contests/contest_views.py`
- `backend/cs_clips/api/ratings/rating_serializers.py`
- `backend/cs_clips/api/ratings/rating_urls.py`
- `backend/cs_clips/api/ratings/rating_views.py`
- `backend/cs_clips/api/users/user_serializers.py`
- `backend/cs_clips/api/users/user_urls.py`
- `backend/cs_clips/api/users/user_views.py`
- `backend/cs_clips/api/videos/video_serializers.py`
- `backend/cs_clips/api/videos/video_urls.py`
- `backend/cs_clips/api/videos/video_views.py`
- `backend/cs_clips/exceptions/error_handler.py`
- `backend/cs_clips/exceptions/error_response_serializer.py`
- `backend/cs_clips/utils/desempate.py`
- `backend/cs_clips/utils/get_date_util.py`
- `backend/cs_clips/management/commands/close_contests.py`
- `backend/cs_clips/management/commands/test_spareggio.py`
- `backend/cs_clips/tests/test_permissions.py`
- `backend/manage.py`
