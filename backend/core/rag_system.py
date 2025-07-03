import time
import asyncio
from typing import Dict, List, Any
from pathlib import Path
import os
import shutil

from backend.reader.pdf_reader import PDFReader
from backend.chunker.structure_aware_chunker import StructureAwareChunker
from backend.embedder.hf_embedder import HuggingFaceEmbedder
from backend.vectorstore.faiss_store import FaissVectorStore
from backend.generator.cohere_generator import CohereGenerator
from backend.reranker.hf_reranker import HuggingFaceReranker
from backend.utils.index_manager import IndexManager
from backend.models.chunk_document import ChunkDocument

BACKEND_DIR = Path(__file__).parent.parent

class RAGSystem:
    def __init__(self):
        self.reader = PDFReader()
        self.chunker = StructureAwareChunker()
        self.embedder = HuggingFaceEmbedder()
        self.vectorstore = FaissVectorStore()
        self.generator = CohereGenerator()
        self.reranker = HuggingFaceReranker()
        self.index_manager = IndexManager()
        
        # Initialize with existing documents
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize index with existing PDF files"""
        pdf_files = self._get_pdf_files()
        if pdf_files:
            index_path = self.index_manager.get_index_path(pdf_files)
            if self.vectorstore.exists(index_path):
                self.vectorstore.load(index_path)
                print(f"✅ Loaded existing index with {len(self.vectorstore.documents)} documents")
            else:
                self._build_index(pdf_files)
    
    def _get_pdf_files(self) -> List[str]:
        """Get all PDF files from data directory"""
        data_dir = BACKEND_DIR / "data"
        if not data_dir.exists():
            data_dir.mkdir()
            return []
        return [str(f) for f in data_dir.glob("*.pdf")]
    
    def _build_index(self, pdf_files: List[str]):
        """Build index from PDF files"""
        index_path = self.index_manager.get_index_path(pdf_files)
        # Remove old index if exists
        if os.path.exists(index_path):
            shutil.rmtree(index_path)
        for path in pdf_files:
            source_file = os.path.basename(path)
            pages = self.reader.read(path)
            chunk_docs = self.chunker.chunk(pages, source_file)
            embeddings = self.embedder.embed(chunk_docs)
            self.vectorstore.add(embeddings, chunk_docs)
        # Save index
        if pdf_files:
            self.vectorstore.save(index_path)
    
    async def process_query(self, query: str, top_k: int = 5, use_self_rag: bool = True) -> Dict[str, Any]:
        """
        Process query with optional Self-RAG
        """
        start_time = time.time()
        
        # Get query embedding
        query_vector = self.embedder.embed([
            ChunkDocument(text=query, page=0, chunk_id=0, source_file="query")
        ])[0]
        
        # Initial retrieval
        initial_chunks = self.vectorstore.search(query_vector, k=10)
        
        # Rerank
        reranked_chunks = self.reranker.rerank(query, initial_chunks, top_k=top_k)
        
        # Generate answer
        chunks_for_generation = [chunk for chunk, _ in reranked_chunks]
        answer = self.generator.generate_answer(query, chunks_for_generation)
        
        # Self-RAG evaluation (placeholder for now)
        self_rag_info = None
        if use_self_rag:
            self_rag_info = await self._evaluate_with_self_rag(query, chunks_for_generation, answer)
        
        processing_time = time.time() - start_time
        
        return {
            "answer": answer,
            "chunks": [
                {
                    "text": chunk.text,
                    "source_file": chunk.source_file,
                    "page": chunk.page,
                    "chunk_id": chunk.chunk_id,
                    "score": score
                }
                for chunk, score in reranked_chunks
            ],
            "processing_time": processing_time,
            "self_rag_info": self_rag_info
        }
    
    async def _evaluate_with_self_rag(self, query: str, chunks: List[ChunkDocument], answer: str) -> Dict[str, Any]:
        """
        Self-RAG evaluation (basic implementation)
        """
        # Placeholder implementation - will be enhanced in Phase 2
        return {
            "retrieval_confidence": 0.85,
            "generation_confidence": 0.90,
            "final_score": 0.87,
            "reflection_notes": ["Good chunk relevance", "Answer covers main points"]
        }
    
    async def rebuild_index(self):
        """Rebuild index with current PDF files"""
        pdf_files = self._get_pdf_files()
        # Remove all old indices before creating a new one
        indices_dir = BACKEND_DIR / "indices"
        if indices_dir.exists():
            for item in indices_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
        if pdf_files:
            # Clear current index
            self.vectorstore = FaissVectorStore()
            self._build_index(pdf_files)
            print(f"✅ Index rebuilt with {len(pdf_files)} documents")