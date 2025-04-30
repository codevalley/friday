from typing import List

import numpy as np

from src.config import get_settings
from src.core.services.vector_service import VectorService


class BasicVectorService(VectorService):
    """Simple implementation of VectorService using cosine similarity"""
    
    async def create_embedding(self, text: str) -> List[float]:
        """
        Create a simple embedding for text.
        
        In a real application, you would use a proper embedding model
        like OpenAI's text-embedding-ada-002 or a local model.
        This is just a simple implementation for testing.
        """
        # Create a very simple embedding (not useful for real search)
        import hashlib
        
        # Generate a hash of the text
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert hash to a list of floats
        np_array = np.frombuffer(hash_bytes, dtype=np.uint8)
        
        # Get dimensions from settings
        settings = get_settings()
        dimensions = getattr(settings, "vector_dimensions", 384)
        
        # Resize to correct dimensions and normalize
        embedding = np.zeros(dimensions)
        for i, value in enumerate(np_array):
            if i < dimensions:
                embedding[i] = value / 255.0
        
        # Normalize to unit length
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding.tolist()
    
    async def similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        # Convert to numpy arrays
        a = np.array(vec1)
        b = np.array(vec2)
        
        # Calculate cosine similarity
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return dot_product / (norm_a * norm_b)