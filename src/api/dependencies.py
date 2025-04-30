from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.note_uc import NoteService
from src.application.use_cases.user_uc import UserService
from src.core.repositories.note_repo import NoteRepository
from src.core.repositories.user_repo import UserRepository
from src.core.services.auth_service import AuthService
from src.core.services.cache_service import CacheService
from src.core.services.vector_service import VectorService
from src.infrastructure.persistence.sqlalchemy import get_db_session
from src.infrastructure.persistence.sqlalchemy.note_repo import SQLAlchemyNoteRepository
from src.infrastructure.persistence.sqlalchemy.user_repo import SQLAlchemyUserRepository
from src.infrastructure.services.jwt.auth_service import JWTAuthService
from src.infrastructure.services.redis.cache_service import RedisCacheService

# OAuth2 setup for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Service dependencies
def get_auth_service() -> AuthService:
    """Get auth service instance"""
    return JWTAuthService()


def get_cache_service() -> CacheService:
    """Get cache service instance"""
    return RedisCacheService()


# Service dependencies for vector features
def get_vector_service() -> VectorService:
    """Get vector service instance"""
    from src.infrastructure.services.vector.basic_vector_service import BasicVectorService
    return BasicVectorService()


# Repository dependencies
def get_user_repository(
    session: AsyncSession = Depends(get_db_session)
) -> UserRepository:
    """Get user repository instance"""
    return SQLAlchemyUserRepository(session)


async def get_note_repository(
    session: AsyncSession = Depends(get_db_session),
    vector_service: VectorService = Depends(get_vector_service)
) -> NoteRepository:
    """Get note repository instance based on database type"""
    from src.config import get_settings
    settings = get_settings()
    
    if not settings.vector_search_enabled:
        return SQLAlchemyNoteRepository(session)
    
    # Detect database features
    from src.infrastructure.persistence.utils import get_db_features
    features = await get_db_features(session.bind)
    
    if features.get("vector_search_type") == "pgvector":
        # Use PostgreSQL with pgvector
        from src.infrastructure.persistence.sqlalchemy.pg_note_repo import PostgreSQLNoteRepository
        return PostgreSQLNoteRepository(
            session, 
            vector_service,
            has_vector_support=True
        )
    else:
        # Use regular SQLAlchemy repository 
        repo = SQLAlchemyNoteRepository(session)
        return repo


# Use case services
def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserService:
    """Get user service instance"""
    return UserService(user_repo, auth_service)


def get_note_service(
    note_repo: NoteRepository = Depends(get_note_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    cache_service: CacheService = Depends(get_cache_service)
) -> NoteService:
    """Get note service instance"""
    return NoteService(note_repo, user_repo, cache_service)


# Current user dependency
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service)
):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Validate token
    payload = await auth_service.validate_token(token)
    if not payload:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception
    
    # Get user from repository
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise credentials_exception
    
    return user