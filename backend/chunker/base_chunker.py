from abc import ABC, abstractmethod
from typing import List, Tuple
from backend.models.chunk_document import ChunkDocument

class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, pages: List[Tuple[int, str]], source_file: str) -> List[ChunkDocument]:
        """
        Chunk the text from the provided pages into smaller segments.

        :param pages: List of tuples containing (page_number, text_content).
        :param source_file: The source file from which the text is extracted.
        :return: List of ChunkDocument objects representing the chunks.
        """
        pass