---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories
  - step-04-final-validation
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/architecture.md
  - _bmad-output/planning-artifacts/ux-design-specification.md
---

# Video_clip - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Video_clip, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

**Gestione Utenti (6 FR):**
- FR1: Utente non registrato può creare un account con username, email e password
- FR2: Utente registrato può autenticarsi con le proprie credenziali
- FR3: Utente registrato può visualizzare e modificare il proprio profilo pubblico
- FR4: Utente registrato può seguire altri utenti
- FR5: Utente registrato può smettere di seguire utenti che segue
- FR6: Utente registrato può visualizzare le proprie liste follower e following

**Creazione & Gestione Contenuti (10 FR):**
- FR7: Utente registrato può caricare una clip video (durata 10s-1min)
- FR8: Il sistema valida la durata della clip e rifiuta video fuori range con messaggio di errore specifico
- FR9: Il sistema valida il formato della clip e fornisce errore specifico per formati non supportati
- FR10: *(Pianificato Fase 2)* Il sistema converte le clip caricate in formato H.264/MP4 ottimizzato
- FR11: Utente registrato può impostare titolo e tag tipo per la clip caricata
- FR12: Utente registrato può impostare se la propria clip è scaricabile da altri utenti
- FR13: Utente registrato può scaricare le proprie clip
- FR14: Utente registrato può scaricare clip altrui quando il download è abilitato dall'autore
- FR15: Il sistema archivia le clip su storage cloud con URL di accesso autenticato a scadenza temporale
- FR16: Il sistema mostra una modale di errore con opzione "Riprova" quando l'upload fallisce

**Scoperta & Fruizione Contenuti (6 FR):**
- FR17: Utente registrato può visualizzare un feed Home con le clip degli utenti seguiti
- FR18: Utente può visualizzare la pagina dettaglio clip con player, commenti e metadati
- FR19: Le pagine dettaglio clip sono accessibili tramite URL diretto per la condivisione
- FR20: Il sistema genera link preview ricche (titolo, thumbnail) per gli URL delle clip condivisi su piattaforme esterne
- FR21: Il feed presenta le clip come card con thumbnail, titolo e metadati
- FR22: Utente può navigare dalla card nel feed alla pagina dettaglio della clip

**Sistema Commenti & Interazioni (8 FR):**
- FR23: Utente registrato può pubblicare un commento su una clip senza timestamp
- FR24: Utente registrato può pubblicare un commento temporizzato su una clip con timestamp specifico
- FR25: Il timestamp corrente del video viene pre-compilato nel form commento quando il video è in pausa
- FR26: Utente può rimuovere il timestamp pre-suggerito per pubblicare un commento normale
- FR27: Utente registrato può mettere like a un commento
- FR28: Utente registrato può mettere like a una clip
- FR29: La pagina dettaglio mostra tutti i commenti in vista gerarchica
- FR30: La pagina dettaglio offre due viste commenti: "Tutti" (cronologica) e "Nel video" (solo temporizzati, ordinati per timestamp)

**Popup & Loop di Engagement (6 FR):**
- FR31: Il sistema identifica il commento con più like per ogni timestamp di una clip
- FR32: Durante la riproduzione video, popup overlay mostrano il commento con più like per il timestamp corrente
- FR33: I popup overlay scompaiono dopo 3 secondi con fade-out
- FR34: I popup richiedono una soglia minima di 1 like per essere promossi
- FR35: La Sidebar Dinamica mostra i commenti con più like per la clip corrente
- FR36: Quando un commento viene disabilitato dalla moderazione, il sistema ricalcola il prossimo commento con più like per quel timestamp

**Sistema Contest (13 FR):**

*Backoffice Admin:*
- FR37: Admin può creare un contest tramite backoffice, scegliendo la tipologia (settimanale auto-gestito o bracket Champions League)
- FR38: Utente registrato può visualizzare i contest disponibili (entrambe le tipologie)

*Tipologia A — Contest Settimanale Auto-gestito:*
- FR39a: Un contest settimanale viene creato automaticamente quando un video è caricato con un tag contest (periodo lun-ven)
- FR39b: Le clip caricate vengono auto-assegnate al contest settimanale corrente in base al tag
- FR40a: Utente registrato può votare da 1 a 5 stelle sulle clip del contest settimanale
- FR41a: Il sistema chiude automaticamente il contest al termine del periodo
- FR42a: Il vincitore è la clip con la media voti più alta. In caso di parimerito: spareggio ponderato (50% numero voti, 30% visualizzazioni, 20% like)
- FR43a: Utente può visualizzare classifica e risultati del contest settimanale

*Tipologia B — Contest Bracket Champions League:*
- FR39c: Utente registrato può iscriversi a un contest bracket inviando una clip
- FR40b: Il sistema genera un bracket a eliminazione diretta per i partecipanti
- FR41b: Il contest mostra un albero grafico interattivo del bracket (stile torneo, con visualizzazione scontri, clip passate e risultati)
- FR42b: Utente registrato può votare da 1 a 5 stelle sulle clip di un matchup del contest bracket
- FR43b: Il sistema calcola la media dei voti interni al matchup e fa avanzare il vincitore (nessun fattore esterno)
- FR44: Utente può visualizzare stato del contest bracket, risultati passati e progressione nel bracket
- FR44b: Il vincitore del contest bracket riceve un premio (Fase 1: premi finanziati Video_clip; Fase 2: premi da partnership publisher)

**Amministrazione & Moderazione (8 FR):**
- FR45: Moderatore può disabilitare commenti inappropriati
- FR46: Admin può eliminare video
- FR47: Admin può sospendere account utente
- FR48: Admin può promuovere utenti tra ruoli (es. toconfirm → user)
- FR49: Admin può visualizzare la lista dei video per utente
- FR50: Il sistema invia notifiche in-app per eventi chiave (commento ricevuto, like ricevuto, commento promosso a popup, contest aperto, invito contest bracket, turno contest disponibile, risultati contest)
- FR51: Utente registrato può visualizzare la propria lista notifiche
- FR52: Il sistema mostra un badge con il conteggio delle notifiche non lette

**Requisiti Aggiuntivi PRD:**
- FR53: Utente può visualizzare il profilo di un altro utente tramite username
- FR54: Il sistema valida la durata del video all'upload e rifiuta automaticamente clip fuori range 10s-1min
- FR55: Admin può gestire contest tramite backoffice dedicato nel frontend (creazione, monitoraggio, chiusura manuale)

### NonFunctional Requirements

**Performance:**
- NFR1: First Contentful Paint < 1.5s su pagine pubbliche con SSR
- NFR2: Time to Interactive < 3s con priorità al player video
- NFR3: Video Start Playback < 2s via presigned URL MinIO
- NFR4: Lighthouse Score > 80
- NFR5: Risposta API (lettura) < 500ms — feed, commenti, notifiche
- NFR6: Risposta API (scrittura) < 1s — like, commenti, follow
- NFR7: Upload video < 30s per 500MB su connessione stabile
- NFR8: Latenza popup overlay vs timestamp < 200ms — dati popup pre-caricati in singola chiamata API al caricamento pagina
- NFR9: Progress bar upload con aggiornamento in tempo reale

**Security:**
- NFR10: Autenticazione JWT con refresh token (SimpleJWT), migrazione pianificata a Keycloak
- NFR11: CORS da restringere a origini specifiche prima del deploy di produzione
- NFR12: Validazione input su tutti gli endpoint (durata clip, formato file, lunghezza commenti)
- NFR13: Vincolo integrità voto contest — un voto per utente per clip/matchup, enforced backend + frontend
- NFR14: Upload limitato a formati video whitelist (MP4, MOV, AVI, MKV, WebM)
- NFR15: Limite dimensione file upload: max 500MB
- NFR16: Limiti lunghezza input: commenti max 500 caratteri, titolo clip max 100 caratteri
- NFR17: Password con requisiti minimi (lunghezza, complessità base)
- NFR18: Protezione CSRF sui form
- NFR19: Sanitizzazione testo commenti per prevenire XSS

**Resilienza & Error Handling:**
- NFR20: Error handler centralizzato backend con formato standard {code, detail}
- NFR21: Ogni pagina frontend deve avere isError + ErrorMessage con onRetry
- NFR22: Upload con modale errore e opzione retry con messaggi specifici

**Scalabilità:**
- NFR23: Il sistema deve supportare fino a 50 utenti concorrenti con risposta API < 1s
- NFR24: Architettura predisposta per Celery, proxy API e WebSocket senza riscritture maggiori

**Accessibilità:**
- NFR25: WCAG 2.1 livello AA base per MVP
- NFR26: Contrasti di colore sufficienti su testi e controlli
- NFR27: Navigazione completa via keyboard (tab, enter, escape)
- NFR28: Alt text su thumbnail e immagini
- NFR29: Player video con controlli accessibili (play/pause/volume via keyboard)
- NFR30: Label sui form (registrazione, login, upload, commenti)

**Integrazione:**
- NFR31: Backend REST API con comunicazione HTTP/JSON, auth token-based, CORS configurato
- NFR32: Storage cloud S3-compatible con URL autenticati a scadenza temporale
- NFR33: Estrazione metadati video all'upload per validazione
- NFR34: Task scheduling per chiusura automatica contest settimanali

### Additional Requirements

**Da Architecture — Decisioni Architetturali (D1-D7):**
- D1: Notifiche via polling REST ogni 15s (nessun WebSocket/SSE per MVP). Modello Notification con FK espliciti (no GenericForeignKey)
- D2: Champions League bracket con modelli separati (Bracket, ContestEntry, Matchup) — dominio API `/api/brackets/` indipendente da `/api/contests/`
- D3: Presigned URL refresh via lazy re-fetch al play (catch onerror → spinner → refetch → retry max 2). Verificare `@lru_cache` su client MinIO
- D4: Testing stack — Backend: Django TestCase + conftest.py con 5 fixture. Frontend: Vitest + RTL + MSW con 5 endpoint critici
- D5: Linter backend → ruff come unico linter + formatter Python in pyproject.toml
- D6: Rate limiting → DRF throttling built-in: anon 100/hour, user 2000/hour, upload 10/hour
- D7: Rimuovere celery e redis da requirements.txt (peso morto, non configurati)

**Da Architecture — Gap Backend Critici:**
- Modello `Notification` + infrastruttura delivery mancante (7 tipi notifica)
- Endpoint `by-username` mancante (404 a runtime su profilo utente)
- Modelli `VideoLike` e `CommentLike` mancanti (bloccano FR27, FR28, FR31, FR34, FR35)
- Endpoint `followers_count`, `following_count`, `is_followed_by_me` mancanti nel UserSerializer
- Sistema Champions League bracket da zero (modelli + logica + UI)
- `useUserVideos` filtra client-side (manca endpoint `?uploader=` backend)
- Hook `useDeleteComment`, `useDeleteVideo`, `useUpdateRating` mancanti nel frontend
- Paginazione followers/following non implementata (array piatti)
- Campo `bio` User mancante
- Campo `allow_download` Video mancante
- Campo `is_disabled` Comment mancante

**Da Architecture — Bug FIX-READY (10 bug Story 0):**
- FIX-1: `STATICFILES_DIRS` contiene path inesistente
- FIX-2: `DEFAULT_FILE_STORAGE` deprecato in Django 5.x
- FIX-3: Import circolare potenziale in `models/__init__.py`
- FIX-4: `django-cleanup` non in `INSTALLED_APPS`
- FIX-5: `CORS_ALLOWED_ORIGINS` hardcoded
- FIX-6: Manca `DEFAULT_AUTO_FIELD`
- FIX-7: `AUTH_USER_MODEL` dopo `INSTALLED_APPS` con migrazioni
- FIX-8: Bug `RoleBasedPermission.has_object_permission()` su Video (controlla `obj.user` invece di `obj.uploader`)
- FIX-9: Bug import `Response` in `user_views.py` (follow/unfollow crashano)
- FIX-10: `CorsMiddleware` posizionato dopo `CommonMiddleware` (deve essere prima)

**Da Architecture — Story 0 Prerequisiti Infrastruttura:**
- Linting: ruff (backend), Prettier (frontend), ESLint esteso
- Editor: `.editorconfig` alla root
- Debug: Django Debug Toolbar, React Query DevTools
- Validazione env: `env.ts` con Zod
- CI/CD: GitHub Actions con quality gates (ruff + test backend + lint + test + build frontend)
- Testing baseline: conftest.py con 5 fixture, MSW con 5 handlers
- Backoffice admin: Django Admin per MVP (nessuna interfaccia admin custom nel frontend)

**Da Architecture — Asimmetria Frontend-Avanti:**
- Il frontend è più avanzato del backend: ogni hook che chiama API inesistenti è un requisito implicito
- Le story backend devono essere prioritizzate in base a ciò che il frontend già consuma
- Tipi TypeScript in `src/types/` definiscono la shape attesa delle risposte backend

**Da UX Design — Requisiti Experience:**
- Dark mode come default (il gaming vive nel dark mode)
- Glassmorphism sui popup overlay (sfondo frosted glass semi-trasparente)
- Micro-animazioni a 3 tier: significato (Framer Motion), transizione (Framer Motion), delizia (CSS native)
- Spinner unico del sito che si costruisce dal gradiente (branding custom)
- Visual DNA con gradiente ricorrente (viola→ciano) su barra progresso, bordi card, spinner, popup
- Comment markers sulla timeline del player (dot luminosi con hover preview del commento top)
- CTA contestuale empatico sulla pagina pubblica per utenti non loggati
- Timestamp pre-compilato alla pausa come punto di conversione critico
- Notifica come racconto, non evento generico
- La pagina pubblica SSR è la demo vivente del prodotto (popup funzionanti + CTA)
- Skeleton loading come placeholder animati nel feed
- Toast notification per feedback non intrusivo

**Da UX Design — Pattern di Navigazione:**
- Desktop: sidebar sinistra collassabile + area centrale + sidebar destra commenti
- Mobile: header (logo V + search + avatar) + MobileBottomBar (Home, Esplora, Upload, Profilo)
- Card-to-detail: feed card → pagina dettaglio clip
- Doppio tap per like su clip (mobile/desktop)

### FR Coverage Map

**Gestione Utenti:**
- FR1: Epic 1 — Registrazione account
- FR2: Epic 1 — Autenticazione credenziali
- FR3: Epic 1 — Visualizzazione e modifica profilo (incluso campo bio)
- FR4: Epic 1 — Follow utente
- FR5: Epic 1 — Unfollow utente
- FR6: Epic 1 — Liste follower/following

**Creazione & Gestione Contenuti:**
- FR7: Epic 2 — Upload clip 10s-1min
- FR8: Epic 2 — Validazione durata clip
- FR9: Epic 2 — Validazione formato clip
- FR10: Escluso MVP — Transcoding H.264 (Fase 2)
- FR11: Epic 2 — Titolo e tag per clip
- FR12: Epic 2 — Impostazione allow_download
- FR13: Epic 2 — Download proprie clip
- FR14: Epic 2 — Download clip altrui (se abilitato)
- FR15: Epic 2 — Storage MinIO con presigned URL
- FR16: Epic 2 — Modale errore upload con retry

**Scoperta & Fruizione Contenuti:**
- FR17: Epic 2 — Feed Home (following)
- FR18: Epic 2 — Pagina dettaglio clip
- FR19: Epic 2 — URL diretto per condivisione
- FR20: Epic 2 — Link preview SSR (OG tags)
- FR21: Epic 2 — Card nel feed
- FR22: Epic 2 — Navigazione card → dettaglio

**Sistema Commenti & Interazioni:**
- FR23: Epic 2 — Commento senza timestamp
- FR24: Epic 2 — Commento temporizzato con timestamp
- FR25: Epic 2 — Timestamp pre-compilato alla pausa
- FR26: Epic 2 — Rimozione timestamp pre-suggerito
- FR27: Epic 3 — Like su commento (richiede CommentLike)
- FR28: Epic 3 — Like su clip (richiede VideoLike)
- FR29: Epic 2 — Vista commenti gerarchica
- FR30: Epic 2 — Dual-view "Tutti" / "Nel video"

**Popup & Loop di Engagement:**
- FR31: Epic 3 — Commento con più like per timestamp
- FR32: Epic 3 — Popup overlay durante riproduzione
- FR33: Epic 3 — Popup fade-out dopo 3s
- FR34: Epic 3 — Soglia minima 1 like per popup
- FR35: Epic 3 — Sidebar Dinamica (commenti più likati)
- FR36: Epic 3 — Ricalcolo popup dopo disabilitazione commento

**Sistema Contest — Tipologia A Settimanale:**
- FR37: Epic 4 (parziale) — Creazione contest da Django Admin (settimanale)
- FR38: Epic 4 — Visualizzazione contest disponibili
- FR39a: Epic 4 — Creazione automatica contest settimanale
- FR39b: Epic 4 — Auto-assegnazione clip al contest corrente
- FR40a: Epic 4 — Votazione 1-5 stelle clip contest
- FR41a: Epic 4 — Chiusura automatica contest
- FR42a: Epic 4 — Vincitore per media voti + spareggio
- FR43a: Epic 4 — Classifica e risultati contest

**Sistema Contest — Tipologia B Bracket:**
- FR37: Epic 6 (parziale) — Creazione contest bracket da Django Admin
- FR39c: Epic 6 — Iscrizione a contest bracket
- FR40b: Epic 6 — Generazione bracket eliminazione diretta
- FR41b: Epic 6 — Albero grafico interattivo
- FR42b: Epic 6 — Votazione matchup
- FR43b: Epic 6 — Avanzamento vincitore per media voti
- FR44: Epic 6 — Stato bracket e progressione
- FR44b: Epic 6 — Premio vincitore

**Amministrazione & Moderazione:**
- FR45: Epic 0 — Disabilita commenti (Django Admin + campo is_disabled)
- FR46: Epic 0 — Elimina video (Django Admin)
- FR47: Epic 0 — Sospendi account (Django Admin)
- FR48: Epic 0 — Promozione ruoli (Django Admin)
- FR49: Epic 0 — Lista video per utente (Django Admin)

**Notifiche:**
- FR50: Epic 5 — Notifiche in-app per eventi chiave (7 tipi)
- FR51: Epic 5 — Lista notifiche utente
- FR52: Epic 5 — Badge conteggio non lette

**Requisiti Aggiuntivi PRD:**
- FR53: Epic 1 — Profilo per username (endpoint by-username)
- FR54: Epic 2 — Validazione durata con reject automatico
- FR55: Epic 4 (parziale) — Gestione contest da Django Admin

**Copertura:** 55 FR totali → 54 coperti, 1 escluso MVP (FR10 transcoding).

## Epic List

### Epic 0: Fondamenta di Sviluppo e Admin
Ambiente di sviluppo solido: bug bloccanti risolti, linting automatico, testing baseline, CI/CD, moderazione base via Django Admin funzionante.
**FRs coperti:** FR45, FR46, FR47, FR48, FR49, FR55 (parziale)
**Decisioni architetturali:** D4 (testing), D5 (ruff), D6 (throttling), D7 (rimozione celery/redis)
**Include:** 10 bug FIX-READY, conftest.py 5 fixture, MSW 5 handlers, .editorconfig, CI/CD base, Django Admin per moderazione/gestione contest, campo `is_disabled` su Comment

### Epic 1: Core Platform — Allineamento Backend
Gli utenti possono registrarsi, accedere, gestire il profilo completo (con bio), seguire/smettere di seguire altri utenti, navigare ai profili via username. Tutto ciò che il frontend già mostra funziona realmente end-to-end.
**FRs coperti:** FR1, FR2, FR3, FR4, FR5, FR6, FR53
**Include:** endpoint `by-username`, `followers_count`/`following_count`/`is_followed_by_me` nel UserSerializer, campo `bio` User, paginazione followers/following, fix bug `Response` import, fix `RoleBasedPermission`, endpoint `?uploader=` su video

### Epic 2: Upload, Player e Commenti
Gli utenti caricano clip con validazione completa, le guardano con il player integrato, commentano (con e senza timestamp), vedono i commenti nella dual-view, navigano nel feed Home, condividono clip via link con preview SSR, scaricano clip proprie e altrui.
**FRs coperti:** FR7, FR8, FR9, FR11, FR12, FR13, FR14, FR15, FR16, FR17, FR18, FR19, FR20, FR21, FR22, FR23, FR24, FR25, FR26, FR29, FR30, FR54
**Include:** campo `allow_download` Video, validazione durata con reject (FR54), lazy re-fetch presigned URL (D3), hook `useDeleteComment`/`useDeleteVideo` frontend

### Epic 3: Like, Popup e Engagement Loop
Gli utenti mettono like a clip e commenti. Il commento con più like per ogni timestamp diventa popup overlay visibile a tutti durante la riproduzione. La Sidebar Dinamica mostra i commenti più likati. Il commentatore diventa co-protagonista della clip — il cuore del prodotto.
**FRs coperti:** FR27, FR28, FR31, FR32, FR33, FR34, FR35, FR36
**Include:** modelli `VideoLike` e `CommentLike`, endpoint CRUD like, hook frontend `useVideoLike`/`useCommentLike`, UI bottoni like, aggiornamento popup/sidebar con dati reali, ricalcolo popup dopo moderazione

### Epic 4: Contest Settimanale
Gli utenti partecipano a contest settimanali automatici caricando clip con tag. Votano 1-5 stelle, vedono la classifica in tempo reale e il vincitore. L'admin gestisce i contest da Django Admin.
**FRs coperti:** FR37 (settimanale), FR38, FR39a, FR39b, FR40a, FR41a, FR42a, FR43a, FR55 (parziale)
**Include:** pagina contest frontend completa (non solo vincitori), UI voto per clip, classifica attiva, pagina risultati, integrazione con Django Admin per backoffice

### Epic 5: Notifiche In-App
Gli utenti ricevono notifiche per commenti ricevuti, like ricevuti, commenti promossi a popup, eventi contest. Vedono il badge non-lette nella sidebar e la lista notifiche completa.
**FRs coperti:** FR50, FR51, FR52
**Decisione architetturale:** D1 (polling REST 15s, modello Notification con FK espliciti)
**Include:** modello `Notification`, endpoint API `/api/notifications/`, pagina `/notifiche` frontend, campanella con badge, hook `useNotifications` con `refetchInterval: 15000`

### Epic 6: Contest Bracket Champions League
L'admin crea tornei bracket da Django Admin. Gli utenti si iscrivono inviando clip, votano nei matchup 1v1, seguono la progressione nell'albero grafico interattivo. Il vincitore di ogni matchup avanza per media voti. Il vincitore finale riceve un premio.
**FRs coperti:** FR37 (bracket), FR39c, FR40b, FR41b, FR42b, FR43b, FR44, FR44b
**Decisione architetturale:** D2 (modelli separati Bracket, ContestEntry, Matchup — dominio API `/api/brackets/` indipendente)
**Include:** 3 nuovi modelli, logica progressione turni, UI bracket visualization (libreria React), pagina contest bracket frontend, backoffice Django Admin

---

## Definition of Done (per ogni Story)

Ogni story si considera completata SOLO quando soddisfa tutti i seguenti criteri:

1. **Test passanti:** `python manage.py test` e `npm run test` passano al 100% (nessuna regressione)
2. **Nuovo codice testato:** ogni nuovo endpoint backend o logica critica ha almeno 1 test dedicato
3. **Linting pulito:** `ruff check backend/` e `ruff format --check backend/` passano con 0 errori (dopo Story 0.2)
4. **Build senza errori:** `npm run build` nel frontend compila senza errori TypeScript
5. **Error handling frontend:** ogni nuova pagina frontend include `isError` + `<ErrorMessage onRetry={refetch} />` (pattern retro Epic 1)
6. **Accessibilità base:** nuovi elementi interattivi hanno `role`, `aria-label` e supporto keyboard (pattern retro Epic 1)
7. **Nessun segreto committato:** file `.env`, credenziali e token non sono nel repository

---

## Epic 0: Fondamenta di Sviluppo e Admin

Ambiente di sviluppo solido: bug bloccanti risolti, linting automatico, testing baseline, CI/CD, moderazione base via Django Admin funzionante.

**Nota parallelizzazione:** L'ordine consigliato è 0.1 → 0.2 → 0.4 → (0.3 ∥ Epic 1). La Story 0.3 (Testing/CI) può procedere in parallelo con l'inizio dell'Epic 1, purché Story 0.1 (bug fix) e 0.2 (linting) siano completate. Questo evita di bloccare lo sviluppo delle feature in attesa della CI.

### Story 0.1: Bug Fix, Configurazione Settings e Verifica Ambiente

As a sviluppatore,
I want un backend Django con configurazione corretta, senza bug noti, e l'intero ambiente di sviluppo funzionante,
So that posso sviluppare nuove feature su una base solida e verificata.

**Acceptance Criteria:**

**Given** il backend Django attuale con bug noti in settings.py e nelle views
**When** applico tutti i fix documentati nell'Architecture e verifico l'ambiente
**Then** `STATICFILES_DIRS` punta a path esistenti (FIX-1)
**And** `DEFAULT_FILE_STORAGE` usa la sintassi Django 5.x `STORAGES` (FIX-2)
**And** nessun import circolare in `models/__init__.py` (FIX-3)
**And** `django-cleanup` è in `INSTALLED_APPS` (FIX-4)
**And** `CORS_ALLOWED_ORIGINS` è configurabile via env var (FIX-5)
**And** `DEFAULT_AUTO_FIELD` è impostato a `BigAutoField` (FIX-6)
**And** `AUTH_USER_MODEL` è dichiarato prima di `INSTALLED_APPS` che eseguono migrazioni (FIX-7)
**And** `RoleBasedPermission.has_object_permission()` controlla sia `obj.uploader` che `obj.user` (FIX-8)
**And** `Response` è importato correttamente in `user_views.py` (FIX-9)
**And** `CorsMiddleware` è posizionato prima di `CommonMiddleware` in `MIDDLEWARE` (FIX-10)
**And** `celery` e `redis` sono rimossi da `requirements.txt` (D7)
**And** `python manage.py check` non produce errori
**And** `python manage.py migrate` esegue senza errori
**And** `npm run dev` dalla root avvia correttamente Docker (PostgreSQL + MinIO), backend Django e frontend Next.js tramite `concurrently` + `wait-on`
**And** il frontend compila e si connette al backend senza errori CORS

### Story 0.2: Linting, Formatting e Developer Tools

As a sviluppatore,
I want linting automatico e strumenti di debug configurati,
So that il codice è consistente e posso identificare problemi (N+1 queries, cache issues) rapidamente.

**Acceptance Criteria:**

**Given** il progetto senza linter Python né formatter configurato
**When** configuro ruff e gli strumenti di sviluppo
**Then** `pyproject.toml` contiene configurazione ruff allineata alle regole di `project-context.md` (D5)
**And** `ruff check backend/` e `ruff format --check backend/` passano con 0 errori
**And** `.editorconfig` alla root definisce indent, line endings e trailing whitespace
**And** Django Debug Toolbar è installato e attivo in `DEBUG=True` (visibilità query SQL, N+1 detection)
**And** React Query DevTools è importato nel `QueryProvider` (già dipendenza installata)
**And** rate limiting DRF è configurato in `settings.py`: `anon: 100/hour`, `user: 2000/hour`, `upload: 10/hour` (D6)

### Story 0.3: Testing Baseline e CI/CD

As a sviluppatore,
I want una baseline di test automatici e una CI pipeline,
So that ogni modifica futura è protetta da regressioni e il codice è validato ad ogni push.

**Acceptance Criteria:**

**Given** nessun test automatizzato né CI/CD configurati
**When** creo la baseline di testing e la pipeline CI
**Then** `cs_clips/tests/conftest.py` contiene 5 fixture: `authenticated_user`, `admin_user`, `sample_video`, `api_client_authenticated`, `sample_contest` (D4)
**And** almeno 1 test backend Django passa (es. test auth flow: registrazione crea utente con gruppo `toconfirm`)
**And** `frontend/src/test/setup.ts` configura MSW server con `beforeAll`/`afterAll`
**And** `frontend/src/test/handlers.ts` contiene handler per 5 endpoint: `POST /api/token/`, `POST /api/users/`, `GET /api/videos/`, `GET /api/videos/{id}/`, `GET /api/users/{id}/` (D4)
**And** almeno 1 test frontend Vitest passa
**And** `.github/workflows/ci.yml` esegue: ruff check + test backend + npm lint + vitest + npm build
**And** `npm run build` nel frontend compila senza errori

**Nota priorità:** I test locali funzionanti (conftest.py, MSW handlers, almeno 1 test per lato) sono il deliverable obbligatorio. La CI/CD GitHub Actions è fortemente consigliata ma non bloccante se ci sono problemi infrastrutturali (permessi, Docker nel runner). In quel caso, documentare il problema e procedere — la CI verrà fixata come follow-up.

### Story 0.4: Django Admin per Moderazione e Gestione Contest

As an admin/moderatore,
I want gestire utenti, video, commenti e contest tramite Django Admin,
So that posso moderare la piattaforma e gestire i contest senza interfaccia frontend dedicata.

**Acceptance Criteria:**

**Given** un admin autenticato nell'interfaccia Django Admin
**When** accede alla sezione di moderazione
**Then** può disabilitare un commento (campo `is_disabled` BooleanField su Comment, default False) (FR45)
**And** può eliminare un video (file rimosso da MinIO via `django-cleanup`) (FR46)
**And** può sospendere un account utente (toggle `is_active`) (FR47)
**And** può promuovere un utente tra ruoli (modifica gruppi Django: `toconfirm` → `user` → `admin`) (FR48)
**And** può visualizzare la lista dei video filtrata per uploader (FR49)
**And** può visualizzare, creare e chiudere manualmente contest settimanali (FR55)
**And** il campo `is_disabled` su Comment è creato via migrazione Django
**And** i commenti disabilitati non appaiono nelle risposte API (`is_disabled=False` filter nel queryset di `CommentViewSet`)

---

## Epic 1: Core Platform — Allineamento Backend

Gli utenti possono registrarsi, accedere, gestire il profilo completo (con bio), seguire/smettere di seguire altri utenti, navigare ai profili via username. Tutto ciò che il frontend già mostra funziona realmente end-to-end.

### Story 1.1: Registrazione e Login End-to-End

As a utente non registrato,
I want creare un account e autenticarmi,
So that posso accedere alle funzionalità della piattaforma.

**Acceptance Criteria:**

**Given** un utente non registrato
**When** invia username, email e password all'endpoint di registrazione
**Then** viene creato un account con gruppo `toconfirm` assegnato automaticamente (FR1)
**And** la risposta contiene i dati utente serializzati

**Given** un utente registrato
**When** invia credenziali corrette all'endpoint `/api/token/`
**Then** riceve access token e refresh token JWT (FR2)
**And** `last_login` viene aggiornato

**Given** un access token scaduto e un refresh token valido
**When** chiama `/api/token/refresh/`
**Then** riceve un nuovo access token
**And** il refresh token ruota (rotation attiva)

**Given** credenziali errate
**When** tenta il login
**Then** riceve errore 401 con formato `{code, detail}` in italiano

### Story 1.2: Profilo Utente Completo con Bio e By-Username

As a utente registrato,
I want visualizzare e modificare il mio profilo con bio, e visitare profili altrui via username,
So that la mia identità sulla piattaforma è completa e posso scoprire altri utenti.

**Acceptance Criteria:**

**Given** un utente autenticato
**When** chiama `GET /api/users/by-username/{username}/`
**Then** riceve il profilo dell'utente con `followers_count` (intero), `following_count` (intero), `is_followed_by_me` (booleano), `bio` (stringa) (FR53, FR3)
**And** i contatori usano `Count()` annotation con `distinct=True` (no N+1)

**Given** un utente autenticato che modifica il proprio profilo
**When** invia `PATCH /api/users/{id}/` con campo `bio`
**Then** il campo `bio` viene aggiornato (max 500 caratteri) (FR3)
**And** la risposta contiene il profilo aggiornato

**Given** un username inesistente
**When** chiama `GET /api/users/by-username/{username}/`
**Then** riceve errore 404 con formato `{code, detail}`

**Given** il campo `bio` nel modello User
**When** viene creata la migrazione
**Then** è un `TextField` opzionale (`blank=True, default=''`) con `help_text` in italiano

### Story 1.3: Follow, Unfollow e Liste Paginate

As a utente registrato,
I want seguire e smettere di seguire altri utenti e vedere le liste follower/following,
So that posso costruire il mio network e scoprire chi mi segue.

**Acceptance Criteria:**

**Given** un utente autenticato
**When** chiama `POST /api/users/{id}/follow/`
**Then** l'utente target viene aggiunto ai following (FR4)
**And** la risposta conferma con `{detail: "Ora segui {username}."}` in italiano

**Given** un utente che segue un altro utente
**When** chiama `POST /api/users/{id}/unfollow/`
**Then** l'utente target viene rimosso dai following (FR5)
**And** la risposta conferma con `{detail: "Hai smesso di seguire {username}."}` in italiano

**Given** un utente autenticato
**When** chiama `GET /api/users/{id}/followers/` o `GET /api/users/{id}/following/`
**Then** riceve risposta paginata `{count, next, previous, results}` (FR6)
**And** NON un array piatto (fix paginazione attuale)
**And** usa `self.paginate_queryset()` + `self.get_paginated_response()` nelle custom actions

**Given** un utente che tenta di seguire sé stesso
**When** chiama `POST /api/users/{id}/follow/` con il proprio ID
**Then** riceve errore 400 con messaggio specifico

### Story 1.4: Filtro Video per Uploader Backend

As a utente registrato,
I want che il mio profilo carichi solo i miei video dal backend,
So that la pagina profilo è performante anche con molti video sulla piattaforma.

**Acceptance Criteria:**

**Given** un utente che visita il profilo di un altro utente
**When** il frontend chiama `GET /api/videos/?uploader={id}`
**Then** il backend ritorna solo i video di quell'uploader, paginati
**And** il filtro è implementato tramite `filterset_fields = ['uploader']` nel `VideoViewSet` (django-filter già installato)

**Given** un uploader senza video
**When** chiama `GET /api/videos/?uploader={id}`
**Then** riceve risposta paginata vuota `{count: 0, next: null, previous: null, results: []}`

---

## Epic 2: Upload, Player e Commenti

Gli utenti caricano clip con validazione completa, le guardano con il player integrato, commentano (con e senza timestamp), vedono i commenti nella dual-view, navigano nel feed Home, condividono clip via link con preview SSR, scaricano clip proprie e altrui.

### Story 2.1: Upload Clip con Validazione Completa

As a utente registrato,
I want caricare clip con validazione automatica di durata e formato,
So that ricevo feedback immediato se il video non è accettabile.

**Acceptance Criteria:**

**Given** un utente autenticato che carica un video
**When** il video ha durata tra 10s e 1min, formato supportato (MP4/MOV/AVI/MKV/WebM) e dimensione < 500MB
**Then** il video viene salvato su MinIO con durata estratta via MoviePy (FR7, FR15)
**And** il campo `allow_download` (BooleanField, default True) viene salvato dal serializer (FR12)
**And** il campo `title` (max 100 char) e `tag` vengono salvati (FR11)
**And** la risposta contiene il video con presigned URL

**Given** un utente che carica un video con durata < 10s o > 60s
**When** il backend valida la durata dopo estrazione MoviePy
**Then** il video viene rifiutato con errore 400: "La durata del video deve essere tra 10 secondi e 1 minuto" (FR8, FR54)

**Given** un utente che carica un file con formato non supportato
**When** il backend valida l'estensione e il content type
**Then** il file viene rifiutato con errore 400: "Formato non supportato. Formati accettati: MP4, MOV, AVI, MKV, WebM" (FR9)

**Given** un utente che carica un file > 500MB
**When** il backend valida la dimensione
**Then** il file viene rifiutato con errore 400: "Il file supera la dimensione massima di 500MB"

**Given** un video la cui durata non può essere estratta da MoviePy (file corrotto o codec non supportato)
**When** il backend tenta l'estrazione dei metadati
**Then** il video viene rifiutato con errore 400: "Impossibile leggere i metadati del video. Verifica che il file non sia corrotto"

**Given** un upload che fallisce per errore di rete
**When** il frontend mostra la modale di errore
**Then** il bottone "Riprova" ri-esegue l'upload (FR16)

### Story 2.2: Download Clip e Presigned URL Refresh

As a utente registrato,
I want scaricare le mie clip e quelle di altri utenti (se permesso), e guardare video senza interruzioni,
So that posso salvare le clip e non subisco errori per URL scadute.

**Acceptance Criteria:**

**Given** un utente autenticato che vuole scaricare la propria clip
**When** richiede il download
**Then** riceve la presigned URL per il download diretto da MinIO (FR13)

**Given** un utente che vuole scaricare la clip di un altro utente con `allow_download=True`
**When** richiede il download
**Then** riceve la presigned URL per il download (FR14)

**Given** un utente che vuole scaricare una clip con `allow_download=False`
**When** richiede il download
**Then** riceve errore 403: "Il download non è abilitato per questa clip"

**Given** un video in riproduzione la cui presigned URL è scaduta (>1h)
**When** il `<video>` genera un evento `onerror`
**Then** il player mostra un mini-spinner (non errore visibile)
**And** ri-chiama `videos.detail(id)` per ottenere una nuova presigned URL (D3)
**And** riprova il playback automaticamente
**And** dopo 2 tentativi falliti mostra "Video non disponibile, ricarica la pagina"

### Story 2.3: Feed Home e Navigazione Clip

As a utente registrato,
I want scorrere il feed con le clip dei miei following e aprire le clip in dettaglio,
So that posso scoprire nuovi contenuti dai creatori che seguo.

**Acceptance Criteria:**

**Given** un utente autenticato con following
**When** accede al feed Home
**Then** vede le clip degli utenti seguiti ordinate per data, come card con thumbnail, titolo e metadati (FR17, FR21)
**And** lo scroll infinito carica pagine successive (FR22)

**Given** un utente che clicca su una card nel feed
**When** naviga alla pagina dettaglio
**Then** vede il player video con controlli, metadati della clip e sezione commenti (FR18, FR22)

**Given** un visitatore non autenticato che accede a `/clip/{id}` via URL diretto
**When** la pagina viene servita
**Then** il server genera meta tag OG (titolo, thumbnail) per link preview su piattaforme esterne (FR19, FR20)
**And** il video è riproducibile senza autenticazione
**And** il CTA "Vuoi commentare e votare?" è visibile

**Given** un utente senza following
**When** accede al feed Home
**Then** vede un EmptyState con suggerimento di seguire utenti

### Story 2.4: Commenti Dual-Layer con Timestamp

As a utente registrato,
I want commentare le clip con e senza timestamp e vedere i commenti in due viste,
So that posso esprimere reazioni precise ancorate al momento esatto del video.

**Acceptance Criteria:**

**Given** un utente autenticato sulla pagina dettaglio clip con video in pausa
**When** il form commento è visibile
**Then** il timestamp corrente del video è pre-compilato nel campo timestamp (FR25)
**And** l'utente può rimuovere il timestamp per un commento normale (FR26)

**Given** un utente che invia un commento con timestamp
**When** il backend riceve `timestamp_second` con valore tra 0 e `video.duration`
**Then** il commento viene salvato con il timestamp associato (FR24)
**And** appare nella vista "Nel video" ordinato per timestamp (FR30)

**Given** un utente che invia un commento senza timestamp
**When** il backend riceve `timestamp_second` nullo o assente
**Then** il commento viene salvato come commento normale (FR23)
**And** appare nella vista "Tutti" ordinata cronologicamente (FR29)

**Given** la pagina dettaglio clip
**When** l'utente usa i tab "Tutti" / "Nel video"
**Then** la vista "Tutti" mostra tutti i commenti in ordine cronologico (FR29)
**And** la vista "Nel video" mostra solo commenti temporizzati ordinati per timestamp (FR30)

**Given** un utente autenticato che è autore di un commento
**When** elimina il proprio commento
**Then** il commento viene rimosso (hook `useDeleteComment` + endpoint `DELETE /api/comments/{id}/`)
**And** la lista commenti si aggiorna

### Story 2.5: Delete Video e Operazioni CRUD Mancanti

As a utente registrato,
I want eliminare le mie clip e modificare i miei voti,
So that ho pieno controllo sui miei contenuti e interazioni.

**Acceptance Criteria:**

**Given** un utente autenticato proprietario di un video
**When** elimina il proprio video
**Then** il video e il file su MinIO vengono rimossi (hook `useDeleteVideo` + endpoint `DELETE /api/videos/{id}/`)
**And** la lista video nel profilo si aggiorna

**Given** un utente autenticato che ha già votato una clip in un contest
**When** modifica il voto
**Then** il rating viene aggiornato (hook `useUpdateRating` + endpoint `PATCH /api/ratings/{id}/`)
**And** il feedback visivo conferma la modifica

**Given** un utente non proprietario
**When** tenta di eliminare un video altrui
**Then** riceve errore 403

---

## Epic 3: Like, Popup e Engagement Loop

Gli utenti mettono like a clip e commenti. Il commento con più like per ogni timestamp diventa popup overlay visibile a tutti durante la riproduzione. La Sidebar Dinamica mostra i commenti più likati. Il commentatore diventa co-protagonista della clip — il cuore del prodotto.

### Story 3.1: Modelli VideoLike e CommentLike Backend

As a sviluppatore,
I want i modelli VideoLike e CommentLike con endpoint CRUD,
So that il sistema di like è disponibile per il frontend e per il calcolo dei popup.

**Acceptance Criteria:**

**Given** i modelli `VideoLike` e `CommentLike` non esistenti
**When** vengono creati come file separati in `cs_clips/models/`
**Then** `VideoLike` ha campi `user` (FK get_user_model), `video` (FK Video), `created_at`, con `unique_together = ('user', 'video')` e `related_name='likes'`
**And** `CommentLike` ha campi `user` (FK get_user_model), `comment` (FK Comment), `created_at`, con `unique_together = ('user', 'comment')` e `related_name='likes'`
**And** entrambi sono registrati in `admin.py` e esportati da `models/__init__.py`
**And** la migrazione Django è creata e applicata

**Given** un utente autenticato
**When** chiama `POST /api/videos/{id}/like/`
**Then** un VideoLike viene creato (FR28)
**And** un secondo like dallo stesso utente ritorna errore 409 (IntegrityError → `{code, detail}`)

**Given** un utente autenticato
**When** chiama `DELETE /api/videos/{id}/like/`
**Then** il VideoLike viene rimosso (unlike)

**Given** un utente autenticato
**When** chiama `POST /api/comments/{id}/like/`
**Then** un CommentLike viene creato (FR27)
**And** un secondo like dallo stesso utente ritorna errore 409

**Given** un utente autenticato
**When** chiama `DELETE /api/comments/{id}/like/`
**Then** il CommentLike viene rimosso (unlike)

**Given** il `VideoOutputSerializer`
**When** serializza un video
**Then** include `like_count` (intero, annotazione `Count`) e `is_liked_by_me` (booleano, relativo all'utente autenticato)

**Given** il `CommentSerializer` (output)
**When** serializza un commento
**Then** include `like_count` (intero) e `is_liked_by_me` (booleano)

### Story 3.2: UI Like su Clip e Commenti Frontend

As a utente registrato,
I want mettere e togliere like a clip e commenti con feedback visivo immediato,
So that posso esprimere apprezzamento e contribuire alla promozione dei migliori commenti.

**Acceptance Criteria:**

**Given** la pagina dettaglio clip
**When** l'utente clicca il bottone like sulla clip
**Then** il like viene registrato con optimistic update (FR28)
**And** il contatore like si aggiorna immediatamente
**And** in caso di errore, il like viene rollbackato

**Given** la sezione commenti
**When** l'utente clicca il bottone like su un commento
**Then** il like viene registrato con optimistic update (FR27)
**And** il contatore like sul commento si aggiorna immediatamente

**Given** un utente che ha già messo like
**When** clicca nuovamente il bottone like
**Then** il like viene rimosso (toggle unlike)
**And** il contatore si decrementa

**Given** un utente sulla pagina dettaglio clip (mobile o desktop)
**When** fa double-tap sul video
**Then** viene registrato un like con la stessa logica del bottone (FR28)
**And** un'animazione cuore appare brevemente al centro del video come feedback visivo

**Given** i nuovi hook frontend
**When** vengono creati
**Then** `useVideoLike` e `useVideoUnlike` esistono in `use-videos.ts` con optimistic update pattern
**And** `useCommentLike` e `useCommentUnlike` esistono in `use-comments.ts` con optimistic update pattern
**And** le query keys sono definite in `query-keys.ts`
**And** i tipi `Video` e `Comment` in `src/types/` includono `like_count` e `is_liked_by_me`

### Story 3.3: Popup Overlay con Dati Reali e Sidebar Dinamica

As a spettatore,
I want vedere i commenti più likati apparire come popup durante la riproduzione e nella sidebar,
So that scopro le reazioni migliori della community ancorati al momento esatto.

**Acceptance Criteria:**

**Given** una clip con commenti temporizzati che hanno ricevuto like
**When** il frontend carica la pagina dettaglio clip
**Then** un endpoint backend ritorna i popup data: per ogni timestamp con almeno 1 commento likato, il commento con più like (FR31, FR34)
**And** i dati sono pre-caricati in una singola chiamata API (NFR8)

**Given** il video in riproduzione
**When** il playback raggiunge un timestamp con un popup disponibile
**Then** il popup overlay appare in alto a destra con username, timestamp badge e testo del commento (FR32)
**And** il popup scompare dopo 3 secondi con animazione fade-out Framer Motion (FR33)
**And** la latenza tra timestamp e popup è < 200ms (NFR8)

**Given** un commento con 0 like
**When** il sistema calcola i popup
**Then** quel commento NON diventa popup (soglia minima 1 like) (FR34)

**Given** la Sidebar Dinamica (desktop ≥1280px)
**When** viene renderizzata
**Then** mostra i commenti con più like per la clip corrente, ordinati per like count (FR35)
**And** NON più per data come proxy (aggiornamento dal workaround attuale)

**Given** un commento che era popup e viene disabilitato dalla moderazione
**When** il sistema ricalcola
**Then** il prossimo commento con più like per quel timestamp diventa il nuovo popup (FR36)

### Story 3.4: Aggiornamento Algoritmo Spareggio Contest con Like

As a sistema,
I want che l'algoritmo di spareggio contest usi i like reali invece dei commenti come fallback,
So that la classifica contest riflette il reale engagement della community.

**Acceptance Criteria:**

**Given** l'algoritmo di spareggio in `desempate.py`
**When** calcola il vincitore in caso di parimerito
**Then** usa il peso 20% basato su `VideoLike.count` per video (non più commenti come fallback) (FR42a)
**And** i pesi restano: 50% numero voti, 30% visualizzazioni, 20% like

**Given** un video senza like
**When** il sistema calcola lo spareggio
**Then** il peso like contribuisce 0 senza errori

### Story 3.5: Comment Markers sulla Timeline del Player (Opzionale)

As a spettatore,
I want vedere dei marker luminosi sulla barra di progresso del player nei punti dove ci sono commenti temporizzati,
So that posso scoprire a colpo d'occhio dove si concentra la conversazione e saltare ai momenti più commentati.

**Acceptance Criteria:**

**Given** una clip con commenti temporizzati
**When** il player viene renderizzato
**Then** sulla progress bar appaiono dot luminosi (gradiente viola→ciano) nelle posizioni corrispondenti ai timestamp dei commenti
**And** i dot usano posizionamento percentuale (`left: (timestamp / duration) * 100%`)

**Given** un utente che fa hover su un dot marker
**When** il tooltip appare
**Then** mostra il testo del commento con più like per quel timestamp (o il primo se nessun like)
**And** mostra il timestamp formattato (es. "0:18")

**Given** un utente che clicca su un dot marker
**When** il click viene registrato
**Then** il video salta al timestamp corrispondente e inizia la riproduzione

**Given** una clip senza commenti temporizzati
**When** il player viene renderizzato
**Then** nessun marker appare sulla progress bar

**Nota:** Questa story è opzionale e può essere implementata come enhancement post-Epic 3. I dati necessari (commenti per timestamp) sono già disponibili dall'endpoint popup data della Story 3.3.

---

## Epic 4: Contest Settimanale

Gli utenti partecipano a contest settimanali automatici caricando clip con tag. Votano 1-5 stelle, vedono la classifica in tempo reale e il vincitore. L'admin gestisce i contest da Django Admin.

### Story 4.1: Backend Contest Settimanale — Endpoint e Listing

As a utente registrato,
I want vedere i contest settimanali disponibili e i loro dettagli,
So that posso decidere a quale contest partecipare.

**Acceptance Criteria:**

**Given** un utente autenticato
**When** chiama `GET /api/contests/`
**Then** riceve la lista paginata dei contest (attivi e chiusi) con campi: id, name, tag, start_date, end_date, is_closed, winner (FR38)

**Given** un utente che carica una clip con tag "clutch"
**When** la clip viene salvata
**Then** viene auto-assegnata al contest settimanale corrente per quel tag via `get_or_create_current_contest('clutch')` (FR39a, FR39b)

**Given** nessun contest attivo per il tag "funny" nella settimana corrente
**When** un utente carica una clip con tag "funny"
**Then** un nuovo contest settimanale viene creato automaticamente (FR39a)

**Given** un contest settimanale scaduto
**When** APScheduler esegue `close_contests` (giovedì 11:33 UTC)
**Then** il contest viene chiuso, il vincitore viene assegnato (media voti + spareggio se parimerito) (FR41a, FR42a)
**And** la chiusura è idempotente (ri-esecuzione non cambia risultato)

### Story 4.2: Votazione Contest e Classifica Frontend

As a utente registrato,
I want votare le clip in un contest e vedere la classifica,
So that posso partecipare attivamente e seguire la competizione.

**Acceptance Criteria:**

**Given** un utente autenticato che visualizza un contest attivo
**When** accede alla pagina contest
**Then** vede la lista delle clip partecipanti con player embedded e sistema di voto 1-5 stelle (FR40a)

**Given** un utente che vota una clip nel contest
**When** seleziona un rating da 1 a 5 stelle
**Then** il voto viene registrato (un voto per utente per clip, `unique_together` enforced) (FR40a, NFR13)
**And** il feedback visivo conferma il voto

**Given** un utente che ha già votato una clip
**When** tenta di votare di nuovo
**Then** il frontend mostra il voto esistente con UI disabilitata (NFR13)

**Given** un utente che visualizza un contest (attivo o chiuso)
**When** accede alla pagina classifica
**Then** vede le clip ordinate per media voti con posizione in classifica (FR43a)
**And** per contest chiusi, il vincitore è evidenziato

**Given** la pagina contest nel frontend
**When** viene riscritta
**Then** mostra: lista contest attivi, lista contest chiusi con vincitori, pagina dettaglio singolo contest con clip + voto + classifica
**And** utilizza `isError` + `<ErrorMessage onRetry={refetch} />`

---

## Epic 5: Notifiche In-App

Gli utenti ricevono notifiche per commenti ricevuti, like ricevuti, commenti promossi a popup, eventi contest. Vedono il badge non-lette nella sidebar e la lista notifiche completa.

### Story 5.1: Modello Notification e API Backend

As a sviluppatore,
I want il modello Notification con endpoint REST e creazione automatica per eventi chiave,
So that il sistema può tracciare e servire notifiche agli utenti.

**Acceptance Criteria:**

**Given** il modello `Notification` non esistente
**When** viene creato in `cs_clips/models/notification.py`
**Then** ha campi: `recipient` (FK User), `sender` (FK User nullable), `type` (CharField choices: comment_received, like_received, comment_promoted, contest_opened, bracket_invite, bracket_turn, contest_results), `is_read` (BooleanField default False), `created_at` (DateTimeField), `video` (FK nullable), `comment` (FK nullable), `contest` (FK nullable) (D1)
**And** NON usa `GenericForeignKey`
**And** ha `related_name` su ogni FK e `help_text` in italiano
**And** è registrato in `admin.py` e esportato da `models/__init__.py`

**Given** un utente autenticato
**When** chiama `GET /api/notifications/`
**Then** riceve la lista paginata delle proprie notifiche ordinate per `-created_at` (FR51)

**Given** un utente autenticato
**When** chiama `GET /api/notifications/unread-count/`
**Then** riceve `{count: N}` con il numero di notifiche non lette (FR52)

**Given** un utente autenticato
**When** chiama `POST /api/notifications/{id}/mark-read/`
**Then** la notifica viene marcata come letta (`is_read=True`)

**Given** un utente autenticato
**When** chiama `POST /api/notifications/mark-all-read/`
**Then** tutte le notifiche non lette vengono marcate come lette

**Given** un evento che genera notifica (commento ricevuto, like su clip/commento, commento promosso a popup, contest aperto)
**When** l'evento si verifica
**Then** una `Notification` viene creata automaticamente per il destinatario (FR50)

### Story 5.2: Frontend Notifiche — Pagina, Badge e Polling

As a utente registrato,
I want vedere un badge con le notifiche non lette e consultare la lista completa,
So that sono sempre aggiornato su cosa succede con le mie clip e i miei commenti.

**Acceptance Criteria:**

**Given** un utente autenticato
**When** è su qualsiasi pagina dell'app
**Then** vede un'icona campanella nella sidebar (desktop) / header (mobile) con badge numerico delle non lette (FR52)
**And** il conteggio è aggiornato via polling ogni 15 secondi (`refetchInterval: 15000`) (D1)

**Given** un utente che clicca sulla campanella
**When** naviga a `/notifiche`
**Then** vede la lista completa delle notifiche con: icona tipo, testo descrittivo ("Marco ha commentato al secondo 0:18 della tua clip"), timestamp relativo (FR51)
**And** le notifiche non lette sono visivamente distinte
**And** la pagina ha `isError` + `<ErrorMessage onRetry={refetch} />`

**Given** un utente sulla pagina notifiche
**When** clicca una notifica
**Then** viene marcata come letta e naviga al contenuto collegato (clip, commento, contest)

**Given** un utente sulla pagina notifiche
**When** clicca "Segna tutte come lette"
**Then** tutte le notifiche vengono marcate come lette e il badge si azzera

**Given** i nuovi moduli frontend
**When** vengono creati
**Then** `src/lib/api/notifications.ts` con metodi getAll, getUnreadCount, markRead, markAllRead
**And** `src/lib/hooks/use-notifications.ts` con `useNotifications` (polling 15s), `useUnreadCount`, `useMarkRead`, `useMarkAllRead`
**And** `src/types/notification.ts` con tipo `Notification`
**And** query keys in `query-keys.ts`: `notifications.all`, `notifications.unreadCount`

---

## Epic 6: Contest Bracket Champions League

L'admin crea tornei bracket da Django Admin. Gli utenti si iscrivono inviando clip, votano nei matchup 1v1, seguono la progressione nell'albero grafico interattivo. Il vincitore di ogni matchup avanza per media voti. Il vincitore finale riceve un premio.

### Story 6.1: Modelli Bracket Backend e Logica Turni

As a sviluppatore,
I want i modelli Bracket, ContestEntry e Matchup con logica di progressione turni,
So that il sistema può gestire tornei a eliminazione diretta.

**Acceptance Criteria:**

**Given** i modelli bracket non esistenti
**When** vengono creati in `cs_clips/models/`
**Then** `Bracket` ha campi: name, description, status (choices: registration/active/completed), max_participants, current_round, created_by (FK User), created_at, prize_description
**And** `ContestEntry` ha campi: bracket (FK Bracket), user (FK User), video (FK Video), created_at, con `unique_together = ('bracket', 'user')`
**And** `Matchup` ha campi: bracket (FK Bracket), round_number, position, entry_1 (FK ContestEntry nullable), entry_2 (FK ContestEntry nullable), winner (FK ContestEntry nullable), is_completed (BooleanField)
**And** tutti hanno `related_name`, `help_text` in italiano, registrazione in `admin.py`

**Given** un bracket con N partecipanti iscritti
**When** l'admin avvia il torneo
**Then** il sistema genera automaticamente il bracket a eliminazione diretta (matchup per ogni coppia del primo turno) (FR40b)
**And** partecipanti dispari ricevono un "bye" (avanzamento automatico)

**Given** un matchup completato (entrambe le clip hanno ricevuto voti)
**When** l'admin chiude il matchup
**Then** il vincitore è la clip con media voti più alta (FR43b)
**And** il vincitore avanza al matchup successivo nel turno seguente

**Given** il turno finale completato
**When** l'ultimo matchup viene chiuso
**Then** il bracket status diventa "completed" e il vincitore finale è determinato (FR44b)

### Story 6.2: API Bracket e Votazione Matchup

As a utente registrato,
I want iscrivermi a un bracket, votare nei matchup e vedere la progressione,
So that posso partecipare alla competizione Champions League.

**Acceptance Criteria:**

**Given** un utente autenticato e un bracket in stato "registration"
**When** chiama `POST /api/brackets/{id}/enter/` con un video_id
**Then** viene creata una ContestEntry (FR39c)
**And** un'iscrizione duplicata ritorna errore 409

**Given** un utente autenticato e un matchup attivo
**When** chiama `POST /api/brackets/matchups/{id}/vote/` con rating 1-5
**Then** il voto viene registrato (un voto per utente per matchup) (FR42b)
**And** il voto è basato solo sulla media voti interni al matchup (nessun fattore esterno) (FR43b)

**Given** un utente autenticato
**When** chiama `GET /api/brackets/{id}/`
**Then** riceve i dettagli del bracket con stato, turno corrente, lista matchup per turno, risultati (FR44)

**Given** un utente autenticato
**When** chiama `GET /api/brackets/`
**Then** riceve la lista paginata dei bracket (attivi + completati) (FR38)

**Given** dominio API separato per brackets
**When** gli endpoint vengono creati
**Then** risiedono in `cs_clips/api/brackets/` con views, serializers propri (D2)
**And** route registrate in `cs_clips/urls.py`

### Story 6.3: UI Bracket — Albero Interattivo e Pagina Torneo

As a utente registrato,
I want visualizzare il bracket come albero grafico interattivo e votare nei matchup,
So that posso seguire la competizione e partecipare alle votazioni.

**Acceptance Criteria:**

**Given** un utente che accede alla pagina di un bracket
**When** il bracket è visualizzato
**Then** mostra un albero grafico interattivo stile torneo con scontri, clip passate e risultati per turno (FR41b)
**And** usa una libreria React dedicata per bracket visualization (es. react-brackets, bracketry)

**Given** un matchup attivo nell'albero
**When** l'utente clicca su un matchup
**Then** vede le due clip embedded con player e il sistema di voto 1-5 stelle (FR42b)

**Given** un matchup completato
**When** visualizzato nell'albero
**Then** mostra il vincitore evidenziato e il punteggio medio di entrambe le clip

**Given** un bracket completato
**When** l'utente visualizza la pagina
**Then** vede il vincitore finale con il premio indicato (FR44b)
**And** l'intero albero è navigabile per rivedere tutti i matchup passati

**Given** i nuovi moduli frontend
**When** vengono creati
**Then** `src/lib/api/brackets.ts` con metodi CRUD + enter + vote
**And** `src/lib/hooks/use-brackets.ts` con hook per lista, dettaglio, iscrizione, voto
**And** `src/types/bracket.ts` con tipi Bracket, ContestEntry, Matchup
**And** componenti in `src/components/brackets/` per albero, matchup card, voto
**And** pagina `/contest/bracket/[id]/page.tsx`
**And** `isError` + `<ErrorMessage onRetry={refetch} />` su ogni pagina
