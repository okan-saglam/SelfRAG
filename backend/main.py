import sys
import os

# Add the project root directory to Python path
# Since this file is in backend/main.py, we need to go up one level to reach project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.reader.pdf_reader import PDFReader
from backend.chunker.hf_token_chunker import HFTokenChunker
from backend.embedder.hf_embedder import HuggingFaceEmbedder
from backend.vectorstore.faiss_store import FaissVectorStore
from backend.generator.cohere_generator import CohereGenerator
from backend.models.chunk_document import ChunkDocument

def build_index(pdf_paths: list[str]) -> tuple[FaissVectorStore, HuggingFaceEmbedder, CohereGenerator]:
    reader = PDFReader()
    chunker = HFTokenChunker()
    embedder = HuggingFaceEmbedder()
    vectorstore = FaissVectorStore()
    generator = CohereGenerator()

    for path in pdf_paths:
        print(f"\n📄 Processing: {path}")
        source_file = os.path.basename(path)
        pages = reader.read(path)
        chunk_docs = chunker.chunk(pages, source_file)
        embeddings = embedder.embed(chunk_docs)
        vectorstore.add(embeddings, chunk_docs)

    return vectorstore, embedder, generator

def interactive_qa(vectorstore: FaissVectorStore, embedder: HuggingFaceEmbedder, generator: CohereGenerator):
    print("\n🔍 Ask questions! Type 'exit' to quit.")
    while True:
        question = input("\n❓ Your question: ").strip()
        if question.lower() in {"exit", "quit"}:
            print("👋 Exiting. Goodbye!")
            break

        query_vector = embedder.embed([
            ChunkDocument(text=question, page=0, chunk_id=0, source_file="query")
        ])[0]

        top_chunks = vectorstore.search(query_vector, k=3)
        print("\n📄 Top Matching Chunks:")
        for i, (chunk, score) in enumerate(top_chunks, 1):
            print(f"\n{i}. Score: {score:.4f}")
            print(f"📘 {chunk.source_file} | 📄 Page: {chunk.page} | 🔢 Chunk ID: {chunk.chunk_id}")
            print(chunk.text)

        answer = generator.generate_answer(question, [c for c, _ in top_chunks])
        print("\n🧠 Answer:")
        print(answer)

if __name__ == "__main__":
    # Example usage
    pdf_dir = "data/"
    pdf_files = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) if f.endswith(".pdf")]

    if not pdf_files:
        print("⚠️ No PDF files found in data/ folder.")
        sys.exit(1)

    vectorstore, embedder, generator = build_index(pdf_files)
    interactive_qa(vectorstore, embedder, generator)