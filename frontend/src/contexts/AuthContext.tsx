import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { api, authApi } from '@/services/api';

interface AuthUser {
  id: string;
  email: string;
}

interface AuthContextType {
  user: AuthUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = api.getToken();
    if (token) {
      // Token exists — decode basic info from localStorage
      const saved = localStorage.getItem('pos-user');
      if (saved) {
        try {
          setUser(JSON.parse(saved));
        } catch {
          localStorage.removeItem('pos-user');
        }
      }
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const { access_token } = await authApi.login({ email, password });
    api.setToken(access_token);
    // Decode user from token payload (sub = user id)
    const base64Url = access_token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const payload = JSON.parse(atob(base64));
    const userData = { id: payload.sub, email };
    setUser(userData);
    localStorage.setItem('pos-user', JSON.stringify(userData));
  }, []);

  const register = useCallback(async (email: string, password: string) => {
    await authApi.register({ email, password });
    await login(email, password);
  }, [login]);

  const logout = useCallback(() => {
    api.setToken(null);
    setUser(null);
    localStorage.removeItem('pos-user');
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
