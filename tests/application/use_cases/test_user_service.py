import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.application.use_cases.user_uc import UserService
from src.core.domain.user import User
from src.core.repositories.user_repo import UserRepository
from src.core.services.auth_service import AuthService
from src.core.use_cases.user_dtos import UserCreateDTO, UserLoginDTO, UserUpdateDTO


@pytest.fixture
def mock_user_repo():
    """Create a mocked user repository"""
    mock = AsyncMock(spec=UserRepository)
    
    # Mock user for tests
    user = User(
        user_id="user123",
        name="testuser",
        user_secret="hashed_password",
        tier="free",
        created_at=datetime.now()
    )
    
    # Configure mock methods
    mock.get_by_id.return_value = user
    mock.get_by_name.return_value = user
    mock.create.return_value = user
    mock.update.return_value = user
    mock.delete.return_value = True
    mock.list.return_value = [user]
    
    return mock


@pytest.fixture
def mock_auth_service():
    """Create a mocked auth service"""
    mock = AsyncMock(spec=AuthService)
    
    # Configure mock methods
    mock.hash_password.return_value = "hashed_password"
    mock.verify_password.return_value = True
    mock.create_token.return_value = "mock_token"
    
    return mock


@pytest.fixture
def user_service(mock_user_repo, mock_auth_service):
    """Create a user service with mocked dependencies"""
    return UserService(mock_user_repo, mock_auth_service)


@pytest.mark.asyncio
async def test_create_user_success(user_service, mock_user_repo, mock_auth_service):
    """Test successful user creation"""
    # Configure mock to simulate non-existent user (for name check)
    mock_user_repo.get_by_name.return_value = None
    
    # Create DTO
    user_dto = UserCreateDTO(
        name="newuser",
        password="password123",
        tier="free"
    )
    
    # Call service method
    result = await user_service.create_user(user_dto)
    
    # Verify result
    assert result.name == "testuser"  # From the mocked response
    
    # Verify interactions
    mock_user_repo.get_by_name.assert_called_once_with("newuser")
    mock_auth_service.hash_password.assert_called_once_with("password123")
    mock_user_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_duplicate_name(user_service, mock_user_repo):
    """Test user creation with duplicate name raises error"""
    # Mock will return a user, simulating a duplicate name
    user_dto = UserCreateDTO(
        name="existinguser",
        password="password123"
    )
    
    # Call service method and expect error
    with pytest.raises(ValueError, match="User with name .* already exists"):
        await user_service.create_user(user_dto)
    
    # Verify interactions
    mock_user_repo.get_by_name.assert_called_once_with("existinguser")
    mock_user_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_authenticate_user_success(user_service, mock_user_repo, mock_auth_service):
    """Test successful user authentication"""
    login_dto = UserLoginDTO(
        name="testuser",
        password="password123"
    )
    
    # Call service method
    result = await user_service.authenticate_user(login_dto)
    
    # Verify result
    assert result is not None
    assert result.access_token == "mock_token"
    assert result.token_type == "bearer"
    
    # Verify interactions
    mock_user_repo.get_by_name.assert_called_once_with("testuser")
    mock_auth_service.verify_password.assert_called_once_with(
        "password123", "hashed_password"
    )
    mock_auth_service.create_token.assert_called_once()


@pytest.mark.asyncio
async def test_authenticate_user_invalid_credentials(user_service, mock_user_repo, mock_auth_service):
    """Test authentication with invalid credentials returns None"""
    # Configure mock to fail password verification
    mock_auth_service.verify_password.return_value = False
    
    login_dto = UserLoginDTO(
        name="testuser",
        password="wrong_password"
    )
    
    # Call service method
    result = await user_service.authenticate_user(login_dto)
    
    # Verify result
    assert result is None
    
    # Verify interactions
    mock_user_repo.get_by_name.assert_called_once_with("testuser")
    mock_auth_service.verify_password.assert_called_once()
    mock_auth_service.create_token.assert_not_called()


@pytest.mark.asyncio
async def test_authenticate_user_nonexistent(user_service, mock_user_repo):
    """Test authentication with non-existent user returns None"""
    # Configure mock to return no user
    mock_user_repo.get_by_name.return_value = None
    
    login_dto = UserLoginDTO(
        name="nonexistent",
        password="password123"
    )
    
    # Call service method
    result = await user_service.authenticate_user(login_dto)
    
    # Verify result
    assert result is None
    
    # Verify interactions
    mock_user_repo.get_by_name.assert_called_once_with("nonexistent")


@pytest.mark.asyncio
async def test_get_user_by_id(user_service, mock_user_repo):
    """Test getting a user by ID"""
    # Call service method
    result = await user_service.get_user_by_id("user123")
    
    # Verify result
    assert result is not None
    assert result.user_id == "user123"
    assert result.name == "testuser"
    
    # Verify interactions
    mock_user_repo.get_by_id.assert_called_once_with("user123")


@pytest.mark.asyncio
async def test_get_nonexistent_user(user_service, mock_user_repo):
    """Test getting a non-existent user returns None"""
    # Configure mock to return no user
    mock_user_repo.get_by_id.return_value = None
    
    # Call service method
    result = await user_service.get_user_by_id("nonexistent")
    
    # Verify result
    assert result is None
    
    # Verify interactions
    mock_user_repo.get_by_id.assert_called_once_with("nonexistent")


@pytest.mark.asyncio
async def test_update_user(user_service, mock_user_repo, mock_auth_service):
    """Test updating a user"""
    # Create update DTO
    update_dto = UserUpdateDTO(
        name="updateduser",
        password="newpassword",
        tier="premium"
    )
    
    # Call service method
    result = await user_service.update_user("user123", update_dto)
    
    # Verify result
    assert result is not None
    
    # Verify interactions
    mock_user_repo.get_by_id.assert_called_once_with("user123")
    mock_auth_service.hash_password.assert_called_once_with("newpassword")
    mock_user_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_partial_user(user_service, mock_user_repo):
    """Test updating a user with partial data"""
    # Create update DTO with only name
    update_dto = UserUpdateDTO(name="updateduser")
    
    # Call service method
    result = await user_service.update_user("user123", update_dto)
    
    # Verify result
    assert result is not None
    
    # Verify interactions
    mock_user_repo.get_by_id.assert_called_once_with("user123")
    mock_user_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_nonexistent_user(user_service, mock_user_repo):
    """Test updating a non-existent user returns None"""
    # Configure mock to return no user
    mock_user_repo.get_by_id.return_value = None
    
    update_dto = UserUpdateDTO(name="updateduser")
    
    # Call service method
    result = await user_service.update_user("nonexistent", update_dto)
    
    # Verify result
    assert result is None
    
    # Verify interactions
    mock_user_repo.get_by_id.assert_called_once_with("nonexistent")
    mock_user_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_delete_user(user_service, mock_user_repo):
    """Test deleting a user"""
    # Call service method
    result = await user_service.delete_user("user123")
    
    # Verify result
    assert result is True
    
    # Verify interactions
    mock_user_repo.delete.assert_called_once_with("user123")


@pytest.mark.asyncio
async def test_list_users(user_service, mock_user_repo):
    """Test listing users with pagination"""
    # Call service method
    result = await user_service.list_users(skip=10, limit=20)
    
    # Verify result
    assert len(result) == 1
    assert result[0].name == "testuser"
    
    # Verify interactions
    mock_user_repo.list.assert_called_once_with(skip=10, limit=20)