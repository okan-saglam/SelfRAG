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
    
    @abstractmethod
    def save(self, index_path: str) -> None:
        """
        Save the vector store index and metadata to disk.
        
        :param index_path: Path where to save the index files.
        """
        pass
    
    @abstractmethod
    def load(self, index_path: str) -> bool:
        """
        Load the vector store index and metadata from disk.
        
        :param index_path: Path where the index files are stored.
        :return: True if loading was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def exists(self, index_path: str) -> bool:
        """
        Check if an index exists at the given path.
        
        :param index_path: Path to check for index files.
        :return: True if index exists, False otherwise.
        """
        pass