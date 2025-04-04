from abc import ABC, abstractmethod
from typing import List, Optional

from src.core.domain.user import User


class UserRepository(ABC):
    """Abstract interface for user persistence operations"""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[User]:
        """Get a user by name"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update a user"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Delete a user"""
        pass
    
    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users with pagination"""
        pass