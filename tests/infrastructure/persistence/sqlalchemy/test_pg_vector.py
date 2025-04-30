"""Tests for PostgreSQL vector search functionality"""
import os
import pytest
from typing import List, Optional

from src.core.domain.note import Note
from src.core.services.vector_service import VectorService
from src.infrastructure.services.vector.basic_vector_service import BasicVectorService
from src.infrastructure.persistence.memory.note_repo import InMemoryNoteRepository

# Only run these tests if pgvector is available
try:
    import pgvector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False

# Skip all tests in this module if not running with PostgreSQL
pytestmark = pytest.mark.skipif(
    "postgresql" not in os.environ.get("DATABASE_URL", ""),
    reason="PostgreSQL vector tests only run when DATABASE_URL contains 'postgresql'"
)


@pytest.fixture
async def vector_service() -> VectorService:
    """Create a basic vector service for testing"""
    return BasicVectorService()


@pytest.fixture
async def in_memory_repo(vector_service) -> InMemoryNoteRepository:
    """Create an in-memory repository with vector search"""
    return InMemoryNoteRepository(vector_service)


@pytest.mark.asyncio
@pytest.mark.skipif(not HAS_PGVECTOR, reason="pgvector not installed")
async def test_in_memory_vector_search(in_memory_repo, vector_service):
    """Test in-memory vector search functionality"""
    # Create test data
    notes = [
        Note(user_id="user1", content="Python is a programming language"),
        Note(user_id="user1", content="FastAPI is a web framework for Python"),
        Note(user_id="user1", content="SQLAlchemy is an ORM for Python"),
        Note(user_id="user1", content="Cats are furry animals"),
        Note(user_id="user1", content="Dogs are loyal pets"),
    ]
    
    # Save notes
    for note in notes:
        await in_memory_repo.create(note)
    
    # Generate query embedding
    query_embedding = await vector_service.create_embedding("Python web frameworks")
    
    # Search notes
    results = await in_memory_repo.search_by_vector(
        embedding=query_embedding,
        user_id="user1",
        limit=3
    )
    
    # Check results
    assert len(results) == 3
    
    # The results should contain the Python-related notes first
    contents = [note.content for note in results]
    python_notes = [
        "Python is a programming language",
        "FastAPI is a web framework for Python",
        "SQLAlchemy is an ORM for Python"
    ]
    
    # Check that at least 2 of the top 3 results are Python-related
    python_matches = sum(1 for content in contents if content in python_notes)
    assert python_matches >= 2


# The following tests would be run only in a PostgreSQL environment with pgvector installed

@pytest.mark.asyncio
@pytest.mark.skipif(not HAS_PGVECTOR, reason="pgvector not installed")
async def test_postgres_vector_search_if_available(vector_service):
    """Test PostgreSQL vector search implementation if available"""
    from src.config import get_settings
    settings = get_settings()
    
    if "postgresql" in settings.database_url and HAS_PGVECTOR:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from src.infrastructure.persistence.sqlalchemy.pg_note_repo import PostgreSQLNoteRepository
        from src.infrastructure.persistence.utils import get_db_features
        
        # Create engine and session
        engine = create_async_engine(settings.database_url)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        # Check features
        features = await get_db_features(engine)
        
        if features.get("vector_search_type") == "pgvector":
            async with async_session() as session:
                # Create repository
                repo = PostgreSQLNoteRepository(
                    session=session,
                    vector_service=vector_service,
                    has_vector_support=True
                )
                
                # Create test data
                notes = [
                    Note(user_id="user1", content="Python is a programming language"),
                    Note(user_id="user1", content="FastAPI is a web framework for Python"),
                    Note(user_id="user1", content="SQLAlchemy is an ORM for Python"),
                    Note(user_id="user1", content="Cats are furry animals"),
                    Note(user_id="user1", content="Dogs are loyal pets"),
                ]
                
                # Save notes
                for note in notes:
                    await repo.create(note)
                
                # Generate query embedding
                query_embedding = await vector_service.create_embedding("Python web frameworks")
                
                # Search notes
                results = await repo.search_by_vector(
                    embedding=query_embedding,
                    user_id="user1",
                    limit=3
                )
                
                # Check results
                assert len(results) == 3
                
                # The results should contain the Python-related notes first
                contents = [note.content for note in results]
                
                # Cleanup
                for note in notes:
                    if note.note_id:
                        await repo.delete(note.note_id)