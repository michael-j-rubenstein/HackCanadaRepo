import React, { createContext, useContext, useState, useCallback, useRef } from "react";
import Auth0 from "react-native-auth0";

const DOMAIN = process.env.EXPO_PUBLIC_AUTH0_DOMAIN!;
const CLIENT_ID = process.env.EXPO_PUBLIC_AUTH0_CLIENT_ID!;
const REALM = "Username-Password-Authentication";

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
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const auth0Ref = useRef(new Auth0({ domain: DOMAIN, clientId: CLIENT_ID }));

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true);
    try {
      const credentials = await auth0Ref.current.auth.passwordRealm({
        username: email,
        password,
        realm: REALM,
        scope: "openid profile email",
      });
      setUser(decodeIdToken(credentials.idToken));
    } finally {
      setLoading(false);
    }
  }, []);

  const signUp = useCallback(async (email: string, password: string) => {
    setLoading(true);
    try {
      await auth0Ref.current.auth.createUser({
        email,
        password,
        connection: REALM,
      });
      // Auto-login after signup
      const credentials = await auth0Ref.current.auth.passwordRealm({
        username: email,
        password,
        realm: REALM,
        scope: "openid profile email",
      });
      setUser(decodeIdToken(credentials.idToken));
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
