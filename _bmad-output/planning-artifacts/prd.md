---
stepsCompleted:
  - step-01-init
  - step-02-discovery
  - step-03-success
  - step-04-journeys
  - step-05-domain
  - step-06-innovation
  - step-07-project-type
  - step-08-scoping
  - step-09-functional
  - step-10-nonfunctional
  - step-11-polish
  - step-e-01-discovery
  - step-e-02-review
  - step-e-03-edit
classification:
  projectType: web_app
  domain: social_media_entertainment
  complexity: medium
  projectContext: brownfield
inputDocuments:
  - _bmad-output/planning-artifacts/product-brief-Video_clip-2026-02-14.md
  - _bmad-output/project-context.md
  - docs/index.md
  - docs/project-overview.md
  - docs/architecture-backend.md
  - docs/architecture-frontend.md
  - docs/api-contracts-backend.md
  - docs/data-models-backend.md
  - docs/source-tree-analysis.md
  - docs/development-guide.md
documentCounts:
  briefs: 1
  research: 0
  brainstorming: 0
  projectDocs: 8
  projectContext: 1
workflowType: 'prd'
lastEdited: '2026-02-28'
editHistory:
  - date: '2026-02-28'
    changes: 'Aggiornamento infrastruttura backend: Vercel Blob→MinIO, video processing stato reale, CORS documentato, Keycloak roadmap, Contest System riscritto con 2 tipologie (settimanale auto + bracket CL) e backoffice admin, FR aggiornati/aggiunti (FR53-55), modelli mancanti segnalati, mobile layout corretto'
---

# Product Requirements Document - Video_clip

**Author:** AcchippameQuisso
**Date:** 2026-02-14

## Executive Summary

**Video_clip** è un social network verticale per gaming clip — "l'Instagram del gaming con commenti temporizzati". La piattaforma permette ai gamer di caricare clip brevi (10s-1min) e ricevere commenti ancorati a momenti specifici del video. I commenti più apprezzati diventano popup overlay visibili a tutti gli spettatori futuri, trasformando il commentatore in co-protagonista della clip.

**Differenziatore competitivo:** Dual-layer commenting system (commenti normali + temporizzati) con promozione automatica a popup nel player — modello SoundCloud applicato al gaming video. Nessun competitor diretto combina commenti temporizzati + gaming-only + contest bracket.

**Target users:** Gamer che vogliono condividere momenti epici (creator), spettatori attivi che commentano e analizzano giocate (commentatori), archivisti che organizzano le proprie clip.

**Contesto tecnico:** Brownfield — backend Django 5.1.6 REST (DRF, PostgreSQL, SimpleJWT — migrazione pianificata a Keycloak). Storage video su MinIO (S3-compatible). Frontend Next.js (React) greenfield, desktop-first. Infra locale Docker Compose (PostgreSQL, MinIO, PgAdmin). Deploy: da definire.

**MVP a due pilastri:** Commenti temporizzati (innovazione) + Contest con due tipologie — auto-gestito settimanale e bracket Champions League — (engagement ricorrente). Validazione con gruppo ristretto di amici/sviluppatori.

## Success Criteria

### User Success

| Persona | Criterio di Successo | Momento "aha!" |
|---------|---------------------|----------------|
| **Streamer/Creator** | Le clip ricevono commenti temporizzati dalla community gaming entro 24h | Vede i commenti apparire al secondo esatto del clutch |
| **Gamer Casual** | La clip raggiunge più persone di WhatsApp — commenti da non-follower | Clip per 5 amici riceve commenti da sconosciuti che capiscono la giocata |
| **Spettatore Attivo** | I commenti vengono riconosciuti — like e promozione a popup nel player | Il suo commento diventa il popup visibile a tutti su una clip |
| **Archivista** | Clip organizzate per gioco e accessibili — download sempre disponibile | Trova tutte le sue clip ordinate cercando nel profilo |

**Time-to-First-Value:**
- Creator: primo upload → primo commento temporizzato ricevuto
- Casual: registrazione → primo commento da un non-amico
- Spettatore: primo commento → primo like ricevuto
- Archivista: registrazione → prima clip scaricata

### Business Success

**A 3 mesi (validazione con gruppo iniziale):**
- Il gruppo di amici/sviluppatori usa attivamente la piattaforma
- I commenti temporizzati vengono usati naturalmente (non solo commenti generici)
- Il feed Esplora ha contenuti sufficienti da rendere il browsing interessante
- Il passaparola parte — almeno qualche utente esterno al gruppo iniziale

**A 12 mesi (crescita organica):**
- Community attive per i giochi principali
- Contest funzionanti con partecipazione reale
- Retention stabile — gli utenti tornano per clip, commenti e contest
- Base sufficiente per valutare partnership con publisher

### Technical Success

- **Video 10s-1min**: upload e playback fluido per questa dimensione
- **Player con commenti temporizzati**: popup e sidebar funzionano correttamente sincronizzati al video
- **Feed performante**: scroll fluido senza lag su mobile
- **Nessun target numerico rigido per ora** — si ottimizza a prodotto completato in base all'esperienza d'uso reale
- **Pipeline upload-to-playback funzionante end-to-end**: upload → storage MinIO → playback con presigned URL
- **Backend nuovo codebase modulare**: 5 modelli base implementati (User, Video, Contest, Rating, Comment). Modelli da implementare: VideoLike, CommentLike, Notification, campo `bio` User, campo `allow_download` Video, campo `is_disabled` Comment. Integrazione API con frontend in corso

### Measurable Outcomes

**North Star Metric:** Commenti temporizzati al giorno — se cresce, il prodotto funziona.

| KPI | Cosa Misura | Frequenza |
|-----|-------------|-----------|
| Commenti temporizzati/giorno | Salute del prodotto (North Star) | Giornaliera |
| Clip caricate/giorno | Volume contenuti | Giornaliera |
| DAU/MAU | Utenti attivi | Giornaliera/Mensile |
| % commenti con like > 0 | Qualità engagement | Settimanale |
| Inviti/utente | Crescita organica | Mensile |

*Target numerici da definire dopo la fase di validazione con il gruppo iniziale.*

## User Journeys

### Journey 1: Luca — Il primo upload che cambia tutto (Gamer Casual - Happy Path)

Luca ha appena fatto un ace su Valorant. Le mani tremano ancora, il cuore batte forte. L'istinto è il solito: apre WhatsApp, cerca il gruppo degli amici. Ma poi si ricorda — un suo compagno gli ha mandato un link a Video_clip la settimana scorsa.

Apre Video_clip, si registra in 30 secondi — username, email, password. Vede il bottone Upload al centro della bottom-bar. Tap. Seleziona la clip dalla gallery (42 secondi). Scrive "Ace con Jett round 12" come titolo, seleziona "clutch" come tag. Conferma. La clip si carica, appare nel suo profilo.

Manda il link ai 5 amici nel gruppo WhatsApp. Loro si registrano, lo seguono, guardano la clip. Il primo commento temporizzato arriva al secondo 0:18 — esattamente quando parte il terzo kill: "MA CHE FLICK È QUESTO". Poi un altro al secondo 0:31: "freddo come il ghiaccio". Luca sorride.

Il giorno dopo apre Video_clip per controllare. La clip è finita nella sezione Esplora. Ha 3 commenti da gente che non conosce. Uno ha scritto al secondo 0:25: "questo crosshair placement è da predator". Luca non aveva mai ricevuto un complimento tecnico da uno sconosciuto. **Questo è il momento aha!** — la clip che avrebbe mandato su WhatsApp e sarebbe morta in ore, qui vive e cresce.

**Requisiti rivelati:** Registrazione rapida, upload con tag, player con commenti temporizzati, feed Esplora, condivisione link esterno.

### Journey 2: Marco — Dal live alla clip che vive (Streamer/Creator - Happy Path)

Marco ha appena chiuso lo stream serale di Valorant. 3 ore, 200 viewer, 2-3 momenti epici. Apre Video_clip, va su Upload. Ha già tagliato le clip migliori durante lo stream. Carica la prima — un clutch 1v4 da 35 secondi. Poi una seconda — un fail comico dove muore per danno da caduta al round decisivo. Tag "clutch" e "fail".

I suoi follower Twitch che lo seguono anche su Video_clip vedono le clip nella Home. I commenti temporizzati iniziano ad arrivare. Sul clutch, il commento più likato è al secondo 0:22: "letteralmente impossibile con Vandal a quella distanza". Quel commento diventa il popup che tutti vedono quando la clip arriva a 0:22. Marco condivide il link su Twitter — "guardate cosa succede al secondo 22".

Due settimane dopo, una sua clip finisce in tendenza nella sezione Esplora. Arrivano 30 nuovi follower che non lo conoscevano da Twitch. **Momento aha!**: Video_clip non è solo un archivio — è un canale di crescita parallelo.

**Requisiti rivelati:** Upload multiplo, feed Home (following), commenti popup con più like per timestamp, sharing link esterno, sezione Esplora con trending.

### Journey 3: Sara — Il commento che diventa leggenda (Spettatore Attivo - Happy Path)

Sara scorre il feed Esplora durante la pausa pranzo. Vede una clip di Valorant — un clutch con Omen. La guarda. Al secondo 0:15, l'Omen fa un teleport dietro due nemici. Sara pausa, scrive un commento ancorato al secondo 15: "il timing del TP è perfetto perché l'ulti del Sova era appena finita — sapeva esattamente quando muoversi". Riprende la visione.

Torna la sera. Il suo commento ha 12 like — è diventato il popup che appare a tutti al secondo 0:15 della clip. Ogni persona che guarda quella clip ora vede l'analisi di Sara apparire esattamente nel momento giusto. Sara non ha mai caricato una clip — la sua reputazione è costruita interamente sui commenti. **Momento aha!**: il suo commento è stato visto da centinaia di persone, ancorato al secondo esatto che conta.

**Requisiti rivelati:** Like sui commenti, algoritmo popup (commento con più like per timestamp), sidebar commenti, navigazione Esplora senza necessità di caricare clip.

### Journey 4: Davide — L'archivio che funziona (Archivista - Happy Path)

Davide ha clip sparse ovunque — 200 nella gallery del telefono, 50 su Twitch, screenshot su Steam. Scopre Video_clip e decide di usarlo come archivio. Si registra. Inizia a caricare: 10 clip di Elden Ring (boss fight), 5 di Valorant, 3 di Rocket League. Per ogni clip sceglie titolo e tag.

Una settimana dopo, vuole rivedere la boss fight contro Malenia. Apre il suo profilo, scorre le clip — sono tutte lì, ordinate per data. Scarica quella di Malenia per mandarla a un amico su Discord. **Momento aha!**: "Finalmente non devo cercare in 5 cartelle diverse."

*Nota: Journey 4 e Journey 6 anticipano funzionalità di Fase 2 (profilo privato, follow con pending). Per l'MVP i profili sono pubblici e il follow è immediato.*

**Requisiti rivelati:** Upload batch, download proprie clip, organizzazione clip nel profilo, filtro/ricerca nel profilo. *(Profilo privato → Fase 2)*

### Journey 5: Luca — Upload fallito (Edge Case - Error Recovery)

Luca prova a caricare una clip da 58 secondi. La connessione è instabile. L'upload arriva al 70% e fallisce. Appare una modale di errore: "Upload fallito. Riprova?" con un bottone "Riprova". Luca tap su Riprova. Questa volta il caricamento va a buon fine. La clip appare nel suo profilo.

Se il video è troppo lungo (oltre 1 minuto) o in formato non supportato, l'errore è specifico: "Il video supera la durata massima di 1 minuto" oppure "Formato non supportato". Luca sa subito cosa fare.

**Requisiti rivelati:** Validazione durata video (10s-1min), messaggi errore specifici, modale retry, gestione upload interrotto.

### Journey 6: Marco — Richiesta follow da profilo privato (Edge Case)

Marco nota che un utente con profilo privato ha commentato una sua clip. Vuole vedere le clip di questo utente. Va sul suo profilo — vede "Profilo privato". Tap su "Segui" — la richiesta resta in pending. L'utente riceve la notifica e accetta. Ora Marco vede le clip nel profilo e nel feed Home.

**Requisiti rivelati:** Profilo privato, richiesta follow pending/accepted/rejected, stato follow visibile.

### Journey 7: Moderatore — Commento inappropriato (Moderator Path)

Un moderatore scorre i report (o naviga normalmente). Vede un commento offensivo su una clip popolare. Apre l'interfaccia admin nel frontend, trova il commento, e lo disabilita. Il commento non è più visibile nella clip. Se il commento era il popup per quel timestamp, il sistema seleziona automaticamente il successivo commento con più like.

**Requisiti rivelati:** Interfaccia admin frontend, ruolo moderatore, azione disabilita commento, ricalcolo popup dopo disabilitazione.

### Journey 8: Admin — Sospensione account e rimozione video (Admin Path)

L'admin riceve segnalazioni su un utente che carica contenuti inappropriati ripetutamente. Accede all'interfaccia admin nel frontend. Cerca l'utente, vede la lista dei suoi video. Elimina i video inappropriati (i file vengono rimossi dallo storage MinIO). Poi sospende l'account — l'utente non può più accedere, i suoi contenuti non sono più visibili.

Se necessario, l'admin può anche promuovere utenti da `toconfirm` a `user` (confermare la registrazione).

**Requisiti rivelati:** Interfaccia admin frontend, eliminazione video da admin, sospensione account, promozione ruoli utente, lista video per utente nell'admin.

### Journey Requirements Summary

| Area Capability | Journey che la rivela |
|-----------------|----------------------|
| **Registrazione/Login** | Luca (J1), tutti |
| **Upload con validazione** | Luca (J1), Marco (J2), Davide (J4), Error (J5) |
| **Player + commenti temporizzati** | Luca (J1), Marco (J2), Sara (J3) |
| **Like commenti + popup** | Sara (J3), Moderatore (J7) |
| **Feed Home (following)** | Marco (J2), Marco (J6) |
| **Feed Esplora** | Luca (J1), Sara (J3) |
| **Profilo pubblico** | Davide (J4) |
| **Profilo privato + Follow con pending** *(Fase 2)* | Davide (J4), Marco (J6) |
| **Download clip** | Davide (J4) |
| **Error handling upload** | Luca (J5) |
| **Admin: disabilita commenti** | Moderatore (J7) |
| **Admin: elimina video, sospendi account** | Admin (J8) |
| **Admin: promozione ruoli** | Admin (J8) |
| **Condivisione link esterno** | Luca (J1), Marco (J2) |

## Domain-Specific Requirements

### Storage Video

- **Servizio:** MinIO (S3-compatible), self-hosted via Docker Compose
- **Accesso video:** Presigned URL con scadenza temporale (già implementato nel backend)
- **Stato video processing:** MoviePy estrae la durata del video all'upload. Transcoding (conversione a formato leggero H.264/MP4 ottimizzato via ffmpeg) non ancora implementato — da pianificare per ridurre spazio di archiviazione e migliorare playback
- **Vincolo dimensione:** Video da 10 secondi a 1 minuto — validazione durata da implementare lato backend (attualmente solo estrazione durata, nessun reject automatico)

### Copyright & Contenuti

- Le clip gaming possono contenere musica interna al gioco o provenire da edit/applicazioni esterne
- Per le prime fasi di sviluppo, la gestione copyright non è un requisito — da rivalutare in fase di scala

### Privacy & Moderazione

- Moderazione manuale per l'MVP: moderatori disabilitano commenti, admin eliminano video e sospendono account
- GDPR e data retention da considerare in fase di deploy commerciale, non bloccante per la validazione iniziale

## Innovation & Novel Patterns

### Detected Innovation Areas

**Commenti temporizzati come DNA del prodotto — il modello SoundCloud applicato al gaming**

L'innovazione centrale di Video_clip non è una feature isolata ma un principio organizzativo. I commenti temporizzati stile SoundCloud, mai applicati al gaming video in modo integrato, creano un doppio protagonismo: il creator della clip e il commentatore che scrive la reazione perfetta al momento giusto. **Il commento diventa contenuto di prima classe** — non una reazione usa e getta ma parte permanente dell'esperienza video.

**Dual-layer commenting system:**
- **Commenti normali** (senza timestamp): sezione commenti classica stile Instagram — barriera zero, chiunque può commentare
- **Commenti temporizzati** (con timestamp opzionale): appaiono nella sezione commenti ma i più likati diventano popup nel player per tutti gli spettatori futuri
- **Timestamp pre-compilato**: quando l'utente pausa il video e inizia a scrivere, il timestamp corrente viene pre-suggerito automaticamente (rimuovibile). Il path di minor resistenza porta naturalmente al commento temporizzato senza forzare nulla
- **Due viste commenti** nella pagina dettaglio: "Tutti" (cronologico, stile Instagram) e "Nel video" (solo temporizzati, ordinati per timestamp)

**Il dual-layer è un funnel interno:** i commenti normali catturano i lurker, i popup durante la riproduzione dimostrano la feature e convertono lurker in power user che iniziano a usare i timestamp.

**Soglia popup:** il commento con più like per ogni timestamp appare nel player, con soglia minima di 1 like per essere promosso a popup.

**Prerequisiti backend non ancora implementati:** Il sistema popup richiede il modello `CommentLike` (da creare) per tracciare i like sui commenti e determinare la promozione. Il campo `timestamp_second` sul modello Comment esiste (default=0) ma non distingue tra "nessun timestamp" e "timestamp al secondo 0" — da chiarire nella data model (nullable vs valore sentinella).

### Market Context & Competitive Landscape

| Competitor | Cosa offre | Cosa manca |
|-----------|-----------|------------|
| **TikTok/YouTube Shorts/Reels** | Video brevi, grande reach | Generalisti, nessun commento temporizzato, nessuna categorizzazione gaming |
| **Twitch Clips** | Clip da stream | Ancillare al live, nessun social standalone |
| **Medal.tv** | Cattura e condivisione clip | Manca dimensione social profonda, no commenti temporizzati, no contest |
| **SoundCloud** | Commenti temporizzati per audio | Solo audio, nessun focus gaming |
| **Video_clip** | **Commenti temporizzati + gaming-only + contest (settimanale + bracket)** | **Combinazione unica, nessun competitor diretto** |

**Blue Ocean positioning:** Tutti i competitor competono sullo stesso asse (reach, algoritmo, viralità). Video_clip crea un nuovo asse di valore: il commento come contenuto, il commentatore come co-creator.

### Validation Approach

**Metrica critica:** % commenti con timestamp sul totale dei commenti — target minimo 20% dopo fase di validazione.

| Metrica di Validazione | Cosa Indica |
|----------------------|-------------|
| % commenti con timestamp vs senza | Adozione della feature killer |
| % commenti temporizzati con almeno 1 like | Qualità dei commenti temporizzati |
| Numero di popup attivi nel player | La feature è visibile e funzionante |
| Engagement su clip con popup vs senza | Impatto dei popup sull'esperienza |

### Risk Mitigation

| Rischio | Mitigazione |
|---------|-------------|
| Gli utenti ignorano il timestamp e commentano solo in modo generico | Timestamp pre-compilato al momento della pausa — il default guida il comportamento. Popup come ricompensa visiva naturale |
| Pochi commenti = nessun popup = esperienza vuota | Nella fase iniziale con amici, i primi commenti temporizzati saranno organici. Il feed Esplora mostrerà clip con popup attivi |
| Troppi popup su clip popolari | Solo il commento con più like per timestamp — un popup per secondo max |
| Senza i commenti temporizzati, il prodotto è "l'ennesimo TikTok gaming" | La verticalità gaming-only ha valore autonomo, ma i commenti temporizzati sono il fossato competitivo — validazione prioritaria |

## Web App Specific Requirements

### Project-Type Overview

Video_clip è una web app **desktop-first** (approccio Reddit) costruita con **Next.js (React)** e App Router. La scelta desktop-first è una decisione deliberata: l'esperienza di visione clip con commenti temporizzati, sidebar e overlay funziona meglio su schermo largo. Il responsive mobile segue come adattamento, non come driver del design.

### Technical Architecture Considerations

#### Framework & Stack Frontend

| Componente | Scelta | Motivazione |
|-----------|--------|-------------|
| **Framework** | Next.js (App Router) | SSR per link preview (OG meta tags), API Routes come proxy, React ecosystem |
| **UI Library** | React | Componente ecosistema maturo, community ampia |
| **Styling** | Tailwind CSS | Utility-first, veloce per prototipare, consistente |
| **Deploy Frontend** | Da definire | Next.js compatibile con diverse piattaforme (Vercel, Docker, self-hosted) |
| **Storage Video** | MinIO (S3-compatible) | Self-hosted via Docker Compose, presigned URL per accesso |

#### Proxy API Pattern *(Fase 2)*

*Per l'MVP il frontend comunica direttamente con il backend Django via CORS. Il proxy API pattern è pianificato per Fase 2.*

Next.js API Routes fungeranno da proxy verso il backend Django REST:

- **CORS risolto**: il frontend chiama solo il proprio dominio
- **Backend nascosto**: l'URL Django non è esposto al client
- **JWT in httpOnly cookies**: i token non sono accessibili via JavaScript (XSS protection)
- **Flessibilità**: logica di trasformazione/caching possibile nel layer proxy

**Flusso MVP:** Browser → Django REST API → PostgreSQL / MinIO
**Flusso Fase 2:** Browser → Next.js API Route → Django REST API → PostgreSQL / MinIO

**Nota CORS MVP:** L'attuale configurazione usa `CORS_ALLOW_ALL_ORIGINS = True` — da restringere a origini specifiche prima del deploy di produzione.

#### SSR per Link Preview

Le pagine pubbliche (`/clip/{id}`) usano Server-Side Rendering per generare meta tag OpenGraph:
- **Titolo clip** nel tag `og:title`
- **Thumbnail video** nel tag `og:image`
- Quando un link viene condiviso su WhatsApp, Twitter, Discord → preview ricca con titolo e anteprima visiva

### Browser Support

| Browser | Supporto |
|---------|----------|
| Chrome (ultimi 2) | Completo |
| Firefox (ultimi 2) | Completo |
| Safari (ultimi 2) | Completo |
| Edge (ultimi 2) | Completo |
| IE11 / browser legacy | Non supportato |

### Responsive Design — Desktop-First

#### Desktop Layout
- **Sidebar sinistra** (stile Reddit/Discord): navigazione principale, collassabile
- **Area centrale**: feed clip / player video / contenuto principale
- **Sidebar destra** (pagina dettaglio clip): Sidebar Dinamica con commenti più likati

#### Mobile Layout
- **Header**: logo "V" + search + avatar
- **MobileBottomBar**: Home, Esplora, Upload, Profilo
- Layout single-column adattato — no hamburger menu

#### Due Layout Distinti
- **Autenticato**: sidebar + feed personalizzato + azioni (upload, like, commenta)
- **Pubblico** (non loggato): pagina clip con SSR, CTA registrazione, funzionalità limitate

### Video Processing

- **Stato attuale:** MoviePy (imageio-ffmpeg) estrae la durata del video all'upload. Il file originale viene salvato direttamente su MinIO senza conversione
- **Upload flow attuale:** file originale → estrazione durata (MoviePy) → storage su MinIO
- **Upload flow pianificato:** file originale → validazione durata (10s-1min, reject automatico) → conversione H.264/MP4 ottimizzato (ffmpeg) → storage su MinIO
- **Processing asincrono:** Celery + Redis presenti in requirements ma non configurati. APScheduler è attivo per auto-close contest. Conversione video asincrona da implementare quando il transcoding sarà aggiunto

### Navigazione & UX Specifiche

#### Sidebar Dinamica (Stile Twitch)
- Presente nella pagina dettaglio clip, a destra del player
- **Non è real-time**: si popola automaticamente con i commenti che hanno ricevuto il maggior numero di like
- Dà l'**illusione di un feed vivo** basato sulla popolarità
- Aggiornamento al caricamento della pagina (non WebSocket per MVP)

#### Navigazione Card-to-Detail
- Nel feed (Home/Esplora): le clip sono presentate come **card** (thumbnail + titolo + meta)
- Al click sulla card → **redirect alla pagina dettaglio** della clip
- Nella pagina dettaglio: player video + sotto il player la **sezione completa e gerarchica di tutti i commenti** (non solo i top)

#### Sistema di Overlay (Pop-up Temporali)
- Durante la riproduzione del video, **pop-up grafici** appaiono sopra il player
- Logica: mostra il **commento con più like associato a quel preciso timestamp** (es. a 0:15, poi a 0:25)
- Il pop-up **sparisce dopo pochi secondi** per non ostruire la visuale
- Posizione: angolo in alto a destra del player
- Soglia minima: almeno 1 like per essere promosso a popup

### Real-Time Strategy

- **MVP**: Nessun real-time. Tutti i dati sono fetch-based (caricamento pagina / polling manuale)
- **Growth**: Valutare WebSocket o SSE per notifiche commenti e aggiornamento sidebar in tempo reale
- **Motivazione**: il prodotto funziona senza real-time — la sidebar dinamica basata sui like dà già l'illusione di attività

### Implementation Considerations

- **State Management**: React Context per auth/user state, fetch-based per dati clip/commenti (no Redux per MVP)
- **Video Player**: HTML5 `<video>` con controller custom per gestire overlay popup e sincronizzazione timestamp
- **Image/Video Optimization**: Next.js Image per thumbnail, lazy loading nel feed
- **SEO**: pagine clip pubbliche indicizzabili, sitemap dinamica per clip popolari
- **Accessibilità**: livello base AA per MVP — focus su contrasti, navigazione keyboard, alt text

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**Approccio MVP:** Experience MVP — validare che il core loop (upload → guarda → commenta con timestamp → vedi popup) e i contest creino engagement reale con un gruppo ristretto di amici/sviluppatori.

**Principio guida:** Due pilastri, zero distrazioni. I commenti temporizzati dimostrano l'innovazione. I contest (settimanale auto-gestito + bracket Champions League) creano eventi ricorrenti che generano retention. Tutto il resto è Fase 2.

**Strategia di rilascio interno:**
- **Release A:** Core Platform + Clip Experience — validare il loop commenti temporizzati
- **Release B:** Contest System — validare due tipologie contest (settimanale + bracket) come secondo motore di engagement
- Questo approccio produce dati di validazione puliti su ciascun pilastro

**Team:** Sviluppatore singolo (AcchippameQuisso) + amici sviluppatori come tester iniziali.

**Debito tecnico consapevole MVP:**
- CORS diretto Django ↔ Next.js — attualmente `CORS_ALLOW_ALL_ORIGINS = True` (da restringere a origini specifiche). Proxy API pattern in Fase 2
- Nessun transcoding video (file salvato così com'è su MinIO, solo estrazione durata)
- Nessun real-time (fetch-based, polling manuale)

### MVP Feature Set (Fase 1)

**Struttura Epic:**

#### Epic 1: Core Platform
- Auth (registrazione/login JWT)
- Profilo pubblico base
- Follow/Unfollow semplice (senza pending)
- Layout desktop (sidebar sinistra nav + area centrale + sidebar destra commenti)
- Admin/moderazione base (disabilita commenti, elimina video, sospendi account)
- Notifiche in-app base (pagina `/notifications`, lista cronologica eventi)

#### Epic 2: Clip Experience
- Upload clip 10s-1min con validazione + storage MinIO (transcoding ffmpeg pianificato, non ancora implementato)
- Player video HTML5 con overlay popup temporali
- Dual-layer commenti (normali + temporizzati con timestamp pre-compilato)
- Like sulle clip + Like sui commenti *(richiede modelli VideoLike e CommentLike — da implementare)*
- Sidebar Dinamica (commenti più likati, stile Twitch)
- Feed Home (clip degli utenti seguiti)
- Link preview SSR per condivisione esterna (OG meta tags)
- Download clip proprie + allow_download per altri *(campo `allow_download` da aggiungere al modello Video)*
- Card-to-Detail navigation (card nel feed → pagina dettaglio con tutti i commenti)

#### Epic 3: Contest System

**Backoffice Admin per Contest:** interfaccia admin nel frontend per creare contest e scegliere la tipologia.

**Tipologia A — Contest Settimanale Auto-gestito:**
- Creazione automatica: un contest settimanale viene creato quando un video è caricato con un tag contest (lun-ven)
- Chiusura automatica (già implementato nel backend: `get_or_create_current_contest`, `close_contests`, APScheduler)
- Utenti caricano clip che vengono auto-assegnate al contest corrente
- Votazione 1-5 stelle sulle singole clip del contest
- **Vincitore (già implementato):** clip con media voti più alta. In caso di parimerito: spareggio ponderato — 50% numero voti ricevuti, 30% visualizzazioni, 20% like (attualmente commenti come fallback fino a implementazione VideoLike)
- Pagina contest con classifica e risultati
- Nessun premio — il contest settimanale è un meccanismo di engagement e visibilità

**Tipologia B — Contest Bracket Champions League:**
- Creazione manuale da admin tramite backoffice
- Iscrizione partecipanti con invio clip
- Bracket eliminazione diretta con albero grafico interattivo (stile torneo — visualizzazione scontri, clip passate, risultati per turno, libreria React dedicata)
- Votazione 1-5 stelle per matchup
- **Avanzamento e vincitore: solo voti interni al matchup** (media voti per matchup, nessun fattore esterno come views o commenti)
- Pagina contest con stato bracket e progressione
- **Premi esclusivi Champions League:** Fase 1 premi finanziati Video_clip (skins, crediti in-game shop). Fase 2 partnership con publisher per premi premium

**Modelli backend da implementare per Tipologia B:** Bracket, Matchup, ContestEntry (il modello Contest esiste, gli altri sono da creare)

**Notifiche in-app:**

| Evento | Notifica |
|--------|----------|
| Commento ricevuto sulla tua clip | "X ha commentato la tua clip" |
| Like ricevuto su un commento | "Il tuo commento ha ricevuto N like" |
| Commento promosso a popup | "Il tuo commento è ora visibile nel player!" |
| Nuovo contest settimanale aperto | "Un nuovo contest settimanale è iniziato!" |
| Invito/iscrizione contest bracket | "Sei stato invitato al contest X" |
| Turno contest bracket disponibile | "È il tuo turno di votare nel contest X" |
| Risultati contest pubblicati | "Il contest X è terminato — scopri i risultati!" |

Implementazione: modello `Notification` backend *(da creare)* + endpoint `GET /notifications/` + campanella con badge nella sidebar frontend.

**Core User Journeys Supportati:**
- J1 (Luca - primo upload), J2 (Marco - creator), J3 (Sara - spettatore attivo), J5 (error recovery)
- J7 (Moderatore) e J8 (Admin) — per gestione contest e moderazione

**Escluso dall'MVP (decisione esplicita):**

| Feature | Motivo esclusione | Fase target |
|---------|-------------------|-------------|
| Feed Esplora (trending) | Insufficiente contenuto con pochi utenti | Fase 2 |
| Profili privati + follow pending | Complessità non necessaria con gruppo amici | Fase 2 |
| Proxy API pattern | CORS diretto restrittivo sufficiente per fase amici | Fase 2 |
| Rating 1-5 stelle su clip normali | Rating solo nei contest, non nel feed | N/A — non previsto |
| Categorizzazione per gioco | Poco contenuto per giustificare filtri | Fase 2 |
| Transcoding video (ffmpeg) | Nessun transcoding attivo, file originali su MinIO | Fase 2 |
| Processing video asincrono | Celery+Redis in requirements, non configurato | Fase 2 |
| Real-time (WebSocket/SSE) | Fetch-based sufficiente | Fase 2 |
| Contest creati da utenti | Inizialmente solo admin/moderatori | Fase 3 |

### Post-MVP Features

**Fase 2 — Growth (dopo validazione con gruppo iniziale):**
- Feed Esplora con trending/algoritmo
- Profili privati + follow con pending/accepted/rejected
- Proxy API pattern (Next.js API Routes → Django)
- Categorizzazione per gioco (modello Game)
- Processing video asincrono (Celery + Redis)
- Questionario giochi all'onboarding
- Real-time: WebSocket/SSE per notifiche e sidebar live
- Contest creati da utenti verificati (non solo admin)
- Notifiche push (browser)

**Fase 3 — Expansion (scala):**
- Contest creati dagli utenti
- Integrazione Steam e Twitch
- Partnership con publisher per premi contest Champions League (upgrade da premi interni)
- App mobile nativa (iOS/Android)
- Notifiche push mobile
- Sistema reputazione commentatori
- Feed Esplora personalizzato per giochi preferiti

### Risk Mitigation Strategy

**Rischi Tecnici:**

| Rischio | Mitigazione |
|---------|-------------|
| Contest bracket richiede modelli aggiuntivi | Solo modello `Contest` esiste. Bracket, Matchup, ContestEntry da creare. Contest settimanale auto-gestito è parzialmente implementato (APScheduler + get_or_create_current_contest) |
| Nessun transcoding video | File originali su MinIO, nessuna conversione. Accettabile per MVP con volumi bassi. Aggiungere ffmpeg + Celery quando lo spazio storage diventa critico |
| CORS aperto espone URL backend | Attualmente `CORS_ALLOW_ALL_ORIGINS = True` — restringere a origini specifiche prima del deploy. Proxy API come upgrade Fase 2 |
| Libreria bracket React non adatta | Valutare alternative: react-brackets, bracketry, o componente custom con SVG/Canvas |

**Rischi di Mercato:**

| Rischio | Mitigazione |
|---------|-------------|
| Gli amici usano il prodotto per cortesia | Monitorare North Star: commenti temporizzati/giorno + notifiche lette vs ignorate |
| Contest senza partecipanti | Contest settimanale auto-gestito ha barriera zero (basta caricare una clip). Bracket da 4-8 amici funziona per contest manuali |
| Nessuna crescita oltre il gruppo | Link preview SSR + condivisione esterna. Contest generano clip condivisibili |

**Rischi Risorse:**

| Rischio | Mitigazione |
|---------|-------------|
| Sviluppatore singolo, troppo scope | Due release interne (A: clip, B: contest). Se serve tagliare, contest parte dopo |
| Storage MinIO cresce senza transcoding | File originali occupano più spazio. Volumi bassi iniziali rendono il problema gestibile. Aggiungere transcoding ffmpeg come priorità quando lo storage cresce |

## Functional Requirements

### Gestione Utenti

- FR1: Utente non registrato può creare un account con username, email e password
- FR2: Utente registrato può autenticarsi con le proprie credenziali
- FR3: Utente registrato può visualizzare e modificare il proprio profilo pubblico
- FR4: Utente registrato può seguire altri utenti
- FR5: Utente registrato può smettere di seguire utenti che segue
- FR6: Utente registrato può visualizzare le proprie liste follower e following

### Creazione & Gestione Contenuti

- FR7: Utente registrato può caricare una clip video (durata 10s-1min)
- FR8: Il sistema valida la durata della clip e rifiuta video fuori range con messaggio di errore specifico
- FR9: Il sistema valida il formato della clip e fornisce errore specifico per formati non supportati
- FR10: *(Pianificato)* Il sistema converte le clip caricate in formato H.264/MP4 ottimizzato. Attualmente il file originale viene salvato direttamente su MinIO
- FR11: Utente registrato può impostare titolo e tag tipo per la clip caricata
- FR12: Utente registrato può impostare se la propria clip è scaricabile da altri utenti
- FR13: Utente registrato può scaricare le proprie clip
- FR14: Utente registrato può scaricare clip altrui quando il download è abilitato dall'autore
- FR15: Il sistema archivia le clip su storage cloud con URL di accesso autenticato a scadenza temporale
- FR16: Il sistema mostra una modale di errore con opzione "Riprova" quando l'upload fallisce

### Scoperta & Fruizione Contenuti

- FR17: Utente registrato può visualizzare un feed Home con le clip degli utenti seguiti
- FR18: Utente può visualizzare la pagina dettaglio clip con player, commenti e metadati
- FR19: Le pagine dettaglio clip sono accessibili tramite URL diretto per la condivisione
- FR20: Il sistema genera link preview ricche (titolo, thumbnail) per gli URL delle clip condivisi su piattaforme esterne
- FR21: Il feed presenta le clip come card con thumbnail, titolo e metadati
- FR22: Utente può navigare dalla card nel feed alla pagina dettaglio della clip

### Sistema Commenti & Interazioni

- FR23: Utente registrato può pubblicare un commento su una clip senza timestamp
- FR24: Utente registrato può pubblicare un commento temporizzato su una clip con timestamp specifico
- FR25: Il timestamp corrente del video viene pre-compilato nel form commento quando il video è in pausa
- FR26: Utente può rimuovere il timestamp pre-suggerito per pubblicare un commento normale
- FR27: Utente registrato può mettere like a un commento
- FR28: Utente registrato può mettere like a una clip
- FR29: La pagina dettaglio mostra tutti i commenti in vista gerarchica
- FR30: La pagina dettaglio offre due viste commenti: "Tutti" (cronologica) e "Nel video" (solo temporizzati, ordinati per timestamp)

### Popup & Loop di Engagement

- FR31: Il sistema identifica il commento con più like per ogni timestamp di una clip
- FR32: Durante la riproduzione video, popup overlay mostrano il commento con più like per il timestamp corrente
- FR33: I popup overlay scompaiono dopo 3 secondi con fade-out
- FR34: I popup richiedono una soglia minima di 1 like per essere promossi
- FR35: La Sidebar Dinamica mostra i commenti con più like per la clip corrente
- FR36: Quando un commento viene disabilitato dalla moderazione, il sistema ricalcola il prossimo commento con più like per quel timestamp

### Sistema Contest

**Backoffice Admin:**
- FR37: Admin può creare un contest tramite backoffice, scegliendo la tipologia (settimanale auto-gestito o bracket Champions League)
- FR38: Utente registrato può visualizzare i contest disponibili (entrambe le tipologie)

**Tipologia A — Contest Settimanale Auto-gestito:**
- FR39a: Un contest settimanale viene creato automaticamente quando un video è caricato con un tag contest (periodo lun-ven)
- FR39b: Le clip caricate vengono auto-assegnate al contest settimanale corrente in base al tag
- FR40a: Utente registrato può votare da 1 a 5 stelle sulle clip del contest settimanale
- FR41a: Il sistema chiude automaticamente il contest al termine del periodo
- FR42a: Il vincitore è la clip con la media voti più alta. In caso di parimerito: spareggio ponderato (50% numero voti, 30% visualizzazioni, 20% like)
- FR43a: Utente può visualizzare classifica e risultati del contest settimanale

**Tipologia B — Contest Bracket Champions League:**
- FR39c: Utente registrato può iscriversi a un contest bracket inviando una clip
- FR40b: Il sistema genera un bracket a eliminazione diretta per i partecipanti
- FR41b: Il contest mostra un albero grafico interattivo del bracket (stile torneo, con visualizzazione scontri, clip passate e risultati)
- FR42b: Utente registrato può votare da 1 a 5 stelle sulle clip di un matchup del contest bracket
- FR43b: Il sistema calcola la media dei voti interni al matchup e fa avanzare il vincitore (nessun fattore esterno)
- FR44: Utente può visualizzare stato del contest bracket, risultati passati e progressione nel bracket
- FR44b: Il vincitore del contest bracket riceve un premio (Fase 1: premi finanziati Video_clip; Fase 2: premi da partnership publisher)

### Amministrazione & Moderazione

- FR45: Moderatore può disabilitare commenti inappropriati
- FR46: Admin può eliminare video
- FR47: Admin può sospendere account utente
- FR48: Admin può promuovere utenti tra ruoli (es. toconfirm → user)
- FR49: Admin può visualizzare la lista dei video per utente
- FR50: Il sistema invia notifiche in-app per eventi chiave (commento ricevuto, like ricevuto, commento promosso a popup, contest aperto, invito contest bracket, turno contest disponibile, risultati contest)
- FR51: Utente registrato può visualizzare la propria lista notifiche
- FR52: Il sistema mostra un badge con il conteggio delle notifiche non lette
- FR53: Utente può visualizzare il profilo di un altro utente tramite username
- FR54: Il sistema valida la durata del video all'upload e rifiuta automaticamente clip fuori range 10s-1min
- FR55: Admin può gestire contest tramite backoffice dedicato nel frontend (creazione, monitoraggio, chiusura manuale)

## Non-Functional Requirements

### Performance

| Requisito | Target | Contesto |
|-----------|--------|----------|
| First Contentful Paint | < 1.5s | Pagine pubbliche con SSR |
| Time to Interactive | < 3s | Priorità al player video |
| Video Start Playback | < 2s | Via presigned URL MinIO, formato originale (transcoding pianificato) |
| Lighthouse Score | > 80 | Target iniziale, migliorabile |
| Risposta API (lettura) | < 500ms | Feed, commenti, notifiche |
| Risposta API (scrittura) | < 1s | Like, commenti, follow |
| Upload video (escl. conversione) | < 30s per 500MB | Su connessione stabile |
| Conversione video ffmpeg *(pianificata)* | < 2x durata clip | Es. clip 30s → conversione < 60s. Non ancora implementato |
| Latenza popup overlay vs timestamp | < 200ms | Dati popup pre-caricati in singola chiamata API al caricamento pagina |
| Progress bar upload | Aggiornamento in tempo reale | Feedback visivo obbligatorio per upload file grandi |

**Strategia pre-caricamento popup:** I dati dei popup (timestamp + testo commento + autore) per una clip devono essere caricati in un'unica chiamata API al caricamento della pagina dettaglio. Il player legge i dati localmente durante il playback — nessuna chiamata API on-demand durante la riproduzione.

### Security

- Autenticazione tramite JWT con refresh token (SimpleJWT). Migrazione pianificata a **Keycloak** per SSO e gestione centralizzata identità
- CORS: attualmente `CORS_ALLOW_ALL_ORIGINS = True` — **da restringere a origini specifiche** prima del deploy di produzione
- Validazione input su tutti gli endpoint (durata clip, formato file, lunghezza commenti)
- **Vincolo integrità voto contest:** Ogni utente può votare **una sola volta** per clip (contest settimanale) o per matchup (contest bracket) — enforced lato backend e lato frontend (UI disabilitata dopo il voto). Gestione edge case: double-click, tab multipli
- Upload limitato a formati video consentiti — whitelist: **MP4, MOV, AVI, MKV, WebM**
- Limite dimensione file upload: **max 500MB** per file raw (nessuna conversione attiva)
- **Limiti lunghezza input:** commenti max **500 caratteri**, titolo clip max **100 caratteri**
- Password con requisiti minimi (lunghezza, complessità base)
- Protezione CSRF sui form
- Sanitizzazione testo commenti per prevenire XSS

### Resilienza & Error Handling

- **Fallimento conversione ffmpeg *(quando implementato)*:** il sistema mantiene il file originale, esegue 1 retry automatico, e in caso di fallimento definitivo notifica l'utente con errore specifico
- **Upload diretto a Django** per file video (il frontend comunica direttamente con il backend Django, CORS diretto per MVP)
- **Nessun target di uptime rigido** per la fase amici — downtime accettabile per debugging e fix

### Scalability

- **MVP**: il sistema deve supportare fino a **50 utenti concorrenti** con tempo di risposta API < 1s
- **Storage**: MinIO self-hosted, file video originali (senza transcoding). Spazio limitato dalle risorse del server — monitorare utilizzo e aggiungere transcoding quando necessario
- **Crescita**: l'architettura deve permettere l'aggiunta di processing asincrono (Celery), proxy API pattern, e real-time (WebSocket) senza riscritture maggiori

### Accessibility

- WCAG 2.1 livello AA base per MVP
- Contrasti di colore sufficienti su testi e controlli
- Navigazione completa via keyboard (tab, enter, escape)
- Alt text su thumbnail e immagini
- Player video con controlli accessibili (play/pause/volume via keyboard)
- Label sui form (registrazione, login, upload, commenti)

### Integration

> **Nota:** Questa sezione è un riferimento architetturale dello stack corrente. I dettagli implementativi completi sono documentati in `docs/architecture-backend.md`.

| Sistema | Tipo | Requisito di qualità |
|---------|------|---------------------|
| Backend REST API | Backend API | Comunicazione HTTP/JSON, auth token-based con refresh, CORS configurato per origini consentite |
| Storage cloud S3-compatible | Storage video | Upload/download con URL autenticati a scadenza temporale per streaming sicuro |
| Estrazione metadati video | Video processing | Estrazione durata video all'upload per validazione |
| Conversione video *(pianificata)* | Video processing | Conversione server-side a formato ottimizzato per streaming web |
| Task scheduling | Automazione | Chiusura automatica contest settimanali al termine del periodo |
| Task asincroni *(pianificato)* | Elaborazione | Processing asincrono per operazioni pesanti (transcoding, batch) |
| Meta tags social | SEO/Sharing | Generazione meta tags per link preview su pagine clip pubbliche |
