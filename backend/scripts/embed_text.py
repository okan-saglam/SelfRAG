import sys
import os

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from backend.reader.pdf_reader import PDFReader
from backend.chunker.hf_token_chunker import HFTokenChunker
from backend.embedder.hf_embedder import HuggingFaceEmbedder

if __name__ == "__main__":
    reader = PDFReader()
    chunker = HFTokenChunker()
    embedder = HuggingFaceEmbedder()

    text = reader.read("data/Okan_Sağlam_CV.pdf")
    chunks = chunker.chunk(text)
    vectors = embedder.embed(chunks)
    
    print(f"{len(vectors)} vectors are generated.\n")
    print("--- First Vector ---\n")
    print(vectors[0])
    print(vectors[0][:10], "...")