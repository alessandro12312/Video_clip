"use client";

import { useEffect, useRef } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { cn } from "@/lib/utils";

interface GradientSpinnerProps {
  size?: number;
  className?: string;
  variant?: "full" | "inline";
  onAnimationReady?: () => void;
}

function SpinnerRing({ size = 32, className }: { size?: number; className?: string }) {
  return (
    <div
      className={cn("relative", className)}
      style={{ width: size, height: size }}
    >
      <div
        className="absolute inset-0 animate-spin-gradient rounded-full"
        style={{
          background: `conic-gradient(from 0deg, var(--gradient-start), var(--gradient-end), transparent)`,
          mask: "radial-gradient(farthest-side, transparent calc(100% - 3px), #fff calc(100% - 3px))",
          WebkitMask:
            "radial-gradient(farthest-side, transparent calc(100% - 3px), #fff calc(100% - 3px))",
        }}
      />
    </div>
  );
}

export function GradientSpinner({
  size = 32,
  className,
  variant = "inline",
  onAnimationReady,
}: GradientSpinnerProps) {
  const readyFired = useRef(false);
  const prefersReducedMotion = useReducedMotion();

  useEffect(() => {
    if (variant === "full" && onAnimationReady && !readyFired.current) {
      readyFired.current = true;
      onAnimationReady();
    }
  }, [variant, onAnimationReady]);

  if (variant === "inline") {
    return <SpinnerRing size={size} className={className} />;
  }

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-background"
      aria-label="Caricamento in corso"
    >
      <motion.h1
        className="gradient-text text-4xl font-bold tracking-tight sm:text-5xl"
        animate={prefersReducedMotion ? {} : { scale: [1, 1.05, 1] }}
        transition={
          prefersReducedMotion
            ? undefined
            : { duration: 1.5, repeat: Infinity, ease: "easeInOut" }
        }
      >
        Video_clip
      </motion.h1>

      <div className="mt-6">
        <SpinnerRing size={size} />
      </div>
    </div>
  );
}
