"""PostgreSQL implementation of NoteRepository with vector search capabilities"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.domain.note import Note
from src.core.repositories.note_repo import NoteRepository
from src.core.services.vector_service import VectorService
from src.infrastructure.persistence.sqlalchemy.note_repo import SQLAlchemyNoteRepository

# Try to import pgvector, but don't fail if not available
try:
    from pgvector.sqlalchemy import Vector, cosine_distance
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False
    Vector = None
    cosine_distance = None


class PostgreSQLNoteRepository(SQLAlchemyNoteRepository):
    """PostgreSQL implementation of NoteRepository with vector search"""
    
    def __init__(
        self, 
        session: AsyncSession, 
        vector_service: VectorService,
        has_vector_support: bool = False
    ):
        super().__init__(session)
        self.vector_service = vector_service
        self.has_vector_support = has_vector_support
    
    async def create(self, note: Note) -> Note:
        """Create a new note with embedding"""
        # Import here to avoid circular imports
        from src.infrastructure.persistence.sqlalchemy.enhanced_models import NoteModel
        
        # Generate embedding if not provided and vector search is supported
        if not note.embedding and self.has_vector_support:
            note.embedding = await self.vector_service.create_embedding(note.content)
        
        # Create model instance
        db_note = NoteModel(
            user_id=note.user_id,
            content=note.content,
            created=note.created
        )
        
        # Only set embedding if vector support is available and the model has the embedding attribute
        if self.has_vector_support and hasattr(db_note, "embedding") and note.embedding:
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
    
    async def update(self, note: Note) -> Note:
        """Update a note with embedding"""
        # Import here to avoid circular imports
        from src.infrastructure.persistence.sqlalchemy.enhanced_models import NoteModel
        
        # Regenerate embedding if content changed and vector search is supported
        if self.has_vector_support and not note.embedding:
            note.embedding = await self.vector_service.create_embedding(note.content)
        
        result = await self.session.execute(
            select(NoteModel).where(NoteModel.note_id == note.note_id)
        )
        db_note = result.scalars().first()
        
        if not db_note:
            raise ValueError(f"Note with ID {note.note_id} not found")
        
        # Update fields
        db_note.content = note.content
        
        # Update embedding if vector support is available
        if self.has_vector_support and hasattr(db_note, "embedding") and note.embedding:
            db_note.embedding = note.embedding
        
        await self.session.commit()
        
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
        if not self.has_vector_support or not HAS_PGVECTOR:
            # Fallback to basic search if vector search not available
            return await self._fallback_search_by_content(embedding, user_id, limit)
        
        try:
            # Import here to avoid circular imports
            from src.infrastructure.persistence.sqlalchemy.enhanced_models import NoteModel
            
            # Create query with vector search
            query = select(NoteModel)
            
            # Filter by user_id if provided
            if user_id:
                query = query.where(NoteModel.user_id == user_id)
                
            # Add vector similarity using pgvector
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
            # If no user_id provided, we'd need a method to list all notes
            # For now we'll just return an empty list
            return []
        
        # Compute similarities in memory
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