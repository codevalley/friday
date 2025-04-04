from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.domain.user import User
from src.core.repositories.user_repo import UserRepository
from src.core.services.auth_service import AuthService
from src.core.use_cases.user_dtos import (
    TokenResponseDTO, UserCreateDTO, UserLoginDTO, UserReadDTO, UserUpdateDTO
)


class UserService:
    """User use cases implementation"""
    
    def __init__(self, user_repo: UserRepository, auth_service: AuthService):
        self.user_repo = user_repo
        self.auth_service = auth_service
    
    async def create_user(self, user_create: UserCreateDTO) -> UserReadDTO:
        """Create a new user"""
        # Check if user already exists
        existing_user = await self.user_repo.get_by_name(user_create.name)
        if existing_user:
            raise ValueError(f"User with name {user_create.name} already exists")
        
        # Hash password
        hashed_password = await self.auth_service.hash_password(user_create.password)
        
        # Create user domain entity
        user = User(
            name=user_create.name,
            user_secret=hashed_password,
            tier=user_create.tier
        )
        
        # Save to repository
        created_user = await self.user_repo.create(user)
        
        # Convert to DTO
        return UserReadDTO(
            user_id=created_user.user_id,
            name=created_user.name,
            tier=created_user.tier,
            created_at=created_user.created_at
        )
    
    async def authenticate_user(self, login_data: UserLoginDTO) -> Optional[TokenResponseDTO]:
        """Authenticate a user and return token if valid"""
        # Get user by name
        user = await self.user_repo.get_by_name(login_data.name)
        if not user:
            return None
        
        # Verify password
        is_valid = await self.auth_service.verify_password(
            login_data.password, user.user_secret
        )
        
        if not is_valid:
            return None
        
        # Generate token
        token = await self.auth_service.create_token(
            user.user_id,
            {"name": user.name, "tier": user.tier}
        )
        
        return TokenResponseDTO(
            access_token=token,
            token_type="bearer"
        )
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserReadDTO]:
        """Get a user by ID"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None
        
        return UserReadDTO(
            user_id=user.user_id,
            name=user.name,
            tier=user.tier,
            created_at=user.created_at
        )
    
    async def update_user(self, user_id: str, user_update: UserUpdateDTO) -> Optional[UserReadDTO]:
        """Update a user"""
        # Get existing user
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None
        
        # Update fields if provided
        if user_update.name:
            user.name = user_update.name
        
        if user_update.password:
            user.user_secret = await self.auth_service.hash_password(user_update.password)
        
        if user_update.tier:
            user.tier = user_update.tier
        
        # Save changes
        updated_user = await self.user_repo.update(user)
        
        return UserReadDTO(
            user_id=updated_user.user_id,
            name=updated_user.name,
            tier=updated_user.tier,
            created_at=updated_user.created_at
        )
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        return await self.user_repo.delete(user_id)
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[UserReadDTO]:
        """List users with pagination"""
        users = await self.user_repo.list(skip=skip, limit=limit)
        
        return [
            UserReadDTO(
                user_id=user.user_id,
                name=user.name,
                tier=user.tier,
                created_at=user.created_at
            )
            for user in users
        ]