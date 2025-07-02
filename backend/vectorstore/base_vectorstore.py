from abc import ABC, abstractmethod
from typing import List, Tuple
from backend.models.chunk_document import ChunkDocument

class BaseVectorStore(ABC):
    @abstractmethod
    def add(self, embeddings: List[List[float]], documents: List[ChunkDocument]) -> None:
        """
        Adds embeddings and corresponding documents to the vector store.

        :param embeddings: List of vector representations of the documents.
        :param documents: List of ChunkDocument objects to be added.
        """
        pass
    
    @abstractmethod
    def search(self, query_vector: List[float], k: int) -> List[Tuple[ChunkDocument, float]]:
        """
        Searches the vector store for the most similar texts to the query vector.

        :param query_vector: The vector representation of the query text.
        :param k: The number of nearest neighbors to return.
        :return: A list of tuples containing ChunkDocument and similarity score.
        """
        pass