import faiss
import numpy as np
import pickle
import os
from pathlib import Path
from sklearn.preprocessing import normalize
from typing import List, Tuple
from backend.vectorstore.base_vectorstore import BaseVectorStore
from backend.models.chunk_document import ChunkDocument

class FaissVectorStore(BaseVectorStore):
    def __init__(self, embedding_dim: int = 384):
        """
        Initializes the FaissVectorStore with a specified embedding dimension.

        :param embedding_dim: The dimension of the embeddings.
        """
        # self.index = faiss.IndexFlatL2(embedding_dim) # L2 distance index
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatIP(embedding_dim)  # Inner product index
        self.documents: List[ChunkDocument] = []
        
    def add(self, embeddings: List[List[float]], documents: List[ChunkDocument]) -> None:
        vectors = np.array(embeddings).astype("float32")
        vectors = normalize(vectors)
        self.index.add(vectors)
        self.documents.extend(documents)
        
    def search(self, query_vector: List[float], k: int = 5) -> List[Tuple[ChunkDocument, float]]:
        query = np.array([query_vector]).astype("float32")
        query = normalize(query)
        distances, indices = self.index.search(query, k)

        results = []
        for idx, score in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(score)))
        return results
    
    def save(self, index_path: str) -> None:
        try:
            # Create directory if it doesn't exist
            Path(index_path).mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            faiss_path = os.path.join(index_path, "faiss_index.bin")
            faiss.write_index(self.index, faiss_path)
            
            # Save documents metadata
            docs_path = os.path.join(index_path, "documents.pkl")
            with open(docs_path, 'wb') as f:
                pickle.dump(self.documents, f)
            
            # Save configuration
            config_path = os.path.join(index_path, "config.pkl")
            config = {
                'embedding_dim': self.embedding_dim,
                'num_documents': len(self.documents)
            }
            with open(config_path, 'wb') as f:
                pickle.dump(config, f)
                
            print(f"✅ Index saved successfully to {index_path}")
            
        except Exception as e:
            print(f"❌ Error saving index: {e}")
            raise
    
    def load(self, index_path: str) -> bool:
        try:
            faiss_path = os.path.join(index_path, "faiss_index.bin")
            docs_path = os.path.join(index_path, "documents.pkl")
            config_path = os.path.join(index_path, "config.pkl")
            
            # Check if all required files exist
            if not all(os.path.exists(p) for p in [faiss_path, docs_path, config_path]):
                return False
            
            # Load configuration
            with open(config_path, 'rb') as f:
                config = pickle.load(f)
            
            # Verify embedding dimension matches
            if config['embedding_dim'] != self.embedding_dim:
                print(f"⚠️ Embedding dimension mismatch: expected {self.embedding_dim}, got {config['embedding_dim']}")
                return False
            
            # Load FAISS index
            self.index = faiss.read_index(faiss_path)
            
            # Load documents
            with open(docs_path, 'rb') as f:
                self.documents = pickle.load(f)
            
            print(f"✅ Index loaded successfully from {index_path}")
            print(f"📊 Loaded {len(self.documents)} documents")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading index: {e}")
            return False
    
    def exists(self, index_path: str) -> bool:
        required_files = [
            os.path.join(index_path, "faiss_index.bin"),
            os.path.join(index_path, "documents.pkl"),
            os.path.join(index_path, "config.pkl")
        ]
        return all(os.path.exists(f) for f in required_files)