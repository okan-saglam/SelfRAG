from functools import lru_cache
from backend.core.rag_system import RAGSystem

@lru_cache()
def get_rag_system() -> RAGSystem:
    """
    Dependency to get RAG system instance (singleton)
    """
    return RAGSystem()