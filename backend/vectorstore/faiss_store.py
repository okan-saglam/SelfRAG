import faiss
import numpy as np
from sklearn.preprocessing import normalize
from typing import List, Tuple
from backend.vectorstore.base_vectorstore import BaseVectorStore
from backend.models.chunk_document import ChunkDocument

class FaissVectorStore(BaseVectorStore):
    def __init__(self, embedding_dim: int = 384):
        """
        Initializes the FaissVectorStore with a specified embedding dimension.

        :param embedding_dim: The dimension of the embeddings.
        """
        # self.index = faiss.IndexFlatL2(embedding_dim) # L2 distance index
        self.index = faiss.IndexFlatIP(embedding_dim)  # Inner product index
        self.documents: List[ChunkDocument] = []
        
    def add(self, embeddings: List[List[float]], documents: List[ChunkDocument]) -> None:
        vectors = np.array(embeddings).astype("float32")
        vectors = normalize(vectors)
        self.index.add(vectors)
        self.documents.extend(documents)
        
    def search(self, query_vector: List[float], k: int = 3) -> List[Tuple[ChunkDocument, float]]:
        query = np.array([query_vector]).astype("float32")
        query = normalize(query)
        distances, indices = self.index.search(query, k)

        results = []
        for idx, score in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(score)))
        return results