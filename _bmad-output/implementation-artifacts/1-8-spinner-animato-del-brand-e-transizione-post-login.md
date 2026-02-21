# Story 1.8: Spinner Animato del Brand e Transizione Post-Login

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utente,
I want vedere uno spinner animato unico del brand durante i caricamenti e un'animazione fluida dopo il login,
so that l'esperienza sia coerente con l'identita visiva della piattaforma e il passaggio tra stati sia piacevole e cinematografico.

## Acceptance Criteria

1. **AC1 — Spinner animato del brand a schermo intero (stato authenticating)**
   Given: un utente che accede al sito con un refresh token valido
   When: il sistema e nello stato "authenticating" (refresh token in corso)
   Then: viene mostrato lo spinner animato del brand a schermo intero:
   - Logo/titolo "Video_clip" come elemento centrale con testo gradient animato (shimmer)
   - Animazione con il gradiente DNA del brand (viola→ciano) — pulsazione fluida, NON un semplice anello rotante
   - Il `GradientSpinner` esistente ruota sotto il logo come indicatore di caricamento
   - Sfondo scuro coerente con il dark mode (`bg-background`)

2. **AC2 — Transizione cinematografica post-login**
   Given: un utente che completa il login con successo (form login)
   When: l'autenticazione e confermata
   Then: viene mostrata una transizione animata orchestrata:
   - **Fase 1 (dissolve form):** Il form di login si dissolve con fade-out + blur (0.4s)
   - **Fase 2 (logo al centro):** Il logo/titolo "Video_clip" appare al centro dello schermo, leggermente ingrandito, su sfondo completamente nero
   - **Fase 3 (caricamento):** Il GradientSpinner appare sotto il logo, indicando che l'app sta caricando
   - **Fase 4 (logo si dissolve verso l'angolo):** Quando tutto e pronto, il logo si riduce (`scale: 0.5`), si muove verso alto-sinistra (`x: -30vw, y: -30vh`) e si dissolve (`opacity: 0`) — il logo NON arriva alla destinazione esatta nella sidebar, si dissolve al ~70% del percorso per evitare discontinuita pixel con il logo reale nella sidebar (insight Party Mode: niente `layoutId` cross-route)
   - **Fase 5 (reveal):** Lo sfondo dell'overlay fa fade-out (`opacity: 0`) rivelando l'interfaccia completa della Home (gia montata sotto l'overlay grazie a `router.replace("/home")` chiamato durante la Fase 3)
   - Durata totale transizione: 800ms-1200ms (percepibile ma non lenta)
   - L'animazione usa Framer Motion (Tier 1)

3. **AC3 — Variante `full` e `inline` del GradientSpinner**
   Given: lo spinner del brand usato come loader generico
   When: viene utilizzato in contesti diversi (caricamento pagina, caricamento feed)
   Then: il componente `GradientSpinner` accetta una prop `variant`:
   - `full` — a schermo intero (stato authenticating, primo caricamento): logo + spinner + sfondo pieno
   - `inline` — dimensione ridotta per loading inline (dentro card, sezioni): solo l'anello rotante come attualmente

4. **AC4 — Durata minima animazione (anti-flash)**
   Given: un utente con connessione veloce
   When: il login o il refresh avviene in < 300ms
   Then: l'animazione di transizione viene comunque mostrata per un minimo di 500ms per evitare flash visivi

5. **AC5 — Transizione post-refresh (auto-login)**
   Given: un utente che accede al sito con refresh token valido
   When: il refresh token viene rinnovato con successo e l'utente e autenticato
   Then: lo spinner full-screen si dissolve con una transizione fluida verso il contenuto (senza la sequenza completa del login form, solo fase 4-5)

## Tasks / Subtasks

> **NOTA:** Questa story e interamente frontend. Zero modifiche backend. Richiede padronanza di Framer Motion e attenzione maniacale ai timing delle animazioni.

### Codice esistente (gia implementato)

- [x] `GradientSpinner` in `frontend/src/components/shared/gradient-spinner.tsx` — spinner CSS-only con conic-gradient e `animate-spin-gradient` (1.5s). Props: `size`, `className`. Da evolvere con prop `variant`
- [x] `PageLoader` in `frontend/src/components/shared/page-loader.tsx` — wrapper che mostra `GradientSpinner size={48}` centrato. Usato nel main layout durante `isAuthenticating`
- [x] `AuthProvider` in `frontend/src/providers/auth-provider.tsx` — espone `user`, `isAuthenticated`, `isAuthenticating`, `login()`, `logout()`. Lo stato `isAuthenticating` e `true` durante il mount iniziale e diventa `false` dopo il check sessione
- [x] Login page `frontend/src/app/(auth)/login/page.tsx` — form con username/password, chiama `login()` poi `router.replace("/home")`. Ha loading state locale per lo spinner nel bottone
- [x] Auth layout `frontend/src/app/(auth)/layout.tsx` — layout centrato con titolo "Video_clip" gradient e tagline
- [x] Main layout `frontend/src/app/(main)/layout.tsx` — guard: se `isAuthenticating` mostra `<PageLoader />`, se `!isAuthenticated` return null (middleware redirect)
- [x] Root layout `frontend/src/app/layout.tsx` — Provider hierarchy: QueryProvider > AuthProvider > TooltipProvider > Toaster
- [x] Landing page `frontend/src/app/page.tsx` — mostra GradientSpinner e redirecta a `/home` o `/login` quando `isAuthenticating` diventa false
- [x] `globals.css` con design tokens: `--gradient-start: #7c3aed`, `--gradient-end: #06b6d4`, keyframes `spin-gradient`, `shimmer`, classi `.gradient-text`, `.glass`
- [x] `framer-motion@^12.34.0` installato, pattern gia usato in `popup-overlay.tsx` con `AnimatePresence` + `motion.div`
- [x] Middleware `frontend/src/middleware.ts` — check cookie `session_active` per route protection server-side

### Gap identificati (lavoro da completare)

- [x] Task 1: Evolvere `GradientSpinner` con prop `variant` (AC: #3)
  - [x] 1.1 — Modificare `frontend/src/components/shared/gradient-spinner.tsx`: aggiungere prop `variant?: "full" | "inline"` (default `"inline"` per backward-compatibility)
  - [x] 1.2 — Quando `variant="inline"`: renderizzare SOLO l'anello rotante come attualmente (nessun cambiamento di comportamento)
  - [x] 1.3 — Quando `variant="full"`: renderizzare un layout a schermo intero con:
    - Container `fixed inset-0 z-50 flex flex-col items-center justify-center bg-background`
    - Logo "Video_clip" come `<motion.h1>` con classe `gradient-text` e animazione pulsazione (`scale: [1, 1.05, 1]`, `duration: 1.5s`, `repeat: Infinity`)
    - Anello spinner sotto il logo (il componente esistente, size configurabile)
    - Import da `"framer-motion"` (pacchetto installato; `motion/react` non disponibile senza pacchetto `motion` separato)
  - [x] 1.4 — Aggiungere prop `onAnimationReady?: () => void` — callback opzionale invocato quando lo spinner e montato e animato (per orchestrazione esterna)

- [x] Task 2: Creare `LoginTransitionOverlay` (AC: #2, #4)
  - [x] 2.1 — Creare `frontend/src/components/shared/login-transition-overlay.tsx` come Client Component (`"use client"`)
  - [x] 2.2 — Props interface:
    ```typescript
    interface LoginTransitionOverlayProps {
      isActive: boolean;       // true quando la transizione e in corso
      onTransitionEnd: () => void; // callback quando la transizione e completata e si puo navigare
    }
    ```
  - [x] 2.3 — Struttura overlay: `<AnimatePresence>` wrappa un `<motion.div>` `fixed inset-0 z-50` con sfondo `bg-background` (nero/scuro)
  - [x] 2.4 — Contenuto overlay: logo "Video_clip" centrato con `<motion.h1 className="gradient-text">` + `GradientSpinner` sotto
  - [x] 2.5 — Sequenza animazione con `useAnimate` (Framer Motion timeline API):
    - **Fase 2** (0ms): Logo appare al centro con `scale: [0.9, 1.1]` e `opacity: [0, 1]` (0.4s ease-out)
    - **Fase 3** (400ms): Spinner appare sotto il logo con `opacity: [0, 1]` (0.3s)
    - **Fase 4** (attende `minDisplayTime` di 500ms totali dall'attivazione): Logo si riduce (`scale: 0.5`), si muove verso alto-sinistra (`x: "-30vw", y: "-30vh"`) e si dissolve (`opacity: 0`) simultaneamente (0.5s ease-in-out). Il logo NON arriva alla destinazione esatta — si dissolve al ~70% del percorso. Niente `layoutId`, niente calcoli pixel.
    - **Fase 5** (dopo dissolve logo): Overlay intero fa fade-out con `opacity: 0` (0.3s), poi chiama `onTransitionEnd`
  - [x] 2.6 — Implementare `minDisplayTime`: se l'overlay e attivo da meno di 500ms, attendere il tempo restante prima di procedere alla Fase 4 (AC4)
  - [x] 2.7 — Export: `export function LoginTransitionOverlay()` (named export)

- [x] Task 3: Integrare la transizione nella pagina Login (AC: #2, #4)
  - [x] 3.1 — Modificare `frontend/src/app/(auth)/login/page.tsx`:
    - Aggiungere state `showTransition: boolean` (default false)
    - Aggiungere state `isLoggingIn: boolean` per tracciare il login in corso
    - Wrappare l'intero contenuto della pagina in `<AnimatePresence mode="wait">`
    - Il form di login diventa un `<motion.div>` con animazione di exit: `opacity: 0`, `scale: 0.95`, `filter: "blur(8px)"`, `transition: { duration: 0.4 }`
  - [x] 3.2 — Flow login modificato:
    1. Utente clicca "Accedi" → `setIsLoggingIn(true)`, spinner nel bottone
    2. `await login(username, password)` completa con successo
    3. `setShowTransition(true)` → triggera exit animation del form
    4. `LoginTransitionOverlay` appare con `isActive={showTransition}`
    5. L'overlay chiama `router.replace("/home")` DURANTE la Fase 3 (mentre il logo e lo spinner sono visibili) — cosi il main layout inizia a montarsi sotto l'overlay
    6. Quando `onTransitionEnd` viene chiamato, l'overlay si smonta — la Home e gia visibile sotto
    **NOTA CRITICA (Party Mode insight):** dopo `login()`, lo stato `isAuthenticating` resta `false` nel `AuthProvider`, quindi il main layout NON mostra `PageLoader`. I due overlay (`LoginTransitionOverlay` e `PageLoader`) non coesistono MAI. Nessun flag sessionStorage necessario.
  - [x] 3.3 — Gestione errori: se `login()` fallisce, il form resta visibile con messaggio di errore (nessuna transizione)
  - [x] 3.4 — Importare `motion` da `"framer-motion"`, `LoginTransitionOverlay` dal componente creato

- [x] Task 4: Evolvere `PageLoader` per usare `GradientSpinner variant="full"` (AC: #1, #5)
  - [x] 4.1 — Modificare `frontend/src/components/shared/page-loader.tsx`:
    - Sostituire il layout manuale con `<GradientSpinner variant="full" size={32} />`
    - Il PageLoader diventa un thin wrapper che passa `variant="full"` al GradientSpinner
  - [x] 4.2 — Il main layout (`frontend/src/app/(main)/layout.tsx`) continua a usare `<PageLoader />` durante `isAuthenticating` — nessuna modifica al layout necessaria
  - [x] 4.3 — Il root landing page (`frontend/src/app/page.tsx`) puo opzionalmente usare `<GradientSpinner variant="full" />` al posto del semplice spinner centrato

- [x] Task 5: Gestire transizione fluida post-refresh (AC: #5, #4)
  - [x] 5.1 — La landing page (`frontend/src/app/page.tsx`) gia mostra GradientSpinner durante `isAuthenticating`. Con `variant="full"` (Task 4.3) mostra il brand loader
  - [x] 5.2 — Quando `isAuthenticating` diventa `false` e `isAuthenticated` e `true`:
    - La pagina fa `router.replace("/home")`
    - Il `GradientSpinner variant="full"` era gia visibile
    - Il main layout monta e mostra il contenuto — la transizione e gia coperta dal cambio pagina
  - [x] 5.3 — **Assicurare minimum display time (500ms)**: nella landing page, quando `isAuthenticating` diventa `false`, attendere che siano passati almeno 500ms dal mount prima di navigare. Pattern:
    ```typescript
    const mountTime = useRef(Date.now());
    useEffect(() => {
      if (!isAuthenticating) {
        const elapsed = Date.now() - mountTime.current;
        const remaining = Math.max(0, 500 - elapsed);
        const timer = setTimeout(() => {
          router.replace(isAuthenticated ? "/home" : "/login");
        }, remaining);
        return () => clearTimeout(timer);
      }
    }, [isAuthenticating, isAuthenticated]);
    ```

- [x] Task 6: Verifica finale (AC: #1, #2, #3, #4, #5)
  - [x] 6.1 — Eseguire `npm run build` da `frontend/` — TypeScript strict, 0 errori ✅ Build passato
  - [ ] 6.2 — Verificare visivamente: login → form dissolve → logo al centro → spinner → logo si muove → interfaccia appare (richiede test manuale utente)
  - [ ] 6.3 — Verificare visivamente: refresh con token valido → brand loader fullscreen → dissolve a home (con minimum 500ms) (richiede test manuale utente)
  - [x] 6.4 — Verificare: `GradientSpinner variant="inline"` funziona come prima (backward-compatible) ✅ Default "inline", SpinnerRing invariato
  - [ ] 6.5 — Verificare: login veloce (< 300ms) mostra comunque animazione per almeno 500ms (richiede test manuale utente)
  - [ ] 6.6 — Verificare: animazioni rispettano timing 800ms-1200ms totale transizione post-login (richiede test manuale utente)

## Dev Notes

### Analisi architetturale — flusso di autenticazione attuale

Il sistema di autenticazione ha **tre punti di ingresso** con loading state:

| Punto | File | Stato attuale | Da modificare |
|-------|------|---------------|---------------|
| **Landing page** (`/`) | `app/page.tsx` | Mostra `GradientSpinner size={48}` nudo, poi redirecta | Usare `variant="full"` + minimum display time 500ms |
| **Login success** | `app/(auth)/login/page.tsx` | Spinner nel bottone, poi `router.replace("/home")` istantaneo | Aggiungere `LoginTransitionOverlay` con transizione cinematografica |
| **Main layout guard** | `app/(main)/layout.tsx` | Mostra `<PageLoader />` durante `isAuthenticating` | `PageLoader` usa automaticamente `GradientSpinner variant="full"` |

### Librerie e dipendenze

**Framer Motion 12.34.0 — GIA INSTALLATO, SUFFICIENTE.**
- Nessuna libreria aggiuntiva necessaria
- NO Lottie, NO GSAP, NO Rive — tutto e fattibile con Framer Motion
- Import path raccomandato: `import { motion, AnimatePresence, useAnimate } from "motion/react"`
- Il vecchio import `from "framer-motion"` continua a funzionare ma e deprecato

**API Framer Motion da usare:**

| API | Uso in questa story |
|-----|---------------------|
| `AnimatePresence` | Exit animation del form login (dissolve) |
| `motion.div` / `motion.h1` | Elementi animati (logo, overlay, form) |
| `useAnimate` | Timeline orchestrata della transizione post-login (sequenza multi-step) |
| `animate` prop con keyframes | Pulsazione logo (`scale: [1, 1.05, 1]`) |
| `exit` prop | Animazione di uscita del form (`opacity: 0, blur, scale`) |

### Pattern di animazione — Sequenza post-login dettagliata

```
Timeline post-login (totale ~1200ms):

t=0ms      LoginTransitionOverlay monta con bg-background fixed
           Form login inizia exit animation (opacity→0, scale→0.95, blur→8px)
t=400ms    Form completamente dissolto
           Logo "Video_clip" appare al centro (scale 0.9→1.1, opacity 0→1)
t=700ms    GradientSpinner appare sotto il logo (fade in)
           router.replace("/home") chiamato ORA — main layout inizia a montarsi SOTTO l'overlay
t=500ms*   Minimum display time raggiunto (* contato dall'attivazione overlay)
           Logo inizia a dissolversi verso alto-sinistra: scale→0.5, x→-30vw, y→-30vh, opacity→0
t=1000ms   Logo completamente dissolto (~70% del percorso)
           Overlay bg fa fade-out (opacity→0) — rivela la Home gia montata sotto
t=1200ms   Overlay unmount, transizione completa
```

*Nota: la Fase 4 (logo dissolve) NON parte prima che siano trascorsi 500ms dall'attivazione dell'overlay (AC4). Il `router.replace` avviene DURANTE la transizione (Fase 3), non alla fine. Dopo `login()`, `isAuthenticating` e `false` nel AuthProvider → il main layout NON mostra PageLoader → nessun doppio overlay.*

### Calcolo posizione target del logo (Party Mode insight)

Il logo NON deve arrivare alla posizione esatta della sidebar. Si dissolve al ~70% del percorso. L'approccio:

```typescript
// useAnimate, Fase 4:
[".brand-logo", { scale: 0.5, x: "-30vw", y: "-30vh", opacity: 0 },
 { duration: 0.5, ease: "easeInOut" }]
```

- **Valori `vw/vh` relativi** — zero calcoli pixel, zero `getBoundingClientRect()`
- **Niente `layoutId`** — non funziona cross-route con Next.js App Router (layout `(auth)` e `(main)` sono alberi React diversi)
- **Dissolve prima della destinazione** — l'effetto visivo e "il logo vola verso l'angolo e svanisce". Piu elegante e robusto di un arrivo pixel-perfect
- **Se la posizione del logo nella sidebar cambia in futuro, l'animazione non si rompe**

### Nessun doppio overlay (Party Mode insight)

Un potenziale rischio era la coesistenza di `LoginTransitionOverlay` (z-50) e `PageLoader` (usato nel main layout durante `isAuthenticating`). Analisi:

- Dopo `login()`, lo stato `isAuthenticating` nel `AuthProvider` resta `false` (non c'e un refresh in corso)
- Il guard nel main layout `if (isAuthenticating) return <PageLoader />` NON triggera
- I due overlay sono **mutuamente esclusivi per design**: `LoginTransitionOverlay` appare solo dopo login form, `PageLoader` appare solo durante auto-refresh
- **Nessun flag `sessionStorage` necessario** — complessita eliminata

### GradientSpinner `variant="full"` — design del loader

Il layout del brand loader fullscreen:
```
┌──────────────────────────────────────────┐
│                                          │
│                                          │
│                                          │
│            V i d e o _ c l i p           │  ← gradient-text con animazione shimmer/pulse
│                                          │
│                 ◌                         │  ← GradientSpinner (anello rotante gradient)
│                                          │
│                                          │
│                                          │
└──────────────────────────────────────────┘
   bg-background (sfondo scuro coerente dark mode)
```

### Componenti da RIUTILIZZARE (NON ricreare)

| Componente | File | Riuso |
|-----------|------|-------|
| `GradientSpinner` | `components/shared/gradient-spinner.tsx` | **EVOLVERE** — aggiungere `variant` prop, mantenere backward-compatibility |
| `PageLoader` | `components/shared/page-loader.tsx` | **SEMPLIFICARE** — usare `GradientSpinner variant="full"` |
| `.gradient-text` | `globals.css` | Classe CSS per testo con gradiente (gia definita) |
| `useAuth()` | `providers/auth-provider.tsx` | Per `isAuthenticating`, `isAuthenticated`, `login()` |
| `AnimatePresence` | `motion/react` (framer-motion) | Per exit animations |
| `motion.*` | `motion/react` (framer-motion) | Per tutti gli elementi animati |
| `useAnimate` | `motion/react` (framer-motion) | Per timeline orchestrata |

### Lezioni dalla Story 1-7 (da applicare)

- **Named exports**: tutti i componenti usano `export function ComponentName()`, MAI default export (tranne pagine Next.js)
- **File naming**: kebab-case per tutti i file (`login-transition-overlay.tsx`)
- **Dark mode**: usare Tailwind semantic tokens (`bg-background`, `text-foreground`). Lo sfondo dell'overlay DEVE essere `bg-background` per coerenza dark mode, NON un nero hardcodato
- **Import Framer Motion**: usare `import { motion, AnimatePresence } from "motion/react"` — nuovo import path raccomandato per FM 12.x
- **Lingua**: messaggi utente/alt text in italiano, codice in inglese
- **a11y**: `aria-label` sugli elementi animati, rispettare `prefers-reduced-motion` (vedi vincolo critico #8)

### Git intelligence

Ultimi commit rilevanti:
- `6456640` — Story 1-4/1-5/1-6 con code review fix
- `d6b0b79` — Story 1-2 registrazione + Story 1-3 login JWT + code review fix

Pattern stabiliti nei commit precedenti:
- Client Component con `"use client"` per tutto cio che usa hooks/interattivita
- Componenti layout in `components/layout/`, componenti condivisi in `components/shared/`
- Pattern Framer Motion: `AnimatePresence` + `motion.div` con `initial/animate/exit` (vedi `popup-overlay.tsx`)

### Project Structure Notes

| File | Ruolo | Azione |
|------|-------|--------|
| `frontend/src/components/shared/gradient-spinner.tsx` | Spinner gradient del brand | **MODIFICARE** — aggiungere `variant` prop (`full`/`inline`), layout fullscreen con logo animato |
| `frontend/src/components/shared/login-transition-overlay.tsx` | Overlay transizione cinematografica post-login | **CREARE** — `AnimatePresence` + `useAnimate` per sequenza multi-step |
| `frontend/src/components/shared/page-loader.tsx` | Loader pagina intero | **MODIFICARE** — usare `GradientSpinner variant="full"` |
| `frontend/src/app/(auth)/login/page.tsx` | Pagina login | **MODIFICARE** — aggiungere exit animation form + integrazione `LoginTransitionOverlay` |
| `frontend/src/app/page.tsx` | Landing page (redirect) | **MODIFICARE** — usare `GradientSpinner variant="full"` + minimum display time 500ms |

**File NON da toccare:**
- `frontend/src/providers/auth-provider.tsx` — il `isAuthenticating` state e gia perfetto cosi com'e
- `frontend/src/app/(main)/layout.tsx` — il guard `isAuthenticating → PageLoader` funziona gia correttamente
- `frontend/src/app/layout.tsx` — root layout invariato
- `frontend/src/middleware.ts` — middleware invariato
- `frontend/src/app/globals.css` — i design tokens e keyframes esistenti sono sufficienti (nessun nuovo keyframe necessario, Framer Motion gestisce tutto)
- `backend/` — Zero modifiche backend

### Stack tecnologico rilevante

- **Frontend:** Next.js 16.1.6, React 19, TypeScript 5
- **Animazioni:** Framer Motion 12.34.0 (import da `"motion/react"`)
- **UI:** TailwindCSS 4 (design tokens, dark mode), classi CSS `.gradient-text`, `.gradient-bg`
- **State:** `useAuth()` context per `isAuthenticating` e `login()`
- **Routing:** Next.js App Router, `router.replace("/home")` per navigazione post-login

### Vincoli critici per lo sviluppatore

1. **NESSUNA LIBRERIA AGGIUNTIVA:** Framer Motion 12.34.0 e gia installato e sufficiente per tutto. NON installare Lottie, GSAP, anime.js o altre librerie di animazione
2. **IMPORT PATH:** Usare `import { ... } from "motion/react"` per tutti i nuovi file. L'import `"framer-motion"` funziona ma e il path legacy
3. **BACKWARD COMPATIBILITY GradientSpinner:** Il default di `variant` DEVE essere `"inline"` per non rompere tutti gli usi esistenti del componente (landing page, login button, page-loader, ecc.)
4. **BG-BACKGROUND, NON NERO HARDCODATO:** L'overlay DEVE usare `bg-background` (che e near-black nel dark mode), NON `bg-black` o `#000`. Cosi rispetta il tema e funziona anche se il light mode venisse attivato in futuro
5. **MINIMUM DISPLAY TIME 500ms:** Sia la transizione post-login che il brand loader del refresh DEVONO rimanere visibili per almeno 500ms, anche se il login/refresh avviene in millisecondi. Questo previene flash visivi sgradevoli (AC4)
6. **TIMING TOTALE 800-1200ms:** La transizione completa post-login (da form dissolve a interfaccia visibile) deve durare tra 800ms e 1200ms. Non troppo veloce (percepisce un glitch), non troppo lenta (frustra l'utente)
7. **Z-INDEX OVERLAY:** L'overlay di transizione DEVE avere `z-50` (stesso livello degli overlay principali). NON usare z-index superiori a 50 per non conflittare con il sistema di layering dell'app
8. **PREFERS-REDUCED-MOTION:** Se l'utente ha `prefers-reduced-motion: reduce` attivo nel sistema operativo, le animazioni piu complesse (pulsazione, movimento logo) devono essere ridotte a un **semplice fade** (opacity-only, nessun movement/scale). NON disabilitare completamente — un fade dolce e comunque un'esperienza piacevole senza causare motion sickness (Party Mode insight). Pattern: wrappare in `@media (prefers-reduced-motion: reduce)` o usare `transition={{ reduce: { duration: 0 } }}` di Framer Motion. Requisito WCAG 2.1 AA (WCAG 2.3.3)
9. **FLOW LOGIN → NAVIGAZIONE:** Il `router.replace("/home")` deve essere chiamato DURANTE la transizione (non dopo), cosi il main layout inizia a montarsi in parallelo. L'overlay copre il montaggio e si dissolve quando la home e pronta
10. **NO DEFAULT EXPORT:** Tutti i nuovi componenti usano named export. Le pagine Next.js continuano con default export (richiesto dal framework)

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.8]
- [Source: _bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- [Source: _bmad-output/planning-artifacts/architecture.md#Loading-State-Pattern]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Spinner-unico-del-sito]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Micro-animazioni-a-3-tier]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Visual-DNA-con-gradiente-ricorrente]
- [Source: _bmad-output/project-context.md#Regole-Frontend]
- [Source: _bmad-output/implementation-artifacts/1-7-header-utente-desktop-con-menu-profilo.md#Dev-Notes]
- [Source: frontend/src/components/shared/gradient-spinner.tsx — componente spinner attuale da evolvere]
- [Source: frontend/src/components/shared/page-loader.tsx — loader attuale da aggiornare]
- [Source: frontend/src/providers/auth-provider.tsx — isAuthenticating state]
- [Source: frontend/src/app/(auth)/login/page.tsx — pagina login da arricchire con transizione]
- [Source: frontend/src/app/page.tsx — landing page con redirect]
- [Source: frontend/src/components/video/popup-overlay.tsx — pattern Framer Motion esistente]
- [Source: frontend/src/app/globals.css — design tokens gradient, keyframes animazioni]
- [Source: Web Research — Framer Motion 12.x: useAnimate timeline API, AnimatePresence mode="wait", motion/react import path]
- [Source: Web Research — Nessuna libreria aggiuntiva necessaria: FM12 copre tutte le esigenze]

## Change Log

- 2026-02-15: Implementazione completa Story 1-8 — Spinner animato brand + transizione cinematografica post-login. 6 task completati, build OK.
- 2026-02-15: Refinement iterativo transizione post-login con feedback utente:
  - Creato `LoginTransitionProvider` (context in root layout) per overlay che sopravvive al cambio route (auth→main)
  - Fix race condition `useAnimate` con `requestAnimationFrame` + `try/catch` safety net
  - Rimossa dissolvenza durante movimento logo (Fase 4) su richiesta utente
  - Aggiunto `id="sidebar-brand-logo"` a left-sidebar.tsx + `getBoundingClientRect()` per posizionamento pixel-perfect
  - Fase 4 splittata in 4a (scale) + 4b (translate) per ridimensionamento prima dell'arrivo
  - Fix bug scale: Fase 2 ora termina a `scale: 1.0` (keyframe `[0.9, 1.05, 1]`) per calcolo `targetScale` corretto via `getBoundingClientRect`
  - Rimosso `tracking-tight` dal logo overlay per combaciare con letter-spacing sidebar
- 2026-02-14: Code Review fix (3 CRITICAL, 1 HIGH, 2 MEDIUM):
  - Fix C1: `PageLoader` ora usa `<GradientSpinner variant="full" />` (AC1 — brand loader durante authenticating)
  - Fix C2: Landing page ora usa `<GradientSpinner variant="full" />` (AC5 — brand loader durante refresh)
  - Fix H1: `MIN_DISPLAY_TIME` ricalcolato al punto di utilizzo (non piu all'inizio della sequenza)
  - Fix M2: Aggiunto `role="status"` all'overlay di transizione per accessibilita ARIA

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Build iniziale fallito per import `"motion/react"` non risolvibile (pacchetto installato e `framer-motion`, non `motion`). Corretto tutti gli import a `"framer-motion"`. Build successivo passato con 0 errori.

### Completion Notes List

- **Task 1:** `GradientSpinner` evoluto con prop `variant` (`full`/`inline`, default `inline`). Variante `full` mostra logo "Video_clip" pulsante + spinner su sfondo `bg-background` fullscreen. Aggiunta prop `onAnimationReady`. Supporto `useReducedMotion` per WCAG 2.1 AA.
- **Task 2:** Creato `LoginTransitionOverlay` con sequenza animata orchestrata via `useAnimate`: Fase 2 (logo appare), Fase 3 (spinner fade-in), Fase 4 (logo dissolve verso alto-sinistra con `x:-30vw, y:-30vh`), Fase 5 (overlay fade-out). Min display time 500ms implementato (AC4). Supporto `prefers-reduced-motion` con fallback a fade semplice.
- **Task 3:** Login page integrata con `AnimatePresence mode="wait"` per exit animation form (opacity+scale+blur 0.4s). Flow: login() → setShowTransition → overlay monta → router.replace("/home") durante transizione → onTransitionEnd smonta overlay. Gestione errori preservata.
- **Task 4:** `PageLoader` semplificato a thin wrapper: `<GradientSpinner variant="full" size={32} />`. Main layout invariato.
- **Task 5:** Landing page usa `GradientSpinner variant="full"` con minimum display time 500ms via `useRef(Date.now())` + `setTimeout`. Pattern anti-flash implementato.
- **Task 6:** Build TypeScript passato con 0 errori. Verifiche visive (6.2, 6.3, 6.5, 6.6) richiedono test manuale utente.
- **Nota import:** Il Dev Notes suggeriva `import from "motion/react"` ma il pacchetto installato e `framer-motion@12.34.0` che non espone quel path. Usato `"framer-motion"` coerente con il codebase esistente (`popup-overlay.tsx`).

### File List

- `frontend/src/components/shared/gradient-spinner.tsx` — MODIFICATO: aggiunta prop `variant` (full/inline), `onAnimationReady`, `useReducedMotion`, componente `SpinnerRing` interno
- `frontend/src/components/shared/login-transition-overlay.tsx` — CREATO: overlay transizione cinematografica post-login con `useAnimate`, sequenza 5 fasi, min display time 500ms
- `frontend/src/providers/login-transition-provider.tsx` — CREATO: context provider in root layout per overlay che persiste tra route groups (auth→main)
- `frontend/src/components/shared/page-loader.tsx` — MODIFICATO: semplificato a thin wrapper che usa `GradientSpinner variant="full"`
- `frontend/src/app/(auth)/login/page.tsx` — MODIFICATO: aggiunto `AnimatePresence`, exit animation form, integrazione `useLoginTransition` context, stati `isLoggingIn`/`showTransition`
- `frontend/src/app/layout.tsx` — MODIFICATO: aggiunto `LoginTransitionProvider` nella gerarchia provider
- `frontend/src/app/page.tsx` — MODIFICATO: usa `GradientSpinner variant="full"`, minimum display time 500ms con `useRef(Date.now())`
- `frontend/src/components/layout/left-sidebar.tsx` — MODIFICATO: aggiunto `id="sidebar-brand-logo"` per targeting `getBoundingClientRect`
- `frontend/src/app/(auth)/layout.tsx` — MODIFICATO: aggiunto `id="auth-brand-logo"`, struttura gradient 3 zone per logo brand
- `frontend/src/components/layout/header.tsx` — MODIFICATO: aggiunto `id="mobile-brand-logo"` per targeting mobile transizione
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — MODIFICATO: status 1-8 aggiornato
