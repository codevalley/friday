import pytest
from datetime import datetime, timedelta

from src.core.domain.user import User


def test_user_creation():
    """Test user entity creation with all attributes"""
    now = datetime.now()
    user = User(
        user_id="user123",
        name="testuser",
        user_secret="hashed_password",
        tier="free",
        created_at=now
    )
    
    assert user.user_id == "user123"
    assert user.name == "testuser"
    assert user.user_secret == "hashed_password"
    assert user.tier == "free"
    assert user.created_at == now


def test_user_defaults():
    """Test user entity defaults"""
    user = User()
    
    assert user.user_id is None
    assert user.name == ""
    assert user.user_secret == ""
    assert user.tier == "free"
    assert isinstance(user.created_at, datetime)


def test_user_minimal_creation():
    """Test user creation with minimal attributes"""
    user = User(name="testuser", user_secret="hashed_password")
    
    assert user.user_id is None
    assert user.name == "testuser"
    assert user.user_secret == "hashed_password"
    assert user.tier == "free"
    assert isinstance(user.created_at, datetime)


def test_user_with_premium_tier():
    """Test user with premium tier"""
    user = User(
        name="premiumuser",
        user_secret="hashed_password",
        tier="premium"
    )
    
    assert user.tier == "premium"


def test_user_instance_identity():
    """Test user instance identity"""
    now = datetime.now()
    user1 = User(user_id="user123", name="user1", created_at=now)
    
    # Same instance comparison
    assert user1 is user1