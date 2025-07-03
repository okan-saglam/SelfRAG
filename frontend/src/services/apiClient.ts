import axios from 'axios';
import type { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';
import type { Token } from '../types/api';

// Default API configuration
const API_URL = 'http://localhost:8000';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to attach auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    
    if (token && config.headers) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };
    
    // Handle unauthorized errors (401)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Get refresh token
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (!refreshToken) {
          // No refresh token, logout
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.dispatchEvent(new Event('auth-logout'));
          return Promise.reject(error);
        }
        
        // Try to refresh the token
        const response = await axios.post(`${API_URL}/api/auth/refresh`, {
          refresh_token: refreshToken
        });
        
        const newToken = response.data as Token;
        
        // Update tokens in localStorage
        localStorage.setItem('access_token', newToken.access_token);
        localStorage.setItem('refresh_token', newToken.refresh_token);
        
        // Update auth header and retry original request
        if (originalRequest.headers) {
          originalRequest.headers['Authorization'] = `Bearer ${newToken.access_token}`;
        }
        
        return axios(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.dispatchEvent(new Event('auth-logout'));
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
