from abc import ABC, abstractmethod
from typing import List

class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        """
        Splits the input text into smaller chunks.

        :param text: The text to be chunked.
        :return: A list of text chunks.
        """
        pass