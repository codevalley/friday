from abc import ABC, abstractmethod
from typing import Dict, Optional


class AuthService(ABC):
    """Abstract interface for authentication and authorization operations"""
    
    @abstractmethod
    async def create_token(self, user_id: str, extra_data: Optional[Dict] = None) -> str:
        """Create an authentication token for a user"""
        pass
    
    @abstractmethod
    async def validate_token(self, token: str) -> Optional[Dict]:
        """Validate an authentication token and return payload if valid"""
        pass
    
    @abstractmethod
    async def hash_password(self, password: str) -> str:
        """Hash a password for secure storage"""
        pass
    
    @abstractmethod
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        pass