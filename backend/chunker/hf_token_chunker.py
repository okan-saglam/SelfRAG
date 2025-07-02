from transformers import AutoTokenizer
from typing import List
from backend.chunker.base_chunker import BaseChunker

class HFTokenChunker(BaseChunker):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", max_tokens: int = 500, overlap: int = 50):
        """
        Initializes the HFTokenChunker with a specified model and parameters.

        :param model_name: The name of the Hugging Face model to use for tokenization.
        :param max_tokens: The maximum number of tokens per chunk.
        :param overlap: The number of overlapping tokens between chunks.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.max_tokens = max_tokens
        self.overlap = overlap
        
    def chunk(self, text: str) -> List[str]:
        input_ids = self.tokenizer.encode(text, add_special_tokens=False)
        chunks = []
        start = 0

        while start < len(input_ids):
            end = start + self.max_tokens
            chunk_ids = input_ids[start:end]
            chunk_text = self.tokenizer.decode(chunk_ids)
            chunks.append(chunk_text)
            start += self.max_tokens - self.overlap
        
        return chunks