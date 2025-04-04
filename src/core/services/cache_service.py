from abc import ABC, abstractmethod
from typing import Any, Optional


class CacheService(ABC):
    """Abstract interface for caching operations"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache by key"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a value in cache with optional expiration in seconds"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a value from cache"""
        pass
    
    @abstractmethod
    async def flush(self) -> bool:
        """Clear all cache entries"""
        pass