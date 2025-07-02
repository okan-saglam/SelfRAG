from transformers import AutoTokenizer
from typing import List, Tuple
from backend.chunker.base_chunker import BaseChunker
from backend.models.chunk_document import ChunkDocument

class RecursiveChunker(BaseChunker):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", max_tokens: int = 500, overlap: int = 50):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.max_tokens = max_tokens
        self.overlap = overlap

    def _split_recursive(self, text: str, level: int = 0) -> List[str]:
        """
        Split text recursively by decreasing granularity:
        0: Headings
        1: Double newlines
        2: Single newlines
        3: Sentences (". ")
        4: Tokens (last resort)
        """
        delimiters = ["\n#", "\n\n", "\n", ". ", " "]  # heading → paragraph → sentence → word
        delimiter = delimiters[level]

        parts = text.split(delimiter)
        chunks = []
        current_chunk = ""

        for part in parts:
            if current_chunk:
                combined = current_chunk + delimiter + part
            else:
                combined = part

            token_count = len(self.tokenizer.encode(combined, add_special_tokens=False))
            if token_count <= self.max_tokens:
                current_chunk = combined
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                if len(self.tokenizer.encode(part, add_special_tokens=False)) > self.max_tokens:
                    if level < len(delimiters) - 1:
                        # recurse on too-long part
                        sub_chunks = self._split_recursive(part, level + 1)
                        chunks.extend(sub_chunks)
                    else:
                        chunks.append(part.strip())  # give up, add as-is
                    current_chunk = ""
                else:
                    current_chunk = part

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def chunk(self, pages: List[Tuple[int, str]], source_file: str) -> List[ChunkDocument]:
        all_chunks = []
        global_chunk_id = 0

        for page_number, text in pages:
            semantic_chunks = self._split_recursive(text)

            for chunk_text in semantic_chunks:
                chunk_doc = ChunkDocument(
                    text=chunk_text,
                    page=page_number,
                    chunk_id=global_chunk_id,
                    source_file=source_file
                )
                all_chunks.append(chunk_doc)
                global_chunk_id += 1

        return all_chunks
