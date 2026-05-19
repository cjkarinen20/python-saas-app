import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';

interface User {
  id: number;
  email: string;
  credits: number;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  signup: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('authToken'));
  const [refreshToken, setRefreshToken] = useState<string | null>(localStorage.getItem('refreshToken'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // ==== TODO: BACKEND API INTEGRATION - User Login ====
  // Implement login function that:
  // 1. Makes POST request to 'http://localhost:8000/auth/login'
  // 2. Sends { email, password } in request body
  // 3. On success, extract access_token and refresh_token from response
  // 4. Store tokens in state and localStorage
  // 5. If user data is in response, set it; otherwise call refreshUser()
  // 6. Return true on success, false on failure
  const login = async (email: string, password: string): Promise<boolean> => {
    // TODO: Implement API call to /auth/login
    try {
      const response = await fetch('http://localhost:8000/auth/login',{
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({email, password}),
      })

      if (response.ok) {
      const data = await response.json();
      setToken(data.access_token);
      setRefreshToken(data.refresh_token);
      localStorage.setItem('authToken', data.access_token);
      localStorage.setItem('refreshToken', data.refresh_token);
      // Set user data from login response
      if (data.user) {
        setUser(data.User);
      } else {
        await refreshUser();
      }
      return true;
    } else {
      console.error('Login Failed');
      return false;
    }
    } catch (error) {
      console.error('Login Error: ', error);
      return false;
    }
  };

  // ==== TODO: BACKEND API INTEGRATION - User Signup ====
  // Implement signup function that:
  // 1. Makes POST request to 'http://localhost:8000/auth/signup'
  // 2. Sends { email, password } in request body
  // 3. Returns true on success, false on failure
  const signup = async (email: string, password: string): Promise<boolean> => {
    // TODO: Implement API call to /auth/signup
    try {
      const response = await fetch('http://localhost:8000/auth/signup',{
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({email, password}),
      })
      if (response.ok) {
      return true;
    } else {
      console.error('Signup Failed');
      return false;
    }
    } catch (error) {
      console.error('Signup Error: ', error);
      return false;
    }
  };

  // ==== TODO: BACKEND API INTEGRATION - Refresh Access Token ====
  // Implement token refresh function that:
  // 1. Makes POST request to 'http://localhost:8000/auth/refresh'
  // 2. Sends { refresh_token: refreshToken } in request body
  // 3. On success, update access_token in state and localStorage
  // 4. On failure, clear all auth data (user is logged out)
  // 5. Returns true on success, false on failure
  const refreshAccessToken = useCallback(async (): Promise<boolean> => {
    if (!refreshToken) return false;

    // TODO: Implement API call to /auth/refresh
    console.log('Token refresh called - API integration needed');
    return false;
  }, [refreshToken]);

  // ==== TODO: BACKEND API INTEGRATION - Refresh User Data ====
  // Implement user data fetch function that:
  // 1. Makes GET request to 'http://localhost:8000/auth/me'
  // 2. Includes 'Authorization: Bearer {token}' header
  // 3. On success, update user state with returned data
  // 4. On 401 error, attempt to refresh token using refreshAccessToken()
  // 5. If refresh fails, clear all auth data
  const refreshUser = useCallback(async (): Promise<void> => {
    if (!token) return;

    // TODO: Implement API call to /auth/me
    console.log('Refresh user called - API integration needed');
  }, [token, refreshAccessToken]);

  useEffect(() => {
    if (token) {
      refreshUser();
    }
  }, [token, refreshUser]);

  // Initialize authentication state on app load
  useEffect(() => {
    const initializeAuth = async () => {
      setIsLoading(true);
      const storedToken = localStorage.getItem('authToken');
      const storedRefreshToken = localStorage.getItem('refreshToken');

      if (storedToken && storedRefreshToken) {
        setToken(storedToken);
        setRefreshToken(storedRefreshToken);
        // refreshUser will be called by the effect above when token changes
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const logout = (): void => {
    setUser(null);
    setToken(null);
    setRefreshToken(null);
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
  };

  const value: AuthContextType = {
    user,
    token,
    isLoading,
    login,
    signup,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthProvider;