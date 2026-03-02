/**
 * Auth Context — JWT v httpOnly cookies.
 *
 * Tokeny nejsou v JS paměti (XSS-safe).
 * Stav přihlášení zjišťujeme voláním /auth/me/.
 */
import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import { authApi } from "../api";
import type { User } from "../types";

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchUser = useCallback(async () => {
    try {
      const { data } = await authApi.me();
      setUser(data);
    } catch {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const login = async (username: string, password: string) => {
    await authApi.login(username, password);
    // Cookie je set automaticky — načti uživatele.
    // Chyby propagujeme do volajícího (LoginPage catch block).
    const { data } = await authApi.me();
    setUser(data);
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch {
      // Ignorujeme chyby při logoutu
    }
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

const ROLE_LEVEL: Record<string, number> = {
  ReadOnly: 0,
  Operator: 1,
  Manager: 2,
  Admin: 3,
};

/** RBAC helpers derived from user.role */
export function useRole() {
  const { user } = useAuth();
  const role = user?.role ?? "ReadOnly";
  const level = ROLE_LEVEL[role] ?? 0;
  return {
    role,
    /** Operator+ — can create / edit */
    canWrite: level >= 1,
    /** Manager+ — can delete */
    canDelete: level >= 2,
    /** Admin — full access */
    isAdmin: level >= 3,
  };
}
