from dataclasses import dataclass

@dataclass
class ChunkDocument:
    text: str                 # The actual chunk content
    page: int                 # Page number in the source document
    chunk_id: int             # Position within the document
    source_file: str          # File name or path for multi-doc support