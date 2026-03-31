import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { api, type User } from "../api/client";

interface AuthState {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (
    username: string,
    email: string,
    password: string,
    roles: string[]
  ) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState>(null!);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      api
        .get<User>("/auth/me")
        .then(setUser)
        .catch(() => localStorage.removeItem("token"))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (username: string, password: string) => {
    const res = await api.post<{ access_token: string }>("/auth/login", {
      username,
      password,
    });
    localStorage.setItem("token", res.access_token);
    const me = await api.get<User>("/auth/me");
    setUser(me);
  };

  const register = async (
    username: string,
    email: string,
    password: string,
    roles: string[]
  ) => {
    const res = await api.post<{ access_token: string }>("/auth/register", {
      username,
      email,
      password,
      roles,
    });
    localStorage.setItem("token", res.access_token);
    const me = await api.get<User>("/auth/me");
    setUser(me);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
