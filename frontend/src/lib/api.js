import axios from "axios";
import { getTokens, saveTokens, clearTokens } from "./session";

export const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

export const api = axios.create({ baseURL: `${API_URL}/api/v1` });

// 1) Attach the access token to every request.
api.interceptors.request.use((config) => {
  const tokens = getTokens();
  if (tokens?.access_token) config.headers.Authorization = `Bearer ${tokens.access_token}`;
  return config;
});

// 2) If a request fails with 401, try ONE refresh, then replay it.
//    `refreshing` is shared so ten parallel 401s trigger a single refresh call.
let refreshing = null;

function refreshTokens(refresh_token) {
  if (!refreshing) {
    refreshing = axios
      .post(`${API_URL}/api/v1/auth/refresh`, { refresh_token })
      .then((res) => {
        saveTokens(res.data);
        return res.data;
      })
      .finally(() => {
        refreshing = null;
      });
  }
  return refreshing;
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const tokens = getTokens();
    const isAuthCall = original?.url?.includes("/auth/");

    if (error.response?.status === 401 && tokens?.refresh_token && !original._retried && !isAuthCall) {
      original._retried = true;
      try {
        const fresh = await refreshTokens(tokens.refresh_token);
        original.headers.Authorization = `Bearer ${fresh.access_token}`;
        return api(original);
      } catch {
        clearTokens();
        window.dispatchEvent(new Event("nb:session-expired"));
      }
    }
    return Promise.reject(error);
  }
);

// Turn any API error into a sentence a human can read.
export function errorMessage(error, fallback = "Something went wrong. Please try again.") {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length) {
    return detail.map((d) => d.msg?.replace(/^Value error, /, "")).filter(Boolean).join(". ");
  }
  if (error?.code === "ERR_NETWORK") return "Can't reach the server. Check your connection.";
  return fallback;
}
