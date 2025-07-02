from transformers import AutoTokenizer
from typing import List, Tuple
import re

from backend.chunker.base_chunker import BaseChunker
from backend.models.chunk_document import ChunkDocument


class SemanticPreservingChunker(BaseChunker):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", max_tokens: int = 500):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.max_tokens = max_tokens

    def _split_into_semantic_blocks(self, text: str) -> List[str]:
        # Split on double newlines – indicates new paragraph or semantic block
        return [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]

    def _hard_split(self, text: str) -> List[str]:
        words = text.split(" ")
        chunks = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if len(self.tokenizer.encode(candidate, add_special_tokens=False)) > self.max_tokens:
                if current:
                    chunks.append(current.strip())
                current = word
            else:
                current = candidate
        if current:
            chunks.append(current.strip())
        return chunks

    def _group_blocks(self, blocks: List[str]) -> List[str]:
        chunks = []
        current = ""

        for block in blocks:
            candidate = f"{current}\n\n{block}".strip() if current else block
            token_count = len(self.tokenizer.encode(candidate, add_special_tokens=False))

            if token_count <= self.max_tokens:
                current = candidate
            else:
                if current:
                    chunks.append(current.strip())
                # check if block itself is too long
                block_token_count = len(self.tokenizer.encode(block, add_special_tokens=False))
                if block_token_count > self.max_tokens:
                    chunks.extend(self._hard_split(block))
                    current = ""
                else:
                    current = block

        if current:
            chunks.append(current.strip())

        return chunks

    def chunk(self, pages: List[Tuple[int, str]], source_file: str) -> List[ChunkDocument]:
        all_chunks = []
        global_chunk_id = 0

        for page_number, text in pages:
            blocks = self._split_into_semantic_blocks(text)
            grouped_chunks = self._group_blocks(blocks)

            for chunk_text in grouped_chunks:
                chunk_doc = ChunkDocument(
                    text=chunk_text,
                    page=page_number,
                    chunk_id=global_chunk_id,
                    source_file=source_file
                )
                all_chunks.append(chunk_doc)
                global_chunk_id += 1

        return all_chunks
