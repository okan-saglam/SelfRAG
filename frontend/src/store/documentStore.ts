import { create } from 'zustand';
import type { Document, QueryRequest, QueryResponse, SystemStatus } from '../types/api';
import { documentService } from '../services/documentService';

interface DocumentState {
  documents: Document[];
  systemStatus: SystemStatus | null;
  queryResult: QueryResponse | null;
  isLoading: boolean;
  isQuerying: boolean;
  error: string | null;
  
  // Actions
  fetchDocuments: () => Promise<void>;
  uploadDocuments: (files: File[]) => Promise<void>;
  deleteDocument: (filename: string) => Promise<void>;
  queryDocuments: (query: string, topK?: number, useSelfRAG?: boolean) => Promise<void>;
  fetchSystemStatus: () => Promise<void>;
  rebuildIndex: () => Promise<void>;
  clearQueryResult: () => void;
  clearError: () => void;
}

export const useDocumentStore = create<DocumentState>((set, get) => ({
  documents: [],
  systemStatus: null,
  queryResult: null,
  isLoading: false,
  isQuerying: false,
  error: null,
  
  fetchDocuments: async () => {
    try {
      set({ isLoading: true, error: null });
      
      const documents = await documentService.getDocuments();
      
      set({ 
        documents,
        isLoading: false,
      });
    } catch (error: any) {
      set({ 
        isLoading: false,
        error: error.response?.data?.detail || 'Failed to fetch documents',
      });
    }
  },
  
  uploadDocuments: async (files: File[]) => {
    try {
      set({ isLoading: true, error: null });
      
      await documentService.uploadDocuments(files);
      
      // Refresh document list after upload
      await get().fetchDocuments();
      // Refresh system status
      await get().fetchSystemStatus();
    } catch (error: any) {
      set({ 
        isLoading: false,
        error: error.response?.data?.detail || 'Failed to upload documents',
      });
    }
  },
  
  deleteDocument: async (filename: string) => {
    try {
      set({ isLoading: true, error: null });
      
      await documentService.deleteDocument(filename);
      
      // Refresh document list after deletion
      await get().fetchDocuments();
      // Refresh system status
      await get().fetchSystemStatus();
    } catch (error: any) {
      set({ 
        isLoading: false,
        error: error.response?.data?.detail || 'Failed to delete document',
      });
    }
  },
  
  queryDocuments: async (query: string, topK: number = 5, useSelfRAG: boolean = true) => {
    try {
      set({ isQuerying: true, error: null });
      
      const queryRequest: QueryRequest = {
        query,
        top_k: topK,
        use_self_rag: useSelfRAG,
      };
      
      const queryResult = await documentService.queryDocuments(queryRequest);
      
      set({ 
        queryResult,
        isQuerying: false,
      });
    } catch (error: any) {
      set({ 
        isQuerying: false,
        error: error.response?.data?.detail || 'Failed to query documents',
      });
    }
  },
  
  fetchSystemStatus: async () => {
    try {
      set({ isLoading: true, error: null });
      
      const systemStatus = await documentService.getSystemStatus();
      
      set({ 
        systemStatus,
        isLoading: false,
      });
    } catch (error: any) {
      set({ 
        isLoading: false,
        error: error.response?.data?.detail || 'Failed to fetch system status',
      });
    }
  },
  
  rebuildIndex: async () => {
    try {
      set({ isLoading: true, error: null });
      
      await documentService.rebuildIndex();
      
      // Refresh system status after rebuilding index
      await get().fetchSystemStatus();
    } catch (error: any) {
      set({ 
        isLoading: false,
        error: error.response?.data?.detail || 'Failed to rebuild index',
      });
    }
  },
  
  clearQueryResult: () => {
    set({ queryResult: null });
  },
  
  clearError: () => {
    set({ error: null });
  },
}));
