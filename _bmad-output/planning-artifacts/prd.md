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
  - _bmad-output/implementation-artifacts/epic-2-retro-2026-03-01.md
documentCounts:
  briefs: 1
  research: 0
  brainstorming: 0
  projectDocs: 8
  projectContext: 1
  retroDoc: 1
workflowType: 'prd'
lastEdited: '2026-03-02'
editHistory:
  - date: '2026-02-28'
    changes: 'Aggiornamento infrastruttura backend: Vercel Blob→MinIO, video processing stato reale, CORS documentato, Keycloak roadmap, Contest System riscritto con 2 tipologie (settimanale auto + bracket CL) e backoffice admin, FR aggiornati/aggiunti (FR53-55), modelli mancanti segnalati, mobile layout corretto'
  - date: '2026-03-01'
    changes: 'Vision card-as-player da retro Epic 2: layout 1 colonna con player inline + sidebar, input MM:SS bidirezionale, rimozione tab commenti, hover preview desktop. Findings validation report: Journey 9+10 contest, purificazione implementation leakage FR/NFR, riconciliazione Esplora in MVP, KPI mancanti ripristinati'
  - date: '2026-03-02'
    changes: 'Post-validation fix: rimossi FR duplicati (FR54, FR35), aggiunto FR59 rating clip nel feed, rimossa esclusione rating da tabella, snellita sezione Innovation (rimanda a Web App per dettagli layout). Tutti i top 3 improvements della validazione risolti'
---

# Product Requirements Document - Video_clip

**Author:** AcchippameQuisso
**Date:** 2026-02-14
**Ultimo aggiornamento:** 2026-03-02

## Executive Summary

**Video_clip** è un social network verticale per gaming clip — "l'Instagram del gaming con commenti temporizzati". La piattaforma permette ai gamer di caricare clip brevi (10s-1min) e ricevere commenti ancorati a momenti specifici del video. I commenti più apprezzati diventano popup overlay visibili a tutti gli spettatori futuri, trasformando il commentatore in co-protagonista della clip.

**Differenziatore competitivo:** Dual-layer commenting system (commenti normali + temporizzati) con promozione automatica a popup nel player — modello SoundCloud applicato al gaming video. Nessun competitor diretto combina commenti temporizzati + gaming-only + contest bracket.

**Paradigma UX card-as-player:** Il feed presenta le clip come card a colonna singola con player video inline e sidebar commenti laterale. L'utente guarda, commenta e interagisce direttamente nel feed senza cambiare pagina. Hover preview su desktop per anteprima rapida. Input timestamp MM:SS esplicito e bidirezionale — il campo compila il player e viceversa. Layout identico per Home, Esplora e Profilo.

**Target users:** Gamer che vogliono condividere momenti epici (creator), spettatori attivi che commentano e analizzano giocate (commentatori), archivisti che organizzano le proprie clip.

**Contesto tecnico:** Brownfield — backend Django REST (DRF, PostgreSQL, SimpleJWT — migrazione pianificata a identity provider esterno). Storage video su object storage S3-compatible. Frontend Next.js (React) con design system dark gaming-themed, desktop-first. Infra locale Docker Compose. Epic 0+1+2 completati: 155 test, 5 modelli core, auth end-to-end, upload con validazione, feed, commenti dual-layer, download, delete video.

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
- Almeno 1 contest settimanale completato con partecipazione reale
- Il passaparola parte — almeno qualche utente esterno al gruppo iniziale

**A 12 mesi (crescita organica):**
- Community attive per i giochi principali
- Contest funzionanti con partecipazione reale (entrambe le tipologie validate)
- Retention stabile — gli utenti tornano per clip, commenti e contest
- Base sufficiente per valutare partnership con publisher

### Technical Success

- **Video 10s-1min**: upload e playback fluido per questa dimensione
- **Player con commenti temporizzati**: popup e sidebar funzionano correttamente sincronizzati al video
- **Feed performante**: scroll fluido con multi-player inline su infinite scroll
- **Card-as-player**: multiple istanze video nel feed senza degradazione performance
- **Pipeline upload-to-playback funzionante end-to-end**: upload → storage cloud → playback con URL autenticato
- **Nessun target numerico rigido per ora** — si ottimizza a prodotto completato in base all'esperienza d'uso reale

### Measurable Outcomes

**North Star Metric:** Commenti temporizzati al giorno — se cresce, il prodotto funziona.

| KPI | Cosa Misura | Frequenza |
|-----|-------------|-----------|
| Commenti temporizzati/giorno | Salute del prodotto (North Star) | Giornaliera |
| Clip caricate/giorno | Volume contenuti | Giornaliera |
| DAU/MAU | Utenti attivi | Giornaliera/Mensile |
| % commenti con like > 0 | Qualità engagement | Settimanale |
| Contest completion rate | % contest che arrivano a fine con tutti i turni votati | Per contest |
| ROI per contest | Costo premi / nuovi utenti acquisiti tramite contest | Per contest |
| Retention D1 / D7 / D30 | Ritorno utenti dopo registrazione | Continua |
| Time-to-first-value | Velocità raggiungimento momento "aha!" per persona | Continua |
| Inviti/utente | Crescita organica | Mensile |
| Clip da Esplora → Follow | Efficacia discovery nel creare connessioni | Settimanale |
| Tasso conversione Lurker → Attivo | Capacità di convertire spettatori passivi | Mensile |

*Target numerici da definire dopo la fase di validazione con il gruppo iniziale.*

## User Journeys

### Journey 1: Luca — Il primo upload che cambia tutto (Gamer Casual - Happy Path)

Luca ha appena fatto un ace su Valorant. Le mani tremano ancora, il cuore batte forte. L'istinto è il solito: apre WhatsApp, cerca il gruppo degli amici. Ma poi si ricorda — un suo compagno gli ha mandato un link a Video_clip la settimana scorsa.

Apre Video_clip, si registra in 30 secondi — username, email, password. Vede il bottone Upload al centro della bottom-bar. Tap. Seleziona la clip dalla gallery (42 secondi). Scrive "Ace con Jett round 12" come titolo, seleziona "clutch" come tag. Conferma. La clip si carica, appare nel suo profilo.

Manda il link ai 5 amici nel gruppo WhatsApp. Loro si registrano, lo seguono, guardano la clip. Nel feed Home, la clip di Luca appare come card a colonna intera con il player inline. Il primo amico preme play direttamente nel feed, pausa al secondo 0:18, e il campo MM:SS si popola automaticamente a "00:18". Scrive: "MA CHE FLICK È QUESTO". Il commento appare nella sidebar accanto al player. Un altro amico clicca nella sidebar, il video salta a 0:31 e scrive: "freddo come il ghiaccio".

Il giorno dopo, Luca apre Video_clip. Scorre il feed Esplora — la sua clip è lì tra le più recenti. Ha 3 commenti da gente che non conosce. Uno ha scritto al campo 00:25: "questo crosshair placement è da predator". Riceve la notifica "X ha commentato la tua clip". Luca non aveva mai ricevuto un complimento tecnico da uno sconosciuto. **Questo è il momento aha!** — la clip che avrebbe mandato su WhatsApp e sarebbe morta in ore, qui vive e cresce.

**Requisiti rivelati:** Registrazione rapida, upload con tag, card-as-player con player inline nel feed, input MM:SS bidirezionale, sidebar commenti nella card, feed Esplora (lista cronologica), condivisione link esterno, notifiche commento ricevuto.

### Journey 2: Marco — Dal live alla clip che vive (Streamer/Creator - Happy Path)

Marco ha appena chiuso lo stream serale di Valorant. 3 ore, 200 viewer, 2-3 momenti epici. Apre Video_clip, va su Upload. Ha già tagliato le clip migliori durante lo stream. Carica la prima — un clutch 1v4 da 35 secondi. Poi una seconda — un fail comico dove muore per danno da caduta al round decisivo. Tag "clutch" e "fail".

I suoi follower Twitch che lo seguono anche su Video_clip vedono le clip nella Home come card a colonna singola. Hovering su desktop, vedono l'anteprima video animata. Click per avviare il playback. I commenti temporizzati iniziano ad arrivare nella sidebar della card. Sul clutch, al secondo 0:22, un commento riceve 5 like e diventa il popup che tutti vedono quando la clip arriva a 0:22. Marco mette like sul commento migliore direttamente dalla sidebar. Clicca "Visualizza tutti i commenti" per aprire la pagina dettaglio con la lista completa.

Due settimane dopo, una sua clip finisce tra le più viste nella sezione Esplora. Arrivano 30 nuovi follower che non lo conoscevano da Twitch. Riceve la notifica "Il tuo commento ha ricevuto N like". **Momento aha!**: Video_clip non è solo un archivio — è un canale di crescita parallelo.

**Requisiti rivelati:** Upload multiplo, card-as-player nel feed Home, hover preview su desktop, commenti popup con più like per timestamp, like sui commenti, bottone "Visualizza tutti i commenti", sharing link esterno, sezione Esplora, notifiche like ricevuto.

### Journey 3: Sara — Il commento che diventa leggenda (Spettatore Attivo - Happy Path)

Sara scorre il feed Esplora durante la pausa pranzo. Le clip appaiono come card a colonna singola con player inline e sidebar commenti. Vede una clip di Valorant — un clutch con Omen. Preme play. Al secondo 0:15, l'Omen fa un teleport dietro due nemici. Sara mette in pausa — il campo MM:SS si popola a "00:15". Scrive nella sidebar: "il timing del TP è perfetto perché l'ulti del Sova era appena finita — sapeva esattamente quando muoversi". Il commento appare nella sidebar della card.

Vuole anche lasciare un commento generale senza timestamp. Cancella il valore dal campo MM:SS e scrive: "Che clip assurda, seguiti!". Questo commento appare nella lista sotto il player, senza badge minutaggio.

Torna la sera. Il suo commento temporizzato ha 12 like — è diventato il popup che appare a tutti al secondo 0:15 della clip. Riceve la notifica "Il tuo commento è ora visibile nel player!". Ogni persona che guarda quella clip ora vede l'analisi di Sara apparire esattamente nel momento giusto. Sara non ha mai caricato una clip — la sua reputazione è costruita interamente sui commenti. Mette like sulla clip di Omen. **Momento aha!**: il suo commento è stato visto da centinaia di persone, ancorato al secondo esatto che conta.

**Requisiti rivelati:** Card-as-player nel feed Esplora, input MM:SS bidirezionale (pausa→popola e manuale→salta), commenti normali senza timestamp, like sui commenti, like sulle clip, algoritmo popup (commento con più like per timestamp), sidebar commenti nella card, navigazione Esplora, notifica promozione a popup.

### Journey 4: Davide — L'archivio che funziona (Archivista - Happy Path)

Davide ha clip sparse ovunque — 200 nella gallery del telefono, 50 su Twitch, screenshot su Steam. Scopre Video_clip e decide di usarlo come archivio. Si registra. Inizia a caricare: 10 clip di Elden Ring (boss fight), 5 di Valorant, 3 di Rocket League. Per ogni clip sceglie titolo e tag.

Una settimana dopo, vuole rivedere la boss fight contro Malenia. Apre il suo profilo — le clip sono tutte lì, in card a colonna singola identiche al feed, ordinate per data. Scarica quella di Malenia per mandarla a un amico su Discord. **Momento aha!**: "Finalmente non devo cercare in 5 cartelle diverse."

*Nota: Journey 4 e Journey 6 anticipano funzionalità di Fase 2 (profilo privato, follow con pending). Per l'MVP i profili sono pubblici e il follow è immediato.*

**Requisiti rivelati:** Upload batch, download proprie clip, organizzazione clip nel profilo con layout identico al feed, profilo pubblico. *(Profilo privato → Fase 2)*

### Journey 5: Luca — Upload fallito (Edge Case - Error Recovery)

Luca prova a caricare una clip da 58 secondi. La connessione è instabile. L'upload arriva al 70% e fallisce. Appare una modale di errore: "Upload fallito. Riprova?" con un bottone "Riprova". Luca tap su Riprova. Questa volta il caricamento va a buon fine. La clip appare nel suo profilo.

Se il video è troppo lungo (oltre 1 minuto) o in formato non supportato, l'errore è specifico: "Il video supera la durata massima di 1 minuto" oppure "Formato non supportato". Luca sa subito cosa fare.

**Requisiti rivelati:** Validazione durata video (10s-1min), messaggi errore specifici per tipo di problema, modale retry, gestione upload interrotto.

### Journey 6: Marco — Richiesta follow da profilo privato (Edge Case)

Marco nota che un utente con profilo privato ha commentato una sua clip. Vuole vedere le clip di questo utente. Va sul suo profilo — vede "Profilo privato". Tap su "Segui" — la richiesta resta in pending. L'utente riceve la notifica e accetta. Ora Marco vede le clip nel profilo e nel feed Home.

**Requisiti rivelati:** Profilo privato, richiesta follow pending/accepted/rejected, stato follow visibile. *(Fase 2)*

### Journey 7: Moderatore — Commento inappropriato (Moderator Path)

Un moderatore scorre i report (o naviga normalmente). Vede un commento offensivo su una clip popolare. Apre l'interfaccia admin nel frontend, trova il commento, e lo disabilita. Il commento non è più visibile nella clip. Se il commento era il popup per quel timestamp, il sistema seleziona automaticamente il successivo commento con più like.

**Requisiti rivelati:** Interfaccia admin frontend, ruolo moderatore, azione disabilita commento, ricalcolo popup dopo disabilitazione.

### Journey 8: Admin — Sospensione account e rimozione video (Admin Path)

L'admin riceve segnalazioni su un utente che carica contenuti inappropriati ripetutamente. Accede all'interfaccia admin nel frontend. Cerca l'utente, vede la lista dei suoi video. Elimina i video inappropriati (i file vengono rimossi dallo storage). Poi sospende l'account — l'utente non può più accedere, i suoi contenuti non sono più visibili.

Se necessario, l'admin può anche confermare la registrazione di utenti in attesa.

**Requisiti rivelati:** Interfaccia admin frontend, eliminazione video da admin, sospensione account, promozione ruoli utente, lista video per utente nell'admin.

### Journey 9: Elena — Il contest settimanale che dà visibilità (Partecipante Contest Settimanale - Happy Path)

Elena gioca a Rocket League ogni sera. Ha una clip pazzesca — un goal aereo da centrocampo. Apre Video_clip, va su Upload, seleziona il tag "clutch". Il sistema le mostra che il video verrà automaticamente iscritto al contest settimanale "Clutch" in corso. Conferma. La clip appare nel suo profilo e nel contest corrente.

Durante la settimana, altri utenti caricano le loro clip con lo stesso tag. Elena scorre la pagina contest e vede tutte le clip iscritte in una classifica provvisoria basata sui voti. Vota 5 stelle su una clip che la impressiona. Riceve la notifica "Un nuovo contest settimanale è iniziato!" quando il ciclo successivo parte.

Il contest si chiude automaticamente a fine settimana. Elena apre la pagina risultati: la sua clip è seconda — il goal aereo ha ricevuto una media voti di 4.3. Il vincitore ha 4.5. Elena vede la classifica finale con i piazzamenti. La clip vincitrice appare in evidenza nella sezione Esplora. Riceve la notifica "Il contest X è terminato — scopri i risultati!".

**Momento aha!**: La sua clip ha ricevuto voti e visibilità da utenti che non la seguivano. Il contest ha trasformato un upload normale in una sfida.

**Requisiti rivelati:** Upload con tag auto-iscrizione a contest settimanale, pagina contest con classifica provvisoria e risultati, votazione 1-5 stelle su clip contest, chiusura automatica contest, notifica apertura e risultati contest, clip vincitrice in evidenza.

### Journey 10: Tommaso — Il bracket che accende la community (Partecipante Contest Bracket - Happy Path)

Tommaso riceve una notifica: "Sei stato invitato al contest Valorant Champions — invia la tua clip entro venerdì". L'admin ha creato un contest bracket Champions League per 8 partecipanti. Tommaso seleziona la sua clip migliore e la invia come entry.

Venerdì sera, il bracket è generato. Tommaso vede il tabellone a eliminazione diretta — 4 matchup al primo turno. La sua clip è opposta a quella di un altro giocatore. Apre il matchup: le due clip sono affiancate. Guarda entrambe, vota 4 stelle sulla clip avversaria e 5 sulla propria (l'autovoto è consentito). Altri utenti votano il matchup.

Il turno si chiude. Tommaso ha vinto — la sua clip ha media 4.2, l'avversario 3.8. Avanza in semifinale. Riceve la notifica "È il tuo turno di votare nel contest X" per gli altri matchup. Segue il tabellone: vede chi avanza, chi è eliminato, i risultati di ogni scontro.

In finale, Tommaso perde per 0.3 punti. Secondo posto. Il vincitore riceve un premio (skin esclusiva finanziata da Video_clip). Tommaso ha guadagnato 15 nuovi follower durante il torneo — gente che ha scoperto le sue clip attraverso il bracket.

**Momento aha!**: Il contest bracket ha trasformato il consumo passivo in competizione attiva. Tommaso torna ogni settimana sperando in un nuovo invito.

**Requisiti rivelati:** Invito contest bracket, invio clip come entry, tabellone a eliminazione diretta con visualizzazione grafica, matchup con clip affiancate, votazione 1-5 stelle per matchup, avanzamento basato su media voti, notifiche turno e risultati, premi per il vincitore, discovery utenti tramite bracket.

### Journey Requirements Summary

| Area Capability | Journey che la rivela |
|-----------------|----------------------|
| **Registrazione/Login** | Luca (J1), tutti |
| **Upload con validazione** | Luca (J1), Marco (J2), Davide (J4), Error (J5), Elena (J9) |
| **Card-as-player (player inline nel feed)** | Luca (J1), Marco (J2), Sara (J3), Davide (J4) |
| **Hover preview desktop** | Marco (J2) |
| **Input MM:SS bidirezionale** | Luca (J1), Sara (J3) |
| **Sidebar commenti nella card** | Luca (J1), Marco (J2), Sara (J3) |
| **Bottone "Visualizza tutti i commenti"** | Marco (J2) |
| **Like commenti** | Marco (J2), Sara (J3) |
| **Like clip** | Sara (J3) |
| **Popup overlay (commento più likato)** | Sara (J3), Moderatore (J7) |
| **Feed Home (following)** | Luca (J1), Marco (J2) |
| **Feed Esplora** | Luca (J1), Sara (J3), Elena (J9) |
| **Profilo pubblico** | Davide (J4) |
| **Profilo privato + Follow con pending** *(Fase 2)* | Davide (J4), Marco (J6) |
| **Download clip** | Davide (J4) |
| **Error handling upload** | Luca (J5) |
| **Contest settimanale (partecipante)** | Elena (J9) |
| **Contest bracket (partecipante)** | Tommaso (J10) |
| **Admin: disabilita commenti** | Moderatore (J7) |
| **Admin: elimina video, sospendi account** | Admin (J8) |
| **Admin: promozione ruoli** | Admin (J8) |
| **Notifiche in-app** | Luca (J1), Marco (J2), Sara (J3), Elena (J9), Tommaso (J10) |
| **Condivisione link esterno** | Luca (J1), Marco (J2) |

## Domain-Specific Requirements

### Storage Video

- **Servizio:** Object storage S3-compatible, self-hosted via Docker Compose
- **Accesso video:** URL autenticato con scadenza temporale (1 ora)
- **Stato video processing:** Estrazione durata video all'upload. Transcoding (conversione a formato leggero ottimizzato) non ancora implementato — da pianificare per ridurre spazio di archiviazione e migliorare playback
- **Vincolo dimensione:** Video da 10 secondi a 1 minuto — validazione durata implementata lato backend

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
- **Commenti normali** (senza timestamp): barriera zero, chiunque può commentare
- **Commenti temporizzati** (con timestamp): i più likati diventano popup nel player — il commento diventa spettacolo
- **Input MM:SS bidirezionale**: il path di minor resistenza guida verso il commento temporizzato

**Il dual-layer è un funnel interno:** i commenti normali catturano i lurker, i popup durante la riproduzione dimostrano la feature e convertono lurker in power user che iniziano a usare i timestamp.

*Per i dettagli di layout (sidebar slot, overlay popup, input MM:SS) → sezione Web App Specific Requirements.*

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
| Gli utenti ignorano il timestamp e commentano solo in modo generico | Campo MM:SS sempre visibile e bidirezionale — il default guida il comportamento. Popup come ricompensa visiva naturale |
| Pochi commenti = nessun popup = esperienza vuota | Nella fase iniziale con amici, i primi commenti temporizzati saranno organici. Il feed Esplora mostrerà clip con popup attivi |
| Troppi popup su clip popolari | Solo il commento con più like per timestamp — un popup per secondo max |
| Senza i commenti temporizzati, il prodotto è "l'ennesimo TikTok gaming" | La verticalità gaming-only ha valore autonomo, ma i commenti temporizzati sono il fossato competitivo — validazione prioritaria |
| Multi-player inline degradano le performance del feed | Lazy loading dei player: solo il video visibile nel viewport è attivo, gli altri mostrano thumbnail statico |

## Web App Specific Requirements

### Project-Type Overview

Video_clip è una web app **desktop-first** (approccio Reddit) costruita con **Next.js (React)** e App Router. La scelta desktop-first è una decisione deliberata: l'esperienza di visione clip con commenti temporizzati, sidebar e overlay funziona meglio su schermo largo. Il responsive mobile segue come adattamento, non come driver del design.

### Technical Architecture Considerations

#### Framework & Stack Frontend

| Componente | Scelta | Motivazione |
|-----------|--------|-------------|
| **Framework** | Next.js (App Router) | SSR per link preview (OG meta tags), React ecosystem |
| **UI Library** | React | Componente ecosistema maturo, community ampia |
| **Styling** | Tailwind CSS | Utility-first, veloce per prototipare, consistente |
| **Deploy Frontend** | Da definire | Next.js compatibile con diverse piattaforme |
| **Storage Video** | Object storage S3-compatible | Self-hosted, URL autenticato per accesso |

#### Proxy API Pattern *(Fase 2)*

*Per l'MVP il frontend comunica direttamente con il backend REST via CORS. Il proxy API pattern è pianificato per Fase 2.*

**Flusso MVP:** Browser → REST API Backend → Database / Object Storage
**Flusso Fase 2:** Browser → Next.js API Route → REST API Backend → Database / Object Storage

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

#### Layout Card-as-Player (1 Colonna)

Feed Home, Esplora e Profilo condividono lo stesso layout: **colonna singola di card** con player video inline e sidebar commenti laterale.

Ogni card contiene:
- **Player video** (click to play, hover preview su desktop)
- **Sidebar commenti** laterale: top N commenti temporizzati per slot (~1 slot ogni 3s)
- **Lista commenti** sotto il player: tutti i commenti (temporizzati con badge MM:SS + normali)
- **Form commento** con campo MM:SS sempre visibile
- **Bottone "Visualizza tutti i commenti"** → naviga a `/clip/{id}` per la vista dettaglio completa
- **Metadati**: titolo, autore, tag, data, like, rating

#### Desktop Layout
- **Sidebar sinistra** (stile Reddit/Discord): navigazione principale, collassabile
- **Area centrale**: feed card-as-player a colonna singola
- **Sidebar commenti** integrata in ogni card (non separata come pannello fisso)

#### Mobile Layout
- **Header**: logo "V" + search + avatar
- **MobileBottomBar**: Home, Esplora, Upload, Profilo
- Layout single-column — card-as-player adattato: sidebar commenti sotto il player (non laterale)
- No hamburger menu

#### Due Layout Distinti
- **Autenticato**: sidebar nav + feed card-as-player + azioni (upload, like, commenta)
- **Pubblico** (non loggato): pagina clip con SSR, CTA registrazione, funzionalità limitate

### Hover Preview Video

Su desktop, quando l'utente passa il mouse sopra una card nel feed senza cliccare:
- Il video mostra un'anteprima animata (primi 3-5 secondi in loop, senza audio)
- L'anteprima si interrompe quando il mouse esce dalla card
- Click per avviare il playback completo con audio

### Video Processing

- **Stato attuale:** Estrazione durata video all'upload. Il file originale viene salvato direttamente su storage senza conversione
- **Upload flow attuale:** file originale → validazione durata (10s-1min, reject automatico) → storage
- **Upload flow pianificato:** file originale → validazione durata → conversione formato ottimizzato → storage
- **Processing asincrono:** da implementare quando il transcoding sarà aggiunto

### Navigazione & UX Card-as-Player

#### Card nel Feed (Home / Esplora / Profilo)
- Layout identico in tutte e tre le sezioni: colonna singola di card
- Ogni card è un'unità autonoma: player + sidebar commenti + form + azioni
- Infinite scroll per caricare card successive
- Lazy loading: solo il player nel viewport è attivo, gli altri mostrano thumbnail

#### Pagina Dettaglio (`/clip/{id}`)
- Stessa struttura della card ma espansa a piena larghezza
- Player video + sidebar commenti completa
- Lista completa di TUTTI i commenti sotto il player
- Form commento con input MM:SS bidirezionale
- Accessibile via URL diretto per condivisione esterna

#### Sistema di Overlay (Pop-up Temporali)
- Durante la riproduzione del video, **pop-up grafici** appaiono sopra il player
- Logica: mostra il **commento con più like associato a quel preciso timestamp** (es. a 0:15, poi a 0:25)
- Il pop-up **sparisce dopo 3 secondi** con fade-out
- Posizione: angolo in alto a destra del player
- Soglia minima: almeno 1 like per essere promosso a popup
- Funziona sia nella card del feed che nella pagina dettaglio

#### Input Timestamp MM:SS Bidirezionale
- Campo MM:SS sempre visibile nel form commento (non nascosto)
- **Player → Campo**: quando l'utente pausa il video, il campo si popola automaticamente con il timestamp corrente
- **Campo → Player**: quando l'utente compila manualmente MM:SS, il video salta a quel secondo
- L'utente può cancellare il valore per pubblicare un commento normale (senza timestamp)
- Validazione: il valore MM:SS non può superare la durata del video

### Real-Time Strategy

- **MVP**: Nessun real-time. Tutti i dati sono fetch-based (caricamento pagina / polling manuale)
- **Growth**: Valutare WebSocket o SSE per notifiche commenti e aggiornamento sidebar in tempo reale
- **Motivazione**: il prodotto funziona senza real-time — la sidebar basata sui like dà già l'illusione di attività

### Implementation Considerations

- **State Management**: React Context per auth/user state, fetch-based per dati clip/commenti
- **Video Player**: HTML5 `<video>` con controller custom per gestire overlay popup e sincronizzazione timestamp
- **Multi-player performance**: lazy loading viewport-based, un solo player attivo alla volta
- **Image/Video Optimization**: Next.js Image per thumbnail, lazy loading nel feed
- **SEO**: pagine clip pubbliche indicizzabili, sitemap dinamica per clip popolari
- **Accessibilità**: livello base AA per MVP — focus su contrasti, navigazione keyboard, alt text

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**Approccio MVP:** Experience MVP — validare che il core loop (upload → guarda → commenta con timestamp → vedi popup) e i contest creino engagement reale con un gruppo ristretto di amici/sviluppatori.

**Principio guida:** Due pilastri, zero distrazioni. I commenti temporizzati dimostrano l'innovazione. I contest (settimanale auto-gestito + bracket Champions League) creano eventi ricorrenti che generano retention. Tutto il resto è Fase 2.

**Strategia di rilascio interno:**
- **Release A:** Core Platform + Clip Experience + Redesign Layout card-as-player — validare il loop commenti temporizzati nel nuovo paradigma UX
- **Release B:** Contest System — validare due tipologie contest (settimanale + bracket) come secondo motore di engagement
- Questo approccio produce dati di validazione puliti su ciascun pilastro

**Team:** Sviluppatore singolo (AcchippameQuisso) + amici sviluppatori come tester iniziali.

**Debito tecnico consapevole MVP:**
- CORS diretto — restrittivo su origini specifiche. Proxy API pattern in Fase 2
- Nessun transcoding video (file salvato così com'è, solo validazione durata)
- Nessun real-time (fetch-based, polling manuale)
- CI pipeline non ancora verificata end-to-end

### MVP Feature Set (Fase 1)

**Struttura Epic:**

#### Epic 1: Core Platform *(completato)*
- Auth (registrazione/login JWT)
- Profilo pubblico base con bio
- Follow/Unfollow semplice (senza pending)
- Admin/moderazione base (disabilita commenti, elimina video, sospendi account)

#### Epic 2: Clip Experience *(completato)*
- Upload clip 10s-1min con validazione completa + storage
- Player video HTML5 con commenti temporizzati
- Dual-layer commenti (normali + temporizzati)
- Feed Home (clip degli utenti seguiti) + Feed Esplora
- Link preview SSR per condivisione esterna (OG meta tags)
- Download clip proprie + allow_download per altri
- Delete video con conferma
- Rating CRUD

#### Epic Intermedio: Redesign Layout Card-as-Player *(prossimo)*
- Trasformazione layout feed da griglia card a colonna singola card-as-player
- Player video inline in ogni card con sidebar commenti laterale
- Input timestamp MM:SS esplicito bidirezionale
- Rimozione tab "Tutti"/"Nel video" → vista unificata (sidebar top + lista sotto)
- Hover preview video su desktop
- Bottone "Visualizza tutti i commenti" per navigazione a dettaglio
- Layout identico Home/Esplora/Profilo
- Ottimizzazione performance multi-player (lazy loading viewport-based)

#### Epic 3: Like, Popup e Engagement Loop
- Like sulle clip + Like sui commenti
- Popup overlay con dati reali e sidebar dinamica a slot temporizzati
- Aggiornamento algoritmo spareggio contest
- Comment markers sulla timeline (opzionale)

#### Epic 4: Contest System
- Backoffice admin per contest: interfaccia admin per creare contest e scegliere la tipologia

**Tipologia A — Contest Settimanale Auto-gestito:**
- Creazione automatica: un contest settimanale viene creato quando un video è caricato con un tag contest (lun-ven)
- Chiusura automatica al termine del periodo
- Utenti caricano clip che vengono auto-assegnate al contest corrente
- Votazione 1-5 stelle sulle singole clip del contest
- **Vincitore:** clip con media voti più alta. In caso di parimerito: spareggio ponderato — 50% numero voti ricevuti, 30% visualizzazioni, 20% like
- Pagina contest con classifica e risultati
- Nessun premio — il contest settimanale è un meccanismo di engagement e visibilità

**Tipologia B — Contest Bracket Champions League:**
- Creazione manuale da admin tramite backoffice
- Iscrizione partecipanti con invio clip
- Bracket eliminazione diretta con visualizzazione grafica interattiva (albero torneo con scontri, risultati per turno)
- Votazione 1-5 stelle per matchup
- **Avanzamento e vincitore: solo voti interni al matchup** (media voti, nessun fattore esterno)
- Pagina contest con stato bracket e progressione
- **Premi esclusivi Champions League:** Fase 1 premi finanziati Video_clip (skins, crediti in-game shop). Fase 2 partnership con publisher per premi premium

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

Implementazione: sistema notifiche backend + endpoint lista notifiche + campanella con badge nella sidebar frontend.

**Core User Journeys Supportati:**
- J1 (Luca - primo upload), J2 (Marco - creator), J3 (Sara - spettatore attivo), J5 (error recovery)
- J7 (Moderatore) e J8 (Admin) — per gestione contest e moderazione
- J9 (Elena - contest settimanale), J10 (Tommaso - contest bracket)

**Escluso dall'MVP (decisione esplicita):**

| Feature | Motivo esclusione | Fase target |
|---------|-------------------|-------------|
| Profili privati + follow pending | Complessità non necessaria con gruppo amici | Fase 2 |
| Proxy API pattern | CORS restrittivo sufficiente per fase amici | Fase 2 |
| Categorizzazione per gioco | Poco contenuto per giustificare filtri | Fase 2 |
| Transcoding video | Nessun transcoding attivo, file originali | Fase 2 |
| Processing video asincrono | Da attivare quando serve transcoding | Fase 2 |
| Real-time (WebSocket/SSE) | Fetch-based sufficiente | Fase 2 |
| Contest creati da utenti | Inizialmente solo admin/moderatori | Fase 3 |

### Post-MVP Features

**Fase 2 — Growth (dopo validazione con gruppo iniziale):**
- Profili privati + follow con pending/accepted/rejected
- Proxy API pattern (Next.js API Routes → Backend REST)
- Categorizzazione per gioco (modello Game)
- Processing video asincrono
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

### Modello Premi Contest

- **Fase 1 (lancio):** Video_clip finanzia i premi (skin, ricariche shop in-game) come investimento di crescita — i contest funzionano come canale di acquisizione utenti più efficiente della pubblicità tradizionale
- **Fase 2 (scala):** Partnership con publisher di giochi che forniscono premi come canale promozionale verso la community gaming
- **Zero fee per i partecipanti** — la barriera di ingresso ai contest deve restare zero

### Risk Mitigation Strategy

**Rischi Tecnici:**

| Rischio | Mitigazione |
|---------|-------------|
| Multi-player inline degradano performance del feed | Lazy loading viewport-based: solo 1 player attivo, gli altri mostrano thumbnail. Benchmark su 20+ card |
| Contest bracket richiede modelli aggiuntivi | Modelli bracket, matchup, entry da creare. Contest settimanale auto-gestito è parzialmente implementato |
| Nessun transcoding video | File originali. Accettabile per MVP con volumi bassi. Aggiungere transcoding quando lo spazio storage diventa critico |
| CORS espone URL backend | CORS restrittivo su origini specifiche. Proxy API come upgrade Fase 2 |

**Rischi di Mercato:**

| Rischio | Mitigazione |
|---------|-------------|
| Gli amici usano il prodotto per cortesia | Monitorare North Star: commenti temporizzati/giorno + notifiche lette vs ignorate |
| Contest senza partecipanti | Contest settimanale auto-gestito ha barriera zero (basta caricare una clip). Bracket da 4-8 amici funziona per contest manuali |
| Nessuna crescita oltre il gruppo | Link preview SSR + condivisione esterna. Contest generano clip condivisibili |

**Rischi Risorse:**

| Rischio | Mitigazione |
|---------|-------------|
| Sviluppatore singolo, troppo scope | Release interne (A: clip + redesign, B: contest). Se serve tagliare, contest parte dopo |
| Storage cresce senza transcoding | File originali occupano più spazio. Volumi bassi iniziali rendono il problema gestibile |

## Functional Requirements

### Gestione Utenti

- FR1: Utente non registrato può creare un account con username, email e password
- FR2: Utente registrato può autenticarsi con le proprie credenziali
- FR3: Utente registrato può visualizzare e modificare il proprio profilo pubblico (inclusa bio)
- FR4: Utente registrato può seguire altri utenti
- FR5: Utente registrato può smettere di seguire utenti che segue
- FR6: Utente registrato può visualizzare le proprie liste follower e following
- FR53: Utente può visualizzare il profilo di un altro utente tramite username

### Creazione & Gestione Contenuti

- FR7: Utente registrato può caricare una clip video (durata 10s-1min)
- FR8: Il sistema valida la durata della clip e rifiuta video fuori range con messaggio di errore che indica il motivo specifico del rifiuto
- FR9: Il sistema valida il formato della clip e fornisce errore che indica il formato non supportato e i formati accettati
- FR10: *(Pianificato)* Il sistema converte le clip caricate in formato ottimizzato per streaming web
- FR11: Utente registrato può impostare titolo e tag tipo per la clip caricata
- FR12: Utente registrato può impostare se la propria clip è scaricabile da altri utenti
- FR13: Utente registrato può scaricare le proprie clip
- FR14: Utente registrato può scaricare clip altrui quando il download è abilitato dall'autore
- FR15: Il sistema archivia le clip su storage cloud con URL di accesso autenticato a scadenza temporale
- FR16: Il sistema mostra una modale di errore con opzione "Riprova" quando l'upload fallisce
- FR56: Utente registrato può eliminare le proprie clip caricate

### Scoperta & Fruizione Contenuti

- FR17: Utente registrato può visualizzare un feed Home con le clip degli utenti seguiti, presentate come card a colonna singola con player video inline
- FR18: Utente può visualizzare la pagina dettaglio clip con player espanso, sidebar commenti completa e lista completa di tutti i commenti
- FR19: Le pagine dettaglio clip sono accessibili tramite URL diretto per la condivisione
- FR20: Il sistema genera link preview ricche (titolo, thumbnail) per gli URL delle clip condivisi su piattaforme esterne
- FR21: Il feed presenta le clip come card a colonna singola con player inline, sidebar commenti laterale e metadati (titolo, autore, tag, like)
- FR22: Su desktop, l'utente può vedere un'anteprima animata della clip (primi 3-5 secondi in loop, senza audio) al passaggio del mouse sulla card
- FR57: Utente può visualizzare un feed Esplora con clip pubbliche recenti, stesso layout card-as-player del feed Home
- FR58: Utente può navigare dalla card nel feed alla pagina dettaglio completa della clip tramite bottone "Visualizza tutti i commenti"

### Sistema Commenti & Interazioni

- FR23: Utente registrato può pubblicare un commento su una clip senza timestamp
- FR24: Utente registrato può pubblicare un commento temporizzato su una clip con timestamp specifico
- FR25: Il form commento presenta un campo MM:SS sempre visibile. Quando l'utente pausa il video, il campo si popola automaticamente con il timestamp corrente
- FR26: Quando l'utente compila manualmente il campo MM:SS, il video salta a quel secondo. L'utente può cancellare il valore per pubblicare un commento normale
- FR27: Utente registrato può mettere like a un commento
- FR28: Utente registrato può mettere like a una clip
- FR59: Utente registrato può assegnare un rating da 1 a 5 stelle a una clip nel feed. Il rating è modificabile e la media viene mostrata sulla card
- FR29: La sidebar della card mostra i top commenti temporizzati organizzati per slot temporali (~1 slot ogni 3 secondi), con il commento più likato per slot
- FR30: La lista sotto il player mostra tutti i commenti: temporizzati con badge minutaggio MM:SS e normali senza badge, in ordine cronologico

### Popup & Loop di Engagement

- FR31: Il sistema identifica il commento con più like per ogni timestamp di una clip
- FR32: Durante la riproduzione video, popup overlay mostrano il commento con più like per il timestamp corrente
- FR33: I popup overlay scompaiono dopo 3 secondi con fade-out
- FR34: I popup richiedono una soglia minima di 1 like per essere promossi
- FR36: Quando un commento viene disabilitato dalla moderazione, il sistema ricalcola il prossimo commento con più like per quel timestamp

### Sistema Contest

**Backoffice Admin:**
- FR37: Admin può creare un contest tramite backoffice, scegliendo la tipologia (settimanale auto-gestito o bracket Champions League)
- FR38: Utente registrato può visualizzare i contest disponibili (entrambe le tipologie)

**Tipologia A — Contest Settimanale Auto-gestito:**
- FR39a: Un contest settimanale viene creato automaticamente quando un video è caricato con un tag contest (periodo lun-ven)
- FR39b: Le clip caricate vengono auto-assegnate al contest settimanale corrente in base al tag
- FR40a: Utente registrato può votare da 1 a 5 stelle sulle clip del contest settimanale
- FR41a: Il sistema chiude automaticamente il contest al termine del periodo tramite task schedulato
- FR42a: Il vincitore è la clip con la media voti più alta. In caso di parimerito: spareggio ponderato (50% numero voti, 30% visualizzazioni, 20% like)
- FR43a: Utente può visualizzare classifica provvisoria e risultati finali del contest settimanale

**Tipologia B — Contest Bracket Champions League:**
- FR39c: Utente registrato può iscriversi a un contest bracket inviando una clip
- FR40b: Il sistema genera un bracket a eliminazione diretta con minimo 4 e massimo 32 partecipanti, seeding casuale
- FR41b: Il contest mostra un albero grafico del bracket con navigazione: click su matchup per vedere le clip, visualizzazione risultati per turno, evidenziazione del percorso di ogni partecipante
- FR42b: Utente registrato può votare da 1 a 5 stelle sulle clip di un matchup del contest bracket
- FR43b: Il sistema calcola la media dei voti interni al matchup e fa avanzare il vincitore (nessun fattore esterno)
- FR44: Utente può visualizzare stato del contest bracket, risultati passati per turno, e progressione nel bracket
- FR44b: Il vincitore del contest bracket riceve un premio (Fase 1: premi finanziati dalla piattaforma; Fase 2: premi da partnership publisher)

### Amministrazione & Moderazione

- FR45: Moderatore può disabilitare commenti inappropriati
- FR46: Admin può eliminare video
- FR47: Admin può sospendere account utente
- FR48: Admin può promuovere utenti tra ruoli (es. confermare registrazione)
- FR49: Admin può visualizzare la lista dei video per utente
- FR55: Admin può gestire contest tramite backoffice dedicato nel frontend (creazione, monitoraggio, chiusura manuale)

### Notifiche

- FR50: Il sistema invia notifiche in-app per eventi chiave: commento ricevuto, like ricevuto su commento, commento promosso a popup, contest aperto, invito contest bracket, turno contest disponibile, risultati contest
- FR51: Utente registrato può visualizzare la propria lista notifiche in ordine cronologico
- FR52: Il sistema mostra un badge con il conteggio delle notifiche non lette nella navigazione

## Non-Functional Requirements

### Performance

| Requisito | Target | Metodo di Misurazione |
|-----------|--------|----------------------|
| First Contentful Paint | < 1.5s | Lighthouse lab test, p75 |
| Time to Interactive | < 3s | Lighthouse lab test, p75 |
| Video Start Playback | < 2s | Misurazione client-side su connessione broadband (>10 Mbps), p90 |
| Lighthouse Performance Score | > 80 (categorie: Performance, Accessibility, Best Practices) | Lighthouse CI su pagine chiave (home, clip detail, profilo) |
| Risposta API (lettura) | < 500ms p95 | Logging server-side su endpoint feed, commenti, notifiche |
| Risposta API (scrittura) | < 1s p95 | Logging server-side su endpoint like, commenti, follow |
| Upload video (escl. conversione) | < 30s per 500MB | Misurazione client-side su connessione broadband (>10 Mbps) |
| Conversione video *(pianificata)* | < 2x durata clip | Logging server-side, es. clip 30s → conversione < 60s |
| Latenza popup overlay vs timestamp | < 200ms | Dati popup pre-caricati in singola chiamata API al caricamento pagina |
| Progress bar upload | Aggiornamento ogni 500ms minimo | Misurazione client-side tramite evento progress HTTP |

**Strategia pre-caricamento popup:** I dati dei popup (timestamp + testo commento + autore) per una clip devono essere caricati in un'unica chiamata API al caricamento della pagina. Il player legge i dati localmente durante il playback — nessuna chiamata API on-demand durante la riproduzione.

**Multi-player nel feed:** Un solo player attivo per volta (quello nel viewport). Gli altri mostrano thumbnail statico. Transizione thumbnail→player al scroll. Benchmark target: feed con 20+ card senza degradazione visibile del frame rate di scroll.

### Security

- Autenticazione tramite JWT con refresh token. Migrazione pianificata a identity provider esterno per SSO e gestione centralizzata identità
- CORS: restrittivo su origini specifiche in produzione
- Validazione input su tutti gli endpoint (durata clip, formato file, lunghezza commenti)
- **Vincolo integrità voto contest:** Ogni utente può votare una sola volta per clip (contest settimanale) o per matchup (contest bracket) — enforced lato backend e lato frontend (UI disabilitata dopo il voto). Gestione edge case: double-click, tab multipli
- Upload limitato a formati video consentiti — whitelist: MP4, MOV, AVI, MKV, WebM
- Limite dimensione file upload: max 500MB per file
- **Limiti lunghezza input:** commenti max 500 caratteri, titolo clip max 100 caratteri
- **Password:** minimo 8 caratteri, almeno 1 lettera e 1 numero
- Protezione CSRF sui form
- Sanitizzazione testo commenti per prevenire XSS

### Resilienza & Error Handling

- **Fallimento conversione video *(quando implementato)*:** il sistema mantiene il file originale, esegue 1 retry automatico, e in caso di fallimento definitivo notifica l'utente con errore specifico
- **Upload:** il frontend comunica con il backend REST, CORS restrittivo per MVP
- **Nessun target di uptime rigido** per la fase amici — downtime accettabile per debugging e fix

### Scalability

- **MVP**: il sistema deve supportare fino a 50 utenti concorrenti con tempo di risposta API < 1s (misurato con load test tool, burst di 50 richieste simultanee)
- **Storage**: file video originali (senza transcoding). Spazio limitato dalle risorse del server — monitorare utilizzo disco e aggiungere transcoding quando lo storage supera l'80% di capacità
- **Crescita**: l'architettura deve permettere l'aggiunta di processing asincrono, proxy API pattern, e real-time senza riscritture maggiori

### Accessibility

- WCAG 2.1 livello AA base per MVP
- Contrasti di colore: ratio minimo 4.5:1 per testo normale, 3:1 per testo grande
- Navigazione completa via keyboard (tab, enter, escape)
- Alt text su thumbnail e immagini
- Player video con controlli accessibili (play/pause/volume via keyboard)
- Label sui form (registrazione, login, upload, commenti)
