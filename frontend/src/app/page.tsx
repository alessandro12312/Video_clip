"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { GradientSpinner } from "@/components/shared/gradient-spinner";

const MIN_DISPLAY_TIME = 500;

export default function LandingPage() {
  const { isAuthenticated, isAuthenticating } = useAuth();
  const router = useRouter();
  const mountTime = useRef(Date.now());

  useEffect(() => {
    if (!isAuthenticating) {
      const elapsed = Date.now() - mountTime.current;
      const remaining = Math.max(0, MIN_DISPLAY_TIME - elapsed);
      const timer = setTimeout(() => {
        router.replace(isAuthenticated ? "/home" : "/login");
      }, remaining);
      return () => clearTimeout(timer);
    }
  }, [isAuthenticated, isAuthenticating, router]);

  return <GradientSpinner variant="full" size={32} />;
}
