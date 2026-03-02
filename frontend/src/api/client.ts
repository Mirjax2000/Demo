/**
 * API klient — axios instance s JWT v httpOnly cookies.
 *
 * V dev mode se používá Vite proxy (vite.config.ts) → requesty jdou
 * přes localhost:5173/api/... (same-origin → cookies fungují).
 * V produkci VITE_API_URL ukazuje přímo na backend.
 */
import axios from "axios";

/**
 * Dev: VITE_API_URL prázdný → baseURL = "/api/v1" (same-origin, Vite proxy).
 * Prod: VITE_API_URL = "https://example.com" → baseURL = "https://example.com/api/v1".
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || "";

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true, // posílá httpOnly cookies automaticky
});

/** Endpointy, které NEMAJÍ spouštět refresh retry (zabránění smyčce). */
const NO_RETRY_URLS = ["/auth/login/", "/auth/refresh/", "/auth/me/"];

let isRefreshing = false;
let refreshQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

function processQueue(success: boolean) {
  refreshQueue.forEach(({ resolve, reject }) =>
    success ? resolve() : reject()
  );
  refreshQueue = [];
}

// ── Response interceptor: refresh token při 401 ──
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const url: string = originalRequest?.url ?? "";

    // Neretryovat auth endpointy — zabránění infinite loop
    const isAuthUrl = NO_RETRY_URLS.some((p) => url.endsWith(p));

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !isAuthUrl
    ) {
      originalRequest._retry = true;

      // Pokud už probíhá refresh, čekáme na výsledek
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshQueue.push({ resolve, reject });
        }).then(() => api(originalRequest));
      }

      isRefreshing = true;

      try {
        await api.post("/auth/refresh/", {});
        processQueue(true);
        return api(originalRequest);
      } catch {
        processQueue(false);
        return Promise.reject(error);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
