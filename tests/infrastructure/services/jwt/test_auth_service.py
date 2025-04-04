import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch

from src.infrastructure.services.jwt.auth_service import JWTAuthService


@pytest.fixture
def auth_service():
    """Create an instance of JWTAuthService with a test secret key"""
    return JWTAuthService(secret_key="test_secret_key", token_expires_minutes=30)


@pytest.mark.asyncio
async def test_create_token(auth_service):
    """Test token creation"""
    # Create a token
    user_id = "user123"
    extra_data = {"name": "testuser", "tier": "free"}
    
    token = await auth_service.create_token(user_id, extra_data)
    
    # Verify token is a string
    assert isinstance(token, str)
    
    # Decode token and verify payload
    payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
    
    assert payload["sub"] == user_id
    assert payload["name"] == "testuser"
    assert payload["tier"] == "free"
    assert "exp" in payload
    assert "iat" in payload


@pytest.mark.asyncio
async def test_validate_token_valid(auth_service):
    """Test validation of a valid token"""
    # Create payload for a valid token
    user_id = "user123"
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "iat": datetime.utcnow(),
        "name": "testuser"
    }
    
    # Create token with test secret
    token = jwt.encode(payload, "test_secret_key", algorithm="HS256")
    
    # Validate token
    result = await auth_service.validate_token(token)
    
    # Verify result
    assert result is not None
    assert result["sub"] == user_id
    assert result["name"] == "testuser"


@pytest.mark.asyncio
async def test_validate_token_expired(auth_service):
    """Test validation of an expired token"""
    # Create payload for an expired token
    user_id = "user123"
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() - timedelta(minutes=5),  # Expired
        "iat": datetime.utcnow() - timedelta(minutes=35),
        "name": "testuser"
    }
    
    # Create token with test secret
    token = jwt.encode(payload, "test_secret_key", algorithm="HS256")
    
    # Validate token
    result = await auth_service.validate_token(token)
    
    # Verify result
    assert result is None


@pytest.mark.asyncio
async def test_validate_token_invalid_signature(auth_service):
    """Test validation of a token with invalid signature"""
    # Create payload
    user_id = "user123"
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "iat": datetime.utcnow(),
        "name": "testuser"
    }
    
    # Create token with wrong secret
    token = jwt.encode(payload, "wrong_secret_key", algorithm="HS256")
    
    # Validate token
    result = await auth_service.validate_token(token)
    
    # Verify result
    assert result is None


@pytest.mark.asyncio
async def test_validate_token_invalid_format(auth_service):
    """Test validation of a token with invalid format"""
    # Validate token with invalid format
    result = await auth_service.validate_token("not.a.valid.token")
    
    # Verify result
    assert result is None


@pytest.mark.asyncio
async def test_hash_password(auth_service):
    """Test password hashing"""
    password = "secure_password"
    
    # Hash password
    hashed = await auth_service.hash_password(password)
    
    # Verify result
    assert hashed != password
    assert isinstance(hashed, str)
    assert hashed.startswith("$2")  # Bcrypt hash format


@pytest.mark.asyncio
async def test_verify_password_valid(auth_service):
    """Test verification of a valid password"""
    password = "secure_password"
    
    # Hash password
    hashed = await auth_service.hash_password(password)
    
    # Verify correct password
    result = await auth_service.verify_password(password, hashed)
    
    assert result is True


@pytest.mark.asyncio
async def test_verify_password_invalid(auth_service):
    """Test verification of an invalid password"""
    password = "secure_password"
    wrong_password = "wrong_password"
    
    # Hash password
    hashed = await auth_service.hash_password(password)
    
    # Verify wrong password
    result = await auth_service.verify_password(wrong_password, hashed)
    
    assert result is False


@pytest.mark.asyncio
async def test_default_secret_key_generation():
    """Test that a default secret key is generated if not provided"""
    # Create service without providing a secret key
    service = JWTAuthService()
    
    # Verify a secret key was generated
    assert service.secret_key is not None
    assert len(service.secret_key) > 0