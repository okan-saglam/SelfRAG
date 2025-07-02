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

if __name__ == "__main__":
    # Initialize components
    reader = PDFReader()
    chunker = HFTokenChunker()
    embedder = HuggingFaceEmbedder()
    vectorstore = FaissVectorStore()
    generator = CohereGenerator()

    # Read and index document
    text = reader.read("data/Okan_Sağlam_CV.pdf")
    chunks = chunker.chunk(text)
    vectors = embedder.embed(chunks)
    vectorstore.add(vectors, chunks)

    # User question
    question = "What projects has this person worked on?"
    query_vector = embedder.embed([question])[0]
    top_chunks = vectorstore.search(query_vector, k=3)

    # Merge chunks into a single context string
    context = "\n---\n".join(chunk for chunk, _ in top_chunks)

    # Generate final answer
    answer = generator.generate_answer(question, context)

    print("\n🔍 Question:", question)
    print("\n🧠 Answer:")
    print(answer)