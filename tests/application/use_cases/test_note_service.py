import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.application.use_cases.note_uc import NoteService
from src.core.domain.note import Note
from src.core.domain.user import User
from src.core.repositories.note_repo import NoteRepository
from src.core.repositories.user_repo import UserRepository
from src.core.services.cache_service import CacheService
from src.core.use_cases.note_dtos import NoteCreateDTO, NoteUpdateDTO


@pytest.fixture
def mock_note_repo():
    """Create a mocked note repository"""
    mock = AsyncMock(spec=NoteRepository)
    
    # Mock note for tests
    note = Note(
        note_id="note123",
        user_id="user123",
        content="Test note content",
        created=datetime.now()
    )
    
    # Configure mock methods
    mock.get_by_id.return_value = note
    mock.create.return_value = note
    mock.update.return_value = note
    mock.delete.return_value = True
    mock.list_by_user.return_value = [note]
    
    return mock


@pytest.fixture
def mock_user_repo():
    """Create a mocked user repository"""
    mock = AsyncMock(spec=UserRepository)
    
    # Mock user for tests
    user = User(
        user_id="user123",
        name="testuser",
        user_secret="hashed_password",
        tier="free"
    )
    
    # Configure mock methods
    mock.get_by_id.return_value = user
    
    return mock


@pytest.fixture
def mock_cache_service():
    """Create a mocked cache service"""
    mock = AsyncMock(spec=CacheService)
    
    # Configure mock methods
    mock.get.return_value = None  # Default to cache miss
    mock.set.return_value = True
    mock.delete.return_value = True
    
    return mock


@pytest.fixture
def note_service(mock_note_repo, mock_user_repo, mock_cache_service):
    """Create a note service with mocked dependencies"""
    return NoteService(mock_note_repo, mock_user_repo, mock_cache_service)


@pytest.mark.asyncio
async def test_create_note_success(note_service, mock_note_repo, mock_user_repo, mock_cache_service):
    """Test successful note creation"""
    # Create DTO
    note_dto = NoteCreateDTO(content="New test note")
    
    # Call service method
    result = await note_service.create_note(note_dto, "user123")
    
    # Verify result
    assert result.content == "Test note content"  # From the mocked response
    
    # Verify interactions
    mock_user_repo.get_by_id.assert_called_once_with("user123")
    mock_note_repo.create.assert_called_once()
    mock_cache_service.delete.assert_called_once_with("user:user123:notes")


@pytest.mark.asyncio
async def test_create_note_nonexistent_user(note_service, mock_user_repo):
    """Test note creation with non-existent user raises error"""
    # Configure mock to return no user
    mock_user_repo.get_by_id.return_value = None
    
    note_dto = NoteCreateDTO(content="New test note")
    
    # Call service method and expect error
    with pytest.raises(ValueError, match="User with ID .* not found"):
        await note_service.create_note(note_dto, "nonexistent")
    
    # Verify interactions
    mock_user_repo.get_by_id.assert_called_once_with("nonexistent")


@pytest.mark.asyncio
async def test_get_note_by_id_success(note_service, mock_note_repo):
    """Test successful note retrieval by ID"""
    # Call service method
    result = await note_service.get_note_by_id("note123", "user123")
    
    # Verify result
    assert result is not None
    assert result.note_id == "note123"
    assert result.content == "Test note content"
    
    # Verify interactions
    mock_note_repo.get_by_id.assert_called_once_with("note123")


@pytest.mark.asyncio
async def test_get_note_by_id_not_found(note_service, mock_note_repo):
    """Test note retrieval when not found returns None"""
    # Configure mock to return no note
    mock_note_repo.get_by_id.return_value = None
    
    # Call service method
    result = await note_service.get_note_by_id("nonexistent", "user123")
    
    # Verify result
    assert result is None
    
    # Verify interactions
    mock_note_repo.get_by_id.assert_called_once_with("nonexistent")


@pytest.mark.asyncio
async def test_get_note_by_id_wrong_user(note_service, mock_note_repo):
    """Test note retrieval by wrong user returns None"""
    # Call service method with different user ID
    result = await note_service.get_note_by_id("note123", "wrong_user")
    
    # Verify result
    assert result is None
    
    # Verify interactions
    mock_note_repo.get_by_id.assert_called_once_with("note123")


@pytest.mark.asyncio
async def test_update_note_success(note_service, mock_note_repo, mock_cache_service):
    """Test successful note update"""
    # Create update DTO
    update_dto = NoteUpdateDTO(content="Updated content")
    
    # Call service method
    result = await note_service.update_note("note123", update_dto, "user123")
    
    # Verify result
    assert result is not None
    assert result.note_id == "note123"
    
    # Verify interactions
    mock_note_repo.get_by_id.assert_called_once_with("note123")
    mock_note_repo.update.assert_called_once()
    mock_cache_service.delete.assert_called_once_with("user:user123:notes")


@pytest.mark.asyncio
async def test_update_note_not_found(note_service, mock_note_repo):
    """Test note update when not found returns None"""
    # Configure mock to return no note
    mock_note_repo.get_by_id.return_value = None
    
    update_dto = NoteUpdateDTO(content="Updated content")
    
    # Call service method
    result = await note_service.update_note("nonexistent", update_dto, "user123")
    
    # Verify result
    assert result is None
    
    # Verify interactions
    mock_note_repo.get_by_id.assert_called_once_with("nonexistent")
    mock_note_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_update_note_wrong_user(note_service, mock_note_repo):
    """Test note update by wrong user returns None"""
    update_dto = NoteUpdateDTO(content="Updated content")
    
    # Call service method with different user ID
    result = await note_service.update_note("note123", update_dto, "wrong_user")
    
    # Verify result
    assert result is None
    
    # Verify interactions
    mock_note_repo.get_by_id.assert_called_once_with("note123")
    mock_note_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_delete_note_success(note_service, mock_note_repo, mock_cache_service):
    """Test successful note deletion"""
    # Call service method
    result = await note_service.delete_note("note123", "user123")
    
    # Verify result
    assert result is True
    
    # Verify interactions
    mock_note_repo.get_by_id.assert_called_once_with("note123")
    mock_note_repo.delete.assert_called_once_with("note123")
    mock_cache_service.delete.assert_called_once_with("user:user123:notes")


@pytest.mark.asyncio
async def test_delete_note_not_found(note_service, mock_note_repo):
    """Test note deletion when not found returns False"""
    # Configure mock to return no note
    mock_note_repo.get_by_id.return_value = None
    
    # Call service method
    result = await note_service.delete_note("nonexistent", "user123")
    
    # Verify result
    assert result is False
    
    # Verify interactions
    mock_note_repo.get_by_id.assert_called_once_with("nonexistent")
    mock_note_repo.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_note_wrong_user(note_service, mock_note_repo):
    """Test note deletion by wrong user returns False"""
    # Call service method with different user ID
    result = await note_service.delete_note("note123", "wrong_user")
    
    # Verify result
    assert result is False
    
    # Verify interactions
    mock_note_repo.get_by_id.assert_called_once_with("note123")
    mock_note_repo.delete.assert_not_called()


@pytest.mark.asyncio
async def test_list_user_notes_from_repo(note_service, mock_note_repo, mock_cache_service):
    """Test listing user notes from repository (cache miss)"""
    # Call service method
    result = await note_service.list_user_notes("user123")
    
    # Verify result
    assert len(result) == 1
    assert result[0].note_id == "note123"
    assert result[0].content == "Test note content"
    
    # Verify interactions
    mock_cache_service.get.assert_called_once_with("user:user123:notes")
    mock_note_repo.list_by_user.assert_called_once_with(
        user_id="user123", skip=0, limit=100
    )
    mock_cache_service.set.assert_called_once()


@pytest.mark.asyncio
async def test_list_user_notes_from_cache(note_service, mock_note_repo, mock_cache_service):
    """Test listing user notes from cache (cache hit)"""
    # Configure mock to return cached notes
    cached_notes = [
        {
            "note_id": "note123",
            "user_id": "user123",
            "content": "Cached note content",
            "created": datetime.now().isoformat()
        }
    ]
    mock_cache_service.get.return_value = cached_notes
    
    # Call service method
    result = await note_service.list_user_notes("user123")
    
    # Verify result
    assert len(result) == 1
    assert result[0].note_id == "note123"
    assert result[0].content == "Cached note content"
    
    # Verify interactions
    mock_cache_service.get.assert_called_once_with("user:user123:notes")
    mock_note_repo.list_by_user.assert_not_called()
    mock_cache_service.set.assert_not_called()


@pytest.mark.asyncio
async def test_list_user_notes_with_pagination(note_service, mock_note_repo, mock_cache_service):
    """Test listing user notes with pagination (should bypass cache)"""
    # Call service method with pagination
    result = await note_service.list_user_notes("user123", skip=10, limit=5)
    
    # Verify result
    assert len(result) == 1
    
    # Verify interactions
    # Should not use cache for custom pagination
    mock_cache_service.get.assert_not_called()
    mock_note_repo.list_by_user.assert_called_once_with(
        user_id="user123", skip=10, limit=5
    )
    mock_cache_service.set.assert_not_called()


@pytest.mark.asyncio
async def test_list_user_notes_no_cache_service(mock_note_repo, mock_user_repo):
    """Test listing user notes without cache service"""
    # Create service without cache
    service = NoteService(mock_note_repo, mock_user_repo)
    
    # Call service method
    result = await service.list_user_notes("user123")
    
    # Verify result
    assert len(result) == 1
    
    # Verify interactions
    mock_note_repo.list_by_user.assert_called_once_with(
        user_id="user123", skip=0, limit=100
    )