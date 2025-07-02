from sentence_transformers import SentenceTransformer
from typing import List
from backend.embedder.base_embedder import BaseEmbedder
from backend.models.chunk_document import ChunkDocument

class HuggingFaceEmbedder(BaseEmbedder):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initializes the HuggingFaceEmbedder with a specified model.

        :param model_name: The name of the Hugging Face model to use for embedding.
        """
        self.model = SentenceTransformer(model_name)
        
    def embed(self, documents: List[ChunkDocument]) -> List[List[float]]:
        texts = [doc.text for doc in documents]
        embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        return embeddings.tolist()