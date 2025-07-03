import sys
import os

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from backend.reader.pdf_reader import PDFReader
from backend.chunker.structure_aware_chunker import StructureAwareChunker
from backend.embedder.hf_embedder import HuggingFaceEmbedder
from backend.vectorstore.faiss_store import FaissVectorStore
from backend.reranker.hf_reranker import HuggingFaceReranker
from backend.models.chunk_document import ChunkDocument

def test_reranker_effectiveness():
    # Initialize components
    reader = PDFReader()
    chunker = StructureAwareChunker()
    embedder = HuggingFaceEmbedder()
    vectorstore = FaissVectorStore()
    reranker = HuggingFaceReranker()

    # Process documents
    pdf_dir = "data/"
    pdf_files = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
    
    for path in pdf_files:
        source_file = os.path.basename(path)
        pages = reader.read(path)
        chunk_docs = chunker.chunk(pages, source_file)
        embeddings = embedder.embed(chunk_docs)
        vectorstore.add(embeddings, chunk_docs)

    # Test questions that should benefit from reranking
    test_questions = [
        "What technologies does this person know?",
        "Tell me about the THE3 project",
        "What algorithms were used for image segmentation?",
        "What is the education background?",
        "Which clustering method performed best?"
    ]

    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"🔍 QUESTION: {question}")
        print('='*60)
        
        # Get query embedding
        query_vector = embedder.embed([
            ChunkDocument(text=question, page=0, chunk_id=0, source_file="query")
        ])[0]

        # Get initial search results
        initial_chunks = vectorstore.search(query_vector, k=10)
        
        print(f"\n📄 BEFORE RERANKING (Top 5):")
        for i, (chunk, score) in enumerate(initial_chunks[:5], 1):
            print(f"\n{i}. Vector Score: {score:.4f}")
            print(f"📘 {chunk.source_file} | Page: {chunk.page}")
            print(f"Text: {chunk.text[:150]}...")

        # Apply reranking
        reranked_chunks = reranker.rerank(question, initial_chunks, top_k=5)
        
        print(f"\n🎯 AFTER RERANKING (Top 5):")
        for i, (chunk, score) in enumerate(reranked_chunks, 1):
            print(f"\n{i}. Rerank Score: {score:.4f}")
            print(f"📘 {chunk.source_file} | Page: {chunk.page}")
            print(f"Text: {chunk.text[:150]}...")
            
        # Show if order changed
        original_order = [chunk.chunk_id for chunk, _ in initial_chunks[:5]]
        reranked_order = [chunk.chunk_id for chunk, _ in reranked_chunks]
        
        if original_order != reranked_order:
            print(f"\n✅ ORDER CHANGED: Reranking had an effect!")
        else:
            print(f"\n⚪ NO CHANGE: Order remained the same")

if __name__ == "__main__":
    test_reranker_effectiveness()