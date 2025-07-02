from typing import List, Optional
import re
from transformers import AutoTokenizer
from backend.models.chunk_document import ChunkDocument


class SemanticTextSplitter:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", max_tokens: int = 500):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.max_tokens = max_tokens

    def split_text(self, text: str) -> List[str]:
        """
        Split raw text into semantically meaningful chunks based on markdown-style structure.
        """
        lines = text.splitlines()
        blocks = []
        current_block = []

        for line in lines:
            line = line.rstrip()

            if self._is_heading(line):
                if current_block:
                    blocks.append("\n".join(current_block).strip())
                    current_block = []
                current_block.append(line)
            elif line.strip() == "":
                if current_block:
                    blocks.append("\n".join(current_block).strip())
                    current_block = []
            else:
                current_block.append(line)

        if current_block:
            blocks.append("\n".join(current_block).strip())

        return self._combine_blocks(blocks)

    def _combine_blocks(self, blocks: List[str]) -> List[str]:
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
                block_tokens = len(self.tokenizer.encode(block, add_special_tokens=False))
                if block_tokens > self.max_tokens:
                    chunks.extend(self._hard_split(block))
                    current = ""
                else:
                    current = block

        if current:
            chunks.append(current.strip())

        return chunks

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

    def _is_heading(self, line: str) -> bool:
        return bool(re.match(r"^(#{1,6}\s|[A-Z]\.|I\.|II\.|[0-9]+\.)", line.strip()))
