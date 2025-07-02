import sys
import os

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from backend.reader.pdf_reader import PDFReader
from backend.chunker.hf_token_chunker import HFTokenChunker

if __name__ == "__main__":
    reader = PDFReader()
    chunker = HFTokenChunker()

    text = reader.read("data/Okan_Sağlam_CV.pdf")
    chunks = chunker.chunk(text)

    print(f"{len(chunks)} tokens are generated.\n")
    print("--- First Token ---\n")
    print(chunks[0])
