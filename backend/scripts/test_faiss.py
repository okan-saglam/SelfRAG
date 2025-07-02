import sys
import os

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from backend.reader.pdf_reader import PDFReader
from backend.chunker.hf_token_chunker import HFTokenChunker
from backend.embedder.hf_embedder import HuggingFaceEmbedder
from backend.vectorstore.faiss_store import FaissVectorStore

if __name__ == "__main__":
    # Initialize pipeline components
    reader = PDFReader()
    chunker = HFTokenChunker()
    embedder = HuggingFaceEmbedder()
    vectorstore = FaissVectorStore()

    # Load and preprocess document
    text = reader.read("data/Okan_Sağlam_CV.pdf")
    chunks = chunker.chunk(text)
    embeddings = embedder.embed(chunks)

    # Add embeddings and texts to the vector store
    vectorstore.add(embeddings, chunks)

    # Define a user query
    query = "What technologies does this person know?"
    query_vector = embedder.embed([query])[0]

    # Search for the top 3 most relevant chunks
    results = vectorstore.search(query_vector, k=3)

    print("\n🔍 Query:", query)
    print("\n📄 Top Matching Chunks:")
    for i, (text, score) in enumerate(results, 1):
        print(f"\n{i}. Score: {score:.2f}")
        print(text)