import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch

from src.infrastructure.services.redis.cache_service import RedisCacheService


@pytest.fixture
def mock_redis():
    """Create a mock Redis client"""
    mock = AsyncMock()
    
    # Configure mock methods
    mock.get.return_value = None  # Default to cache miss
    mock.set.return_value = True
    mock.setex.return_value = True
    mock.delete.return_value = 1
    mock.flushdb.return_value = True
    
    return mock


@pytest.fixture
def cache_service(mock_redis):
    """Create a cache service with mocked Redis client"""
    service = RedisCacheService("redis://localhost:6379/0")
    service.redis = mock_redis
    return service


@pytest.mark.asyncio
async def test_get_cache_hit(cache_service, mock_redis):
    """Test getting an item from cache (cache hit)"""
    # Configure mock to return cached data
    cached_data = json.dumps({"key": "value"})
    mock_redis.get.return_value = cached_data
    
    # Call service method
    result = await cache_service.get("test_key")
    
    # Verify result
    assert result == {"key": "value"}
    
    # Verify interactions
    mock_redis.get.assert_called_once_with("test_key")


@pytest.mark.asyncio
async def test_get_cache_miss(cache_service, mock_redis):
    """Test getting an item from cache (cache miss)"""
    # Mock is already configured for cache miss
    
    # Call service method
    result = await cache_service.get("test_key")
    
    # Verify result
    assert result is None
    
    # Verify interactions
    mock_redis.get.assert_called_once_with("test_key")


@pytest.mark.asyncio
async def test_get_deserialize_error(cache_service, mock_redis):
    """Test getting an item with deserialization error"""
    # Configure mock to return invalid JSON
    mock_redis.get.return_value = "not valid json"
    
    # Call service method
    result = await cache_service.get("test_key")
    
    # Verify result (should return None on error)
    assert result is None
    
    # Verify interactions
    mock_redis.get.assert_called_once_with("test_key")


@pytest.mark.asyncio
async def test_set_without_expiration(cache_service, mock_redis):
    """Test setting an item in cache without expiration"""
    # Call service method
    result = await cache_service.set("test_key", {"key": "value"})
    
    # Verify result
    assert result is True
    
    # Verify interactions
    mock_redis.set.assert_called_once_with("test_key", json.dumps({"key": "value"}))
    mock_redis.setex.assert_not_called()


@pytest.mark.asyncio
async def test_set_with_expiration(cache_service, mock_redis):
    """Test setting an item in cache with expiration"""
    # Call service method
    result = await cache_service.set("test_key", {"key": "value"}, expire=60)
    
    # Verify result
    assert result is True
    
    # Verify interactions
    mock_redis.set.assert_not_called()
    mock_redis.setex.assert_called_once_with("test_key", 60, json.dumps({"key": "value"}))


@pytest.mark.asyncio
async def test_set_serialize_error(cache_service, mock_redis):
    """Test setting an item with serialization error"""
    # Create an object that can't be serialized to JSON
    class UnserializableObject:
        def __init__(self):
            self.circular_ref = self
    
    unserializable = UnserializableObject()
    
    # Call service method
    result = await cache_service.set("test_key", unserializable)
    
    # Verify result (should return False on error)
    assert result is False
    
    # Verify interactions
    mock_redis.set.assert_not_called()
    mock_redis.setex.assert_not_called()


@pytest.mark.asyncio
async def test_delete(cache_service, mock_redis):
    """Test deleting an item from cache"""
    # Call service method
    result = await cache_service.delete("test_key")
    
    # Verify result
    assert result is True
    
    # Verify interactions
    mock_redis.delete.assert_called_once_with("test_key")


@pytest.mark.asyncio
async def test_delete_not_found(cache_service, mock_redis):
    """Test deleting a non-existent item from cache"""
    # Configure mock to return 0 (no keys deleted)
    mock_redis.delete.return_value = 0
    
    # Call service method
    result = await cache_service.delete("non_existent_key")
    
    # Verify result (should still return True)
    assert result is True
    
    # Verify interactions
    mock_redis.delete.assert_called_once_with("non_existent_key")


@pytest.mark.asyncio
async def test_flush(cache_service, mock_redis):
    """Test flushing the cache"""
    # Call service method
    result = await cache_service.flush()
    
    # Verify result
    assert result is True
    
    # Verify interactions
    mock_redis.flushdb.assert_called_once()


@pytest.mark.asyncio
async def test_no_redis_connection():
    """Test behavior when Redis connection fails"""
    # Create service with no Redis connection
    service = RedisCacheService("redis://nonexistent:6379/0")
    service.redis = None  # Simulate connection failure
    
    # Test all methods
    assert await service.get("test_key") is None
    assert await service.set("test_key", {"key": "value"}) is False
    assert await service.delete("test_key") is False
    assert await service.flush() is False