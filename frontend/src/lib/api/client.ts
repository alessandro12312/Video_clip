import axios from "axios";
import { toast } from "sonner";
import { API_BASE_URL } from "@/lib/constants";

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: { "Content-Type": "application/json" },
});

// In-memory token storage (access MAI in localStorage — by design)
let accessToken: string | null = null;
let refreshTokenValue: string | null = null;

// Mutex/queue pattern per gestione refresh concorrente
let isRefreshing = false;
let failedQueue: {
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}[] = [];

function processQueue(error: unknown, token: string | null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token!);
    }
  });
  failedQueue = [];
}

function setSessionCookie() {
  if (typeof document !== "undefined") {
    const secure = window.location.protocol === "https:" ? "; Secure" : "";
    document.cookie = `session_active=1; path=/; max-age=86400; SameSite=Lax${secure}`;
  }
}

function clearSessionCookie() {
  if (typeof document !== "undefined") {
    document.cookie = "session_active=; path=/; max-age=0";
  }
}

export function setTokens(access: string, refresh: string) {
  accessToken = access;
  refreshTokenValue = refresh;
  if (typeof window !== "undefined") {
    localStorage.setItem("refresh_token", refresh);
    setSessionCookie();
  }
}

export function getAccessToken(): string | null {
  return accessToken;
}

export function getRefreshToken(): string | null {
  if (refreshTokenValue) return refreshTokenValue;
  if (typeof window !== "undefined") {
    refreshTokenValue = localStorage.getItem("refresh_token");
  }
  return refreshTokenValue;
}

export function clearTokens() {
  accessToken = null;
  refreshTokenValue = null;
  if (typeof window !== "undefined") {
    localStorage.removeItem("refresh_token");
    clearSessionCookie();
  }
}

// Request interceptor: attach JWT
apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: handle 401 con mutex/queue pattern
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    const currentRefresh = getRefreshToken();
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      currentRefresh
    ) {
      if (isRefreshing) {
        return new Promise<string>((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return apiClient(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const response = await axios.post(
          `${API_BASE_URL}/api/token/refresh/`,
          { refresh: currentRefresh }
        );
        const { access, refresh: newRefresh } = response.data;

        setTokens(access, newRefresh || currentRefresh);
        processQueue(null, access);
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        clearTokens();
        toast.warning("Sessione scaduta, effettua di nuovo l'accesso");
        if (typeof window !== "undefined") {
          window.dispatchEvent(new Event("auth:logout"));
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);
