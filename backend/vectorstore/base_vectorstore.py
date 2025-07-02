from abc import ABC, abstractmethod
from typing import List, Tuple

class BaseVectorStore(ABC):
    @abstractmethod
    def add(self, embeddings: List[List[float]], texts: List[str]) -> None:
        """
        Adds embeddings and their corresponding texts to the vector store.

        :param embeddings: A list of vector representations of the texts.
        :param texts: A list of strings corresponding to the embeddings.
        """
        pass
    
    @abstractmethod
    def search(self, query_vector: List[float], k: int) -> List[Tuple[str, float]]:
        """
        Searches the vector store for the k most similar texts to the query vector.

        :param query_vector: The vector representation of the query text.
        :param k: The number of top results to return.
        :return: A list of tuples, each containing a text and its similarity score.
        """
        pass