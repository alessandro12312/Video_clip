"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import { jwtDecode } from "jwt-decode";
import type { User } from "@/types";
import { authApi } from "@/lib/api/auth";
import {
  setTokens,
  getAccessToken,
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
  isLoading: boolean;
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
  const [isLoading, setIsLoading] = useState(true);

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

  // On mount: restore session from stored tokens
  useEffect(() => {
    const init = async () => {
      const token = getAccessToken();
      const refresh = getRefreshToken();

      if (token) {
        try {
          const decoded = jwtDecode<JwtPayload>(token);
          const isExpired = decoded.exp * 1000 < Date.now();

          if (isExpired && refresh) {
            const { access } = await authApi.refreshToken(refresh);
            setTokens(access, refresh);
            await fetchUser(access);
          } else if (!isExpired) {
            await fetchUser(token);
          } else {
            clearTokens();
          }
        } catch {
          clearTokens();
        }
      }
      setIsLoading(false);
    };

    init();
  }, [fetchUser]);

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
      // Auto-login after registration
      await login(username, password);
    },
    [login]
  );

  const logout = useCallback(() => {
    clearTokens();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
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
