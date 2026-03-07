import React, { createContext, useContext, useState, useCallback } from "react";

const DOMAIN = process.env.EXPO_PUBLIC_AUTH0_DOMAIN;
const CLIENT_ID = process.env.EXPO_PUBLIC_AUTH0_CLIENT_ID;
const SKIP_AUTH = process.env.EXPO_PUBLIC_SKIP_AUTH === "true";

function decodeIdToken(idToken: string): User {
  const payload = idToken.split(".")[1];
  const decoded = JSON.parse(atob(payload));
  return {
    sub: decoded.sub,
    email: decoded.email,
    name: decoded.name || decoded.nickname || decoded.email,
  };
}

interface User {
  email: string;
  name?: string;
  sub?: string;
  [key: string]: any;
}

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  loading: false,
  login: async () => {},
  signUp: async () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(
    SKIP_AUTH ? { email: "dev@local", name: "Dev User" } : null
  );
  const [loading, setLoading] = useState(false);

  const login = useCallback(async (email: string, password: string) => {
    if (SKIP_AUTH) {
      setUser({ email, name: email.split("@")[0] });
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(`https://${DOMAIN}/oauth/token`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          grant_type: "password",
          client_id: CLIENT_ID,
          username: email,
          password,
          scope: "openid profile email",
          connection: "Username-Password-Authentication",
        }),
      });
      const text = await response.text();
      let data: any;
      try { data = JSON.parse(text); } catch { data = {}; }
      if (!response.ok) throw new Error(data.error_description || data.error || text || "Login failed");
      setUser(decodeIdToken(data.id_token));
    } finally {
      setLoading(false);
    }
  }, []);

  const signUp = useCallback(async (email: string, password: string) => {
    if (SKIP_AUTH) {
      setUser({ email, name: email.split("@")[0] });
      return;
    }
    setLoading(true);
    try {
      const signUpRes = await fetch(`https://${DOMAIN}/dbconnections/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          client_id: CLIENT_ID,
          email,
          password,
          connection: "Username-Password-Authentication",
        }),
      });
      const signUpText = await signUpRes.text();
      let signUpData: any;
      try { signUpData = JSON.parse(signUpText); } catch { signUpData = {}; }
      if (!signUpRes.ok) throw new Error(signUpData.description || signUpData.error || signUpText || "Sign up failed");

      // Auto-login after signup
      const loginRes = await fetch(`https://${DOMAIN}/oauth/token`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          grant_type: "password",
          client_id: CLIENT_ID,
          username: email,
          password,
          scope: "openid profile email",
          connection: "Username-Password-Authentication",
        }),
      });
      const loginText = await loginRes.text();
      let loginData: any;
      try { loginData = JSON.parse(loginText); } catch { loginData = {}; }
      if (!loginRes.ok) throw new Error(loginData.error_description || "Login failed");
      setUser(decodeIdToken(loginData.id_token));
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, signUp, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
