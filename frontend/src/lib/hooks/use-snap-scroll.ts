"use client";

import { useEffect, useRef } from "react";

const MIN_PADDING = 16;
const DELTA_THRESHOLD = 80;
const GESTURE_TIMEOUT_MS = 200;
const ANIMATION_DURATION_MS = 400;
const POST_SNAP_COOLDOWN_MS = 600;

function easeOutCubic(t: number) {
  return 1 - Math.pow(1 - t, 3);
}

/**
 * Intercepts wheel events on <main> and snaps one card at a time.
 * Uses manual RAF animation instead of browser smooth scroll for reliability.
 */
export function useSnapScroll() {
  const isAnimatingRef = useRef(false);
  const accumulatedDeltaRef = useRef(0);
  const gestureTimerRef = useRef<NodeJS.Timeout>(null);
  const lastSnapDirectionRef = useRef<1 | -1 | 0>(0);
  const postSnapCooldownRef = useRef(false);
  const postSnapTimerRef = useRef<NodeJS.Timeout>(null);
  const rafRef = useRef<number>(0);

  useEffect(() => {
    const container = document.querySelector("main");
    if (!container) return;

    function getTargets() {
      return Array.from(container!.querySelectorAll<HTMLElement>("[data-snap-target]"));
    }

    function getPositionInContainer(target: HTMLElement) {
      const containerRect = container!.getBoundingClientRect();
      const targetRect = target.getBoundingClientRect();
      return targetRect.top - containerRect.top + container!.scrollTop;
    }

    function getSnapPosition(target: HTMLElement) {
      const pos = getPositionInContainer(target);
      const viewH = container!.clientHeight;
      const cardH = target.clientHeight;
      const padding = Math.max(MIN_PADDING, (viewH - cardH) / 2);
      return pos - padding;
    }

    function getCurrentIndex() {
      const targets = getTargets();
      if (targets.length === 0) return -1;

      const scrollTop = container!.scrollTop;
      const firstSnap = getSnapPosition(targets[0]);

      if (scrollTop < firstSnap * 0.5) return -1;

      let closest = 0;
      let minDist = Infinity;
      for (let i = 0; i < targets.length; i++) {
        const dist = Math.abs(getSnapPosition(targets[i]) - scrollTop);
        if (dist < minDist) {
          minDist = dist;
          closest = i;
        }
      }
      return closest;
    }

    function animateScrollTo(targetTop: number, direction: 1 | -1) {
      isAnimatingRef.current = true;
      lastSnapDirectionRef.current = direction;
      const start = container!.scrollTop;
      const distance = targetTop - start;
      const startTime = performance.now();

      if (rafRef.current) cancelAnimationFrame(rafRef.current);

      function step(now: number) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / ANIMATION_DURATION_MS, 1);
        container!.scrollTop = start + distance * easeOutCubic(progress);

        if (progress < 1) {
          rafRef.current = requestAnimationFrame(step);
        } else {
          // Animation complete
          rafRef.current = 0;
          isAnimatingRef.current = false;

          // Post-snap cooldown: block opposite-direction bounce
          postSnapCooldownRef.current = true;
          if (postSnapTimerRef.current) clearTimeout(postSnapTimerRef.current);
          postSnapTimerRef.current = setTimeout(() => {
            postSnapCooldownRef.current = false;
            lastSnapDirectionRef.current = 0;
          }, POST_SNAP_COOLDOWN_MS);
        }
      }

      rafRef.current = requestAnimationFrame(step);
    }

    function snapTo(idx: number, direction: 1 | -1) {
      if (idx < 0) {
        animateScrollTo(0, direction);
      } else {
        const targets = getTargets();
        const target = targets[idx];
        if (!target) return;
        animateScrollTo(getSnapPosition(target), direction);
      }
    }

    function resetGesture() {
      accumulatedDeltaRef.current = 0;
      if (gestureTimerRef.current) clearTimeout(gestureTimerRef.current);
      gestureTimerRef.current = null;
    }

    function handleWheel(e: WheelEvent) {
      if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) return;
      if (e.ctrlKey) return;

      const targets = getTargets();
      if (targets.length === 0) return;

      e.preventDefault();

      if (isAnimatingRef.current) {
        resetGesture();
        return;
      }

      accumulatedDeltaRef.current += e.deltaY;

      if (gestureTimerRef.current) clearTimeout(gestureTimerRef.current);
      gestureTimerRef.current = setTimeout(resetGesture, GESTURE_TIMEOUT_MS);

      if (Math.abs(accumulatedDeltaRef.current) < DELTA_THRESHOLD) return;

      const direction: 1 | -1 = accumulatedDeltaRef.current > 0 ? 1 : -1;
      resetGesture();

      // Anti-bounce: block opposite-direction during cooldown
      if (postSnapCooldownRef.current && lastSnapDirectionRef.current !== 0 && direction !== lastSnapDirectionRef.current) {
        return;
      }

      const currentIdx = getCurrentIndex();
      const maxIdx = targets.length - 1;
      const nextIdx = Math.max(-1, Math.min(maxIdx, currentIdx + direction));

      if (nextIdx === currentIdx) return;
      snapTo(nextIdx, direction);
    }

    container.addEventListener("wheel", handleWheel, { passive: false });

    return () => {
      container.removeEventListener("wheel", handleWheel);
      resetGesture();
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      if (postSnapTimerRef.current) clearTimeout(postSnapTimerRef.current);
    };
  }, []);
}
