import json
import logging
from typing import Any, Dict, Optional

import redis.asyncio as redis

from src.config import get_settings
from src.core.services.cache_service import CacheService

settings = get_settings()
logger = logging.getLogger(__name__)


class RedisCacheService(CacheService):
    """Redis implementation of CacheService"""
    
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize Redis connection"""
        self.redis_url = redis_url or settings.redis_url
        try:
            self.redis = redis.from_url(self.redis_url)
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache by key"""
        if not self.redis:
            return None
        
        try:
            value = await self.redis.get(key)
            if not value:
                return None
            
            return json.loads(value)
        except Exception as e:
            logger.error(f"Error getting key {key} from Redis: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a value in cache with optional expiration in seconds"""
        if not self.redis:
            return False
        
        try:
            serialized = json.dumps(value)
            if expire:
                await self.redis.setex(key, expire, serialized)
            else:
                await self.redis.set(key, serialized)
            return True
        except Exception as e:
            logger.error(f"Error setting key {key} in Redis: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete a value from cache"""
        if not self.redis:
            return False
        
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting key {key} from Redis: {e}")
            return False
    
    async def flush(self) -> bool:
        """Clear all cache entries"""
        if not self.redis:
            return False
        
        try:
            await self.redis.flushdb()
            return True
        except Exception as e:
            logger.error(f"Error flushing Redis: {e}")
            return False