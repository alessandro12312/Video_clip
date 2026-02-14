"use client";

import { cn } from "@/lib/utils";

interface GradientSpinnerProps {
  size?: number;
  className?: string;
}

export function GradientSpinner({ size = 32, className }: GradientSpinnerProps) {
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
