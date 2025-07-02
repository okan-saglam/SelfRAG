import sys
import os

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from backend.chunker.hf_token_chunker import HFTokenChunker
from backend.reader.pdf_reader import PDFReader
from backend.embedder.hf_embedder import HuggingFaceEmbedder
from backend.vectorstore.faiss_store import FaissVectorStore
from backend.generator.cohere_generator import CohereGenerator
from backend.models.chunk_document import ChunkDocument

if __name__ == "__main__":
    # === SETUP ===
    file_path = "data/Okan_Sağlam_CV.pdf"
    source_file = os.path.basename(file_path)

    reader = PDFReader()
    chunker = HFTokenChunker()
    embedder = HuggingFaceEmbedder()
    vectorstore = FaissVectorStore()
    generator = CohereGenerator()

    # === PIPELINE ===
    pages = reader.read(file_path)
    chunk_docs: list[ChunkDocument] = chunker.chunk(pages, source_file)
    embeddings = embedder.embed(chunk_docs)
    vectorstore.add(embeddings, chunk_docs)

    # === QUERY ===
    question = "What projects has this person worked on?"
    query_vector = embedder.embed([ChunkDocument(text=question, page=0, chunk_id=0, source_file="query")])[0]
    top_chunks = vectorstore.search(query_vector, k=3)

    # === OUTPUT ===
    print(f"\n🔍 Question: {question}")
    print("\n📄 Top Matching Chunks:")
    for i, (chunk, score) in enumerate(top_chunks, 1):
        print(f"\n{i}. Score: {score:.4f}")
        print(f"📘 Source: {chunk.source_file} | 📄 Page: {chunk.page} | 🔢 Chunk ID: {chunk.chunk_id}")
        print(chunk.text)

    # === GENERATE ANSWER ===
    answer = generator.generate_answer(question, [c for c, _ in top_chunks])
    print("\n🧠 Answer:")
    print(answer)