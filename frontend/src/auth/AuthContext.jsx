import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api";
import { clearTokens, getTokens, saveTokens, TOKEN_KEY } from "../lib/session";

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const queryClient = useQueryClient();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(getTokens())); // only "loading" if there is a session to restore

  const loadUser = useCallback(async () => {
    const { data } = await api.get("/auth/me");
    setUser(data);
    return data;
  }, []);

  // On first load: if tokens exist, find out who they belong to.
  useEffect(() => {
    if (!getTokens()) return;
    loadUser()
      .catch(() => clearTokens())
      .finally(() => setLoading(false));
  }, [loadUser]);

  const login = useCallback(
    async (email, password) => {
      const { data } = await api.post("/auth/login", { email, password });
      saveTokens(data);
      return loadUser();
    },
    [loadUser]
  );

  const register = useCallback(
    async (name, email, password) => {
      await api.post("/auth/register", { name, email, password });
      return login(email, password);
    },
    [login]
  );

  const logout = useCallback(async () => {
    const tokens = getTokens();
    try {
      // Best effort: tell the server to revoke the tokens, but never trap the user if it fails.
      await api.post("/auth/logout", { refresh_token: tokens?.refresh_token });
    } catch {
      /* ignore */
    }
    clearTokens();
    setUser(null);
    queryClient.clear(); // so the next person never glimpses this person's cached data
  }, [queryClient]);

  // The API client fires this when a refresh fails; another tab clearing tokens triggers `storage`.
  useEffect(() => {
    const endSession = () => {
      setUser(null);
      queryClient.clear();
    };
    const onStorage = (e) => {
      if (e.key === TOKEN_KEY && e.newValue === null) endSession();
    };
    window.addEventListener("nb:session-expired", endSession);
    window.addEventListener("storage", onStorage);
    return () => {
      window.removeEventListener("nb:session-expired", endSession);
      window.removeEventListener("storage", onStorage);
    };
  }, [queryClient]);

  const value = useMemo(
    () => ({
      user,
      loading,
      login,
      register,
      logout,
      refreshUser: loadUser,
      isAdmin: user?.role === "admin",
      canManage: user?.role === "admin" || Boolean(user?.is_group_owner),
    }),
    [user, loading, login, register, logout, loadUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
