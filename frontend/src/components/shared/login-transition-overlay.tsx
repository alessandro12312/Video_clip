/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║           SISTEMA DI TRANSIZIONE POST-LOGIN (Brand)            ║
 * ╠══════════════════════════════════════════════════════════════════╣
 * ║                                                                ║
 * ║  Animazione cinematografica che collega la schermata di login   ║
 * ║  alla UI principale. Il logo del brand fa da filo conduttore.  ║
 * ║                                                                ║
 * ║  FLUSSO COMPLETO:                                              ║
 * ║  1. Login riuscito → cattura posizione logo auth               ║
 * ║  2. Overlay si monta (bg trasparente, logo alla pos. auth)     ║
 * ║  3. Fase 1: bg fade-in + logo si muove al centro              ║
 * ║  4. Fase 2: spinner appare                                     ║
 * ║  5. Fase 3: logo si sposta verso il target finale              ║
 * ║     - Desktop: "Video_clip" intero → sidebar                   ║
 * ║     - Mobile: dissolve lettere → "V" → header                  ║
 * ║  6. Fase 4: overlay fade-out rivela la UI                      ║
 * ║                                                                ║
 * ║  STRUTTURA DEL LOGO (3 zone gradiente):                        ║
 * ║  ┌─────────────┬──────────────┬─────────────────┐              ║
 * ║  │ V           │ ideo_cli     │ p               │              ║
 * ║  │ gradient-   │ solid cyan   │ gradient-text-  │              ║
 * ║  │ text        │ --gradient-  │ reverse         │              ║
 * ║  │ (viola→     │ end          │ (ciano→viola)   │              ║
 * ║  │  ciano)     │              │                 │              ║
 * ║  └─────────────┴──────────────┴─────────────────┘              ║
 * ║                                                                ║
 * ║  FILE CHE CONTENGONO IL LOGO (aggiornare TUTTI se cambia):     ║
 * ║  1. (auth)/layout.tsx        → #auth-brand-logo (text-3xl)     ║
 * ║  2. Questo file (overlay)    → .brand-logo (text-4xl/5xl)      ║
 * ║  3. left-sidebar.tsx         → #sidebar-brand-logo (text-xl)   ║
 * ║  4. header.tsx               → #mobile-brand-logo (solo "V")   ║
 * ║                                                                ║
 * ║  CLASSI CSS RICHIESTE (globals.css):                           ║
 * ║  - .gradient-text         → gradiente 135deg start→end         ║
 * ║  - .gradient-text-reverse → gradiente 135deg end→start         ║
 * ║                                                                ║
 * ║  ANIMAZIONE MOBILE — struttura span richiesta:                 ║
 * ║  - .brand-letter-first  → prima lettera (rimane visibile)      ║
 * ║  - .brand-letters-rest  → resto lettere (dissolte via width:0) ║
 * ║                                                                ║
 * ║  ID RICHIESTI PER IL TARGETING:                                ║
 * ║  - #auth-brand-logo    → sorgente animazione (login page)      ║
 * ║  - #sidebar-brand-logo → target desktop                        ║
 * ║  - #mobile-brand-logo  → target mobile                         ║
 * ║                                                                ║
 * ║  PROVIDER: login-transition-provider.tsx                       ║
 * ║  - Coordina login page ↔ overlay (sopravvive al cambio route)  ║
 * ║  - startLoginTransition(sourceRect?) avvia la sequenza         ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

"use client";

import { useEffect, useRef } from "react";
import { motion, useAnimate, useReducedMotion } from "framer-motion";
import { GradientSpinner } from "./gradient-spinner";
import type { SourceRect } from "@/providers/login-transition-provider";

interface LoginTransitionOverlayProps {
  isActive: boolean;
  sourceRect: SourceRect | null;
  onTransitionEnd: () => void;
}

const MIN_DISPLAY_TIME = 500;

export function LoginTransitionOverlay({
  isActive,
  sourceRect,
  onTransitionEnd,
}: LoginTransitionOverlayProps) {
  const [scope, animate] = useAnimate<HTMLDivElement>();
  const activatedAt = useRef(0);
  const isRunning = useRef(false);
  const prefersReducedMotion = useReducedMotion();
  const onTransitionEndRef = useRef(onTransitionEnd);
  onTransitionEndRef.current = onTransitionEnd;
  const sourceRectRef = useRef<SourceRect | null>(null);
  sourceRectRef.current = sourceRect;

  useEffect(() => {
    if (!isActive || isRunning.current) return;
    isRunning.current = true;
    activatedAt.current = Date.now();

    // Attende il prossimo frame per garantire che il DOM sia pronto
    const frameId = requestAnimationFrame(() => {
      runSequence();
    });

    async function runSequence() {
      try {
        const srcRect = sourceRectRef.current;

        if (prefersReducedMotion) {
          // Mostra tutto istantaneamente, attendi min time, poi dissolvi
          await animate(".overlay-bg", { opacity: 1 }, { duration: 0 });
          await animate(
            ".brand-logo",
            { opacity: 1, scale: 1, x: 0, y: 0 },
            { duration: 0 }
          );
          const elapsedReduced = Date.now() - activatedAt.current;
          const remainingReduced = Math.max(0, MIN_DISPLAY_TIME - elapsedReduced);
          if (remainingReduced > 0) {
            await new Promise((r) => setTimeout(r, remainingReduced));
          }
          await animate(scope.current, { opacity: 0 }, { duration: 0.3 });
          onTransitionEndRef.current();
          return;
        }

        // ── Fase 1: Logo dalla posizione auth al centro ──
        if (srcRect) {
          const overlayLogo = scope.current?.querySelector(
            ".brand-logo"
          ) as HTMLElement | null;

          if (overlayLogo) {
            // Misura la posizione naturale del logo overlay (al centro, opacity 0)
            const naturalRect = overlayLogo.getBoundingClientRect();
            const scaleRatio = srcRect.height / naturalRect.height;
            const dx =
              srcRect.left +
              srcRect.width / 2 -
              (naturalRect.left + naturalRect.width / 2);
            const dy =
              srcRect.top +
              srcRect.height / 2 -
              (naturalRect.top + naturalRect.height / 2);

            // Posiziona il logo esattamente sopra il logo auth (istantaneo)
            await animate(
              ".brand-logo",
              { x: dx, y: dy, scale: scaleRatio, opacity: 1 },
              { duration: 0 }
            );

            // Fade-in sfondo + logo si muove al centro simultaneamente
            animate(".overlay-bg", { opacity: 1 }, { duration: 0.3 });
            await animate(
              ".brand-logo",
              { x: 0, y: 0, scale: 1 },
              { duration: 0.5, ease: "easeInOut" }
            );
          } else {
            // Fallback: comportamento originale
            await animate(".overlay-bg", { opacity: 1 }, { duration: 0 });
            await animate(
              ".brand-logo",
              { scale: [0.9, 1.05, 1], opacity: [0, 1] },
              { duration: 0.45, ease: "easeOut" }
            );
          }
        } else {
          // Nessun sourceRect: comportamento originale (scale-in al centro)
          await animate(
            ".brand-logo",
            { scale: [0.9, 1.05, 1], opacity: [0, 1] },
            { duration: 0.45, ease: "easeOut" }
          );
        }

        // ── Fase 2: Spinner appare ──
        await animate(
          ".brand-spinner",
          { opacity: [0, 1] },
          { duration: 0.3 }
        );

        // Attendi minimum display time (AC4) — ricalcola al punto di utilizzo
        const elapsed = Date.now() - activatedAt.current;
        const remaining = Math.max(0, MIN_DISPLAY_TIME - elapsed);
        if (remaining > 0) {
          await new Promise((r) => setTimeout(r, remaining));
        }

        // ── Fase 3: Rileva desktop (sidebar visibile) o mobile (header visibile) ──
        const sidebarLogo = document.getElementById("sidebar-brand-logo");
        const mobileLogo = document.getElementById("mobile-brand-logo");
        const overlayLogo = scope.current?.querySelector(
          ".brand-logo"
        ) as HTMLElement | null;
        const sidebarVisible =
          sidebarLogo && sidebarLogo.getBoundingClientRect().width > 0;

        if (sidebarVisible && overlayLogo) {
          // — DESKTOP: "Video_clip" intero si scala e si sposta verso la sidebar —
          const target = sidebarLogo.getBoundingClientRect();
          const source = overlayLogo.getBoundingClientRect();
          const targetX = `${target.left + target.width / 2 - (source.left + source.width / 2)}px`;
          const targetY = `${target.top + target.height / 2 - (source.top + source.height / 2)}px`;
          const targetScale = target.width / source.width;

          await animate(
            ".brand-logo",
            { scale: targetScale },
            { duration: 0.25, ease: "easeInOut" }
          );
          await animate(
            ".brand-logo",
            { x: targetX, y: targetY },
            { duration: 0.35, ease: "easeInOut" }
          );
        } else if (mobileLogo && overlayLogo) {
          // — MOBILE: dissolvi "ideo_clip", poi posiziona "V" sull'header —
          const restEl = scope.current?.querySelector(
            ".brand-letters-rest"
          ) as HTMLElement | null;
          if (restEl) {
            const currentWidth = restEl.getBoundingClientRect().width;
            restEl.style.display = "inline-block";
            restEl.style.overflow = "hidden";
            restEl.style.whiteSpace = "nowrap";
            restEl.style.width = `${currentWidth}px`;
          }
          await animate(
            ".brand-letters-rest",
            { opacity: 0, width: 0 },
            { duration: 0.3, ease: "easeInOut" }
          );

          // Misura dopo il collasso (h1 ora contiene solo "V")
          const target = mobileLogo.getBoundingClientRect();
          const source = overlayLogo.getBoundingClientRect();
          const targetX = `${target.left + target.width / 2 - (source.left + source.width / 2)}px`;
          const targetY = `${target.top + target.height / 2 - (source.top + source.height / 2)}px`;
          const targetScale = target.height / source.height;

          await animate(
            ".brand-logo",
            { scale: targetScale },
            { duration: 0.25, ease: "easeInOut" }
          );
          await animate(
            ".brand-logo",
            { x: targetX, y: targetY },
            { duration: 0.35, ease: "easeInOut" }
          );
        } else {
          // Fallback
          await animate(
            ".brand-logo",
            { scale: 0.5, x: "-30vw", y: "-30vh" },
            { duration: 0.5, ease: "easeInOut" }
          );
        }

        // ── Fase 4: Overlay fade-out — rivela la UI sottostante ──
        await animate(scope.current, { opacity: 0 }, { duration: 0.3 });

        onTransitionEndRef.current();
      } catch {
        // Se l'animazione fallisce, completa comunque la transizione
        onTransitionEndRef.current();
      }
    }

    return () => {
      cancelAnimationFrame(frameId);
    };
  }, [isActive, animate, scope, prefersReducedMotion]);

  // Reset quando la transizione finisce
  useEffect(() => {
    if (!isActive) {
      isRunning.current = false;
    }
  }, [isActive]);

  if (!isActive) return null;

  return (
    <motion.div
      ref={scope}
      className="fixed inset-0 z-50"
      initial={{ opacity: 1 }}
      role="status"
      aria-label="Transizione in corso"
    >
      {/* Background — trasparente se parte dal logo auth, opaco altrimenti */}
      <div
        className="overlay-bg absolute inset-0 bg-background"
        style={{ opacity: sourceRect ? 0 : 1 }}
      />

      {/* Contenuto centrato */}
      <div className="relative z-10 flex h-full flex-col items-center justify-center">
        <motion.h1
          className="brand-logo text-4xl font-bold sm:text-5xl"
          initial={{ opacity: 0 }}
        >
          <span className="brand-letter-first gradient-text">V</span>
          <span className="brand-letters-rest">
            <span style={{ color: "var(--gradient-end)" }}>ideo_cli</span>
            <span className="gradient-text-reverse">p</span>
          </span>
        </motion.h1>

        <motion.div className="brand-spinner mt-6" initial={{ opacity: 0 }}>
          <GradientSpinner size={32} />
        </motion.div>
      </div>
    </motion.div>
  );
}
