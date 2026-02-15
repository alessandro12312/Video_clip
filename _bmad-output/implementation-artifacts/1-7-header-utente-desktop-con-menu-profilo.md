# Story 1.7: Header Utente Desktop con Menu Profilo

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utente autenticato su desktop,
I want avere un cerchietto avatar in alto a destra con un menu profilo,
so that possa accedere rapidamente al mio profilo, alle impostazioni e fare logout da qualsiasi pagina.

## Acceptance Criteria

1. **AC1 — Avatar visibile in alto a destra su desktop**
   Given: un utente autenticato su viewport desktop (>= 1024px)
   When: la pagina si carica
   Then: un cerchietto avatar dell'utente e visibile in alto a destra nel layout, posizionato sopra il contenuto principale (non nella sidebar)

2. **AC2 — Click diretto sull'avatar naviga al profilo**
   Given: un utente desktop che clicca direttamente sul cerchietto avatar
   When: il click viene registrato
   Then: l'utente viene reindirizzato a `/profilo` (il proprio profilo)

3. **AC3 — Click sulla freccia/chevron apre il dropdown**
   Given: un utente desktop che clicca sulla freccia/chevron accanto al cerchietto avatar
   When: il dropdown si apre
   Then: vengono mostrate le voci:
   - **Il mio profilo** (link a `/profilo`)
   - **Impostazioni account** (link a `/impostazioni` — placeholder per ora)
   - **Esci** (esegue logout e redirect a `/login`)

4. **AC4 — Non visibile su mobile**
   Given: un utente su viewport mobile (< 1024px)
   When: la pagina si carica
   Then: il cerchietto avatar desktop NON e visibile (il menu profilo mobile nell'header rimane invariato)

5. **AC5 — Logout con toast**
   Given: un utente che clicca "Esci" dal menu desktop
   When: il logout viene eseguito
   Then: i token JWT vengono rimossi, l'utente viene reindirizzato a `/login` e viene mostrato un toast "Hai effettuato il logout"

## Tasks / Subtasks

> **NOTA:** Il backend non e impattato da questa story. Tutto il lavoro e frontend. L'avatar nella sidebar bottom e NON-interattivo e va rimosso perche duplicato dal nuovo menu desktop in alto a destra.

### Codice esistente (gia implementato)

- [x] `DropdownMenu*` componenti shadcn/ui in `frontend/src/components/ui/dropdown-menu.tsx` — completi e funzionanti
- [x] `UserAvatar` componente in `frontend/src/components/user/user-avatar.tsx` — supporta size sm/md/lg con gradient background
- [x] `useAuth()` hook in `frontend/src/providers/auth-provider.tsx` — espone `user`, `logout()`, `isAuthenticated`
- [x] `Header` mobile in `frontend/src/components/layout/header.tsx` — gia ha dropdown avatar (pattern da riusare), visibile solo su mobile (`lg:hidden`)
- [x] `Toaster` Sonner nel root layout `frontend/src/app/layout.tsx:33` — position bottom-right, richColors, persiste tra navigazioni
- [x] `LeftSidebar` con avatar non-interattivo nel bottom section `frontend/src/components/layout/left-sidebar.tsx:96-118`
- [x] Layout `(main)` in `frontend/src/app/(main)/layout.tsx` — struttura flex con LeftSidebar + content column

### Gap identificati (lavoro da completare)

- [x] Task 1: Creare componente `DesktopUserMenu` (AC: #1, #2, #3, #4, #5)
  - [x] 1.1 — Creare `frontend/src/components/layout/desktop-user-menu.tsx` come Client Component (`"use client"`)
  - [x] 1.2 — Importare: `useAuth` da `@/providers/auth-provider`, `UserAvatar` da `@/components/user/user-avatar`, `DropdownMenu*` da `@/components/ui/dropdown-menu`, `Link` da `next/link`, `Button` da `@/components/ui/button`, `toast` da `sonner`, icone `ChevronDown`, `LogOut`, `User`, `Settings` da `lucide-react`
  - [x] 1.3 — Layout: container `hidden lg:flex` con `items-center gap-1`. Contiene:
    - **Avatar Link**: `<Link href="/profilo">` wrappa `<UserAvatar username={user.username} size="sm" />` con hover effect (`opacity-80 transition-opacity`). Click diretto naviga a `/profilo` (AC2)
    - **Chevron Button**: `<DropdownMenuTrigger asChild>` wrappa `<Button variant="ghost" size="icon" className="h-7 w-7">` con `<ChevronDown className="h-4 w-4" />`. Click apre il dropdown (AC3)
  - [x] 1.4 — DropdownMenuContent con `align="end"` contiene:
    - `<DropdownMenuItem asChild><Link href="/profilo"><User className="mr-2 h-4 w-4" />Il mio profilo</Link></DropdownMenuItem>`
    - `<DropdownMenuItem asChild><Link href="/impostazioni"><Settings className="mr-2 h-4 w-4" />Impostazioni account</Link></DropdownMenuItem>`
    - `<DropdownMenuSeparator />`
    - `<DropdownMenuItem onClick={handleLogout}><LogOut className="mr-2 h-4 w-4" />Esci</DropdownMenuItem>`
  - [x] 1.5 — Funzione `handleLogout`: chiama `toast("Hai effettuato il logout")` PRIMA di `logout()` (il toast persiste perche Toaster e nel root layout e la navigazione e client-side) (AC5)
  - [x] 1.6 — Il componente NON renderizza nulla se `!user` (guard early return `if (!user) return null`)
  - [x] 1.7 — Export: `export function DesktopUserMenu()` (named export, come tutti i componenti)

- [x] Task 2: Creare `DesktopNavbar` e aggiungerla al main layout (AC: #1, #4)
  - [x] 2.1 — Creare `frontend/src/components/layout/desktop-navbar.tsx` come Client Component: header bar desktop-only (`hidden lg:flex`) con `UserSearchBar` (spostata dalla sidebar) centrata e `DesktopUserMenu` allineato a destra. Glassmorphism: `bg-background/80 backdrop-blur-sm`, border-bottom, h-14
  - [x] 2.2 — Modificare `frontend/src/app/(main)/layout.tsx`: importare `DesktopNavbar` da `@/components/layout/desktop-navbar` e inserire `<DesktopNavbar />` subito dopo `<Header />` nel content column
  - [x] 2.3 — Posizionamento: approccio flow-based (la navbar occupa spazio nel layout come elemento normale, non absolute). Nessun `relative` necessario sul content div. La visibilita desktop-only e garantita sia dal `hidden lg:flex` della `DesktopNavbar` che dal `hidden lg:flex` del `DesktopUserMenu` (doppio layer difensivo)

- [x] Task 3: Ristrutturare LeftSidebar — rimuovere avatar, ricerca e spostare toggle (AC: #1)
  - [x] 3.1 — Rimuovere il blocco user avatar+username dalla bottom section di `frontend/src/components/layout/left-sidebar.tsx`. L'avatar e ora nella `DesktopNavbar` (Task 2), la sidebar non deve duplicarlo
  - [x] 3.2 — Rimuovere la `UserSearchBar` dalla sidebar (spostata nella `DesktopNavbar` — Task 2.1). Rimuovere l'import di `UserSearchBar`
  - [x] 3.3 — Spostare il bottone collapse/expand toggle dalla bottom section alla top section accanto al logo. La top section ora ha `justify-between` per logo a sinistra e toggle a destra, con padding condizionale (`collapsed ? "px-2" : "px-4"`)
  - [x] 3.4 — Rimuovere l'intera bottom section (separator + div user/toggle). La sidebar ora termina con `</nav>`
  - [x] 3.5 — Rimuovere gli import di `UserAvatar`, `useAuth` e `UserSearchBar` (non piu usati). Rimuovere `const { user } = useAuth()` dalla funzione

- [x] Task 4: Creare pagina placeholder `/impostazioni` (AC: #3)
  - [x] 4.1 — Creare `frontend/src/app/(main)/impostazioni/page.tsx` come Client Component
  - [x] 4.2 — Contenuto minimale: titolo "Impostazioni account" + `<EmptyState icon={Settings} title="In arrivo" description="Le impostazioni account saranno disponibili prossimamente." />`
  - [x] 4.3 — Usare `EmptyState` da `@/components/shared/empty-state` e `Settings` da `lucide-react`

- [x] Task 5: Verifica finale (AC: #1, #2, #3, #4, #5)
  - [x] 5.1 — Eseguire `npm run build` da `frontend/` — TypeScript strict, 0 errori
  - [x] 5.2 — Eseguire `python manage.py test` da `backend/` — tutti i test passano (nessuna modifica backend, verifica regressioni)
  - [x] 5.3 — Verificare visivamente: su viewport >= 1024px l'avatar appare in alto a destra; su viewport < 1024px l'avatar desktop NON appare

## Dev Notes

### Stato attuale del codice — Analisi gap

Il sistema layout desktop e **parzialmente implementato**: la `LeftSidebar` ha un avatar non-interattivo nella sezione bottom (riga 96-118), ma l'AC richiede un avatar interattivo in alto a destra del content area (non nella sidebar). L'header attuale (`header.tsx`) e mobile-only (`lg:hidden`) e gia implementa un dropdown avatar simile — il pattern va replicato per desktop con le differenze specifiche dell'AC (avatar + chevron separati, voce Impostazioni).

| Gap | Severita | File impattato | Dettaglio |
|-----|----------|----------------|-----------|
| **Nessun menu avatar desktop** | CRITICO | `layout/` | Non esiste un componente per il menu utente desktop. L'avatar nella sidebar e statico |
| **Avatar sidebar ridondante** | MEDIO | `left-sidebar.tsx:96-118` | L'avatar nella bottom section diventa duplicato dopo l'aggiunta del menu desktop |
| **Pagina /impostazioni mancante** | BASSO | `app/(main)/impostazioni/` | Il dropdown include "Impostazioni account" ma la pagina non esiste. Serve placeholder |
| **Logout senza toast** | MEDIO | Nuovo componente | `logout()` nel auth-provider fa redirect ma non mostra toast. L'AC5 richiede toast "Hai effettuato il logout" |

### Interazione avatar vs chevron (design critico)

L'AC specifica due aree cliccabili SEPARATE:
- **Avatar** (il cerchietto): click diretto → naviga a `/profilo`. E un `<Link>`, NON un trigger dropdown
- **Chevron** (la freccia accanto): click → apre il `DropdownMenu`

Questo pattern richiede che l'avatar e il chevron siano elementi DOM distinti. NON wrappare entrambi in un unico `DropdownMenuTrigger`. Il pattern corretto:

```tsx
<div className="hidden lg:flex items-center gap-1">
  <Link href="/profilo" className="...">
    <UserAvatar username={user.username} size="sm" />
  </Link>
  <DropdownMenu>
    <DropdownMenuTrigger asChild>
      <Button variant="ghost" size="icon" className="h-7 w-7">
        <ChevronDown className="h-4 w-4" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end">
      {/* menu items */}
    </DropdownMenuContent>
  </DropdownMenu>
</div>
```

### Posizionamento: DesktopNavbar flow-based

L'approccio iniziale prevedeva positioning `absolute` nel content area. In fase di implementazione si e optato per un approccio **flow-based**: un componente `DesktopNavbar` (header bar h-14 con `hidden lg:flex`) posizionato nel layout flow subito dopo il mobile `<Header />`. Questo:
- Non sovrappone il contenuto (nessun z-index conflict)
- Permette di ospitare sia la `UserSearchBar` (spostata dalla sidebar) che il `DesktopUserMenu`
- Ha glassmorphism coerente col mobile header (`bg-background/80 backdrop-blur-sm`)

**Nota**: l'header mobile usa `z-40` e `lg:hidden`, la `DesktopNavbar` usa `hidden lg:flex`. Mutuamente esclusivi, nessun conflitto.

### Toast logout: persistenza garantita

La sequenza `toast() → logout()` funziona perche:
1. `toast("Hai effettuato il logout")` aggiunge il toast a Sonner
2. `logout()` chiama `router.replace("/login")` — navigazione client-side
3. Il `<Toaster />` e nel root layout (`app/layout.tsx:33`), fuori dal route group `(main)`, quindi persiste durante la navigazione verso `(auth)/login`
4. Il toast rimane visibile sulla pagina di login

### Componenti da RIUTILIZZARE (NON ricreare)

| Componente | File | Riuso |
|-----------|------|-------|
| `UserAvatar` | `components/user/user-avatar.tsx` | Usare con `size="sm"` nel cerchietto avatar. Mostra iniziale con gradient background |
| `DropdownMenu*` | `components/ui/dropdown-menu.tsx` | Gia installato e funzionante. Usare: DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator |
| `Button` | `components/ui/button.tsx` | Per il bottone chevron: `variant="ghost"`, `size="icon"` |
| `EmptyState` | `components/shared/empty-state.tsx` | Per la pagina placeholder /impostazioni |
| `useAuth()` | `providers/auth-provider.tsx` | Per `user` (dati utente) e `logout()` (rimozione token + redirect) |
| `toast()` | da `sonner` (libreria) | Per il toast post-logout. Import: `import { toast } from "sonner"` |

### Lezioni dalla Story 1-6 (da applicare)

- **Named exports**: tutti i componenti usano `export function ComponentName()`, MAI default export (tranne pagine Next.js)
- **File naming**: kebab-case per tutti i file (`desktop-user-menu.tsx`)
- **Dark mode**: usare Tailwind semantic tokens (`text-foreground`, `text-muted-foreground`, `bg-background`). NON hardcodare colori
- **Accessibility**: `aria-label` sui bottoni/link interattivi. Il `DropdownMenuTrigger` ha gia a11y via Radix UI
- **Toast**: Solo su errori e conferme importanti. Il logout e una conferma importante → toast OK
- **Lingua**: messaggi utente in italiano, codice in inglese

### Git intelligence

Ultimi commit rilevanti:
- `6456640` — Story 1-4 profilo utente, 1-5 follow/unfollow, 1-6 liste follower/following + code review fix
- `d6b0b79` — Story 1-2 registrazione + Story 1-3 login JWT + code review fix
- `ededfe7` — code review Story 1-1: sicurezza, performance, dead code
- `f6845e1` — Story 1-1 backend alignment + Story 1-9 ricerca utenti + fix permessi

Pattern stabiliti nei commit precedenti:
- Componenti layout: Client Component con `"use client"`, hooks di contesto, Tailwind utility classes
- Pattern dropdown: `DropdownMenuTrigger asChild` + `Button variant="ghost"` (vedi header.tsx mobile)
- Named export + kebab-case file + Lucide icons

### Project Structure Notes

| File | Ruolo | Azione |
|------|-------|--------|
| `frontend/src/components/layout/desktop-user-menu.tsx` | Menu avatar desktop (avatar Link + chevron DropdownMenu) | **CREATO** — `hidden lg:flex`, avatar Link + chevron DropdownMenu + logout con toast |
| `frontend/src/components/layout/desktop-navbar.tsx` | Header bar desktop (search + user menu) | **CREATO** — wrapper `hidden lg:flex` h-14 con UserSearchBar + DesktopUserMenu |
| `frontend/src/app/(main)/layout.tsx` | Layout principale (main) | **MODIFICATO** — import/render DesktopNavbar dopo Header |
| `frontend/src/components/layout/left-sidebar.tsx` | Sidebar desktop | **MODIFICATO** — rimosso avatar+username+searchbar, toggle spostato in top section |
| `frontend/src/app/(main)/impostazioni/page.tsx` | Pagina impostazioni | **CREATO** — placeholder con EmptyState |

**File NON da toccare:**
- `frontend/src/components/layout/header.tsx` — Header mobile rimane invariato (AC4)
- `frontend/src/components/layout/mobile-bottom-bar.tsx` — Bottom bar mobile invariata
- `frontend/src/providers/auth-provider.tsx` — logout() non va modificato (il toast si gestisce nel componente chiamante)
- `frontend/src/components/user/user-avatar.tsx` — Riusare as-is
- `frontend/src/components/ui/dropdown-menu.tsx` — Gia completo
- `backend/` — Zero modifiche backend

### Stack tecnologico rilevante

- **Frontend:** Next.js 16.1.6, React 19, TypeScript 5
- **UI:** TailwindCSS 4, shadcn/ui (DropdownMenu, Button, Avatar), Lucide React (ChevronDown, LogOut, User, Settings)
- **State:** useAuth() context per dati utente e logout
- **Toast:** Sonner (gia nel root layout, position bottom-right, richColors)
- **Routing:** Next.js App Router, Link da `next/link`

### Vincoli critici per lo sviluppatore

1. **DUE AREE CLICCABILI SEPARATE:** Avatar e un `<Link>` a `/profilo`, chevron e un `<DropdownMenuTrigger>`. NON wrappare entrambi in un unico trigger
2. **HIDDEN LG:FLEX:** Il componente DesktopUserMenu usa `hidden lg:flex` per essere visibile solo su desktop. NON usare JS per controllare la visibilita — Tailwind responsive e sufficiente
3. **FLOW-BASED LAYOUT:** Il menu e in una `DesktopNavbar` (header bar h-14 flow-based) nel content column. NON usare absolute positioning — l'approccio flow-based evita conflitti z-index e sovrapposizioni
4. **TOAST PRIMA DI LOGOUT:** Chiamare `toast()` PRIMA di `logout()` perche logout fa `router.replace()`. L'ordine e critico
5. **RIMUOVERE AVATAR SIDEBAR:** La bottom section della LeftSidebar deve perdere avatar e username. Mantenere SOLO il toggle collapse
6. **PAGINA /IMPOSTAZIONI:** Creare come placeholder minimale. NON implementare funzionalita di impostazioni in questa story
7. **DARK MODE:** Tutti gli stili usano semantic tokens Tailwind. Il chevron button usa `text-muted-foreground` per essere discreto
8. **LINGUA:** Voci menu in italiano: "Il mio profilo", "Impostazioni account", "Esci". Toast: "Hai effettuato il logout"
9. **NO FRAMER MOTION:** Questa story non richiede animazioni Tier 1/2. Il DropdownMenu di Radix ha gia transizioni CSS interne
10. **MOBILE INVARIATO:** L'header mobile con il suo dropdown avatar rimane ESATTAMENTE come e. NON modificare `header.tsx`

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.7]
- [Source: _bmad-output/planning-artifacts/architecture.md#Frontend-Architecture]
- [Source: _bmad-output/planning-artifacts/architecture.md#Component-Boundaries]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Dark-Mode]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Navigazione]
- [Source: _bmad-output/project-context.md#Regole-Frontend]
- [Source: _bmad-output/implementation-artifacts/1-6-liste-follower-e-following.md#Dev-Notes]
- [Source: frontend/src/components/layout/header.tsx — pattern dropdown mobile da replicare]
- [Source: frontend/src/components/layout/left-sidebar.tsx:96-118 — sezione bottom da semplificare]
- [Source: frontend/src/app/(main)/layout.tsx — struttura layout da modificare]
- [Source: frontend/src/app/layout.tsx:33 — Toaster Sonner nel root layout]

## Change Log

- **2026-02-15**: Implementazione completa Story 1-7 — Menu avatar desktop con dropdown profilo, rimozione avatar ridondante sidebar, pagina placeholder /impostazioni. Build OK, 85 test backend OK.
- **2026-02-15 (code review)**: Fix 7 issue (3 HIGH, 3 MEDIUM, 1 LOW). Code fix: aggiunto `hidden lg:flex` a DesktopUserMenu per self-containment desktop-only. Story fix: aggiornati Task 2 e 3, Completion Notes, File List e Dev Notes per riflettere l'architettura reale (DesktopNavbar wrapper flow-based, spostamento UserSearchBar dalla sidebar alla navbar, toggle collapse in top section).

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (claude-opus-4-6)

### Debug Log References

- Backend test richiede `cs_clips.tests` come label esplicita (non scoperto automaticamente da `manage.py test` senza argomenti)
- venv Python non attivabile via `activate` in bash sandbox, usato percorso diretto `.venv/Scripts/python.exe`

### Completion Notes List

- **Task 1**: Creato `DesktopUserMenu` con avatar Link separato dal chevron DropdownMenuTrigger, come da AC. Usati tutti i componenti esistenti (UserAvatar, DropdownMenu*, Button). Toast "Hai effettuato il logout" chiamato PRIMA di `logout()` per persistenza. Guard `if (!user) return null`. Named export. Container `hidden lg:flex items-center gap-1` (self-contained desktop-only).
- **Task 2**: Creato `DesktopNavbar` come wrapper header bar desktop-only (`hidden lg:flex h-14`) con glassmorphism. Contiene `UserSearchBar` (centrata) e `DesktopUserMenu` (destra). Aggiunto al main layout dopo `<Header />`. Approccio flow-based (no absolute, no relative necessario).
- **Task 3**: Ristrutturata `LeftSidebar`: rimosso avatar+username+searchbar dalla sidebar. `UserSearchBar` spostata nella `DesktopNavbar`. Toggle collapse spostato dalla bottom alla top section accanto al logo. Rimossa intera bottom section. Rimossi import `UserAvatar`, `useAuth`, `UserSearchBar`.
- **Task 4**: Creata pagina placeholder `/impostazioni` con `EmptyState` (icon Settings, title "In arrivo"). Client Component con titolo h1.
- **Task 5**: Frontend build OK (0 errori TypeScript, `/impostazioni` nelle routes). Backend 85 test OK, 0 regressioni. Nessuna modifica backend.

### File List

- `frontend/src/components/layout/desktop-user-menu.tsx` — **CREATO** — Componente menu avatar desktop (`hidden lg:flex`) con avatar Link a `/profilo` + chevron DropdownMenu (Il mio profilo, Impostazioni, Esci con toast)
- `frontend/src/components/layout/desktop-navbar.tsx` — **CREATO** — Header bar desktop-only (`hidden lg:flex h-14`) con UserSearchBar centrata e DesktopUserMenu a destra, glassmorphism
- `frontend/src/app/(main)/layout.tsx` — **MODIFICATO** — Import DesktopNavbar, render dopo Header nel content column
- `frontend/src/components/layout/left-sidebar.tsx` — **MODIFICATO** — Rimosso avatar+username+UserSearchBar, toggle collapse spostato da bottom a top section, rimossi import inutilizzati (UserAvatar, useAuth, UserSearchBar)
- `frontend/src/app/(main)/impostazioni/page.tsx` — **CREATO** — Pagina placeholder impostazioni account con EmptyState
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — **MODIFICATO** — Status story 1-7 aggiornato
