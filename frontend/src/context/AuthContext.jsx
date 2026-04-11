import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for saved token on mount
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');

    if (savedToken && savedUser) {
      try {
        const parsed = JSON.parse(savedUser);
        setUser(parsed);
      } catch (e) {
        console.error("Failed to parse user from local storage");
      }
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const data = await authAPI.login(email, password);
      
      const userData = {
        id: data.user.id,
        name: data.user.name,
        email: data.user.email,
        role: data.role || data.user.role,
        business_id: data.business_id || data.user.business_id || null, // No more defaulting to 1
        avatar: data.user.name.substring(0, 2).toUpperCase()
      };

      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      setUser(userData);
      return { success: true, role: userData.role };
    } catch (error) {
      return { success: false, message: error.message };
    }
  };

  const signup = async (userData) => {
    try {
      const data = await authAPI.signup(userData);
      return { success: true, user_id: data.user_id };
    } catch (error) {
      return { success: false, message: error.message };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const refreshUser = async () => {
     try {
       const token = localStorage.getItem('token');
       if (!token) return;
       
       const response = await fetch('/auth/me', {
         headers: { 'Authorization': `Bearer ${token}` }
       });
       
       if (response.ok) {
         const data = await response.json();
         const userData = {
           id: data.id,
           name: data.name,
           email: data.email,
           role: data.role,
           business_id: data.business_id,
           avatar: data.name.substring(0, 2).toUpperCase()
         };
         localStorage.setItem('user', JSON.stringify(userData));
         setUser(userData);
       }
     } catch (e) {
       console.error("Failed to refresh user profile", e);
     }
  };

  return (
    <AuthContext.Provider value={{ user, login, signup, logout, loading, refreshUser }}>
      {!loading && children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
