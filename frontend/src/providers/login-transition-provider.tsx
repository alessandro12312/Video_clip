"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  useRef,
  type ReactNode,
} from "react";
import { LoginTransitionOverlay } from "@/components/shared/login-transition-overlay";

export interface SourceRect {
  top: number;
  left: number;
  width: number;
  height: number;
}

interface LoginTransitionContextValue {
  startLoginTransition: (sourceRect?: SourceRect) => void;
}

const LoginTransitionContext =
  createContext<LoginTransitionContextValue | null>(null);

export function LoginTransitionProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [isActive, setIsActive] = useState(false);
  const sourceRectRef = useRef<SourceRect | null>(null);

  const startLoginTransition = useCallback((sourceRect?: SourceRect) => {
    sourceRectRef.current = sourceRect ?? null;
    setIsActive(true);
  }, []);

  const handleTransitionEnd = useCallback(() => {
    sourceRectRef.current = null;
    setIsActive(false);
  }, []);

  return (
    <LoginTransitionContext.Provider value={{ startLoginTransition }}>
      {children}
      <LoginTransitionOverlay
        isActive={isActive}
        sourceRect={sourceRectRef.current}
        onTransitionEnd={handleTransitionEnd}
      />
    </LoginTransitionContext.Provider>
  );
}

export function useLoginTransition() {
  const context = useContext(LoginTransitionContext);
  if (!context) {
    throw new Error(
      "useLoginTransition deve essere usato dentro LoginTransitionProvider"
    );
  }
  return context;
}
