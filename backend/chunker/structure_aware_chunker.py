from transformers import AutoTokenizer
from typing import List, Tuple
import re

from backend.chunker.base_chunker import BaseChunker
from backend.models.chunk_document import ChunkDocument


class StructureAwareChunker(BaseChunker):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", max_tokens: int = 480):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.max_tokens = max_tokens

    def _is_heading(self, line: str) -> bool:
        return bool(re.match(r"^\s*(I\.|II\.|III\.|[A-Z]\.|[0-9]+\.)", line.strip()))

    def _is_list_item(self, line: str) -> bool:
        return bool(re.match(r"^\s*(-|\•|\d+\.)", line.strip()))

    def _is_json_start(self, line: str) -> bool:
        return "{" in line

    def _is_json_end(self, line: str) -> bool:
        return "}" in line

    def _is_code_line(self, line: str) -> bool:
        return line.startswith("    ") or line.strip().startswith("def ") or line.strip().endswith(":")  # Python-style

    def _group_lines_into_blocks(self, text: str) -> List[str]:
        lines = text.splitlines()
        blocks = []
        current_block = []
        inside_json = False

        for line in lines:
            line = line.rstrip()

            if inside_json:
                current_block.append(line)
                if self._is_json_end(line):
                    inside_json = False
                    blocks.append("\n".join(current_block).strip())
                    current_block = []
                continue

            if self._is_json_start(line):
                inside_json = True
                current_block.append(line)
                continue

            if self._is_heading(line) or self._is_list_item(line) or self._is_code_line(line):
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

        return [b for b in blocks if b]

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

    def chunk(self, pages: List[Tuple[int, str]], source_file: str) -> List[ChunkDocument]:
        all_chunks = []
        global_chunk_id = 0

        for page_number, text in pages:
            blocks = self._group_lines_into_blocks(text)
            grouped = self._combine_blocks(blocks)

            for chunk_text in grouped:
                chunk_doc = ChunkDocument(
                    text=chunk_text,
                    page=page_number,
                    chunk_id=global_chunk_id,
                    source_file=source_file
                )
                all_chunks.append(chunk_doc)
                global_chunk_id += 1

        return all_chunks
