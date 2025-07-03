from sentence_transformers import CrossEncoder
from typing import List, Tuple
from backend.reranker.base_reranker import BaseReranker
from backend.models.chunk_document import ChunkDocument

class HuggingFaceReranker(BaseReranker):
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize HuggingFace cross-encoder reranker.
        
        :param model_name: Cross-encoder model name from HuggingFace.
        """
        self.model = CrossEncoder(model_name)
    
    def rerank(self, query: str, chunks: List[Tuple[ChunkDocument, float]], top_k: int = 5) -> List[Tuple[ChunkDocument, float]]:
        if not chunks:
            return []
        
        # Prepare query-document pairs
        query_doc_pairs = [(query, chunk.text) for chunk, _ in chunks]
        
        # Get cross-encoder scores
        scores = self.model.predict(query_doc_pairs)
        
        # Combine with original chunks and sort by score
        scored_chunks = list(zip([chunk for chunk, _ in chunks], scores))
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k results
        return scored_chunks[:top_k]