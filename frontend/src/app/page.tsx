"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/providers/auth-provider";
import { GradientSpinner } from "@/components/shared/gradient-spinner";

export default function LandingPage() {
  const { isAuthenticated, isAuthenticating } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticating) {
      router.replace(isAuthenticated ? "/home" : "/login");
    }
  }, [isAuthenticated, isAuthenticating, router]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <GradientSpinner size={48} />
    </div>
  );
}
