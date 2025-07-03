import apiClient from './apiClient';
import type { 
  UserLogin, 
  UserRegister, 
  Token, 
  User, 
  UserUpdate, 
  TokenRefresh 
} from '../types/api';

export const authService = {
  // Register a new user
  register: async (userData: UserRegister): Promise<User> => {
    const response = await apiClient.post<User>('/api/auth/register', userData);
    return response.data;
  },
  
  // Login user
  login: async (credentials: UserLogin): Promise<Token> => {
    const response = await apiClient.post<Token>('/api/auth/login', credentials);
    
    // Store tokens in localStorage
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);
    
    return response.data;
  },
  
  // Get current user information
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/api/auth/me');
    return response.data;
  },
  
  // Update user information
  updateUser: async (updates: UserUpdate): Promise<User> => {
    const response = await apiClient.put<User>('/api/auth/me', updates);
    return response.data;
  },
  
  // Refresh access token
  refreshToken: async (token: TokenRefresh): Promise<Token> => {
    const response = await apiClient.post<Token>('/api/auth/refresh', token);
    
    // Update tokens in localStorage
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);
    
    return response.data;
  },
  
  // Logout user
  logout: (): void => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.dispatchEvent(new Event('auth-logout'));
  },
  
  // Check if user is logged in
  isLoggedIn: (): boolean => {
    return !!localStorage.getItem('access_token');
  }
};
