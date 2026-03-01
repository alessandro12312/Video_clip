"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/providers/auth-provider";
import { PageLoader } from "@/components/shared/page-loader";

export default function ProfiloRedirect() {
  const router = useRouter();
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      router.replace(`/profilo/${user.username}`);
    }
  }, [user, router]);

  return <PageLoader />;
}
