import faiss
import numpy as np
from sklearn.preprocessing import normalize
from typing import List, Tuple
from backend.vectorstore.base_vectorstore import BaseVectorStore

class FaissVectorStore(BaseVectorStore):
    def __init__(self, embedding_dim: int = 384):
        """
        Initializes the FaissVectorStore with a specified embedding dimension.

        :param embedding_dim: The dimension of the embeddings.
        """
        # self.index = faiss.IndexFlatL2(embedding_dim) # L2 distance index
        self.index = faiss.IndexFlatIP(embedding_dim)  # Inner product index
        self.texts = []
        
    def add(self, embeddings: List[List[float]], texts: List[str]) -> None:
        vectors = np.array(embeddings, dtype=np.float32)
        vectors = normalize(vectors, axis=1)  # Normalize vectors for inner product search
        self.index.add(vectors)
        self.texts.extend(texts)
        
    def search(self, query_vector: List[float], k: int = 3) -> List[Tuple[str, float]]:
        query = np.array([query_vector], dtype=np.float32)
        query = normalize(query, axis=1)
        distances, indices = self.index.search(query, k)
        
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.texts):
                results.append((self.texts[idx], float(dist)))
        return results