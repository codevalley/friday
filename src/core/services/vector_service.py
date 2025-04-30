from abc import ABC, abstractmethod
from typing import List, Optional


class VectorService(ABC):
    """Interface for vector operations"""
    
    @abstractmethod
    async def create_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        pass
    
    @abstractmethod
    async def similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate similarity between two vectors"""
        pass