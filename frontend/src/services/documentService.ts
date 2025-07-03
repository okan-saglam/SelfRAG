import apiClient from './apiClient';
import type { Document, QueryRequest, QueryResponse, QueryAnalytics, SystemStatus } from '../types/api';

export const documentService = {
  // Get all documents
  getDocuments: async (): Promise<Document[]> => {
    const response = await apiClient.get<Document[]>('/api/documents');
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
};
