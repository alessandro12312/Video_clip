"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import { jwtDecode } from "jwt-decode";
import type { User } from "@/types";
import { authApi } from "@/lib/api/auth";
import {
  setTokens,
  getRefreshToken,
  clearTokens,
} from "@/lib/api/client";

interface JwtPayload {
  user_id: number;
  exp: number;
}

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isAuthenticating: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (
    username: string,
    email: string,
    password: string
  ) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticating, setIsAuthenticating] = useState(true);
  const router = useRouter();

  const fetchUser = useCallback(async (token: string) => {
    try {
      const decoded = jwtDecode<JwtPayload>(token);
      const userData = await authApi.getCurrentUser(decoded.user_id);
      setUser(userData);
    } catch {
      clearTokens();
      setUser(null);
    }
  }, []);

  const logout = useCallback(() => {
    clearTokens();
    setUser(null);
    router.replace("/login");
  }, [router]);

  // On mount: restore session via refresh token (access è memory-only, perso al reload)
  useEffect(() => {
    const init = async () => {
      const refresh = getRefreshToken();

      if (refresh) {
        try {
          const data = await authApi.refreshToken(refresh);
          setTokens(data.access, data.refresh || refresh);
          await fetchUser(data.access);
        } catch {
          clearTokens();
        }
      }
      setIsAuthenticating(false);
    };

    init();
  }, [fetchUser]);

  // Listener per force-logout da client.ts (modulo vanilla, no React context)
  useEffect(() => {
    window.addEventListener("auth:logout", logout);
    return () => window.removeEventListener("auth:logout", logout);
  }, [logout]);

  const login = useCallback(
    async (username: string, password: string) => {
      const tokens = await authApi.login(username, password);
      setTokens(tokens.access, tokens.refresh);
      await fetchUser(tokens.access);
    },
    [fetchUser]
  );

  const register = useCallback(
    async (username: string, email: string, password: string) => {
      await authApi.register({ username, email, password });
      await login(username, password);
    },
    [login]
  );

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isAuthenticating,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth deve essere usato dentro AuthProvider");
  }
  return context;
}
