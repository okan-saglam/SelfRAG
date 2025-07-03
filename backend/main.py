import sys
import os

# Add the project root directory to Python path
# Since this file is in backend/main.py, we need to go up one level to reach project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.reader.pdf_reader import PDFReader
# from backend.chunker.hf_token_chunker import HFTokenChunker
# from backend.chunker.recursive_chunker import RecursiveChunker
# from backend.chunker.semantic_preserving_chunker import SemanticPreservingChunker
from backend.chunker.structure_aware_chunker import StructureAwareChunker
from backend.embedder.hf_embedder import HuggingFaceEmbedder
from backend.vectorstore.faiss_store import FaissVectorStore
from backend.generator.cohere_generator import CohereGenerator
from backend.reranker.hf_reranker import HuggingFaceReranker
from backend.models.chunk_document import ChunkDocument
from backend.utils.index_manager import IndexManager

def build_index(pdf_paths: list[str], force_rebuild: bool = False) -> tuple[FaissVectorStore, HuggingFaceEmbedder, CohereGenerator, HuggingFaceReranker]:
    # Initialize components
    reader = PDFReader()
    chunker = StructureAwareChunker()
    embedder = HuggingFaceEmbedder()
    vectorstore = FaissVectorStore()
    generator = CohereGenerator()
    reranker = HuggingFaceReranker()
    
    # Initialize index manager
    index_manager = IndexManager()
    index_path = index_manager.get_index_path(pdf_paths)
    
    # Check if we can load existing index
    if not force_rebuild and vectorstore.exists(index_path):
        print(f"🔍 Found existing index at: {index_path}")
        if vectorstore.load(index_path):
            print("✅ Successfully loaded existing index!")
            return vectorstore, embedder, generator, reranker
        else:
            print("⚠️ Failed to load existing index, rebuilding...")
    
    # Build new index
    print("🔧 Building new index...")
    
    for path in pdf_paths:
        print(f"\n📄 Processing: {path}")
        source_file = os.path.basename(path)
        pages = reader.read(path)
        chunk_docs = chunker.chunk(pages, source_file)
        embeddings = embedder.embed(chunk_docs)
        vectorstore.add(embeddings, chunk_docs)

    # Save the new index
    print(f"\n💾 Saving index to: {index_path}")
    vectorstore.save(index_path)
    
    # Cleanup old indices
    index_manager.cleanup_old_indices(keep_latest=3)

    return vectorstore, embedder, generator, reranker

def interactive_qa(vectorstore: FaissVectorStore, embedder: HuggingFaceEmbedder, generator: CohereGenerator, reranker: HuggingFaceReranker):
    print("\n🔍 Ask questions! Type 'exit' to quit.")
    while True:
        question = input("\n❓ Your question: ").strip()
        if question.lower() in {"exit", "quit"}:
            print("👋 Exiting. Goodbye!")
            break

        query_vector = embedder.embed([
            ChunkDocument(text=question, page=0, chunk_id=0, source_file="query")
        ])[0]

        # Get initial candidates (more than final k)
        initial_chunks = vectorstore.search(query_vector, k=10)
        
        # Rerank the results
        reranked_chunks = reranker.rerank(question, initial_chunks, top_k=5)
        
        print("\n📄 Top Matching Chunks (After Reranking):")
        for i, (chunk, score) in enumerate(reranked_chunks, 1):
            print(f"\n{i}. Rerank Score: {score:.4f}")
            print(f"📘 {chunk.source_file} | 📄 Page: {chunk.page} | 🔢 Chunk ID: {chunk.chunk_id}")
            print(chunk.text)

        answer = generator.generate_answer(question, [c for c, _ in reranked_chunks])
        print("\n🧠 Answer:")
        print(answer)

if __name__ == "__main__":
    # Example usage
    pdf_dir = "data/"
    pdf_files = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) if f.endswith(".pdf")]

    if not pdf_files:
        print("⚠️ No PDF files found in data/ folder.")
        sys.exit(1)

    # Check for force rebuild flag
    force_rebuild = "--rebuild" in sys.argv
    if force_rebuild:
        print("🔨 Force rebuild requested!")

    vectorstore, embedder, generator, reranker = build_index(pdf_files, force_rebuild)
    interactive_qa(vectorstore, embedder, generator, reranker)