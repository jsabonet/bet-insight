import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const response = await authAPI.getProfile();
        setUser(response.data);
      } catch (error) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    }
    setLoading(false);
  };

  const login = async (username, password) => {
    const response = await authAPI.login({ username, password });
    const { access, refresh } = response.data;
    
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    
    const profileResponse = await authAPI.getProfile();
    setUser(profileResponse.data);
    
    return profileResponse.data;
  };

  const register = async (data) => {
    const response = await authAPI.register(data);
    const { tokens, user: newUser } = response.data;
    
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    
    setUser(newUser);
    return newUser;
  };

  const logout = () => {
    authAPI.logout();
    setUser(null);
  };

  const updateUser = async (data) => {
    const response = await authAPI.updateProfile(data);
    setUser(response.data);
    return response.data;
  };

  const refreshProfile = async () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const response = await authAPI.getProfile();
        setUser(response.data);
        return response.data;
      } catch (error) {
        console.error('Erro ao atualizar perfil:', error);
      }
    }
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    updateUser,
    refreshProfile,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
