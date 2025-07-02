from transformers import AutoTokenizer
from typing import List, Tuple
from backend.chunker.base_chunker import BaseChunker
from backend.models.chunk_document import ChunkDocument

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
        
    def chunk(self, pages: List[Tuple[int, str]], source_file: str) -> List[ChunkDocument]:
        chunks = []
        global_chunk_id = 0

        for page_number, text in pages:
            input_ids = self.tokenizer.encode(text, add_special_tokens=False)
            start = 0

            while start < len(input_ids):
                end = start + self.max_tokens
                chunk_ids = input_ids[start:end]
                chunk_text = self.tokenizer.decode(chunk_ids)
                chunk = ChunkDocument(
                    text=chunk_text,
                    page=page_number,
                    chunk_id=global_chunk_id,
                    source_file=source_file
                )
                chunks.append(chunk)
                global_chunk_id += 1
                start += self.max_tokens - self.overlap

        return chunks