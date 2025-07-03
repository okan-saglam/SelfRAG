import { create } from 'zustand';
import type { User } from '../types/api';
import { authService } from '../services/authService';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  
  login: async (username: string, password: string) => {
    try {
      set({ isLoading: true, error: null });
      
      const response = await authService.login({ username, password });
      
      set({ 
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error: any) {
      set({ 
        isLoading: false,
        error: error.response?.data?.detail || 'Failed to login',
        isAuthenticated: false,
        user: null,
      });
    }
  },
  
  register: async (username: string, email: string, password: string, fullName?: string) => {
    try {
      set({ isLoading: true, error: null });
      
      await authService.register({ 
        username, 
        email, 
        password, 
        full_name: fullName 
      });
      
      // Login after successful registration
      await get().login(username, password);
    } catch (error: any) {
      set({ 
        isLoading: false,
        error: error.response?.data?.detail || 'Failed to register',
      });
    }
  },
  
  logout: () => {
    authService.logout();
    set({ 
      user: null,
      isAuthenticated: false,
    });
  },
  
  loadUser: async () => {
    if (!authService.isLoggedIn()) {
      set({ isAuthenticated: false, user: null });
      return;
    }
    
    try {
      set({ isLoading: true, error: null });
      
      const user = await authService.getCurrentUser();
      
      set({ 
        user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error: any) {
      set({ 
        isLoading: false,
        error: error.response?.data?.detail || 'Failed to load user',
        isAuthenticated: false,
        user: null,
      });
      
      // Logout on failure
      authService.logout();
    }
  },
  
  clearError: () => {
    set({ error: null });
  },
}));
