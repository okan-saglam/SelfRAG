from abc import ABC, abstractmethod
from typing import List
from backend.models.chunk_document import ChunkDocument

class BaseGenerator(ABC):
    @abstractmethod
    def generate_answer(self, question: str, context_chunks: List[ChunkDocument]) -> str:
        """
        Generates an answer to the given question based on the provided context chunks.

        :param question: The question to be answered.
        :param context_chunks: List of ChunkDocument objects providing context for the answer.
        :return: A string containing the generated answer.
        """
        pass