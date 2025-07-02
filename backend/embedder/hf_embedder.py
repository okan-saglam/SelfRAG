from sentence_transformers import SentenceTransformer
from typing import List
from backend.embedder.base_embedder import BaseEmbedder

class HuggingFaceEmbedder(BaseEmbedder):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initializes the HuggingFaceEmbedder with a specified model.

        :param model_name: The name of the Hugging Face model to use for embedding.
        """
        self.model = SentenceTransformer(model_name)
        
    def embed(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True).tolist()