from abc import ABC, abstractmethod
from typing import List, Optional

from src.core.domain.note import Note


class NoteRepository(ABC):
    """Abstract interface for note persistence operations"""
    
    @abstractmethod
    async def create(self, note: Note) -> Note:
        """Create a new note"""
        pass
    
    @abstractmethod
    async def get_by_id(self, note_id: str) -> Optional[Note]:
        """Get a note by ID"""
        pass
    
    @abstractmethod
    async def update(self, note: Note) -> Note:
        """Update a note"""
        pass
    
    @abstractmethod
    async def delete(self, note_id: str) -> bool:
        """Delete a note"""
        pass
    
    @abstractmethod
    async def list_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Note]:
        """List notes for a specific user with pagination"""
        pass
    
    @abstractmethod
    async def search_by_vector(
        self, 
        embedding: List[float], 
        user_id: Optional[str] = None, 
        limit: int = 10
    ) -> List[Note]:
        """Search notes by vector similarity"""
        pass