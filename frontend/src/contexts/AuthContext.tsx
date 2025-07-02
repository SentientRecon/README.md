import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import toast from 'react-hot-toast';
import { User, ApiResponse } from '../types';
import { setSecureStorage, getSecureStorage, removeSecureStorage } from '../lib/utils';
import { authApi } from '../services/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string, mfaCode?: string) => Promise<boolean>;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
  updateUser: (userData: Partial<User>) => void;
  hasPermission: (resource: string, action: string) => boolean;
  requiresMFA: boolean;
  isSessionValid: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [requiresMFA, setRequiresMFA] = useState(false);
  const [isSessionValid, setIsSessionValid] = useState(false);

  // Check for existing session on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = getSecureStorage<string>('auth_token');
        const storedUser = getSecureStorage<User>('user_data');
        
        if (token && storedUser) {
          // Validate token with backend
          const isValid = await validateToken(token);
          if (isValid) {
            setUser(storedUser);
            setIsSessionValid(true);
            // Start session refresh timer
            startTokenRefreshTimer();
          } else {
            // Invalid token, clear storage
            clearAuthData();
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        clearAuthData();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  // Session timeout and refresh management
  useEffect(() => {
    let sessionTimer: NodeJS.Timeout;
    let warningTimer: NodeJS.Timeout;

    if (user && isSessionValid) {
      // Session warning at 25 minutes (5 min before 30 min timeout)
      warningTimer = setTimeout(() => {
        toast('Session expires in 5 minutes. Please save your work.', {
          icon: '⚠️',
          duration: 10000,
        });
      }, 25 * 60 * 1000);

      // Auto logout after 30 minutes of inactivity
      sessionTimer = setTimeout(() => {
        toast.error('Session expired due to inactivity');
        logout();
      }, 30 * 60 * 1000);
    }

    return () => {
      clearTimeout(sessionTimer);
      clearTimeout(warningTimer);
    };
  }, [user, isSessionValid]);

  const validateToken = async (token: string): Promise<boolean> => {
    try {
      const response = await authApi.validateToken(token);
      return response.success;
    } catch (error) {
      return false;
    }
  };

  const startTokenRefreshTimer = () => {
    // Refresh token every 20 minutes
    setInterval(async () => {
      const success = await refreshToken();
      if (!success) {
        toast.error('Session expired. Please log in again.');
        logout();
      }
    }, 20 * 60 * 1000);
  };

  const login = async (username: string, password: string, mfaCode?: string): Promise<boolean> => {
    try {
      setLoading(true);
      
      const response = await authApi.login(username, password, mfaCode);
      
      if (response.success) {
        if (response.data.requiresMFA && !mfaCode) {
          setRequiresMFA(true);
          setLoading(false);
          return false; // Need MFA code
        }

        const { user: userData, token, refreshToken: refresh } = response.data;
        
        // Store auth data securely
        setSecureStorage('auth_token', token);
        setSecureStorage('refresh_token', refresh);
        setSecureStorage('user_data', userData);
        
        setUser(userData);
        setIsSessionValid(true);
        setRequiresMFA(false);
        
        // Start token refresh timer
        startTokenRefreshTimer();
        
        toast.success(`Welcome back, ${userData.username}!`);
        return true;
      } else {
        toast.error(response.message || 'Login failed');
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      toast.error('Login failed. Please check your credentials.');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    try {
      // Call logout endpoint to invalidate token server-side
      const token = getSecureStorage<string>('auth_token');
      if (token) {
        authApi.logout(token).catch(console.error);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearAuthData();
      toast.success('Logged out successfully');
    }
  };

  const refreshToken = async (): Promise<boolean> => {
    try {
      const refresh = getSecureStorage<string>('refresh_token');
      if (!refresh) return false;

      const response = await authApi.refreshToken(refresh);
      
      if (response.success) {
        const { token, refreshToken: newRefresh } = response.data;
        
        setSecureStorage('auth_token', token);
        setSecureStorage('refresh_token', newRefresh);
        
        setIsSessionValid(true);
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Token refresh error:', error);
      return false;
    }
  };

  const updateUser = (userData: Partial<User>) => {
    if (user) {
      const updatedUser = { ...user, ...userData };
      setUser(updatedUser);
      setSecureStorage('user_data', updatedUser);
    }
  };

  const hasPermission = (resource: string, action: string): boolean => {
    if (!user) return false;
    
    return user.permissions.some(permission => 
      permission.resource === resource && permission.action === action
    ) || user.role.permissions.some(permission =>
      permission.resource === resource && permission.action === action
    );
  };

  const clearAuthData = () => {
    removeSecureStorage('auth_token');
    removeSecureStorage('refresh_token');
    removeSecureStorage('user_data');
    setUser(null);
    setIsSessionValid(false);
    setRequiresMFA(false);
  };

  const value: AuthContextType = {
    user,
    loading,
    login,
    logout,
    refreshToken,
    updateUser,
    hasPermission,
    requiresMFA,
    isSessionValid,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};