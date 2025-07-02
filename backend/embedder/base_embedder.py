from abc import ABC, abstractmethod
from typing import List
from backend.models.chunk_document import ChunkDocument

class BaseEmbedder(ABC):
    @abstractmethod
    def embed(self, documents: List[ChunkDocument]) -> List[List[float]]:
        """
        Embed the provided documents into vector representations.

        :param documents: List of ChunkDocument objects to be embedded.
        :return: List of vectors representing the embedded documents.
        """
        pass