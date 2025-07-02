import cohere
import os
from typing import List
from dotenv import load_dotenv
from backend.generator.base_generator import BaseGenerator
from backend.models.chunk_document import ChunkDocument

class CohereGenerator(BaseGenerator):
    def __init__(self):
        """
        Initializes the CohereGenerator with the provided API key.

        :param api_key: The API key for accessing the Cohere service.
        """
        load_dotenv()
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            raise ValueError("COHERE_API_KEY environment variable is not set.")
        self.client = cohere.Client(api_key)
        
    def generate_answer(self, question: str, context_chunks: List[ChunkDocument]) -> str:
        # Merge chunk texts
        context_text = "\n---\n".join(chunk.text for chunk in context_chunks)

        prompt = (
            f"Answer the question based on the context provided.\n\n"
            f"Context: {context_text}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )

        response = self.client.generate(
            prompt=prompt,
            model="command-r-plus",
            max_tokens=200,
            temperature=0.3,
        )
        
        return response.generations[0].text.strip() if response.generations else "No answer generated."