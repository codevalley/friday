from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.domain.user import User
from src.core.repositories.user_repo import UserRepository
from src.infrastructure.persistence.sqlalchemy.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user: User) -> User:
        """Create a new user"""
        db_user = UserModel(
            name=user.name,
            user_secret=user.user_secret,
            tier=user.tier
        )
        self.session.add(db_user)
        await self.session.commit()
        
        # Map DB model back to domain entity
        return User(
            user_id=db_user.user_id,
            name=db_user.name,
            user_secret=db_user.user_secret,
            tier=db_user.tier,
            created_at=db_user.created_at
        )
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.user_id == user_id)
        )
        db_user = result.scalars().first()
        
        if not db_user:
            return None
        
        return User(
            user_id=db_user.user_id,
            name=db_user.name,
            user_secret=db_user.user_secret,
            tier=db_user.tier,
            created_at=db_user.created_at
        )
    
    async def get_by_name(self, name: str) -> Optional[User]:
        """Get a user by name"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.name == name)
        )
        db_user = result.scalars().first()
        
        if not db_user:
            return None
        
        return User(
            user_id=db_user.user_id,
            name=db_user.name,
            user_secret=db_user.user_secret,
            tier=db_user.tier,
            created_at=db_user.created_at
        )
    
    async def update(self, user: User) -> User:
        """Update a user"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.user_id == user.user_id)
        )
        db_user = result.scalars().first()
        
        if not db_user:
            raise ValueError(f"User with ID {user.user_id} not found")
        
        # Update fields if they are provided
        if user.name:
            db_user.name = user.name
        if user.user_secret:
            db_user.user_secret = user.user_secret
        if user.tier:
            db_user.tier = user.tier
        
        await self.session.commit()
        
        return User(
            user_id=db_user.user_id,
            name=db_user.name,
            user_secret=db_user.user_secret,
            tier=db_user.tier,
            created_at=db_user.created_at
        )
    
    async def delete(self, user_id: str) -> bool:
        """Delete a user"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.user_id == user_id)
        )
        db_user = result.scalars().first()
        
        if not db_user:
            return False
        
        await self.session.delete(db_user)
        await self.session.commit()
        
        return True
    
    async def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users with pagination"""
        result = await self.session.execute(
            select(UserModel).offset(skip).limit(limit)
        )
        db_users = result.scalars().all()
        
        return [
            User(
                user_id=db_user.user_id,
                name=db_user.name,
                user_secret=db_user.user_secret,
                tier=db_user.tier,
                created_at=db_user.created_at
            )
            for db_user in db_users
        ]