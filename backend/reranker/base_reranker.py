from abc import ABC, abstractmethod
from typing import List, Tuple
from backend.models.chunk_document import ChunkDocument

class BaseReranker(ABC):
    @abstractmethod
    def rerank(self, query: str, chunks: List[Tuple[ChunkDocument, float]], top_k: int = 5) -> List[Tuple[ChunkDocument, float]]:
        """
        Rerank the provided chunks based on their relevance to the query.

        :param query: The search query string.
        :param chunks: List of tuples containing (ChunkDocument, similarity_score).
        :param top_k: Number of top results to return after reranking.
        :return: Reranked list of tuples containing (ChunkDocument, rerank_score).
        """
        pass