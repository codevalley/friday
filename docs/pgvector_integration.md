# PGVector Integration Plan

This document outlines the plan for integrating pgvector support into the Friday application while maintaining the clean architecture principles and database abstraction.

## Overview

The goal is to add vector search capabilities to the application, enabling semantic search for notes. We'll use pgvector when PostgreSQL is the database, but provide fallback implementations for other databases like SQLite.

## Architecture Approach

1. **Domain Layer Changes**:
   - Add vector field to Note entity
   - Create a VectorService interface in core/services

2. **Repository Layer Changes**:
   - Extend NoteRepository interface with vector search methods
   - Create database-specific implementations

3. **Infrastructure Layer Changes**:
   - Add optional pgvector dependency
   - Implement PostgreSQL-specific vector operations
   - Implement fallback vector operations for other databases

4. **Feature Detection and Graceful Degradation**:
   - Add database feature detection mechanism
   - Provide graceful fallbacks for non-PostgreSQL databases

## Implementation Plan

### 1. Add Optional Dependencies

Update pyproject.toml to include pgvector as an optional dependency:

```toml
[project.optional-dependencies]
postgres = [
    "asyncpg>=0.27.0",
    "pgvector>=0.2.0", 
]
```

### 2. Update Configuration

Extend config.py to add vector search configuration:

```python
# Database settings
database_url: str = "sqlite+aiosqlite:///./app.db"
create_tables: bool = True
vector_search_enabled: bool = True  # Feature flag for vector search
vector_dimensions: int = 384  # Default embedding dimensions
```

### 3. Update Domain Model

Extend Note entity with vector field:

```python
@dataclass
class Note:
    """Note domain entity"""
    note_id: Optional[str] = None
    user_id: str = ""
    content: str = ""
    created: datetime = datetime.now()
    embedding: Optional[List[float]] = None  # Vector embedding for semantic search
```

### 4. Create Vector Service Interface

Create a new service interface in core/services:

```python
from abc import ABC, abstractmethod
from typing import List, Optional

class VectorService(ABC):
    """Interface for vector operations"""
    
    @abstractmethod
    async def create_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        pass
    
    @abstractmethod
    async def similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate similarity between two vectors"""
        pass
```

### 5. Update Repository Interface

Extend NoteRepository interface with vector search methods:

```python
@abstractmethod
async def search_by_vector(
    self, 
    embedding: List[float], 
    user_id: Optional[str] = None, 
    limit: int = 10
) -> List[Note]:
    """Search notes by vector similarity"""
    pass
```

### 6. Database Detection Utility

Create a utility to detect database features:

```python
async def get_db_features(engine) -> Dict[str, bool]:
    """Detect database features"""
    features = {
        "vector_search": False,
        "vector_search_type": "none"
    }
    
    # Check if using PostgreSQL
    dialect = engine.dialect.name
    if dialect == "postgresql":
        try:
            # Test if pgvector is available
            import pgvector
            # Try to create a vector type to verify extension is installed
            async with engine.begin() as conn:
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                    features["vector_search"] = True
                    features["vector_search_type"] = "pgvector"
                except Exception:
                    # Extension couldn't be created
                    pass
        except ImportError:
            # pgvector not installed
            pass
    
    return features
```

### 7. SQLAlchemy Model Updates

Update the SQLAlchemy model to conditionally include vector support:

```python
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Try to import pgvector, but don't fail if not available
try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False
    Vector = None  # Type stub for static analysis

# Get vector dimensions from config
from src.config import get_settings
settings = get_settings()
VECTOR_DIMENSIONS = settings.vector_dimensions

class NoteModel(Base):
    """SQLAlchemy model for Note entity"""
    __tablename__ = "notes"

    note_id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    content = Column(Text, nullable=False)
    created = Column(DateTime, default=datetime.now)

    # Conditionally add vector column if pgvector is available
    if HAS_PGVECTOR:
        embedding = Column(Vector(VECTOR_DIMENSIONS), nullable=True)

    user = relationship("UserModel", back_populates="notes")
```

### 8. PostgreSQL Repository Implementation

Create a PostgreSQL-specific repository implementation:

```python
class PostgreSQLNoteRepository(SQLAlchemyNoteRepository):
    """PostgreSQL implementation of NoteRepository with vector search"""
    
    def __init__(self, session: AsyncSession, vector_service: VectorService):
        super().__init__(session)
        self.vector_service = vector_service
        self.has_vector_search = True  # Will be set based on feature detection
    
    async def create(self, note: Note) -> Note:
        """Create a new note with embedding"""
        if not note.embedding and self.has_vector_search:
            # Generate embedding if not provided
            note.embedding = await self.vector_service.create_embedding(note.content)
        
        # Use parent class implementation but add embedding
        db_note = NoteModel(
            user_id=note.user_id,
            content=note.content,
            created=note.created
        )
        
        # Only set embedding if pgvector is available
        if hasattr(db_note, "embedding") and note.embedding:
            db_note.embedding = note.embedding
            
        self.session.add(db_note)
        await self.session.commit()
        
        # Map DB model back to domain entity
        return Note(
            note_id=db_note.note_id,
            user_id=db_note.user_id,
            content=db_note.content,
            created=db_note.created,
            embedding=note.embedding if hasattr(db_note, "embedding") else None
        )
    
    async def search_by_vector(
        self, 
        embedding: List[float], 
        user_id: Optional[str] = None, 
        limit: int = 10
    ) -> List[Note]:
        """Search notes by vector similarity using cosine distance"""
        if not self.has_vector_search:
            # Fallback to basic search if vector search not available
            return await self._fallback_search_by_content(embedding, user_id, limit)
        
        try:
            # Create query with vector search
            query = select(NoteModel)
            
            # Filter by user_id if provided
            if user_id:
                query = query.where(NoteModel.user_id == user_id)
                
            # Add vector similarity using pgvector
            from pgvector.sqlalchemy import cosine_distance
            query = query.order_by(cosine_distance(NoteModel.embedding, embedding))
            
            # Apply limit
            query = query.limit(limit)
            
            # Execute query
            result = await self.session.execute(query)
            db_notes = result.scalars().all()
            
            # Map to domain entities
            return [
                Note(
                    note_id=db_note.note_id,
                    user_id=db_note.user_id,
                    content=db_note.content,
                    created=db_note.created,
                    embedding=db_note.embedding if hasattr(db_note, "embedding") else None
                )
                for db_note in db_notes
            ]
        except Exception as e:
            # Fallback to basic search if vector search fails
            return await self._fallback_search_by_content(embedding, user_id, limit)
```

### 9. Fallback Implementation

Add a fallback implementation for databases without vector support:

```python
async def _fallback_search_by_content(
    self, 
    embedding: List[float], 
    user_id: Optional[str] = None, 
    limit: int = 10
) -> List[Note]:
    """Fallback for databases without vector search"""
    # Get all notes for the user
    if user_id:
        notes = await self.list_by_user(user_id, skip=0, limit=100)
    else:
        # If no user_id provided, get all notes (with a reasonable limit)
        # In a real implementation, you'd need a method to list all notes
        # For now we'll just return an empty list
        return []
    
    # If we have a vector service, we can still compute similarities in memory
    if hasattr(self, 'vector_service'):
        # Generate embeddings for all notes
        for note in notes:
            if not note.embedding:
                note.embedding = await self.vector_service.create_embedding(note.content)
        
        # Compute similarities
        notes_with_scores = [
            (note, await self.vector_service.similarity(embedding, note.embedding))
            for note in notes
            if note.embedding is not None
        ]
        
        # Sort by similarity (highest first)
        notes_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        return [note for note, _ in notes_with_scores[:limit]]
    
    # If no vector service available, just return notes as-is (no semantic search)
    return notes[:limit]
```

### 10. In-Memory Implementation

Update the in-memory repository to support vector search:

```python
class InMemoryNoteRepository(NoteRepository):
    """In-memory implementation of NoteRepository with vector search support"""
    
    def __init__(self, vector_service: Optional[VectorService] = None):
        self.notes: Dict[str, Note] = {}
        self.user_notes: Dict[str, List[str]] = {}  # Maps user_id -> list of note_ids
        self.vector_service = vector_service
    
    # Implement existing methods...
    
    async def search_by_vector(
        self, 
        embedding: List[float], 
        user_id: Optional[str] = None, 
        limit: int = 10
    ) -> List[Note]:
        """Search notes by vector similarity"""
        # Get relevant notes
        if user_id:
            note_ids = self.user_notes.get(user_id, [])
            notes = [self.notes[note_id] for note_id in note_ids if note_id in self.notes]
        else:
            notes = list(self.notes.values())
        
        # If we have a vector service, compute similarities
        if self.vector_service:
            # Generate embeddings for notes that don't have them
            for note in notes:
                if not note.embedding:
                    note.embedding = await self.vector_service.create_embedding(note.content)
            
            # Compute similarities
            notes_with_scores = []
            for note in notes:
                if note.embedding:
                    similarity = await self.vector_service.similarity(embedding, note.embedding)
                    notes_with_scores.append((note, similarity))
            
            # Sort by similarity (highest first)
            notes_with_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Return top results
            return [note for note, _ in notes_with_scores[:limit]]
        
        # If no vector service, just return notes as-is
        return notes[:limit]
```

### 11. Simple Vector Service Implementation

Create a basic vector service implementation:

```python
class BasicVectorService(VectorService):
    """Simple implementation of VectorService using cosine similarity"""
    
    async def create_embedding(self, text: str) -> List[float]:
        """
        Create a simple embedding for text.
        
        In a real application, you would use a proper embedding model
        like OpenAI's text-embedding-ada-002 or a local model.
        This is just a simple implementation for testing.
        """
        # Create a very simple embedding (not useful for real search)
        import hashlib
        import numpy as np
        
        # Generate a hash of the text
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert hash to a list of floats
        np_array = np.frombuffer(hash_bytes, dtype=np.uint8)
        
        # Normalize to unit length
        from src.config import get_settings
        settings = get_settings()
        
        # Resize to correct dimensions and normalize
        dimensions = settings.vector_dimensions
        embedding = np.zeros(dimensions)
        for i, value in enumerate(np_array):
            if i < dimensions:
                embedding[i] = value / 255.0
        
        # Normalize to unit length
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding.tolist()
    
    async def similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import numpy as np
        
        # Convert to numpy arrays
        a = np.array(vec1)
        b = np.array(vec2)
        
        # Calculate cosine similarity
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return dot_product / (norm_a * norm_b)
```

### 12. Update Dependencies

Update the dependency injection system to provide the appropriate repository:

```python
def get_vector_service() -> VectorService:
    """Get vector service instance"""
    return BasicVectorService()

async def get_note_repository(
    session: AsyncSession = Depends(get_db_session),
    vector_service: VectorService = Depends(get_vector_service)
) -> NoteRepository:
    """Get note repository instance based on database type"""
    # Get database features
    from src.infrastructure.persistence.utils import get_db_features
    features = await get_db_features(session.bind)
    
    if features.get("vector_search_type") == "pgvector":
        # Use PostgreSQL with pgvector
        return PostgreSQLNoteRepository(session, vector_service)
    else:
        # Use regular SQLAlchemy repository
        repo = SQLAlchemyNoteRepository(session)
        if hasattr(repo, 'vector_service'):
            repo.vector_service = vector_service
        return repo
```

## Testing Strategy

1. **Unit Tests**:
   - Test vector service implementations
   - Test in-memory repository with vector search
   - Test fallback mechanisms

2. **Integration Tests**:
   - Test with PostgreSQL when available
   - Test fallback behavior with SQLite

3. **Feature Detection Tests**:
   - Verify correct detection of database capabilities

## Deployment Considerations

1. **Dependencies**:
   - Make pgvector optional to avoid breaking existing deployments
   - Document installation of pgvector extension for PostgreSQL

2. **Database Migration**:
   - Create migration scripts to add vector columns to existing tables
   - Handle both PostgreSQL and other databases

3. **Performance**:
   - Document performance implications of vector search
   - Recommend indexing strategies for PostgreSQL

## Conclusion

This approach allows us to add vector search capabilities to our application while maintaining the clean architecture principles and database abstraction. The key aspects are:

1. **Optional Dependency**: pgvector is optional, allowing the application to work with or without it
2. **Feature Detection**: The application detects database capabilities at runtime
3. **Fallback Mechanisms**: Graceful degradation when vector search is not available
4. **Clean Architecture**: Maintains separation of concerns with clear interfaces

This design ensures that the application can take advantage of pgvector when available, but still works correctly with other databases.