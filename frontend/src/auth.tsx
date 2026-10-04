import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { api, ApiResponse, getToken, setToken, User } from "./api";

interface AuthCtx {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refresh: () => Promise<void>;
}

const Ctx = createContext<AuthCtx>(null!);
export const useAuth = () => useContext(Ctx);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(!!getToken());

  const refresh = async () => {
    const res = await api<ApiResponse<User>>("/users/me");
    setUser(res.data);
  };

  useEffect(() => {
    if (!getToken()) return;
    refresh()
      .catch(() => setToken(null))
      .finally(() => setLoading(false));
  }, []);

  const login = async (email: string, password: string) => {
    const res = await api<ApiResponse<{ access_token: string }>>("/auth/login", {
      method: "POST",
      body: { email, password },
    });
    setToken(res.data.access_token);
    await refresh();
  };

  const logout = () => {
    api("/auth/logout", { method: "POST" }).catch(() => {});
    setToken(null);
    setUser(null);
  };

  return (
    <Ctx.Provider value={{ user, loading, login, logout, refresh }}>
      {children}
    </Ctx.Provider>
  );
}
