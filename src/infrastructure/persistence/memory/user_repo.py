import uuid
from datetime import datetime
from typing import Dict, List, Optional

from src.core.domain.user import User
from src.core.repositories.user_repo import UserRepository


class InMemoryUserRepository(UserRepository):
    """In-memory implementation of UserRepository for testing"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.name_index: Dict[str, str] = {}  # Maps name -> user_id
    
    async def create(self, user: User) -> User:
        """Create a new user"""
        # Generate ID if not provided
        if not user.user_id:
            user.user_id = str(uuid.uuid4())
        
        # Set creation time if not provided
        if not user.created_at:
            user.created_at = datetime.now()
        
        # Check for duplicate name
        if user.name in self.name_index:
            raise ValueError(f"User with name {user.name} already exists")
        
        # Store user
        self.users[user.user_id] = user
        self.name_index[user.name] = user.user_id
        
        return user
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        return self.users.get(user_id)
    
    async def get_by_name(self, name: str) -> Optional[User]:
        """Get a user by name"""
        user_id = self.name_index.get(name)
        if not user_id:
            return None
        
        return self.users.get(user_id)
    
    async def update(self, user: User) -> User:
        """Update a user"""
        if not user.user_id or user.user_id not in self.users:
            raise ValueError(f"User with ID {user.user_id} not found")
        
        # Get existing user
        old_user = self.users[user.user_id]
        
        # If name is changing, update name index
        if user.name != old_user.name:
            # Check new name doesn't exist (except for this user)
            if user.name in self.name_index and self.name_index[user.name] != user.user_id:
                raise ValueError(f"User with name {user.name} already exists")
            
            # Update name index
            del self.name_index[old_user.name]
            self.name_index[user.name] = user.user_id
        
        # Update user
        self.users[user.user_id] = user
        
        return user
    
    async def delete(self, user_id: str) -> bool:
        """Delete a user"""
        if user_id not in self.users:
            return False
        
        # Remove from name index
        user = self.users[user_id]
        del self.name_index[user.name]
        
        # Remove user
        del self.users[user_id]
        
        return True
    
    async def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users with pagination"""
        users = list(self.users.values())
        return users[skip:skip + limit]