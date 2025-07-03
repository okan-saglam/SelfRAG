from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    use_self_rag: bool = True

class ChunkInfo(BaseModel):
    text: str
    source_file: str
    page: int
    chunk_id: int
    score: float

class SelfRAGInfo(BaseModel):
    retrieval_confidence: float
    generation_confidence: float
    final_score: float
    reflection_notes: List[str]

class QueryResponse(BaseModel):
    answer: str
    chunks: List[ChunkInfo]
    processing_time: float
    self_rag_info: Optional[SelfRAGInfo] = None

class DocumentResponse(BaseModel):
    filename: str
    size: int
    uploaded_at: float

class ErrorResponse(BaseModel):
    error: str
    detail: str