from abc import ABC, abstractmethod
from typing import List

class BaseEmbedder(ABC):
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Embeds a list of texts into vector representations.

        :param texts: A list of strings to be embedded.
        :return: A list of lists, where each inner list is a vector representation of the corresponding text.
        """
        pass