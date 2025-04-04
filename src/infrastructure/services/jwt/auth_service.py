import base64
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

import bcrypt
import jwt

from src.config import get_settings
from src.core.services.auth_service import AuthService

settings = get_settings()


class JWTAuthService(AuthService):
    """JWT implementation of AuthService"""
    
    def __init__(self, secret_key: Optional[str] = None, token_expires_minutes: int = 30):
        self.secret_key = secret_key or settings.jwt_secret_key
        if not self.secret_key:
            # Generate a random secret key if not provided
            self.secret_key = base64.b64encode(os.urandom(32)).decode("utf-8")
        
        self.token_expires_minutes = token_expires_minutes or settings.jwt_token_expires_minutes
    
    async def create_token(self, user_id: str, extra_data: Optional[Dict] = None) -> str:
        """Create a JWT token for a user"""
        payload = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(minutes=self.token_expires_minutes),
            "iat": datetime.utcnow(),
        }
        
        # Add any extra data
        if extra_data:
            payload.update(extra_data)
        
        # Create JWT token
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        
        return token
    
    async def validate_token(self, token: str) -> Optional[Dict]:
        """Validate a JWT token and return payload if valid"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.PyJWTError:
            return None
    
    async def hash_password(self, password: str) -> str:
        """Hash a password for secure storage"""
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        return hashed.decode("utf-8")
    
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        password_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        
        return bcrypt.checkpw(password_bytes, hashed_bytes)