---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments:
  - _bmad-output/planning-artifacts/product-brief-Video_clip-2026-02-14.md
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/project-context.md
  - docs/index.md
  - docs/project-overview.md
  - docs/architecture.md
  - docs/data-models.md
  - docs/api-contracts.md
  - docs/development-guide.md
  - docs/source-tree-analysis.md
---

# UX Design Specification Video_clip

**Author:** AcchippameQuisso
**Date:** 2026-02-14

---

<!-- UX design content will be appended sequentially through collaborative workflow steps -->

## Executive Summary

### Project Vision

Video_clip è un social network verticale gaming-only dove la clip breve (10s-1min) è il contenuto atomico e il commento temporizzato è il DNA del prodotto. Il modello SoundCloud applicato al gaming video crea un dual-layer commenting system: commenti normali a barriera zero + commenti temporizzati che, promossi tramite like, diventano popup overlay visibili a tutti gli spettatori futuri. Il commentatore diventa co-protagonista della clip.

L'approccio è desktop-first (stile Reddit) con layout a tre colonne: sidebar navigazione sinistra, area contenuto centrale, sidebar dinamica commenti a destra. Il mobile adatta con bottom-bar e layout single-column. Due pilastri MVP: Clip Experience (upload + player + commenti temporizzati) e Contest System (bracket eliminazione diretta con albero grafico interattivo).

### Target Users

**Ordine di priorità per le decisioni di design (chi serviamo prima):**

1. **Gamer Casual (Luca, 19)** — Utente giorno-1. Carica clip occasionali dei momenti epici. Il suo aha moment è passivo: riceve commenti temporizzati da sconosciuti sulla clip che avrebbe mandato su WhatsApp. Bisogno UX: upload in 2 tap con barriera zero, condivisione link a amici, scoperta organica. Il player in ricezione (con popup e sidebar) è più importante del form commenti per questo utente. La scoperta dei commenti ricevuti deve trasmettere gratificazione emotiva — non è solo una notifica, è validazione sociale da parte di un estraneo che ha riconosciuto il suo momento.

2. **Streamer/Creator (Marco, 24)** — Pubblica highlight post-stream, cerca crescita cross-platform. Bisogno UX: upload rapido multi-clip, visibilità dei commenti ricevuti, partecipazione contest. Condivide link su Twitter per portare traffico.

3. **Spettatore Attivo (Sara, 21)** — Non carica clip ma commenta con precisione chirurgica al timestamp esatto. Bisogno UX: scrivere commenti al momento giusto, raccogliere like, vedere il proprio commento promosso a popup. Il micro-momento della pausa — quando pausa il video e il timestamp si pre-compila — è il punto di conversione critico da lurker a power user.

4. **Archivista (Davide, 22)** — Usa la piattaforma come archivio personale organizzato. Bisogno UX: upload batch, profilo privato, download clip, organizzazione per gioco.

### Key Design Challenges

Le sfide sono stratificate per release, allineate alla strategia MVP (sviluppatore singolo):

**Release A — Core Platform + Clip Experience (sfide critiche):**

1. **Player video come sistema integrato** — Il player con popup overlay, sidebar dinamica commenti e form con timestamp pre-compilato devono funzionare come un'unica esperienza fluida e intuitiva. È il cuore del prodotto.
2. **Dual-layout autenticato vs pubblico** — Due esperienze parallele: utente loggato (sidebar + feed + azioni complete) e visitatore (clip SSR + CTA registrazione). La pagina pubblica non è una versione ridotta — è il pitch visivo del prodotto.
3. **Compressione mobile del player** — Sul mobile, comprimere player + popup + sidebar + form commenti in single-column senza perdere la magia dell'esperienza.

**Release B — Contest System (sfide differibili):**

4. **Contest bracket interattivo** — Albero torneo con scontri, clip embedded, voti e risultati. Complessità UI significativa su desktop e mobile.

**Trasversali (entrambe le release):**

5. **Progressive disclosure** — Rivelare gradualmente la complessità: giorno-1 feed/upload/commenti, poi contest e features avanzate.
6. **Card-to-detail navigation** — Transizione fluida da card nel feed a pagina dettaglio con player espanso e commenti completi.

### Design Opportunities

1. **La pagina pubblica come vetrina del prodotto** — Il visitatore che arriva da un link WhatsApp vede una clip con popup temporizzati al secondo esatto del momento epico. In 3 secondi capisce cosa rende Video_clip diverso da qualsiasi altro TikTok gaming. Questa è la prima differenziazione percepita — avviene prima della registrazione.
2. **CTA contestuale empatico ("il commento che ti chiama")** — Sulla pagina pubblica, quando un popup appare, un micro-CTA contestuale si mostra vicino ad esso per utenti non loggati: "Scrivi la tua reazione a questo momento". Non un generico "Registrati" — un invito ancorato all'emozione che l'utente sta già provando. Quick win a costo tecnico quasi zero (elemento DOM condizionale su auth state), impatto potenziale alto sul conversion rate.
3. **Il micro-momento della pausa come punto di conversione** — Quando l'utente pausa il video, il timestamp si pre-compila e il form commenti appare pronto. Questo istante trasforma il lurker in power user. Progettare questa micro-interazione con cura estrema è il nudge comportamentale più importante del prodotto.
4. **Gratificazione emotiva nella scoperta dei commenti** — La notifica di un nuovo commento ricevuto non è un evento tecnico — è validazione sociale. Le micro-interazioni (animazione, evidenziazione, eventuale suono) devono trasmettere l'emozione di "qualcuno ha visto quello che hai fatto ed era incredibile". Se questo momento non emoziona, il growth loop non parte.
5. **Sidebar dinamica come "chat Twitch asincrona"** — Atmosfera community senza complessità real-time. I commenti più likati creano l'illusione di un feed vivo.
6. **Contest bracket come contenuto virale** — Un albero interattivo visivamente accattivante può diventare condivisibile di per sé su social esterni.

## Core User Experience

### Defining Experience

L'esperienza core di Video_clip è **duale**: guardare e co-creare. Ogni clip ha due protagonisti — chi l'ha caricata e chi ha scritto il commento che diventa popup. Il commento temporizzato non è una reazione al contenuto — **è contenuto**. Il popup trasforma il commento in un elemento permanente della clip, visibile a tutti gli spettatori futuri. Questa co-creazione è ciò che distingue Video_clip da qualsiasi player con commenti.

Il sistema integrato player-commenti è composto da tre elementi inscindibili:
- **Popup overlay** — Il commento con più like per ogni timestamp appare sopra il video durante la riproduzione
- **Sidebar dinamica** — I commenti più likati della clip in formato "chat Twitch asincrona"
- **Form commenti con timestamp pre-compilato** — Alla pausa del video, il timestamp corrente si pre-suggerisce automaticamente

Questo sistema è il cuore del prodotto. Ogni decisione UX che impatta il player ha priorità massima.

### Platform Strategy

- **Desktop-first (stile Reddit)**: layout a tre colonne — sidebar navigazione sinistra (collassabile), area contenuto centrale, sidebar dinamica commenti a destra
- **Mobile responsive**: bottom-bar (Home, Esplora, Upload, Profilo), layout single-column, sidebar come drawer o sezione sotto il player
- **Input primario**: mouse/keyboard su desktop, touch su mobile
- **Web app (Next.js App Router)**: nessuna app nativa per MVP, SSR per pagine pubbliche (link preview OG tags)
- **Nessun requisito offline**: connessione richiesta per tutte le funzionalità
- **Browser target**: Chrome, Firefox, Safari, Edge (ultimi 2 versioni)

### Effortless Interactions

| Interazione | Target di semplicità |
|-------------|---------------------|
| **Upload clip** | Max 3 passaggi: seleziona file → titolo + tag + allow_download → conferma. Progress bar in tempo reale |
| **Transizione play→pausa→commento** | Pausa → il player si ferma, il popup corrente resta visibile come contesto, il form commenti appare in posizione immediata con timestamp 0:XX pre-compilato. Zero ritardo percepito tra l'emozione e la possibilità di esprimerla |
| **Commentare con timestamp** | Dal form già pronto: scrivi testo → invio. Il timestamp è già lì. Un solo passaggio attivo |
| **Commentare senza timestamp** | Rimuovi il timestamp pre-suggerito con un tap → commento normale stile Instagram |
| **Navigazione feed** | Scroll di card → tap sulla card → pagina dettaglio con player. Familiare, zero curva di apprendimento |
| **Condivisione esterna** | Link diretto alla clip con preview ricca (titolo + thumbnail via OG tags SSR). Copia-incolla su qualsiasi piattaforma |
| **Follow** | Un tap per seguire da qualsiasi punto in cui appare un username |
| **Like** | Un tap su clip o commento. Feedback visivo immediato |

### Critical Success Moments

| Momento | Cosa deve succedere | Perché è critico |
|---------|--------------------|-----------------|
| **Prima visita da link esterno** | Il visitatore vede la clip con popup temporizzati funzionanti + CTA contestuale empatico. In 3 secondi capisce la differenza | È il pitch del prodotto. Se fallisce, l'utente non si registra |
| **Primo upload completato** | Clip caricata, visibile nel profilo, link pronto per la condivisione. Feedback positivo: "La tua clip è live!" | È la prima azione attiva di Luca. Se fallisce o è frustrante, non torna |
| **Primo commento temporizzato ricevuto** | Notifica con gratificazione emotiva. L'utente apre la clip e vede il commento ancorato al secondo esatto del momento chiave | È l'aha moment di Luca (utente giorno-1). Se non emoziona, il growth loop non parte |
| **Primo commento temporizzato scritto** | Pausa → timestamp appare → scrive → inviato. Naturale e senza pensarci | Se il flow è confuso, l'utente scrive commenti generici e la feature killer muore |
| **Commento promosso a popup** | Notifica speciale che comunica "il tuo commento è ora visibile a tutti nel player". Senso di realizzazione e co-creazione | Per Sara è l'equivalente del primo upload — il momento in cui diventa co-protagonista della clip. Stesso peso critico dell'upload per Luca |
| **Errore upload** | Modale chiara con errore specifico (durata, formato, connessione) + bottone "Riprova" | Un errore gestito male su un'azione primaria fa abbandonare la piattaforma |

### Experience Principles

0. **Il commento è contenuto** — Il commento temporizzato non è una reazione usa e getta — è co-creazione permanente. Il popup trasforma il commentatore in co-protagonista della clip. Questo principio fondante distingue Video_clip da qualsiasi player con commenti e guida tutti i principi successivi.
1. **Il player è il prodotto** — Ogni decisione UX che impatta il player (popup, sidebar, form commenti) ha priorità massima. In caso di trade-off tra features, il player vince sempre.
2. **Zero latenza emotiva** — Il tempo tra l'emozione provata e la possibilità di esprimerla deve essere percepito come zero. Non solo pochi click — zero ritardo. La transizione play→pausa→form commenti è l'interazione più critica del prodotto.
3. **Mostra, non spiegare** — Il visitatore capisce i commenti temporizzati vedendoli funzionare (popup nel player), non leggendo una descrizione. La pagina pubblica SSR è la demo vivente del prodotto.
4. **La gratificazione è il motore** — Ogni azione dell'utente produce un feedback emotivo proporzionato. L'upload conferma che "la tua clip è live". Il commento ricevuto dice "qualcuno ha reagito al tuo momento". Il popup promosso celebra "il tuo commento è visibile a tutti".
5. **Desktop-first, mobile-worthy** — Il layout a tre colonne desktop è il riferimento di design primario. Il mobile è un adattamento intelligente che preserva l'essenza dell'esperienza, non una versione impoverita.

## Desired Emotional Response

### Primary Emotional Goals

Le tre emozioni dominanti che Video_clip deve evocare:

1. **Riconoscimento** — "Qualcuno ha visto quello che ho fatto e ha capito perché era incredibile." Non un like generico — un commento preciso al secondo esatto che dimostra comprensione tecnica o emotiva del momento. È la differenza tra validazione superficiale e validazione autentica.

2. **Appartenenza** — "Qui la gente parla la mia lingua." L'utente non deve spiegare il contesto — la community gaming lo conosce già. Il feed, i tag, i commenti parlano il linguaggio del gamer.

3. **Co-protagonismo** — "Il mio commento è diventato parte della clip." Il popup non è solo visibilità temporanea — è permanenza. Il contributo del commentatore è ora parte dell'esperienza per tutti gli spettatori futuri.

### Emotional Journey Mapping

| Fase | Emozione target | Anti-emozione (da evitare) |
|------|----------------|---------------------------|
| **Discovery (link esterno)** | Curiosità + sorpresa — "Cos'è questo popup? Figo!" | Confusione — "Non capisco cosa sia questo sito" |
| **Registrazione** | Velocità + familiarità — "Facile come Instagram" | Frustrazione — form lungo, troppi campi |
| **Primo upload** | Orgoglio + impazienza positiva — "La mia clip è live!" | Ansia — "Ha funzionato? Dove la trovo?" |
| **Attesa commenti** | Anticipazione — "Qualcuno la guarderà?" | Abbandono — silenzio totale, zero feedback |
| **Primo commento ricevuto** | Validazione + emozione — "Uno sconosciuto ha capito la mia giocata!" | Delusione — commento generico senza timestamp |
| **Navigazione feed** | Scoperta + intrattenimento — "Cosa c'è di nuovo?" | Noia — feed vuoto o irrilevante |
| **Scrivere un commento** | Flow + espressione — "Devo commentare ADESSO questo momento" | Friction — "Dove commento? Come metto il timestamp?" |
| **Commento promosso a popup** | Orgoglio + realizzazione — "IL MIO commento è visibile a tutti!" | Indifferenza — non se ne accorge |
| **Errore/problema** | Fiducia + controllo — "Capisco, riprovo" | Impotenza — "Ho perso la clip?" |
| **Ritorno** | Appartenenza + curiosità — "Cosa è successo mentre non c'ero?" | Distacco — nessun motivo per tornare |

### Micro-Emotions

| Coppia emotiva | Da coltivare | Strategia |
|---------------|-------------|-----------|
| Fiducia vs Scetticismo | **Fiducia** | Upload con progress bar, feedback su ogni azione, errori specifici e risolvibili |
| Eccitazione vs Ansia | **Eccitazione** | Conferma immediata post-upload, link pronto, preview clip |
| Appartenenza vs Isolamento | **Appartenenza** | Feed gaming-only, commenti in gergo, tag specifici (clutch/funny/fail) |
| Realizzazione vs Frustrazione | **Realizzazione** | Notifica speciale per popup promosso, contatore like visibile |
| Delizia vs Soddisfazione | **Delizia** | Animazione popup, micro-interazioni giocose, momenti "wow" inaspettati |

### Design Implications

| Emozione target | Implicazione UX concreta |
|----------------|--------------------------|
| **Riconoscimento** | Il commento temporizzato mostra username + testo al secondo esatto → l'autore della clip vede chi lo ha riconosciuto e cosa ha detto. La notifica include il testo del commento, non solo "hai un nuovo commento" |
| **Co-protagonismo** | Notifica dedicata "Il tuo commento è ora popup!" con link diretto alla clip al timestamp. Il commentatore vede il suo contributo permanente nel player |
| **Appartenenza** | Feed filtrato, tag gaming, placeholder in gergo gaming ("Descrivi il momento..."). L'ambiente parla la lingua del gamer |
| **Curiosità (discovery)** | Pagina pubblica con popup funzionanti + CTA empatico. Il visitatore sente la differenza prima di registrarsi |
| **Flow (commento)** | Pausa → timestamp pre-compilato → form pronto → invio. Zero latenza emotiva — scrivere è naturale come pensare |
| **Fiducia (errore)** | Modale con errore specifico + "Riprova" + nessuna perdita di dati. L'errore non spaventa, si risolve |

### Emotional Design Principles

1. **La notifica è un racconto, non un evento** — "Marco ha commentato al secondo 0:18 della tua clip: 'quel flick è impossibile'" è emotivamente diverso da "Hai un nuovo commento". Ogni notifica deve raccontare cosa è successo, non solo segnalarlo.
2. **L'errore è un'opportunità di fiducia** — Un errore gestito bene ("Il video supera 1 minuto. Accorcia la clip e riprova") costruisce più fiducia di un'esperienza perfetta. L'utente sa che la piattaforma lo protegge.
3. **Il silenzio è il nemico** — Il momento più pericoloso è l'attesa dopo il primo upload senza commenti. Ogni meccanismo che riduce questo silenzio (feed Esplora, discovery organica) è un investimento emotivo.
4. **La delizia è nei dettagli** — Le micro-interazioni (animazione popup, transizione card→dettaglio, feedback like) non sono polish cosmetico — sono il tessuto emotivo del prodotto. Senza di esse, l'esperienza è funzionale ma fredda.
5. **Il gaming è gioia condivisa** — Il tono della piattaforma deve riflettere l'energia del gaming: entusiasmante, competitivo, divertente. Mai formale, mai aziendale, mai noioso.

## UX Pattern Analysis & Inspiration

### Inspiring Products Analysis

#### TikTok — Mobile UX Reference
- Scroll verticale infinito, transizioni fluide, UI minimale che scompare durante la riproduzione, doppio tap per like con animazione cuore, contenuti prima della registrazione
- **Trasferibile**: Fluidità scroll, "contenuto prima di tutto", animazioni di feedback soddisfacenti
- **Non copiare**: Scroll full-screen (il valore di Video_clip è nella pagina dettaglio con commenti, non nel consumo rapido)

#### Instagram — Desktop Design + Social Model
- Layout pulito con spazio bianco, tipografia chiara, transizioni smooth, dark mode elegante, iconografia riconoscibile
- **Trasferibile**: Estetica pulita e moderna desktop, modello follow/feed, bottom-bar mobile, like con feedback immediato, tono "premium ma accessibile"
- **Non copiare**: Commenti piatti senza timestamp né gerarchia di qualità

#### Reddit — Desktop Layout + Commenti
- Layout a colonne con sidebar, commenti gerarchici con upvote che fanno emergere i migliori, card-to-detail navigation, design system coerente
- **Trasferibile**: Layout tre colonne, card→dettaglio, gerarchia commenti per voti (il commento più votato emerge = popup di Video_clip), sidebar informativa
- **Non copiare**: Densità di testo e complessità visiva (Video_clip è video-first)

#### Twitch — Sidebar Chat + Community
- Chat laterale in tempo reale, emote come linguaggio, badge utente, tono gaming-native
- **Trasferibile**: Sidebar dinamica = chat Twitch asincrona (stessa posizione, stessa sensazione di community live, basata su like anziché real-time)
- **Non copiare**: Complessità sistema emote/badge (non per MVP)

#### SoundCloud — DNA Commenti Temporizzati
- Commenti ancorati alla waveform, visualizzazione commenti sulla timeline, sensazione di co-ascolto
- **Trasferibile**: Modello "commento = posizione nel tempo", indicatori visivi sulla timeline del player (dot che segnalano dove ci sono commenti), hover preview
- **Non copiare**: La waveform (non ha senso su video), ma i marker sulla progress bar con hover preview sì

### Transferable UX Patterns

**Navigazione:**

| Pattern | Origine | Uso in Video_clip |
|---------|---------|-------------------|
| Bottom-bar 4 tab (mobile) | Instagram/TikTok | Home, Esplora, Upload (centrale), Profilo |
| Sidebar sinistra collassabile (desktop) | Reddit/Discord | Navigazione principale desktop |
| Sidebar destra contestuale (desktop) | Twitch/Reddit | Sidebar dinamica commenti nella pagina dettaglio |
| Card-to-detail | Reddit/Instagram | Feed → pagina dettaglio clip |
| Pull-to-refresh | Instagram/TikTok | Aggiornamento feed mobile |

**Interazione:**

| Pattern | Origine | Uso in Video_clip |
|---------|---------|-------------------|
| Doppio tap per like | Instagram/TikTok | Like rapido su clip |
| Comment markers sulla timeline + hover preview | SoundCloud (evoluzione) | Dot luminosi (gradiente) sulla barra progresso video dove ci sono commenti. Hover su un dot mostra micro-preview del commento top per quel timestamp. Pattern unico nel video gaming — discovery visiva dei commenti sulla timeline |
| Commenti ordinati per "migliore" | Reddit | Vista "Nel video" — commenti temporizzati per like |
| Skeleton loading | Instagram/Reddit | Placeholder animati durante caricamento |
| Toast notification | App moderne | Feedback non intrusivo (like, follow, commento inviato) |

**Visual — Design accattivante e alla moda:**

| Pattern | Ispirazione | Applicazione |
|---------|-------------|-------------|
| Dark mode come default | TikTok/Twitch/Discord | Il gaming vive nel dark mode. Sfondi scuri, accent vibranti, video che risalta |
| Glassmorphism sui popup overlay | Apple/trend 2025-2026 | Popup commento con sfondo frosted glass semi-trasparente — moderno, leggibile, non ostruisce il video |
| Micro-animazioni a 3 tier | TikTok/Instagram | **Tier 1 (significato)**: popup che appare/scompare, feedback like, toast commento inviato. **Tier 2 (transizione)**: card→dettaglio, apertura sidebar, navigazione pagine. **Tier 3 (delizia)**: hover card, bounce bottoni, shimmer skeleton |
| Spinner unico del sito | Branding custom | Animazione dove il logo/icona play si "costruisce" dal gradiente, particella dopo particella. 1-2 secondi, ipnotico, memorabile — ispirato ai loading screen dei giochi (Valorant, Fortnite) |
| Visual DNA con gradiente ricorrente | Branding custom | Il gradiente gaming-inspired (viola→ciano o rosso→arancione) È l'identità visiva: barra progresso video, bordi card trending, spinner, bordo popup overlay, elementi interattivi. Come la linea rossa di YouTube — ma è un gradiente, ed è di Video_clip |
| Tipografia bold | Reddit new/TikTok | Font sans-serif moderno (Inter, Geist, Satoshi), titoli bold, corpo leggero |

### Anti-Patterns to Avoid

| Anti-pattern | Perché evitarlo |
|-------------|-----------------|
| Popup invasivi "Registrati!" | Distrugge la prima impressione. CTA empatico contestuale, mai modale bloccante |
| Autoplay con audio | Frustrante. Video autoplay solo muted, click per attivare audio |
| Infinite scroll senza orientamento | Header sticky con contesto per non perdere l'utente |
| Commenti flat senza gerarchia | I migliori devono emergere. Senza ordinamento per like, è rumore |
| Loading spinner generico | Sito gaming con spinner Bootstrap = occasione persa. Lo spinner è branding |
| Notifiche generiche | "Hai una notifica" non dice nulla. Ogni notifica racconta cosa è successo |
| Form upload multi-step | Ogni step è un punto di abbandono. Massimo una schermata |
| Animazioni senza significato | Animazioni puramente decorative diventano rumore visivo. Ogni animazione segue la gerarchia a 3 tier |

### Design Inspiration Strategy

**Adottare:**
- Dark mode come esperienza primaria — il video gaming brilla su sfondo scuro
- Layout tre colonne desktop (Reddit) + bottom-bar mobile (Instagram)
- Gerarchia commenti per like (Reddit) applicata ai commenti temporizzati
- Sidebar dinamica posizionata come chat Twitch
- Card-to-detail come pattern di navigazione principale
- Visual DNA con gradiente ricorrente come identità del brand

**Adattare:**
- Comment markers di SoundCloud evoluti per video: dot luminosi (gradiente) sulla timeline con hover preview del commento top — pattern unico nel gaming video
- Glassmorphism di Apple/iOS adattato ai popup overlay — semi-trasparente, moderno, non ostruisce il video
- Doppio tap di Instagram/TikTok adattato al contesto desktop (click) e mobile (tap)
- Skeleton loading di Instagram adattato alle card clip (thumbnail placeholder animato)
- Micro-animazioni di TikTok organizzate in gerarchia 3 tier (significato → transizione → delizia)

**Creare ex-novo:**
- Spinner unico che si costruisce dal gradiente — elemento di branding memorabile ispirato ai loading screen gaming
- Comment markers con hover preview sulla timeline — discovery visiva dei commenti, pattern mai visto su video player
- CTA contestuale empatico sulla pagina pubblica — pattern originale di Video_clip
- Il gradiente come tratto grafico ricorrente dalla timeline ai bordi, dallo spinner al popup

**Evitare:**
- Qualsiasi elemento che interrompa la fruizione del video (modale, overlay bloccanti)
- Design generico/template — ogni elemento deve comunicare "gaming" e "community"
- Complessità visiva alla Reddit (troppo testo, troppe opzioni) — Video_clip è video-first
- Animazioni decorative senza motivo funzionale — ogni animazione ha un tier e un perché
- Lo spinner come scusa per tempi di caricamento lenti — lo spinner è ciliegina, non torta

## Design System Foundation

### Design System Choice

**Stack selezionato:** Tailwind CSS v4 + shadcn/ui (Radix UI Primitives) + Framer Motion + Lucide React Icons

| Componente | Ruolo | Perché |
|-----------|-------|--------|
| **Tailwind CSS v4** | Utility-first CSS, design tokens | Velocità di sviluppo, CSS variables native, zero runtime, dark mode triviale |
| **shadcn/ui** | Componenti UI base (copy-paste, non dependency) | "Own your components" — zero lock-in, personalizzazione totale, accessibilità Radix UI integrata |
| **Framer Motion** | Animazioni orchestrate (Tier 1 + Tier 2) | API dichiarativa React, layout animations, AnimatePresence per mount/unmount |
| **Lucide React** | Iconografia | Tree-shakeable, leggero, coverage eccellente, coerente con shadcn/ui |

### Rationale for Selection

1. **Zero dependency lock-in** — shadcn/ui copia i componenti nel progetto. Li possiedi, li modifichi, non dipendi da release esterne. Per un progetto con visual identity forte (gradiente, glassmorphism, spinner custom) questo è critico.
2. **Accessibilità di serie** — Radix UI Primitives sotto il cofano garantisce focus management, keyboard navigation, ARIA attributes su ogni componente. Fondamentale per un social network con interazioni intense.
3. **Perfetto per solo developer** — Tre layer chiari: Tailwind è il sistema di design, shadcn/ui è l'acceleratore, i custom components sono il differenziatore. Minimo overhead, massima flessibilità.
4. **Next.js App Router compatibile** — Tailwind è zero-runtime (SSR nativo). Framer Motion richiede `"use client"` ma è isolabile in wrapper minimali. shadcn/ui funziona in entrambi i contesti.
5. **Community e maturità** — Tailwind (v4 stabile), Radix UI (usato da Vercel, Linear), Framer Motion (standard de facto per animazioni React).

### Implementation Approach

**Design Tokens (CSS Variables):**
```
--gradient-start / --gradient-end     → Visual DNA gradiente ricorrente
--background / --foreground           → Dark mode palette
--card / --card-foreground            → Superfici card
--accent / --accent-foreground        → Elementi interattivi
--popup-glass                         → Glassmorphism popup overlay
--ring                                → Focus ring accessibilità
```

**Struttura componenti:**
```
components/
  ui/          ← shadcn/ui (installati + personalizzati con tema Video_clip)
  custom/      ← componenti Video_clip (player, spinner, comment-markers, bracket-tree)
```

Entrambi usano Tailwind + CSS variables + utility `cn()` per classi condizionali. I custom seguono le stesse convenzioni di shadcn/ui per coerenza codebase.

**Componenti shadcn/ui per Release A:**
Button, Card, Dialog, DropdownMenu, Input, Textarea, Tabs, Toast, Avatar, Badge, Skeleton, ScrollArea, Tooltip, Separator

**Componenti custom da costruire:**
- `VideoPlayer` — Player con popup overlay, progress bar con comment markers, controlli
- `CommentSidebar` — Sidebar dinamica "chat Twitch asincrona"
- `CommentForm` — Form con timestamp pre-compilato alla pausa
- `GradientSpinner` — Spinner unico che si costruisce dal gradiente
- `ClipCard` — Card feed con thumbnail, info, hover animation

### Customization Strategy

**Regola Framer Motion (disciplina bundle):**
- **Tier 1 (significato)** + **Tier 2 (transizione)** → Framer Motion consentito (popup appear/disappear, card→detail, page transitions)
- **Tier 3 (delizia)** → CSS transitions/animations native con Tailwind (`transition-all duration-200 ease-out`) — peso zero
- Componenti Framer Motion sempre con `dynamic()` + `ssr: false` dove appropriato per proteggere il Time to Interactive

**Tema Video_clip su shadcn/ui:**
- Dark mode come default (`class` strategy in Tailwind)
- Gradiente gaming-inspired come accent primario applicato via CSS variables
- Glassmorphism (`backdrop-blur + bg-opacity`) sui popup overlay
- Font sans-serif moderno (Inter/Geist) — titoli bold, corpo leggero
