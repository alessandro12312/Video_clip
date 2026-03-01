"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/providers/auth-provider";
import { useLoginTransition } from "@/providers/login-transition-provider";
import { GradientSpinner } from "@/components/shared/gradient-spinner";
import type { ApiError } from "@/types";
import { AxiosError } from "axios";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [showTransition, setShowTransition] = useState(false);
  const { login } = useAuth();
  const { startLoginTransition } = useLoginTransition();
  const router = useRouter();
  const usernameRef = useRef<HTMLInputElement>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setIsLoggingIn(true);

    try {
      await login(username, password);
      // Cattura la posizione del logo auth PRIMA di avviare la transizione
      const authLogo = document.getElementById("auth-brand-logo");
      const rect = authLogo?.getBoundingClientRect();
      const source = rect
        ? { top: rect.top, left: rect.left, width: rect.width, height: rect.height }
        : undefined;

      // Nascondi logo + sottotitolo per evitare che restino visibili sotto l'overlay
      if (authLogo?.parentElement) authLogo.parentElement.style.opacity = "0";

      // Avvia la transizione cinematografica nel root layout (sopravvive al cambio route)
      setShowTransition(true);
      startLoginTransition(source);

      // Ritarda la navigazione per dare tempo all'overlay di diventare opaco
      // (evita flash del layout che cambia sotto il bg semi-trasparente)
      setTimeout(() => router.replace("/home"), 400);
    } catch (err) {
      if (err instanceof AxiosError && err.response?.data) {
        const data = err.response.data as ApiError;
        setError(data.detail || "Credenziali non valide.");
      } else {
        setError("Errore di connessione. Riprova.");
      }
      setIsLoggingIn(false);
      usernameRef.current?.focus();
    }
  }

  return (
    <AnimatePresence mode="wait">
      {!showTransition && (
        <motion.div
          key="login-form"
          exit={{
            opacity: 0,
            scale: 0.95,
            filter: "blur(8px)",
            transition: { duration: 0.4 },
          }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="text-center text-xl">Accedi</CardTitle>
            </CardHeader>
            <form onSubmit={handleSubmit}>
              <CardContent className="space-y-4">
                {error && (
                  <p
                    id="login-error"
                    role="alert"
                    className="text-sm text-destructive text-center"
                  >
                    {error}
                  </p>
                )}
                <div className="space-y-2">
                  <Label htmlFor="username">Username</Label>
                  <Input
                    ref={usernameRef}
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Il tuo username"
                    required
                    autoFocus
                    aria-invalid={!!error || undefined}
                    aria-describedby={error ? "login-error" : undefined}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="La tua password"
                    required
                    aria-invalid={!!error || undefined}
                    aria-describedby={error ? "login-error" : undefined}
                  />
                </div>
              </CardContent>
              <CardFooter className="flex flex-col gap-3">
                <Button
                  type="submit"
                  className="w-full gradient-bg"
                  disabled={isLoggingIn}
                  aria-label={isLoggingIn ? "Accesso in corso" : undefined}
                >
                  {isLoggingIn ? <GradientSpinner size={20} /> : "Accedi"}
                </Button>
                <p className="text-sm text-muted-foreground">
                  Non hai un account?{" "}
                  <Link href="/registrati" className="text-primary hover:underline">
                    Registrati
                  </Link>
                </p>
              </CardFooter>
            </form>
          </Card>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
