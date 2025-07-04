import apiClient from './apiClient';
import type { Document, QueryRequest, QueryResponse, QueryAnalytics, SystemStatus } from '../types/api';

export const documentService = {
  // Get all documents
  getDocuments: async (): Promise<{ filename: string }[]> => {
    const response = await apiClient.get('/api/documents');
    return response.data;
  },
  
  // Upload documents
  uploadDocuments: async (files: File[]): Promise<{ message: string; files: string[] }> => {
    const formData = new FormData();
    
    files.forEach(file => {
      formData.append('files', file);
    });
    
    const response = await apiClient.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },
  
  // Delete a document
  deleteDocument: async (filename: string): Promise<{ message: string }> => {
    const response = await apiClient.delete(`/api/documents/${filename}`);
    return response.data;
  },
  
  // Query documents
  queryDocuments: async (queryData: QueryRequest): Promise<QueryResponse> => {
    const response = await apiClient.post<QueryResponse>('/api/query', queryData);
    return response.data;
  },
  
  // Get query analytics
  getQueryAnalytics: async (): Promise<QueryAnalytics> => {
    const response = await apiClient.get<QueryAnalytics>('/api/analytics/queries');
    return response.data;
  },
  
  // Get system status
  getSystemStatus: async (): Promise<SystemStatus> => {
    const response = await apiClient.get<SystemStatus>('/api/system/status');
    return response.data;
  },
  
  // Rebuild search index
  rebuildIndex: async (): Promise<{ message: string; document_count: number; status: string }> => {
    const response = await apiClient.post('/api/system/rebuild-index');
    return response.data;
  },
  
  // Admin olma isteği gönder
  requestAdmin: async (): Promise<{ message: string }> => {
    const response = await apiClient.post('/api/auth/request-admin');
    return response.data;
  },
  
  // Admin başvurularını listele
  getAdminRequests: async (): Promise<{ username: string; requested_at: string }[]> => {
    const response = await apiClient.get('/api/auth/admin-requests');
    return response.data;
  },

  // Admin başvurusunu onayla
  approveAdmin: async (username: string): Promise<{ message: string }> => {
    const response = await apiClient.post(`/api/auth/approve-admin/${username}`);
    return response.data;
  },

  // Get all pages of a PDF document
  getPdfPages: async (filename: string): Promise<{ page: number; text: string }[]> => {
    const response = await apiClient.get(`/api/documents/${filename}/pages`);
    return response.data;
  },

  // Get PDF as base64
  getPdfBase64: async (filename: string): Promise<{ filename: string; content: string }> => {
    const response = await apiClient.get(`/api/documents/${filename}/base64`);
    return response.data;
  },
};
