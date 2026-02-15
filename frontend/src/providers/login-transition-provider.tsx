"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import { LoginTransitionOverlay } from "@/components/shared/login-transition-overlay";

interface LoginTransitionContextValue {
  startLoginTransition: () => void;
}

const LoginTransitionContext =
  createContext<LoginTransitionContextValue | null>(null);

export function LoginTransitionProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [isActive, setIsActive] = useState(false);

  const startLoginTransition = useCallback(() => {
    setIsActive(true);
  }, []);

  const handleTransitionEnd = useCallback(() => {
    setIsActive(false);
  }, []);

  return (
    <LoginTransitionContext.Provider value={{ startLoginTransition }}>
      {children}
      <LoginTransitionOverlay
        isActive={isActive}
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
