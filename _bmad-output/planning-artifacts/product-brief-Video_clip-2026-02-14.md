---
stepsCompleted: [1, 2, 3, 4, 5, 6]
status: complete
inputDocuments:
  - _bmad-output/project-context.md
  - docs/index.md
  - docs/project-overview.md
  - docs/architecture.md
  - docs/development-guide.md
  - docs/data-models.md
  - docs/api-contracts.md
  - docs/source-tree-analysis.md
date: 2026-02-14
author: AcchippameQuisso
---

# Product Brief: Video_clip

<!-- Content will be appended sequentially through collaborative workflow steps -->

## Executive Summary

Video_clip è l'"Instagram del gaming" — un social network verticale dove ogni gamer è già un creator. In un panorama dove le clip gaming sono disperse su piattaforme generaliste (TikTok, YouTube Shorts, Instagram Reels) o condivise via chat (WhatsApp, Discord) dove muoiono in poche ore, Video_clip offre una casa dedicata ai momenti epici del gaming. L'utente giorno-1 non è un content creator professionista — è il gamer che ha appena fatto un ace su Valorant e vuole condividerlo in 2 tap, anche solo per i 5 amici che lo seguono. La piattaforma si distingue per un sistema di commenti temporizzati stile SoundCloud integrati come DNA in ogni clip, feed personalizzati in base ai giochi dell'utente, e contest a eliminazione diretta con tabellone che trasformano la community in giudici attivi. Il growth loop è organico: momento epico → condivisione amici → commenti temporizzati → contest → discovery → nuovi follower → più momenti condivisi.

---

## Core Vision

### Problem Statement

Le clip di gaming — momenti clutch, fail epici, giocate incredibili — oggi non hanno una casa. Vengono inviate su WhatsApp dove muoiono in poche ore, caricate su YouTube dove nessuno le trova, o disperse nei feed di TikTok e Instagram dove competono con cucina, danza e lifestyle. Twitch è orientato al live streaming, non alla cura delle clip. Non esiste una piattaforma centralizzata pensata per il gamer che vive un momento epico e vuole condividerlo subito, nel posto dove la gente capisce cosa sta guardando.

### Problem Impact

- **Per il gamer casual**: il momento epico finisce su WhatsApp, visto da 3 persone, e sparisce. Non c'è un posto dove quel momento vive, viene visto e commentato dalla community giusta
- **Per i creator/streamer**: le clip si perdono nei feed generalisti, non raggiungono il pubblico gaming, e mancano strumenti per costruire una community attorno ai propri highlight
- **Per la community gaming**: le interazioni sulle clip sono limitate a commenti generici — manca la possibilità di reagire al momento esatto che conta, di competere attraverso i contenuti, di scoprire clip dei giochi che si giocano davvero
- **Per l'ecosistema**: la viralità gaming è frammentata — nessuna piattaforma aggrega e valorizza i momenti migliori del gaming in un unico luogo

### Why Existing Solutions Fall Short

- **WhatsApp / Discord**: le clip vengono condivise ma muoiono in ore. Nessuna discovery, nessuna community, nessuna persistenza
- **TikTok / YouTube Shorts / Instagram Reels**: piattaforme generaliste — le clip gaming competono con ogni tipo di contenuto. Nessuna categorizzazione per gioco, nessun feed personalizzato per gamer, nessuna meccanica competitiva
- **Twitch Clips**: legato all'ecosistema streaming, non pensato come social standalone. I clip restano ancillari al live
- **Medal.tv**: cattura e condivide clip ma manca di una dimensione social profonda — no commenti temporizzati, no contest community-driven, no feed personalizzato
- **Nessuno** offre commenti temporizzati stile SoundCloud applicati al gaming, né contest a eliminazione diretta con tabellone

### Proposed Solution

Video_clip è un social network verticale per gaming clips dove ogni gamer è già un creator. Tre pilastri:

1. **Condivisione a Barriera Zero**
   - Upload in 2 tap: apri, carica, fatto
   - Categorizzazione automatica per gioco e tipo clip (clutch, funny, ace, fail, etc.)
   - Download delle proprie clip sempre disponibile, opzione per abilitare download da altri (impostabile all'upload)
   - Integrazione futura con Steam e Twitch

2. **Commenti Temporizzati come DNA del Prodotto**
   - Commenti ancorati a un secondo specifico del video, timestamp scelto dall'autore del commento
   - Popup nel player: il commento con più like per ogni timestamp appare durante la riproduzione
   - Sidebar tipo chat Twitch: commenti più apprezzati in tempo reale
   - Pagina dettaglio: tutti i commenti ordinati per data
   - Non una feature isolata — integrati in ogni clip, ovunque nel prodotto

3. **Feed Intelligente Dual-Mode**
   - **Home**: clip degli utenti seguiti, indipendentemente dal gioco, con badge identificativi (gioco + tipo clip)
   - **Esplora**: clip personalizzate in base ai giochi nel profilo dell'utente, arricchite da contenuti virali cross-game

4. **Contest a Eliminazione Diretta**
   - Tabellone tipo Champions League (ottavi, quarti, semifinali, finale)
   - La community vota chi avanza ad ogni turno
   - Trasforma il consumo passivo in partecipazione attiva e competitiva

5. **Navigazione Progressive Disclosure**
   - 5 sezioni: Home, Esplora, Upload (centrale), Contest, Profilo
   - Bottom-bar mobile-first, familiare come Instagram
   - Complessità rivelata gradualmente: l'utente giorno-1 vede feed, upload, commenti. I contest si scoprono quando si è pronti

### Key Differentiators

| Differenziatore | Impatto |
|-----------------|---------|
| **Commenti temporizzati stile SoundCloud** | DNA del prodotto — interazione unica nel gaming, nessun competitor la offre |
| **Barriera zero per ogni gamer** | Non serve essere creator — dal momento epico alla condivisione in 2 tap |
| **Contest a tabellone** | Growth engine — trasforma i contenuti stessi in competizione strutturata |
| **Growth loop organico** | Momento → amici → commenti → contest → discovery → follower → più momenti |
| **Verticalità gaming-only** | Feed, discovery e categorizzazione pensati per gamer, non diluiti |
| **Feed personalizzato per giochi** | L'utente vede clip dei giochi che gioca, non contenuti random |
| **Integrazioni gaming native** | Steam, Twitch — l'identità gaming dell'utente al centro |

## Target Users

### Primary Users

#### 1. Lo Streamer/Creator — "Marco, 24 anni, streamer Valorant su Twitch"

**Chi è:** Marco streamma Valorant 4-5 sere a settimana su Twitch con una community di 2.000 follower. Quando succede qualcosa di epico in live, i suoi viewer glielo fanno notare subito in chat. Oggi taglia la clip su Twitch e la posta su Twitter/TikTok sperando che arrivi al pubblico giusto.

**Come vive il problema:** Le clip su TikTok competono con video di cucina. Su Twitter vivono 24 ore. Su Twitch restano sepolte nella sezione clip del canale. I suoi momenti migliori non hanno una casa dove la community gaming li apprezzi davvero.

**Come usa Video_clip:** Dopo ogni stream, pubblica i 2-3 momenti migliori. I suoi follower Twitch lo seguono anche qui. Ma la vera svolta è che una sua clip potrebbe diventare virale nella sezione Esplora, portandogli follower che non lo conoscevano da Twitch. Partecipa ai contest a tabellone per sfidare altri creator dello stesso gioco.

**Momento "aha!":** Quando vede i commenti temporizzati apparire sulla sua clip al momento esatto del clutch, e quando vince un turno di contest con i partecipanti che votano tra di loro.

**Motivazione:** Crescita della community, visibilità cross-platform, competizione tra pari.

---

#### 2. Il Gamer Casual — "Luca, 19 anni, gioca a Fortnite e Rocket League con gli amici"

**Chi è:** Luca gioca 2-3 ore al giorno dopo le lezioni, principalmente su PC ma anche su console. Non è uno streamer, non ha un canale. Ma ogni tanto fa una giocata pazzesca e l'istinto è condividerla.

**Come vive il problema:** Oggi manda la clip nel gruppo WhatsApp con i 5 amici. Loro la guardano, ridono, finita lì. Il momento epico nasce e muore in poche ore, visto da 3 persone.

**Come usa Video_clip:** Appena finisce la partita, carica la clip in 2 tap, seleziona gioco e tipo. I suoi 5 amici la vedono nella Home, commentano al timestamp del momento chiave. A volte la clip finisce nella sezione Esplora — e arrivano commenti e follower da sconosciuti che giocano allo stesso gioco.

**Momento "aha!":** Quando la clip che avrebbe mandato su WhatsApp riceve 50 commenti temporizzati da gente che capisce perché quella giocata era assurda.

**Motivazione:** Condivisione immediata, riconoscimento dalla community, divertimento.

---

#### 3. Lo Spettatore Attivo — "Sara, 21 anni, appassionata di gaming, commenta più che gioca"

**Chi è:** Sara gioca saltuariamente ma segue tantissimo la scena gaming. Guarda stream, segue creator, è sempre nel loop. Non carica clip sue ma è attivissima nei commenti.

**Come vive il problema:** Su TikTok e YouTube il suo commento si perde tra migliaia. Non c'è modo di fare emergere un'osservazione brillante legata a un momento preciso della clip.

**Come usa Video_clip:** Scorre il feed Esplora, guarda clip dei giochi che le interessano. Scrive commenti temporizzati perfettamente sincronizzati — battute al secondo esatto del fail, analisi tecniche al momento del clutch. I suoi commenti prendono like e diventano il popup che tutti vedono a quel timestamp. Non può partecipare ai contest né votare (riservato a chi carica clip), ma segue i tabelloni come spettatrice. La sua "fama" è costruita interamente sui commenti.

**Momento "aha!":** Quando il suo commento timestampato diventa il popup visibile a tutti al secondo 0:15 di una clip virale. Guadagna like, follower, e reputazione come commentatrice della community.

**Motivazione:** Interazione sociale, riconoscimento come commentatore, intrattenimento, costruzione di reputazione.

---

#### 4. L'Archivista — "Davide, 22 anni, gioca a tutto e salva tutto"

**Chi è:** Davide è un gamer attivo che gioca a molti titoli diversi — da Valorant a Elden Ring, da FIFA a indie. Registra spesso le sue giocate, accumula clip, ma non è interessato alla dimensione social o competitiva. Vuole un posto dove mettere ordine.

**Come vive il problema:** Le clip stanno sparse ovunque: cartelle sul PC, gallery del telefono, clip di Twitch/Xbox, screenshot su Steam. Non c'è un unico posto organizzato per gioco dove ritrovarle. Quando vuole rivedere una giocata di 3 mesi fa, deve cercare tra 5 fonti diverse.

**Come usa Video_clip:** Carica le sue clip come archivio personale, categorizzate per gioco. Il profilo può essere privato o semi-privato. Non commenta, non partecipa ai contest, non cerca follower. Usa Video_clip come cloud storage gaming organizzato. Scarica le sue clip quando gli servono per montare video o condividere altrove.

**Momento "aha!":** Quando cerca "Elden Ring" nel suo profilo e trova tutte le clip di boss fight ordinate per data. "Finalmente non devo cercare in 5 cartelle diverse."

**Motivazione:** Organizzazione, archiviazione, accesso rapido alle proprie clip.

### Secondary Users

#### Organizzatori di Contest (futuro)

Utenti con community attiva che potrebbero in futuro creare contest personalizzati (custom bracket con regole specifiche, gioco selezionato, numero di partecipanti). Per la v1 i contest sono gestiti dalla piattaforma, ma il profilo dell'organizzatore emerge come evoluzione naturale.

#### Spettatore Passivo (Lurker)

Chi naviga Video_clip senza account o con account ma senza interagire. Guarda clip nella sezione Esplora, segue i contest come spettatore. Non commenta, non vota, non carica. È il bacino da convertire in Spettatore Attivo o Gamer Casual. Importante per le metriche di traffico e viralità.

### User Journey

| Fase | Streamer/Creator (Marco) | Gamer Casual (Luca) | Spettatore Attivo (Sara) | Archivista (Davide) |
|------|--------------------------|---------------------|--------------------------|---------------------|
| **Discovery** | Vede altri streamer postare clip con link Video_clip | Un amico gli manda un link a una clip su Video_clip invece che su WhatsApp | Vede una clip virale condivisa su Twitter/Discord con commenti temporizzati | Cerca una soluzione per organizzare le sue clip gaming |
| **Onboarding** | Registrazione, collega Twitch/Steam, seleziona giochi | Registrazione rapida, seleziona 2-3 giochi, segue i 5 amici | Registrazione, seleziona giochi che segue, esplora il feed | Registrazione, seleziona tutti i giochi che gioca, imposta profilo privato |
| **Prima azione** | Carica la prima clip da una live recente | Carica la clip dell'ace appena fatto | Scrive il primo commento temporizzato | Carica un batch di clip e le organizza per gioco |
| **Core usage** | Pubblica highlight post-stream, partecipa a contest | Carica clip quando capita il momento epico, commenta clip amici | Commenta con timestamp, accumula like, segue contest come spettatrice | Carica clip regolarmente come backup, scarica quando serve |
| **Momento "aha!"** | Commenti temporizzati + vittoria turno contest | Clip per 5 amici riceve 50 commenti da sconosciuti | Il suo commento diventa popup su clip virale | Trova tutte le sue clip ordinate per gioco e data |
| **Lungo termine** | Video_clip = portfolio gaming + canale crescita parallelo | Da casual diventa partecipante regolare ai contest | Reputazione come commentatore, potenziale futuro creator | Archivio completo, potrebbe iniziare a rendere pubbliche le clip migliori |

## Success Metrics

### North Star Metric

**Commenti temporizzati al giorno** — Se questa metrica cresce, significa che le clip vengono caricate (contenuto), guardate (engagement), e la feature killer funziona (differenziazione). È il battito cardiaco del prodotto.

### Metriche di Successo Utente

| Persona | Metrica di Successo | Indicatore Comportamentale |
|---------|--------------------|-----------------------------|
| **Streamer/Creator (Marco)** | Le clip ricevono engagement dalla community gaming | Commenti temporizzati ricevuti entro 24h; crescita follower cross-platform |
| **Gamer Casual (Luca)** | La clip raggiunge più persone di WhatsApp | Commenti da utenti non-follower (discovery); inviti ad amici |
| **Spettatore Attivo (Sara)** | I commenti vengono riconosciuti dalla community | Like sui commenti temporizzati; commenti promossi a popup nel player |
| **Archivista (Davide)** | Le clip sono organizzate e accessibili | Clip caricate e categorizzate; frequenza di download delle proprie clip |

**Time-to-First-Value per persona:**
- Marco: tempo tra primo upload → primo commento temporizzato ricevuto
- Luca: tempo tra registrazione → primo commento da un non-amico
- Sara: tempo tra primo commento scritto → primo like ricevuto
- Davide: tempo tra registrazione → prima clip scaricata

### Business Objectives

**A 3 mesi dal lancio (validazione):**
- Base utenti attiva con crescita organica (utenti che invitano amici)
- Volume di clip caricate al giorno sufficiente a popolare il feed Esplora
- Commenti temporizzati utilizzati attivamente (la feature killer funziona)
- Almeno 1 contest completato con successo (validazione della meccanica a tabellone)

**A 12 mesi (crescita):**
- Community attive per i giochi principali (Valorant, Fortnite, League of Legends, etc.)
- Contest regolari con premi reali (skin, ricariche shop in-game) finanziati da Video_clip
- Transizione verso partnership con publisher di giochi basata su numeri concreti
- Retention settimanale stabile — utenti tornano per clip, commenti e turni contest

**Modello premi contest:**
- Fase 1 (lancio): Video_clip finanzia i premi (skin, ricariche shop) come investimento di crescita — i contest funzionano come canale di acquisizione utenti più efficiente della pubblicità tradizionale
- Fase 2 (scala): Partnership con publisher di giochi che forniscono premi come canale promozionale verso la community gaming
- Zero fee per i partecipanti — la barriera di ingresso ai contest deve restare zero

### Key Performance Indicators

| KPI | Cosa Misura | Frequenza |
|-----|-------------|-----------|
| **Commenti temporizzati / giorno** | North Star — salute del prodotto | Giornaliera |
| **DAU / MAU** | Utenti attivi giornalieri e mensili | Giornaliera/Mensile |
| **Clip caricate / giorno** | Volume contenuti prodotti dalla community | Giornaliera |
| **% commenti con like > 0** | Qualità e engagement sui commenti | Settimanale |
| **Contest completion rate** | % contest che arrivano a fine tabellone con tutti i turni votati | Per contest |
| **ROI per contest** | Costo premi / nuovi utenti acquisiti tramite contest | Per contest |
| **Retention D1 / D7 / D30** | Ritorno utenti dopo registrazione | Continua |
| **Time-to-first-value** | Velocità con cui ogni persona raggiunge il momento "aha!" | Continua |
| **Inviti / utente** | Crescita organica tramite passaparola | Mensile |
| **Clip da Esplora → Follow** | Efficacia della discovery nel creare connessioni | Settimanale |
| **Tasso conversione Lurker → Attivo** | Capacità di convertire spettatori passivi | Mensile |

## MVP Scope

### Core Features (MVP — Fase 1)

#### Backend — Evoluzione necessaria

| Feature | Stato attuale | Cosa serve |
|---------|--------------|------------|
| **Like sui commenti** | Non esiste | Nuovo modello CommentLike + endpoint API |
| **Profilo pubblico/privato** | Non esiste | Campo privacy su User + logica richiesta follow (pending/accepted/rejected) stile Instagram |
| **CORS** | Non configurato | Aggiungere django-cors-headers per collegare il frontend |
| **Commenti — popup selection** | Commenti con timestamp esistono | Endpoint per ottenere il commento con più like per ogni timestamp |
| **Download clip proprie** | Non esiste endpoint dedicato | Endpoint download file video |
| **Opzione download da altri** | Non esiste | Campo booleano su Video (allow_download) impostabile all'upload |

#### Frontend — Da costruire (greenfield)

| Feature | Descrizione |
|---------|-------------|
| **Registrazione / Login** | Form registrazione, login JWT, gestione token refresh |
| **Upload clip** | Upload video con selezione tag tipo (clutch/funny/fail), titolo, opzione allow_download |
| **Player video con commenti temporizzati** | Player con popup del commento più likato per timestamp + sidebar stile chat Twitch con commenti più apprezzati |
| **Pagina dettaglio video** | Video player espanso + tutti i commenti ordinati per data + form inserimento commento con timestamp |
| **Feed Home** | Clip degli utenti seguiti, ordinate per data, con badge tipo clip |
| **Sezione Esplora** | Clip trending/random (senza personalizzazione per gioco — fase 2) |
| **Profilo utente** | Clip caricate, follower/following, impostazione pubblico/privato |
| **Follow/Unfollow** | Follow diretto se profilo pubblico, richiesta se privato (accept/reject) |
| **Rating clip** | Votazione 1-5 stelle |
| **Like commenti** | Like/unlike sui commenti temporizzati |
| **Download clip** | Download delle proprie clip sempre, clip altrui solo se abilitato dal creator |
| **Navigazione** | Bottom-bar: Home, Esplora, Upload (centrale), Profilo — 4 sezioni (Contest arriva in fase 2) |

### Out of Scope per MVP

| Feature | Fase | Motivazione |
|---------|------|-------------|
| **Contest a tabellone** | Fase 2 | Meccanica complessa (bracket, turni, voto tra partecipanti) — richiede base utenti attiva |
| **Feed personalizzato per giochi** | Fase 2 | Richiede nuovo modello dati "Game", associazione utente-giochi, algoritmo di raccomandazione |
| **Categorizzazione per gioco** | Fase 2 | Collegato al feed per giochi — nell'MVP si usano i 3 tag tipo esistenti (clutch/funny/fail) |
| **Integrazione Steam/Twitch** | Fase 2+ | OAuth + API esterne — non essenziale per validare il core |
| **Premi nei contest** | Fase 2 | Dipende dai contest a tabellone |
| **Questionario giochi all'onboarding** | Fase 2 | Collegato al feed personalizzato per giochi |
| **Notifiche push** | Fase 2+ | Nice-to-have, non essenziale per validazione |
| **App mobile nativa** | Fase 2+ | MVP come web app responsive mobile-first |
| **Processing video asincrono** | Fase 2 | Celery + Redis — necessario per scala, non per validazione |

### MVP Success Criteria

**L'MVP è un successo se:**
1. **La feature killer funziona** — gli utenti scrivono commenti temporizzati e i popup nel player vengono visualizzati. Il North Star (commenti temporizzati/giorno) cresce settimana su settimana
2. **Gli utenti tornano** — retention D7 > 0 (almeno alcuni utenti tornano dopo una settimana)
3. **Il passaparola parte** — almeno alcuni utenti invitano amici tramite condivisione link clip
4. **Il contenuto si genera** — clip caricate al giorno sufficienti a popolare il feed Esplora

**Gate per procedere a Fase 2:**
- Commenti temporizzati utilizzati attivamente (non solo commenti normali)
- Base utenti sufficiente per popolare un contest a tabellone (minimo 8-20 partecipanti)
- Feedback utenti che chiedono categorizzazione per gioco e contest

### Future Vision

#### Fase 2 — Competizione & Personalizzazione
- **Contest a tabellone** con bracket eliminazione diretta, voto peer-to-peer tra partecipanti, premi (skin/ricariche) finanziati da Video_clip
- **Categorizzazione per gioco** — nuovo modello Game, tag gioco su ogni clip
- **Feed Esplora personalizzato** — basato sui giochi nel profilo utente + trending cross-game
- **Questionario giochi all'onboarding** — setup profilo gaming
- **Processing video asincrono** — Celery + Redis per scalare
- **Sezione Contest nella navigazione** — bottom-bar diventa 5 sezioni (Home, Esplora, Upload, Contest, Profilo)

#### Fase 3 — Ecosistema & Scala
- **Integrazione Steam** — importa profilo gaming, libreria giochi, achievement
- **Integrazione Twitch** — importa clip da stream, collega canale
- **Partnership publisher** — premi forniti da Riot, Epic, EA come marketing
- **Contest personalizzati** — utenti creano i propri bracket con regole custom
- **App mobile nativa** — iOS e Android
- **Notifiche push** — nuovi commenti, turni contest, nuovi follower
- **Sistema di reputazione commentatori** — badge e livelli per gli Spettatori Attivi
