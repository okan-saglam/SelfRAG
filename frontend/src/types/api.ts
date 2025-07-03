// User related types
export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  last_login?: string;
}

export interface UserLogin {
  username: string;
  password: string;
}

export interface UserRegister {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
}

// Authentication related types
export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface TokenRefresh {
  refresh_token: string;
}

// Document related types
export interface Document {
  filename: string;
  size: number;
  uploaded_at: number;
}

// Query related types
export interface QueryRequest {
  query: string;
  top_k?: number;
  use_self_rag?: boolean;
}

export interface ChunkInfo {
  text: string;
  source_file: string;
  page: number;
  chunk_id: number;
  score: number;
}

export interface SelfRAGInfo {
  retrieval_confidence: number;
  generation_confidence: number;
  final_score: number;
  reflection_notes: string[];
}

export interface QueryResponse {
  answer: string;
  chunks: ChunkInfo[];
  processing_time: number;
  self_rag_info?: SelfRAGInfo;
}

// Analytics related types
export interface QueryAnalytics {
  total_queries: number;
  avg_processing_time: number;
  avg_self_rag_score?: number;
  recent_queries: RecentQuery[];
}

export interface RecentQuery {
  query: string;
  processing_time: number;
  self_rag_score?: number;
  created_at: string;
}

// System related types
export interface SystemStatus {
  status: string;
  vectorstore: {
    has_documents: boolean;
    document_count: number;
    index_ready: boolean;
  };
  data_directory: {
    path: string;
    exists: boolean;
    pdf_count: number;
    pdf_files: string[];
  };
  components: {
    reader: boolean;
    chunker: boolean;
    embedder: boolean;
    generator: boolean;
    reranker: boolean;
  };
}

// API error type
export interface ApiError {
  status: number;
  message: string;
}
