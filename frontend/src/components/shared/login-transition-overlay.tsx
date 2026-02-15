"use client";

import { useEffect, useRef } from "react";
import { motion, useAnimate, useReducedMotion } from "framer-motion";
import { GradientSpinner } from "./gradient-spinner";

interface LoginTransitionOverlayProps {
  isActive: boolean;
  onTransitionEnd: () => void;
}

const MIN_DISPLAY_TIME = 500;

export function LoginTransitionOverlay({
  isActive,
  onTransitionEnd,
}: LoginTransitionOverlayProps) {
  const [scope, animate] = useAnimate<HTMLDivElement>();
  const activatedAt = useRef(0);
  const isRunning = useRef(false);
  const prefersReducedMotion = useReducedMotion();
  const onTransitionEndRef = useRef(onTransitionEnd);
  onTransitionEndRef.current = onTransitionEnd;

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
        const elapsed = Date.now() - activatedAt.current;
        const remaining = Math.max(0, MIN_DISPLAY_TIME - elapsed);

        if (prefersReducedMotion) {
          if (remaining > 0) {
            await new Promise((r) => setTimeout(r, remaining));
          }
          await animate(scope.current, { opacity: 0 }, { duration: 0.3 });
          onTransitionEndRef.current();
          return;
        }

        // Fase 2: Logo appare al centro (overshoot a 1.05, poi si assesta a 1.0)
        // IMPORTANTE: deve finire a scale 1.0 perché getBoundingClientRect in Fase 4
        // include la transform — se finisse a 1.1 il calcolo di targetScale sarebbe sfalsato
        await animate(
          ".brand-logo",
          { scale: [0.9, 1.05, 1], opacity: [0, 1] },
          { duration: 0.45, ease: "easeOut" }
        );

        // Fase 3: Spinner appare
        await animate(
          ".brand-spinner",
          { opacity: [0, 1] },
          { duration: 0.3 }
        );

        // Attendi minimum display time (AC4)
        if (remaining > 0) {
          await new Promise((r) => setTimeout(r, remaining));
        }

        // Fase 4: Rileva desktop (sidebar visibile) o mobile (header visibile)
        const sidebarLogo = document.getElementById("sidebar-brand-logo");
        const mobileLogo = document.getElementById("mobile-brand-logo");
        const overlayLogo = scope.current?.querySelector(".brand-logo") as HTMLElement | null;
        const sidebarVisible = sidebarLogo && sidebarLogo.getBoundingClientRect().width > 0;

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
          const restEl = scope.current?.querySelector(".brand-letters-rest") as HTMLElement | null;
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

        // Fase 5: Overlay fade-out — lo sfondo opaco si dissolve rivelando
        // naturalmente il logo della sidebar già posizionato sotto
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
      className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-background"
      initial={{ opacity: 1 }}
      aria-label="Transizione in corso"
    >
      <motion.h1
        className="brand-logo text-4xl font-bold sm:text-5xl"
        initial={{ opacity: 0, scale: 0.9 }}
      ><span className="brand-letter-first gradient-text">V</span><span className="brand-letters-rest"><span style={{ color: 'var(--gradient-end)' }}>ideo_cli</span><span className="gradient-text-reverse">p</span></span></motion.h1>

      <motion.div
        className="brand-spinner mt-6"
        initial={{ opacity: 0 }}
      >
        <GradientSpinner size={32} />
      </motion.div>
    </motion.div>
  );
}
