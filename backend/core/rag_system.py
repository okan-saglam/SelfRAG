import time
import asyncio
from typing import Dict, List, Any
from pathlib import Path
import os
import shutil
import numpy as np

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
        self.llm = CohereGenerator()  # LLM değerlendirme ve refine için de kullanılacak
        
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
    
    async def process_query(self, query: str, top_k: int = 10, use_self_rag: bool = True) -> Dict[str, Any]:
        """
        Process query with optional Self-RAG
        """
        start_time = time.time()
        
        # Get query embedding
        query_vector = self.embedder.embed([
            ChunkDocument(text=query, page=0, chunk_id=0, source_file="query")
        ])[0]
        
        # Initial retrieval
        initial_chunks = self.vectorstore.search(query_vector, k=50)
        
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
    
    async def _evaluate_with_self_rag(self, query: str, chunks: List[ChunkDocument], answer: str, max_iterations: int = 2) -> Dict[str, Any]:
        """
        Self-RAG evaluation: Cevabın yeterliliğini LLM ile değerlendir, gerekirse yeni sorgu üret ve döngüsel olarak cevabı iyileştir.
        """
        current_query = query
        current_answer = answer
        history = []
        for iteration in range(max_iterations):
            # 1. Cevabın yeterliliğini LLM ile değerlendir
            sufficient, explanation = await self._is_answer_sufficient_llm(current_query, current_answer)
            history.append({
                "iteration": iteration + 1,
                "query": current_query,
                "answer": current_answer,
                "sufficient": sufficient,
                "explanation": explanation
            })
            if sufficient:
                break
            # 2. Yeni bir sorgu üret (refine query) LLM ile
            current_query = await self._refine_query_llm(current_query, current_answer)
            # 3. Yeni sorgu ile retrieval ve generation
            query_vector = self.embedder.embed([
                ChunkDocument(text=current_query, page=0, chunk_id=0, source_file="query")
            ])[0]
            initial_chunks = self.vectorstore.search(query_vector, k=10)
            reranked_chunks = self.reranker.rerank(current_query, initial_chunks, top_k=5)
            chunks_for_generation = [chunk for chunk, _ in reranked_chunks]
            current_answer = self.generator.generate_answer(current_query, chunks_for_generation)
        # --- Retrieval confidence hesaplama ---
        # İlk retrieval skorlarının normalize edilmiş ortalaması (inner product [-1,1] -> [0,1])
        initial_scores = [score for _, score in self.vectorstore.search(self.embedder.embed([
            ChunkDocument(text=query, page=0, chunk_id=0, source_file="query")
        ])[0], k=10)]
        if initial_scores:
            retrieval_confidence = float(np.mean([(s + 1) / 2 for s in initial_scores]))
        else:
            retrieval_confidence = 0.0

        # --- Generation confidence hesaplama ---
        # Cohere'den likelihood desteği yoksa, cevabın belirsizliğine göre heuristik skor
        def is_uncertain(text):
            lower = text.lower()
            return any(kw in lower for kw in ["emin değilim", "bilinmiyor", "bilgi yok", "bulunamadı", "not sure", "unknown", "cannot answer"])
        if is_uncertain(current_answer):
            generation_confidence = 0.3
        else:
            generation_confidence = 0.85

        final_score = (retrieval_confidence + generation_confidence) / 2
        reflection_notes = [
            f"{len(history)} iterations performed.",
            f"Retrieval confidence: {retrieval_confidence:.2f}",
            f"Generation confidence: {generation_confidence:.2f}",
            f"Final answer: {current_answer[:60]}..."
        ]
        return {
            "final_query": current_query,
            "final_answer": current_answer,
            "iterations": len(history),
            "history": history,
            "retrieval_confidence": retrieval_confidence,
            "generation_confidence": generation_confidence,
            "final_score": final_score,
            "reflection_notes": reflection_notes
        }

    async def _is_answer_sufficient_llm(self, query: str, answer: str) -> (bool, str):
        """
        Evaluate if the answer sufficiently addresses the query using the LLM. Ask for a yes/no and a short explanation in English.
        """
        prompt = (
            f"Question: {query}\n"
            f"Answer: {answer}\n"
            "Evaluate the above answer: Does this answer fully address the question?\n"
            "Start your response with only 'yes' or 'no', then provide a brief explanation."
        )
        response = self.llm.client.generate(
            prompt=prompt,
            model="command-r-plus",
            max_tokens=60,
            temperature=0.3,
        )
        text = response.generations[0].text.strip().lower() if response.generations else "no"
        sufficient = text.startswith("yes")
        explanation = text
        return sufficient, explanation

    async def _refine_query_llm(self, query: str, answer: str) -> str:
        """
        Generate a better/refined query using the LLM, based on the previous answer. Prompt in English.
        """
        prompt = (
            f"Question: {query}\n"
            f"Answer: {answer}\n"
            "Based on the above answer, how should I rephrase or expand the question to get a better and more detailed answer?\n"
            "Please suggest a new and improved question. Only return the new question."
        )
        response = self.llm.client.generate(
            prompt=prompt,
            model="command-r-plus",
            max_tokens=60,
            temperature=0.3,
        )
        new_query = response.generations[0].text.strip() if response.generations else query
        return new_query
    
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