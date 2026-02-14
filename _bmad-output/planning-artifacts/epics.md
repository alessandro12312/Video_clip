---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories
  - step-04-final-validation
workflow_completed: true
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

**Gestione Utenti (FR1-FR6):**
- FR1: Utente non registrato può creare un account con username, email e password
- FR2: Utente registrato può autenticarsi con le proprie credenziali
- FR3: Utente registrato può visualizzare e modificare il proprio profilo pubblico
- FR4: Utente registrato può seguire altri utenti
- FR5: Utente registrato può smettere di seguire utenti che segue
- FR6: Utente registrato può visualizzare le proprie liste follower e following

**Creazione & Gestione Contenuti (FR7-FR16):**
- FR7: Utente registrato può caricare una clip video (durata 10s-1min)
- FR8: Il sistema valida la durata della clip e rifiuta video fuori range con messaggio di errore specifico
- FR9: Il sistema valida il formato della clip e fornisce errore specifico per formati non supportati
- FR10: Il sistema converte le clip caricate in un formato ottimizzato più leggero
- FR11: Utente registrato può impostare titolo e tag tipo per la clip caricata
- FR12: Utente registrato può impostare il permesso allow_download per la propria clip
- FR13: Utente registrato può scaricare le proprie clip
- FR14: Utente registrato può scaricare clip altrui quando allow_download è abilitato
- FR15: Il sistema archivia le clip convertite su storage blob esterno
- FR16: Il sistema mostra una modale di errore con opzione "Riprova" quando l'upload fallisce

**Scoperta & Fruizione Contenuti (FR17-FR22):**
- FR17: Utente registrato può visualizzare un feed Home con le clip degli utenti seguiti
- FR18: Utente può visualizzare la pagina dettaglio clip con player, commenti e metadati
- FR19: Le pagine dettaglio clip sono accessibili tramite URL diretto per la condivisione
- FR20: Il sistema genera link preview ricche (titolo, thumbnail) per gli URL delle clip condivisi su piattaforme esterne
- FR21: Il feed presenta le clip come card con thumbnail, titolo e metadati
- FR22: Utente può navigare dalla card nel feed alla pagina dettaglio della clip

**Sistema Commenti & Interazioni (FR23-FR30):**
- FR23: Utente registrato può pubblicare un commento su una clip senza timestamp
- FR24: Utente registrato può pubblicare un commento temporizzato su una clip con timestamp specifico
- FR25: Il sistema pre-suggerisce il timestamp corrente quando l'utente pausa il video e inizia a commentare
- FR26: Utente può rimuovere il timestamp pre-suggerito per pubblicare un commento normale
- FR27: Utente registrato può mettere like a un commento
- FR28: Utente registrato può mettere like a una clip
- FR29: La pagina dettaglio mostra tutti i commenti in vista gerarchica
- FR30: La pagina dettaglio offre due viste commenti: "Tutti" (cronologica) e "Nel video" (solo temporizzati, ordinati per timestamp)

**Popup & Loop di Engagement (FR31-FR36):**
- FR31: Il sistema identifica il commento con più like per ogni timestamp di una clip
- FR32: Durante la riproduzione video, popup overlay mostrano il commento con più like per il timestamp corrente
- FR33: I popup overlay scompaiono dopo pochi secondi
- FR34: I popup richiedono una soglia minima di 1 like per essere promossi
- FR35: La Sidebar Dinamica mostra i commenti con più like per la clip corrente
- FR36: Quando un commento viene disabilitato dalla moderazione, il sistema ricalcola il prossimo commento con più like per quel timestamp

**Sistema Contest (FR37-FR44):**
- FR37: Admin o Moderatore può creare un contest
- FR38: Utente registrato può visualizzare i contest disponibili
- FR39: Utente registrato può iscriversi a un contest inviando una clip
- FR40: Il sistema genera un bracket a eliminazione diretta per i partecipanti del contest
- FR41: Il contest mostra un albero grafico interattivo del bracket (stile torneo, con visualizzazione scontri, clip passate e risultati)
- FR42: Utente registrato può votare da 1 a 5 stelle sulle clip di un matchup del contest
- FR43: Il sistema calcola la media dei voti per matchup e fa avanzare il vincitore
- FR44: Utente può visualizzare stato del contest, risultati passati e progressione nel bracket

**Amministrazione & Moderazione (FR45-FR52):**
- FR45: Moderatore può disabilitare commenti inappropriati
- FR46: Admin può eliminare video
- FR47: Admin può sospendere account utente
- FR48: Admin può promuovere utenti tra ruoli (es. toconfirm → user)
- FR49: Admin può visualizzare la lista dei video per utente
- FR50: Il sistema invia notifiche in-app per eventi chiave (commento ricevuto, like ricevuto, commento promosso a popup, invito contest, turno contest disponibile)
- FR51: Utente registrato può visualizzare la propria lista notifiche
- FR52: Il sistema mostra un badge con il conteggio delle notifiche non lette

### NonFunctional Requirements

**Performance:**
- NFR1: First Contentful Paint < 1.5s (pagine pubbliche con SSR)
- NFR2: Time to Interactive < 3s (priorità al player video)
- NFR3: Video Start Playback < 2s (post-conversione, formato leggero)
- NFR4: Lighthouse Score > 80
- NFR5: Risposta API lettura < 500ms (feed, commenti, notifiche)
- NFR6: Risposta API scrittura < 1s (like, commenti, follow)
- NFR7: Upload video < 30s per 500MB su connessione stabile (escl. conversione)
- NFR8: Conversione video ffmpeg < 2x durata clip
- NFR9: Latenza popup overlay vs timestamp < 200ms (dati pre-caricati in singola chiamata API)
- NFR10: Progress bar upload con aggiornamento in tempo reale

**Security:**
- NFR11: Autenticazione JWT con refresh token
- NFR12: CORS_ALLOWED_ORIGINS restrittivo (solo dominio Vercel frontend)
- NFR13: Validazione input su tutti gli endpoint (durata clip, formato file, lunghezza commenti)
- NFR14: Vincolo integrità voto contest: un solo voto per utente per matchup (constraint DB unique + UI disabilitata)
- NFR15: Upload limitato a formati video whitelist: MP4, MOV, AVI, MKV, WebM
- NFR16: Limite dimensione file upload: max 500MB
- NFR17: Limiti lunghezza input: commenti max 500 caratteri, titolo clip max 100 caratteri
- NFR18: Password con requisiti minimi (lunghezza, complessità base)
- NFR19: Protezione CSRF sui form
- NFR20: Sanitizzazione testo commenti per prevenire XSS

**Resilienza & Error Handling:**
- NFR21: Fallimento conversione ffmpeg: mantieni file originale, 1 retry automatico, notifica utente su fallimento definitivo
- NFR22: Upload diretto a Django per file video grandi (bypass Next.js API Routes limite 4MB)
- NFR23: Nessun target di uptime rigido per fase amici

**Scalabilità:**
- NFR24: Supporto fino a 50 utenti concorrenti senza degradazione
- NFR25: Storage 100GB Vercel Blob con video convertiti in formato leggero
- NFR26: Architettura che permette evoluzione verso async (Celery), proxy API, WebSocket senza riscritture maggiori

**Accessibilità:**
- NFR27: WCAG 2.1 livello AA base
- NFR28: Contrasti di colore sufficienti su testi e controlli
- NFR29: Navigazione completa via keyboard (tab, enter, escape)
- NFR30: Alt text su thumbnail e immagini
- NFR31: Player video con controlli accessibili via keyboard
- NFR32: Label sui form (registrazione, login, upload, commenti)

**Integrazione:**
- NFR33: Django REST API — comunicazione HTTP/JSON, JWT auth, CORS diretto, upload video diretto
- NFR34: Vercel Blob — upload/download via SDK Vercel, gestione URL pubblici per streaming
- NFR35: ffmpeg — conversione server-side H.264/MP4 ottimizzato, sincrono, retry su fallimento
- NFR36: OpenGraph — SSR per generazione OG tags su pagine clip pubbliche

### Additional Requirements

**Da Architecture — Gap backend critici (modelli/endpoint mancanti):**
- Nuovo modello CommentLike (user FK + comment FK, unique_together, CASCADE) — blocca like commenti, calcolo popup, sidebar dinamica
- Nuovo modello ClipLike/VideoLike (user FK + video FK, unique_together, CASCADE) — blocca like su clip
- Nuovo modello Notification (recipient FK, type enum, content text, related_object_id, read bool, created_at) — blocca notifiche in-app
- Nuovo campo allow_download su Video (booleano, default True) — blocca download clip da altri
- Nuovo campo is_disabled su Comment (booleano, default False) — blocca moderazione commenti (soft-delete)
- Nuovo endpoint GET /api/videos/{id}/popup-comments/ — blocca popup overlay nel player
- Batch migration unica "PRD alignment" per tutti i nuovi modelli
- Rating esistente mantenuto per contest (Release B), ClipLike aggiunto per feed (Release A)

**Da Architecture — Decisioni architetturali che impattano le stories:**
- JWT storage: access in memory + refresh in localStorage, stato "authenticating" con GradientSpinner
- Route protection: Middleware + AuthProvider doppio layer
- API client: Axios interceptors con refresh mutex/queue
- Optimistic UI: React Query useMutation pattern per commenti, like, follow
- Player micro-sistema: VideoPlayerProvider con ref pattern (currentTime come ref, NON state)
- Server Components vs Client Components: "Server fetch, Client render" pattern
- React Query caching strategy con staleTime per risorsa
- Upload: doppio canale (API CORS + upload diretto a Django per file grandi)
- Vercel Blob integrato in Fase 1 (Django → ffmpeg → Blob)
- Sequenza implementazione: backend evolution → auth → API client → upload → player → feed → commenti → notifiche/admin

**Da Architecture — Disallineamento backend esistente ↔ PRD:**
- Rating clip: backend ha rating 1-5, PRD vuole N/A nel feed — ripensare uso modello Rating (solo contest)
- Contest: backend ha settimanali automatici, PRD vuole bracket eliminazione diretta — evoluzione significativa
- Like clip e commenti: non esistono nel backend attuale — nuovi modelli necessari

**Da UX — Requisiti design che impattano implementazione:**
- Dark mode come default (Tailwind class strategy)
- Glassmorphism sui popup overlay (backdrop-blur + bg-opacity)
- Micro-animazioni a 3 tier: Tier 1+2 con Framer Motion, Tier 3 con CSS/Tailwind
- GradientSpinner unico per stato authenticating
- Visual DNA con gradiente ricorrente (viola→ciano o rosso→arancione) su progress bar, bordi card, spinner, popup
- CTA contestuale empatico sulla pagina pubblica (non modale bloccante)
- Comment markers sulla timeline (dot luminosi gradiente) con hover preview
- Desktop-first layout tre colonne, mobile bottom-bar 4 tab
- Doppio tap per like su mobile, click su desktop
- Skeleton loading per card clip
- Toast Sonner solo per errori e conferme importanti

### FR Coverage Map

| FR | Epic | Descrizione |
|----|------|-------------|
| FR1 | Epic 1 | Registrazione account |
| FR2 | Epic 1 | Login/autenticazione |
| FR3 | Epic 1 | Visualizza/modifica profilo |
| FR4 | Epic 1 | Follow utenti |
| FR5 | Epic 1 | Unfollow utenti |
| FR6 | Epic 1 | Liste follower/following |
| FR7 | Epic 2 | Upload clip video |
| FR8 | Epic 2 | Validazione durata clip |
| FR9 | Epic 2 | Validazione formato clip |
| FR10 | Epic 2 | Conversione formato ottimizzato |
| FR11 | Epic 2 | Titolo e tag clip |
| FR12 | Epic 2 | Permesso allow_download |
| FR13 | Epic 2 | Download proprie clip |
| FR14 | Epic 2 | Download clip altrui |
| FR15 | Epic 2 | Storage blob esterno |
| FR16 | Epic 2 | Modale errore upload + Riprova |
| FR17 | Epic 2 | Feed Home (following) |
| FR18 | Epic 2 | Pagina dettaglio clip |
| FR19 | Epic 2 | URL diretto clip |
| FR20 | Epic 2 | Link preview OG tags |
| FR21 | Epic 2 | Card feed con thumbnail |
| FR22 | Epic 2 | Navigazione card→dettaglio |
| FR23 | Epic 3 | Commento senza timestamp |
| FR24 | Epic 3 | Commento temporizzato |
| FR25 | Epic 3 | Timestamp pre-suggerito alla pausa |
| FR26 | Epic 3 | Rimozione timestamp |
| FR27 | Epic 3 | Like commento |
| FR28 | Epic 3 | Like clip |
| FR29 | Epic 3 | Vista gerarchica commenti |
| FR30 | Epic 3 | Due viste commenti (Tutti/Nel video) |
| FR31 | Epic 3 | Calcolo top comment per timestamp |
| FR32 | Epic 3 | Popup overlay durante riproduzione |
| FR33 | Epic 3 | Popup scompaiono dopo pochi secondi |
| FR34 | Epic 3 | Soglia minima 1 like per popup |
| FR35 | Epic 3 | Sidebar Dinamica |
| FR36 | Epic 3 | Ricalcolo popup post-moderazione |
| FR37 | Epic 5 | Creazione contest (admin/mod) |
| FR38 | Epic 5 | Visualizzazione contest |
| FR39 | Epic 5 | Iscrizione contest con clip |
| FR40 | Epic 5 | Generazione bracket |
| FR41 | Epic 5 | Albero grafico interattivo |
| FR42 | Epic 5 | Votazione 1-5 stelle matchup |
| FR43 | Epic 5 | Calcolo media e avanzamento |
| FR44 | Epic 5 | Stato/risultati contest |
| FR45 | Epic 4 | Disabilita commenti (mod) |
| FR46 | Epic 4 | Elimina video (admin) |
| FR47 | Epic 4 | Sospendi account (admin) |
| FR48 | Epic 4 | Promuovi ruoli utente |
| FR49 | Epic 4 | Lista video per utente |
| FR50 | Epic 4 | Notifiche in-app |
| FR51 | Epic 4 | Lista notifiche utente |
| FR52 | Epic 4 | Badge notifiche non lette |
| UX-1 | Epic 1 | Header desktop con menu profilo (avatar + dropdown logout/impostazioni) |
| UX-2 | Epic 1 | Spinner animato del brand + transizione post-login |
| UX-3 | Epic 4 | Layout dashboard admin frontend (tabelle, ricerca, azioni, protezione ruolo) |

## Epic List

### Epic 1: Autenticazione & Profili Utente
Gli utenti possono registrarsi, autenticarsi, gestire il proprio profilo e seguire altri utenti. È la base per ogni interazione sulla piattaforma. Include evoluzione backend (batch migration) come story iniziale di setup, menu profilo desktop e spinner animato del brand.
**FRs coperti:** FR1, FR2, FR3, FR4, FR5, FR6 + UX cross-cutting (header desktop, spinner brand)

### Epic 2: Creazione & Gestione Clip
Gli utenti possono caricare clip video (10s-1min), il sistema le valida, converte e archivia. Gli utenti possono scaricare le proprie clip e quelle altrui (se permesso). Il feed mostra le clip degli utenti seguiti come card navigabili. La pagina dettaglio clip fornisce il player base predisposto per accogliere il sistema commenti/popup dell'Epic 3.
**FRs coperti:** FR7, FR8, FR9, FR10, FR11, FR12, FR13, FR14, FR15, FR16, FR17, FR18, FR19, FR20, FR21, FR22

### Epic 3: Commenti Temporizzati & Popup
Gli utenti possono commentare le clip (con o senza timestamp), mettere like a clip e commenti, e vedere i commenti più apprezzati diventare popup overlay nel player. È il cuore differenziante del prodotto — il player base dell'Epic 2 prende vita con il sistema integrato commenti/popup/sidebar.
**FRs coperti:** FR23, FR24, FR25, FR26, FR27, FR28, FR29, FR30, FR31, FR32, FR33, FR34, FR35, FR36

### Epic 4: Notifiche & Amministrazione
Gli utenti ricevono notifiche per eventi importanti (commenti ricevuti, like, popup promossi). Admin e moderatori possono gestire contenuti e utenti da una dashboard dedicata con interfaccia completa (tabelle, ricerca, azioni) e protezione route per ruolo.
**FRs coperti:** FR45, FR46, FR47, FR48, FR49, FR50, FR51, FR52 + interfaccia admin frontend

### Epic 5: Sistema Contest
Admin/moderatori possono creare contest, gli utenti possono iscriversi con clip, votare nei matchup, e seguire l'avanzamento del bracket a eliminazione diretta con albero grafico interattivo. Release B separata.
**FRs coperti:** FR37, FR38, FR39, FR40, FR41, FR42, FR43, FR44

---

## Epic 1: Autenticazione & Profili Utente

Gli utenti possono registrarsi, autenticarsi, gestire il proprio profilo e seguire altri utenti. È la base per ogni interazione sulla piattaforma. Include evoluzione backend (batch migration) come story iniziale di setup.

### Story 1.1: Evoluzione Backend — Migration PRD Alignment

As a developer,
I want il backend allineato ai requisiti del PRD con i nuovi modelli e campi,
So that il frontend possa integrarsi con tutti gli endpoint necessari.

**Acceptance Criteria:**

**Given** il backend Django esistente con i modelli attuali
**When** viene eseguita la batch migration "PRD alignment"
**Then** i seguenti modelli/campi sono creati:
- Modello `CommentLike` (user FK + comment FK, unique_together, CASCADE)
- Modello `ClipLike`/`VideoLike` (user FK + video FK, unique_together, CASCADE)
- Modello `Notification` (recipient FK, type enum, content text, related_object_id, read bool, created_at)
- Campo `allow_download` su Video (booleano, default True)
- Campo `is_disabled` su Comment (booleano, default False)
**And** l'endpoint `GET /api/videos/{id}/popup-comments/` è implementato e restituisce `{timestamp, comment_id, text, author, like_count}`
**And** gli endpoint per like clip, like commenti, notifiche sono implementati
**And** tutte le migration sono applicabili senza conflitti

### Story 1.2: Registrazione Utente

As a utente non registrato,
I want creare un account con username, email e password,
So that possa accedere alla piattaforma e interagire con la community.

**Acceptance Criteria:**

**Given** un utente non registrato sulla pagina `/registrati`
**When** compila username, email e password e invia il form
**Then** l'account viene creato e l'utente viene autenticato con JWT
**And** l'utente viene reindirizzato alla Home

**Given** un utente che inserisce un username o email già esistente
**When** invia il form di registrazione
**Then** viene mostrato un errore specifico ("Username già in uso" o "Email già registrata")

**Given** un utente che inserisce una password troppo corta o debole
**When** invia il form
**Then** viene mostrato un errore di validazione con requisiti minimi

### Story 1.3: Login e Gestione Sessione JWT

As a utente registrato,
I want autenticarmi con le mie credenziali e mantenere la sessione attiva,
So that possa accedere ai contenuti protetti senza riautenticarmi ad ogni visita.

**Acceptance Criteria:**

**Given** un utente registrato sulla pagina `/login`
**When** inserisce credenziali valide e invia il form
**Then** riceve JWT (access in memory, refresh in localStorage) e viene reindirizzato alla Home

**Given** un utente con refresh token valido in localStorage
**When** ricarica la pagina o torna al sito
**Then** il sistema mostra il GradientSpinner (stato "authenticating"), chiama `/api/token/refresh/`, ottiene un nuovo access token e autentica l'utente senza redirect al login

**Given** un utente non autenticato che tenta di accedere a route `(main)/*`
**When** il middleware intercetta la richiesta
**Then** viene reindirizzato a `/login`

**Given** un utente autenticato che fa una chiamata API e riceve 401
**When** l'Axios interceptor gestisce l'errore
**Then** il mutex/queue pattern triggera il refresh, le chiamate in coda attendono il nuovo token e vengono riprovate
**And** se il refresh fallisce, l'utente viene sloggato con toast "Sessione scaduta"

### Story 1.4: Profilo Utente Pubblico

As a utente registrato,
I want visualizzare e modificare il mio profilo pubblico,
So that gli altri utenti possano sapere chi sono e vedere le mie clip.

**Acceptance Criteria:**

**Given** un utente autenticato che naviga a `/profilo`
**When** la pagina si carica
**Then** vengono mostrati: username, avatar, bio, conteggio follower/following, lista clip caricate

**Given** un utente autenticato sulla pagina profilo
**When** modifica i propri dati (bio, avatar) e salva
**Then** le modifiche sono persistite e il profilo aggiornato è visibile

**Given** un utente che visita `/profilo/[username]` di un altro utente
**When** la pagina si carica
**Then** vengono mostrati: username, avatar, bio, conteggio follower/following, clip pubbliche dell'utente

### Story 1.5: Follow e Unfollow

As a utente registrato,
I want seguire e smettere di seguire altri utenti,
So that possa costruire il mio feed personalizzato con le clip che mi interessano.

**Acceptance Criteria:**

**Given** un utente autenticato che visualizza il profilo di un altro utente
**When** clicca il bottone "Segui"
**Then** inizia a seguire l'utente con feedback visivo immediato (optimistic UI)
**And** il conteggio follower/following si aggiorna

**Given** un utente che già segue un altro utente
**When** clicca il bottone "Smetti di seguire"
**Then** smette di seguire l'utente con feedback visivo immediato
**And** il conteggio si aggiorna

**Given** un errore durante l'operazione di follow/unfollow
**When** la chiamata API fallisce
**Then** l'UI fa rollback allo stato precedente e mostra un toast di errore

### Story 1.6: Liste Follower e Following

As a utente registrato,
I want visualizzare le mie liste follower e following,
So that possa vedere chi mi segue e chi seguo.

**Acceptance Criteria:**

**Given** un utente autenticato sulla propria pagina profilo
**When** clicca su "Follower" o "Following"
**Then** viene mostrata la lista degli utenti con username, avatar e bottone follow/unfollow

**Given** un utente che visualizza il profilo di un altro utente
**When** clicca su "Follower" o "Following"
**Then** viene mostrata la lista follower/following di quell'utente

### Story 1.7: Header Utente Desktop con Menu Profilo

As a utente autenticato su desktop,
I want avere un cerchietto avatar in alto a destra con un menu profilo,
So that possa accedere rapidamente al mio profilo, alle impostazioni e fare logout da qualsiasi pagina.

**Acceptance Criteria:**

**Given** un utente autenticato su viewport desktop (≥ 1024px)
**When** la pagina si carica
**Then** un cerchietto avatar dell'utente è visibile in alto a destra nel layout, posizionato sopra il contenuto principale (non nella sidebar)

**Given** un utente desktop che clicca direttamente sul cerchietto avatar
**When** il click viene registrato
**Then** l'utente viene reindirizzato a `/profilo` (il proprio profilo)

**Given** un utente desktop che clicca sulla freccia/chevron accanto al cerchietto avatar
**When** il dropdown si apre
**Then** vengono mostrate le voci:
- **Il mio profilo** (link a `/profilo`)
- **Impostazioni account** (link a `/impostazioni` — placeholder per ora)
- **Esci** (esegue logout e redirect a `/login`)

**Given** un utente su viewport mobile (< 1024px)
**When** la pagina si carica
**Then** il cerchietto avatar desktop NON è visibile (il menu profilo mobile nell'header rimane invariato)

**Given** un utente che clicca "Esci" dal menu desktop
**When** il logout viene eseguito
**Then** i token JWT vengono rimossi, l'utente viene reindirizzato a `/login` e viene mostrato un toast "Hai effettuato il logout"

### Story 1.8: Spinner Animato del Brand e Transizione Post-Login

As a utente,
I want vedere uno spinner animato unico del brand durante i caricamenti e un'animazione fluida dopo il login,
So that l'esperienza sia coerente con l'identità visiva della piattaforma e il passaggio tra stati sia piacevole.

**Acceptance Criteria:**

**Given** un utente che accede al sito con un refresh token valido
**When** il sistema è nello stato "authenticating" (refresh token in corso)
**Then** viene mostrato lo spinner animato del brand a schermo intero:
- Logo "V" o icona della piattaforma come elemento centrale
- Animazione con il gradiente DNA del brand (viola→ciano) — non un semplice anello rotante
- Pulsazione o morph fluido che trasmette attesa attiva
- Sfondo scuro coerente con il dark mode

**Given** un utente che completa il login con successo (form login o auto-refresh)
**When** l'autenticazione è confermata e il redirect a `/home` sta per avvenire
**Then** viene mostrata una transizione animata:
- Lo spinner/logo si trasforma o dissolve verso il contenuto della home
- Durata totale transizione: 800ms-1200ms (percepibile ma non lenta)
- L'animazione usa Framer Motion (Tier 1)

**Given** lo spinner del brand usato come loader generico
**When** viene utilizzato in contesti diversi (caricamento pagina, caricamento feed)
**Then** il componente `GradientSpinner` accetta una prop `variant`:
- `full` — a schermo intero (stato authenticating, primo caricamento)
- `inline` — dimensione ridotta per loading inline (dentro card, sezioni)

**Given** un utente con connessione veloce
**When** il login o il refresh avviene in < 300ms
**Then** l'animazione di transizione viene comunque mostrata per un minimo di 500ms per evitare flash visivi

### Story 1.9: Ricerca Utenti e Scoperta Profili

As a utente registrato,
I want cercare altri utenti per username tramite una barra di ricerca,
So that possa scoprire nuovi utenti da seguire e visitare i loro profili.

**Acceptance Criteria:**

**Given** un utente autenticato su qualsiasi pagina
**When** clicca sull'icona di ricerca o sulla barra di ricerca nell'header/sidebar
**Then** viene mostrato un campo di ricerca con placeholder "Cerca utenti..."

**Given** un utente che digita almeno 2 caratteri nel campo di ricerca
**When** il testo cambia (debounce 300ms)
**Then** il sistema chiama `GET /api/users/?search=<query>` e mostra i risultati in un dropdown:
- Ogni risultato mostra username
- Cliccando su un risultato si naviga al profilo dell'utente (`/profilo/{id}`)
- Se nessun risultato, mostra "Nessun utente trovato"

**Given** un utente che naviga al profilo di un altro utente
**When** la pagina profilo si carica
**Then** viene mostrato il bottone "Segui" / "Smetti di seguire" (dipendenza: Story 1.5)

**Given** il backend esistente (UserViewSet)
**When** il frontend invia `GET /api/users/?search=<query>`
**Then** il backend filtra gli utenti per username con `icontains` e restituisce la lista paginata

---

## Epic 2: Creazione & Gestione Clip

Gli utenti possono caricare clip video (10s-1min), il sistema le valida, converte e archivia. Gli utenti possono scaricare le proprie clip e quelle altrui (se permesso). Il feed mostra le clip degli utenti seguiti come card navigabili. La pagina dettaglio clip fornisce il player base predisposto per accogliere il sistema commenti/popup dell'Epic 3.

### Story 2.1: Upload Clip con Validazione

As a utente registrato,
I want caricare una clip video dalla mia galleria,
So that possa condividere i miei momenti di gioco con la community.

**Acceptance Criteria:**

**Given** un utente autenticato sulla pagina `/carica`
**When** seleziona un file video e compila titolo (max 100 char), tag tipo (clutch/funny/fail) e opzione allow_download
**Then** il file viene inviato direttamente a Django via upload CORS con progress bar in tempo reale

**Given** un file video con durata compresa tra 10s e 1min e formato nella whitelist (MP4, MOV, AVI, MKV, WebM) e dimensione < 500MB
**When** il backend riceve il file
**Then** la validazione passa e il processing inizia

**Given** un file video con durata fuori range (< 10s o > 1min)
**When** il backend valida il file
**Then** viene restituito errore specifico "Il video deve durare tra 10 secondi e 1 minuto"

**Given** un file in formato non supportato
**When** il backend valida il file
**Then** viene restituito errore specifico "Formato non supportato. Formati accettati: MP4, MOV, AVI, MKV, WebM"

**Given** un file che supera 500MB
**When** il backend valida il file
**Then** viene restituito errore specifico "Il file supera la dimensione massima di 500MB"

### Story 2.2: Conversione Video e Storage Vercel Blob

As a sistema,
I want convertire le clip in formato ottimizzato e archiviarle su Vercel Blob,
So that lo storage sia efficiente e il playback veloce per tutti gli utenti.

**Acceptance Criteria:**

**Given** una clip validata correttamente
**When** il backend avvia la conversione
**Then** ffmpeg converte il file in H.264/MP4 ottimizzato in tempo < 2x la durata della clip

**Given** un file convertito con successo
**When** il backend lo carica su Vercel Blob
**Then** il file viene archiviato con retry x3 (backoff esponenziale) e il `file_url` (blob URL) viene salvato nel modello Video
**And** i file temporanei locali vengono eliminati

**Given** un fallimento della conversione ffmpeg
**When** il sistema esegue il retry automatico (1 tentativo)
**Then** se il retry ha successo il flusso continua normalmente
**And** se il retry fallisce, il file originale viene mantenuto e l'utente riceve errore specifico

**Given** un fallimento dell'upload a Vercel Blob dopo 3 tentativi
**When** tutti i retry sono esauriti
**Then** il file convertito locale viene mantenuto come fallback, l'errore viene loggato e l'utente viene notificato

### Story 2.3: Gestione Errori Upload e Retry

As a utente registrato,
I want poter riprovare quando l'upload fallisce,
So that un errore temporaneo non mi faccia perdere il lavoro di preparazione della clip.

**Acceptance Criteria:**

**Given** un upload in corso che fallisce (errore di rete, timeout, errore server)
**When** l'upload si interrompe
**Then** viene mostrata una modale di errore con messaggio specifico e bottone "Riprova"

**Given** un utente che clicca "Riprova" nella modale di errore
**When** l'upload viene ritentato
**Then** il file viene reinviato con la stessa progress bar e gli stessi metadati (titolo, tag, allow_download)

**Given** un upload completato con successo
**When** il backend conferma il salvataggio
**Then** viene mostrato un toast "La tua clip è live!" e l'utente viene reindirizzato al proprio profilo o alla pagina della clip

### Story 2.4: Download Clip

As a utente registrato,
I want scaricare le mie clip e quelle di altri utenti (se permesso),
So that possa conservare i miei contenuti e condividerli su altre piattaforme.

**Acceptance Criteria:**

**Given** un utente autenticato sulla pagina dettaglio di una propria clip
**When** clicca il bottone "Scarica"
**Then** il download del file video inizia dal URL Vercel Blob

**Given** un utente autenticato sulla pagina dettaglio di una clip altrui con allow_download = true
**When** clicca il bottone "Scarica"
**Then** il download del file video inizia

**Given** un utente sulla pagina dettaglio di una clip altrui con allow_download = false
**When** visualizza la pagina
**Then** il bottone "Scarica" non è visibile

### Story 2.5: Feed Home (Following)

As a utente registrato,
I want vedere un feed con le clip degli utenti che seguo,
So that possa scoprire i nuovi contenuti delle persone che mi interessano.

**Acceptance Criteria:**

**Given** un utente autenticato che naviga a `/home`
**When** la pagina si carica
**Then** vengono mostrate le clip degli utenti seguiti come card con thumbnail, titolo, username autore, tag e data
**And** le card sono ordinate cronologicamente (più recenti prima)
**And** durante il caricamento vengono mostrate skeleton card animate

**Given** un utente che non segue nessuno
**When** naviga al feed Home
**Then** viene mostrato uno stato vuoto con suggerimento "Segui altri utenti per vedere le loro clip"

**Given** un feed con molte clip
**When** l'utente scorre verso il basso
**Then** le clip successive vengono caricate con infinite scroll (paginazione PAGE_SIZE=10)

### Story 2.6: Pagina Dettaglio Clip con Player Base

As a utente (autenticato o visitatore),
I want visualizzare una clip nella sua pagina dettaglio con player video,
So that possa guardare il contenuto in modo completo e immerso.

**Acceptance Criteria:**

**Given** un utente che naviga a `/clip/[id]`
**When** la pagina si carica
**Then** viene mostrato il player video HTML5 con controlli custom (play/pause/volume/fullscreen), progress bar, titolo clip, autore, tag, data
**And** il video usa `<video preload="metadata">` con src dal Vercel Blob CDN
**And** il player è predisposto architetturalmente per accogliere PopupOverlay, CommentMarkers e CommentForm dell'Epic 3 (VideoPlayerProvider con ref pattern)

**Given** un utente che clicca play
**When** il video inizia la riproduzione
**Then** il playback parte entro 2 secondi e la progress bar è seekable

**Given** un utente desktop
**When** visualizza la pagina dettaglio
**Then** il layout è a tre colonne: sidebar nav sinistra, player + metadati al centro, spazio sidebar destra (predisposto per sidebar dinamica commenti Epic 3)

**Given** un visitatore non autenticato che arriva tramite URL diretto
**When** la pagina si carica
**Then** la clip è visibile e riproducibile, ma le azioni (commenta, like) mostrano CTA di registrazione

### Story 2.7: Link Preview SSR per Condivisione Esterna

As a utente che condivide una clip,
I want che il link mostri una preview ricca su WhatsApp, Twitter e Discord,
So that le persone a cui mando il link vedano di cosa si tratta prima di cliccare.

**Acceptance Criteria:**

**Given** una pagina `/clip/[id]` generata con SSR (Server Component)
**When** il server renderizza la pagina
**Then** i meta tag OpenGraph sono generati con:
- `og:title` = titolo della clip
- `og:image` = thumbnail del video
- `og:description` = autore + tag
- `og:url` = URL canonico della clip

**Given** un utente che incolla un link clip su WhatsApp, Twitter o Discord
**When** la piattaforma esterna fetcha i meta tag
**Then** viene mostrata una preview ricca con titolo e anteprima visiva

---

## Epic 3: Commenti Temporizzati & Popup

Gli utenti possono commentare le clip (con o senza timestamp), mettere like a clip e commenti, e vedere i commenti più apprezzati diventare popup overlay nel player. È il cuore differenziante del prodotto — il player base dell'Epic 2 prende vita con il sistema integrato commenti/popup/sidebar.

### Story 3.1: Commenti Normali su Clip

As a utente registrato,
I want pubblicare commenti su una clip,
So that possa esprimere la mia reazione e interagire con il creator.

**Acceptance Criteria:**

**Given** un utente autenticato sulla pagina dettaglio di una clip
**When** scrive un commento (max 500 caratteri) nel form e clicca invio
**Then** il commento viene pubblicato con optimistic UI (appare immediatamente) e sincronizzato in background
**And** il testo è sanitizzato per prevenire XSS

**Given** un utente che pubblica un commento senza timestamp
**When** il commento viene salvato
**Then** appare nella vista "Tutti" dei commenti in ordine cronologico

**Given** un errore durante il salvataggio del commento
**When** la chiamata API fallisce
**Then** l'UI fa rollback (il commento scompare) e viene mostrato un toast di errore

**Given** un visitatore non autenticato
**When** tenta di commentare
**Then** viene mostrata una CTA di registrazione

### Story 3.2: Commenti Temporizzati con Timestamp Pre-compilato

As a utente registrato,
I want scrivere un commento ancorato a un momento specifico del video,
So that la mia reazione sia legata al secondo esatto che l'ha provocata.

**Acceptance Criteria:**

**Given** un utente che sta guardando un video e lo mette in pausa
**When** il video si ferma
**Then** il form commenti appare in posizione immediata con il timestamp corrente pre-compilato (es. "0:18") e il popup corrente resta visibile come contesto
**And** zero ritardo percepito tra la pausa e la disponibilità del form

**Given** un utente con il form commenti aperto e timestamp pre-compilato
**When** scrive il testo e invia
**Then** il commento viene salvato con il timestamp specificato
**And** appare sia nella vista "Tutti" che nella vista "Nel video"

**Given** un utente che vuole rimuovere il timestamp pre-suggerito
**When** clicca sulla X o rimuove il timestamp dal campo
**Then** il commento diventa un commento normale (senza timestamp)

**Given** un utente che modifica manualmente il timestamp
**When** inserisce un valore diverso da quello pre-compilato
**Then** il commento viene ancorato al timestamp modificato

### Story 3.3: Like su Clip e Commenti

As a utente registrato,
I want mettere like alle clip e ai commenti,
So that possa mostrare apprezzamento e contribuire a far emergere i contenuti migliori.

**Acceptance Criteria:**

**Given** un utente autenticato sulla pagina dettaglio di una clip
**When** clicca il bottone like (cuore) sulla clip
**Then** il like viene registrato con optimistic UI (cuore si riempie immediatamente)
**And** il conteggio like si aggiorna

**Given** un utente che ha già messo like a una clip
**When** clicca di nuovo il bottone like
**Then** il like viene rimosso (toggle) con optimistic UI

**Given** un utente autenticato che visualizza un commento
**When** clicca il bottone like sul commento
**Then** il like viene registrato con optimistic UI
**And** il conteggio like del commento si aggiorna

**Given** un errore durante l'operazione di like/unlike
**When** la chiamata API fallisce
**Then** l'UI fa rollback allo stato precedente

**Given** un utente su mobile
**When** esegue doppio tap sulla clip
**Then** viene registrato un like con animazione cuore

### Story 3.4: Viste Commenti (Tutti / Nel Video)

As a utente,
I want visualizzare i commenti in due modi diversi,
So that possa scegliere tra leggere tutti i commenti o solo quelli legati a momenti specifici del video.

**Acceptance Criteria:**

**Given** un utente sulla pagina dettaglio di una clip
**When** seleziona il tab "Tutti"
**Then** vengono mostrati tutti i commenti (con e senza timestamp) in ordine cronologico inverso in vista gerarchica

**Given** un utente sulla pagina dettaglio di una clip
**When** seleziona il tab "Nel video"
**Then** vengono mostrati solo i commenti temporizzati, ordinati per timestamp crescente
**And** ogni commento mostra il badge con il timestamp cliccabile

**Given** un utente che clicca sul badge timestamp di un commento nella vista "Nel video"
**When** il player riceve il comando seek
**Then** il video salta al timestamp indicato

### Story 3.5: Popup Overlay Temporizzati nel Player

As a spettatore,
I want vedere i commenti più apprezzati apparire come popup durante la riproduzione,
So that l'esperienza di visione sia arricchita dalle reazioni della community.

**Acceptance Criteria:**

**Given** una clip con commenti temporizzati che hanno almeno 1 like
**When** la pagina dettaglio si carica
**Then** i dati popup (timestamp, testo, autore, like_count) vengono pre-caricati in una singola chiamata API `GET /api/videos/{id}/popup-comments/`

**Given** un video in riproduzione
**When** il player raggiunge un timestamp che ha un popup associato
**Then** il popup overlay appare in stile glassmorphism (backdrop-blur, semi-trasparente) nell'angolo in alto a destra del player con testo del commento e username autore
**And** la latenza tra il timestamp e l'apparizione del popup è < 200ms (dati letti dal ref locale, nessuna chiamata API)

**Given** un popup visibile
**When** trascorrono pochi secondi (3-5s)
**Then** il popup scompare con animazione fade-out (Framer Motion Tier 1)

**Given** un commento con il massimo numero di like per un timestamp specifico
**When** il player raggiunge quel timestamp
**Then** viene mostrato solo quel commento (un popup per timestamp, quello con più like)

**Given** un commento temporizzato con 0 like
**When** il player raggiunge il suo timestamp
**Then** nessun popup viene mostrato (soglia minima 1 like)

### Story 3.6: Comment Markers sulla Timeline e Sidebar Dinamica

As a spettatore,
I want vedere indicatori sulla timeline del player e i commenti più apprezzati nella sidebar,
So that possa scoprire dove ci sono momenti commentati e leggere le reazioni migliori.

**Acceptance Criteria:**

**Given** una clip con commenti temporizzati
**When** il player è visibile
**Then** dot luminosi (gradiente DNA del brand) appaiono sulla progress bar nei punti dove ci sono commenti temporizzati

**Given** un utente desktop che passa il mouse su un comment marker
**When** l'hover è attivo
**Then** appare una micro-preview del commento top per quel timestamp (testo troncato + username)

**Given** un utente che clicca su un comment marker
**When** il click è registrato
**Then** il video salta al timestamp corrispondente

**Given** un utente desktop sulla pagina dettaglio
**When** la sidebar destra è visibile
**Then** la Sidebar Dinamica mostra i commenti con più like per la clip, ordinati per like decrescente, in stile "chat Twitch asincrona"
**And** i dati si caricano al caricamento della pagina (nessun real-time)

### Story 3.7: CTA Contestuale per Visitatori e Ricalcolo Popup Post-Moderazione

As a visitatore non autenticato,
I want essere invitato a partecipare quando vedo un momento coinvolgente,
So that la piattaforma mi converta da spettatore a utente attivo.

**Acceptance Criteria:**

**Given** un visitatore non autenticato che guarda una clip
**When** un popup overlay appare durante la riproduzione
**Then** un micro-CTA contestuale appare vicino al popup: "Scrivi la tua reazione a questo momento" con link a registrazione
**And** il CTA non è un modale bloccante — è un elemento DOM condizionale su auth state

**Given** un moderatore che disabilita un commento che era il popup per un timestamp
**When** il commento viene disabilitato (is_disabled = true)
**Then** il sistema ricalcola il prossimo commento con più like per quel timestamp
**And** se non ci sono altri commenti con almeno 1 like, nessun popup viene mostrato per quel timestamp

---

## Epic 4: Notifiche & Amministrazione

Gli utenti ricevono notifiche per eventi importanti (commenti ricevuti, like, popup promossi). Admin e moderatori possono gestire contenuti e utenti dalla piattaforma.

### Story 4.1: Notifiche In-App

As a utente registrato,
I want ricevere notifiche quando accadono eventi importanti sulle mie clip e commenti,
So that sappia quando qualcuno interagisce con i miei contenuti senza dover controllare manualmente.

**Acceptance Criteria:**

**Given** un utente che riceve un commento su una propria clip
**When** il commento viene salvato
**Then** viene creata una notifica con testo descrittivo (es. "Marco ha commentato al secondo 0:18 della tua clip: 'quel flick è impossibile'")

**Given** un utente il cui commento riceve like
**When** il like viene registrato
**Then** viene creata una notifica "Il tuo commento ha ricevuto N like"

**Given** un utente il cui commento viene promosso a popup
**When** il commento diventa il top per un timestamp
**Then** viene creata una notifica speciale "Il tuo commento è ora visibile nel player!"

**Given** un utente invitato a un contest o il cui turno di voto è disponibile
**When** l'evento contest si verifica
**Then** viene creata la notifica corrispondente ("Sei stato invitato al contest X" / "È il tuo turno di votare nel contest X")

### Story 4.2: Pagina Notifiche e Badge

As a utente registrato,
I want visualizzare le mie notifiche e sapere quante ne ho non lette,
So that possa restare aggiornato sulle interazioni senza perdere nulla.

**Acceptance Criteria:**

**Given** un utente autenticato
**When** guarda la sidebar/header
**Then** la campanella (notification-bell) mostra un badge con il conteggio delle notifiche non lette

**Given** un utente che clicca sulla campanella
**When** naviga a `/notifiche`
**Then** viene mostrata la lista cronologica delle notifiche con testo descrittivo, data relativa e stato letto/non letto

**Given** un utente che visualizza la pagina notifiche
**When** le notifiche non lette diventano visibili
**Then** vengono marcate come lette e il badge si aggiorna

**Given** un utente che clicca su una notifica relativa a una clip
**When** la notifica viene selezionata
**Then** viene reindirizzato alla pagina dettaglio della clip (al timestamp se applicabile)

### Story 4.3: Moderazione Commenti

As a moderatore,
I want disabilitare commenti inappropriati,
So that la community sia protetta da contenuti offensivi.

**Acceptance Criteria:**

**Given** un moderatore autenticato sulla dashboard admin `/admin`
**When** naviga alla sezione moderazione commenti
**Then** vede la lista dei commenti con opzioni di moderazione

**Given** un moderatore che individua un commento inappropriato
**When** clicca "Disabilita" sul commento
**Then** il commento viene disabilitato (is_disabled = true) e non è più visibile nella clip
**And** se il commento era il popup per un timestamp, il sistema ricalcola il prossimo commento con più like

**Given** un commento disabilitato che era l'unico con like per un timestamp
**When** il ricalcolo avviene
**Then** nessun popup viene mostrato per quel timestamp

### Story 4.4: Gestione Utenti e Contenuti (Admin)

As a admin,
I want gestire utenti e contenuti dalla dashboard,
So that possa mantenere la piattaforma sicura e ordinata.

**Acceptance Criteria:**

**Given** un admin autenticato sulla dashboard `/admin`
**When** cerca un utente
**Then** può visualizzare il profilo utente con la lista dei suoi video

**Given** un admin che individua un video inappropriato
**When** clicca "Elimina" sul video
**Then** il video viene eliminato (i file vengono rimossi) e non è più visibile sulla piattaforma

**Given** un admin che deve sospendere un account
**When** clicca "Sospendi" sull'utente
**Then** l'account viene sospeso — l'utente non può più accedere e i suoi contenuti non sono più visibili

**Given** un admin che deve promuovere un utente (es. da toconfirm a user)
**When** seleziona il nuovo ruolo e conferma
**Then** il ruolo dell'utente viene aggiornato

**Given** un utente non admin/moderatore
**When** tenta di accedere a `/admin`
**Then** viene reindirizzato alla Home (route protetta per ruolo)

### Story 4.5: Layout Dashboard Admin — Interfaccia Frontend e Protezione Route

As a admin o moderatore,
I want una dashboard admin con navigazione tra sezioni e protezione per ruolo,
So that possa gestire la piattaforma da un'interfaccia dedicata, organizzata e accessibile solo a chi ha i permessi.

**Acceptance Criteria:**

**Given** un admin o moderatore autenticato che naviga a `/admin`
**When** la pagina si carica
**Then** viene mostrata una dashboard con:
- Header con titolo "Amministrazione" e nome/ruolo dell'utente loggato
- Navigazione a tab o sidebar interna con le sezioni: **Utenti**, **Video**, **Commenti**
- La sezione di default è "Utenti"

**Given** un admin sulla sezione "Utenti"
**When** la lista si carica
**Then** vengono mostrati gli utenti in una tabella con colonne: username, email, ruolo, stato (attivo/sospeso), data registrazione
**And** ogni riga ha le azioni: "Visualizza profilo", "Promuovi ruolo" (dropdown con ruoli disponibili), "Sospendi" / "Riattiva"
**And** è presente una barra di ricerca per filtrare per username o email

**Given** un admin sulla sezione "Video"
**When** la lista si carica
**Then** vengono mostrati i video in una tabella con colonne: titolo, autore, tag, data caricamento, stato
**And** ogni riga ha le azioni: "Visualizza clip", "Elimina"
**And** è possibile filtrare per autore (username)

**Given** un moderatore sulla sezione "Commenti"
**When** la lista si carica
**Then** vengono mostrati i commenti in una tabella con colonne: testo (troncato), autore, clip associata, data, stato (attivo/disabilitato)
**And** ogni riga ha le azioni: "Visualizza clip", "Disabilita" / "Riabilita"
**And** i commenti disabilitati sono visualmente distinti (opacità ridotta, badge "Disabilitato")

**Given** un admin che clicca "Elimina" su un video
**When** l'azione viene selezionata
**Then** viene mostrato un dialog di conferma "Sei sicuro? Questa azione è irreversibile"
**And** solo dopo la conferma il video viene eliminato e la tabella aggiornata

**Given** un admin che clicca "Sospendi" su un utente
**When** l'azione viene selezionata
**Then** viene mostrato un dialog di conferma
**And** dopo la conferma l'utente viene sospeso e lo stato nella tabella si aggiorna

**Given** un moderatore che clicca "Disabilita" su un commento
**When** il commento viene disabilitato
**Then** il commento non è più visibile nella clip pubblica
**And** se il commento era il popup per un timestamp, il backend ricalcola il prossimo popup

**Given** un utente con ruolo "user" (non admin/moderatore)
**When** tenta di accedere a `/admin`
**Then** viene reindirizzato a `/home` con toast "Accesso non autorizzato"

**Given** un utente con ruolo "moderatore"
**When** accede alla dashboard admin
**Then** può vedere e usare solo la sezione "Commenti" — le sezioni "Utenti" e "Video" sono nascoste o disabilitate

**Given** la dashboard admin su viewport mobile
**When** la pagina si carica
**Then** il layout è responsive con le tabelle che diventano card stackate o scrollabili orizzontalmente

---

## Epic 5: Sistema Contest

Admin/moderatori possono creare contest, gli utenti possono iscriversi con clip, votare nei matchup, e seguire il bracket a eliminazione diretta con albero grafico interattivo. Release B separata.

### Story 5.1: Evoluzione Backend Contest — Bracket e Matchup

As a developer,
I want il sistema contest backend evoluto con bracket eliminazione diretta e matchup,
So that il frontend possa gestire contest completi con scontri, voti e avanzamento.

**Acceptance Criteria:**

**Given** il modello Contest backend esistente (settimanale automatico)
**When** viene eseguita la migrazione per l'evoluzione contest
**Then** il modello Contest supporta: creazione manuale da admin/mod, stato (aperto/in corso/completato), lista partecipanti
**And** il modello Bracket è creato con struttura ad albero (turni, scontri)
**And** il modello Matchup è creato (clip_a FK, clip_b FK, bracket FK, round, vincitore FK nullable)
**And** gli endpoint CRUD contest, iscrizione, generazione bracket, votazione matchup e avanzamento turno sono implementati

**Given** un contest con N partecipanti
**When** viene generato il bracket
**Then** la struttura è a eliminazione diretta con ceil(log2(N)) turni
**And** se N non è potenza di 2, vengono assegnati bye automatici

### Story 5.2: Creazione Contest e Iscrizione Partecipanti

As a admin o moderatore,
I want creare un contest e gestire le iscrizioni,
So that possa organizzare competizioni per la community.

**Acceptance Criteria:**

**Given** un admin/moderatore autenticato sulla pagina `/contest`
**When** clicca "Crea Contest" e inserisce titolo, descrizione e parametri
**Then** il contest viene creato in stato "aperto" e visibile a tutti gli utenti

**Given** un utente registrato che visualizza un contest aperto
**When** naviga alla pagina del contest
**Then** vede i dettagli del contest e il bottone "Iscriviti"

**Given** un utente che vuole iscriversi
**When** clicca "Iscriviti" e seleziona/carica una clip
**Then** viene registrato come partecipante con la clip selezionata

**Given** un utente già iscritto al contest
**When** visualizza il contest
**Then** il bottone "Iscriviti" è disabilitato e mostra "Iscritto"

### Story 5.3: Bracket Eliminazione Diretta e Albero Interattivo

As a utente,
I want visualizzare il bracket del contest come albero grafico interattivo,
So that possa seguire la progressione del torneo e vedere tutti gli scontri.

**Acceptance Criteria:**

**Given** un contest con bracket generato
**When** l'utente naviga alla pagina contest
**Then** viene mostrato un albero grafico interattivo del bracket (stile torneo FIFA) usando una libreria React dedicata
**And** l'albero mostra tutti i turni, gli scontri, le clip partecipanti e i risultati per turno

**Given** un utente che clicca su un matchup nell'albero
**When** il matchup è selezionato
**Then** vengono mostrate le due clip del matchup con player video per entrambe

**Given** un matchup completato
**When** viene visualizzato nell'albero
**Then** il vincitore è evidenziato e il perdente è attenuato

**Given** un utente su mobile
**When** visualizza il bracket
**Then** l'albero è scrollabile/zoomabile per adattarsi allo schermo ridotto

### Story 5.4: Votazione Matchup 1-5 Stelle

As a utente registrato,
I want votare le clip di un matchup da 1 a 5 stelle,
So that possa contribuire a decidere chi avanza nel torneo.

**Acceptance Criteria:**

**Given** un utente autenticato che visualizza un matchup attivo
**When** guarda entrambe le clip
**Then** può assegnare un voto da 1 a 5 stelle a ciascuna clip del matchup

**Given** un utente che ha già votato per un matchup
**When** tenta di votare di nuovo
**Then** l'UI mostra il voto già espresso e non permette modifiche (disabilitata dopo il voto)
**And** il vincolo è enforced sia lato backend (constraint DB unique su user+matchup) che lato frontend

**Given** un utente che tenta di votare con double-click o da tab multipli
**When** il sistema riceve richieste duplicate
**Then** il constraint DB unique previene voti duplicati e l'errore è gestito gracefully

### Story 5.5: Avanzamento Turno e Risultati Contest

As a utente,
I want vedere l'avanzamento automatico del contest e i risultati finali,
So that possa seguire la competizione fino al vincitore.

**Acceptance Criteria:**

**Given** un matchup con voti sufficienti
**When** il sistema calcola la media dei voti per ciascuna clip
**Then** la clip con media più alta avanza al turno successivo
**And** il bracket si aggiorna automaticamente con il vincitore nel matchup successivo

**Given** un turno con tutti i matchup completati
**When** il sistema verifica il completamento
**Then** il turno successivo viene attivato con i nuovi matchup

**Given** un contest con la finale completata
**When** il vincitore è determinato
**Then** la pagina contest mostra il vincitore finale evidenziato nell'albero
**And** lo stato del contest passa a "completato"

**Given** un utente che visita un contest in qualsiasi stato
**When** naviga alla pagina contest
**Then** può vedere: stato attuale, risultati passati, progressione nel bracket, clip di ogni scontro
