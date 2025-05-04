from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.domain.note import Note
from src.core.repositories.note_repo import NoteRepository
from src.infrastructure.persistence.sqlalchemy.models import NoteModel


class SQLAlchemyNoteRepository(NoteRepository):
    """SQLAlchemy implementation of NoteRepository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, note: Note) -> Note:
        """Create a new note"""
        db_note = NoteModel(
            user_id=note.user_id,
            content=note.content,
            created=note.created
        )
        self.session.add(db_note)
        await self.session.commit()
        
        # Map DB model back to domain entity
        return Note(
            note_id=db_note.note_id,
            user_id=db_note.user_id,
            content=db_note.content,
            created=db_note.created
        )
    
    async def get_by_id(self, note_id: str) -> Optional[Note]:
        """Get a note by ID"""
        result = await self.session.execute(
            select(NoteModel).where(NoteModel.note_id == note_id)
        )
        db_note = result.scalars().first()
        
        if not db_note:
            return None
        
        return Note(
            note_id=db_note.note_id,
            user_id=db_note.user_id,
            content=db_note.content,
            created=db_note.created
        )
    
    async def update(self, note: Note) -> Note:
        """Update a note"""
        result = await self.session.execute(
            select(NoteModel).where(NoteModel.note_id == note.note_id)
        )
        db_note = result.scalars().first()
        
        if not db_note:
            raise ValueError(f"Note with ID {note.note_id} not found")
        
        # Update fields
        db_note.content = note.content
        
        await self.session.commit()
        
        return Note(
            note_id=db_note.note_id,
            user_id=db_note.user_id,
            content=db_note.content,
            created=db_note.created
        )
    
    async def delete(self, note_id: str) -> bool:
        """Delete a note"""
        result = await self.session.execute(
            select(NoteModel).where(NoteModel.note_id == note_id)
        )
        db_note = result.scalars().first()
        
        if not db_note:
            return False
        
        await self.session.delete(db_note)
        await self.session.commit()
        
        return True
    
    async def list_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Note]:
        """List notes for a specific user with pagination"""
        result = await self.session.execute(
            select(NoteModel)
            .where(NoteModel.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(NoteModel.created.desc())
        )
        db_notes = result.scalars().all()
        
        return [
            Note(
                note_id=db_note.note_id,
                user_id=db_note.user_id,
                content=db_note.content,
                created=db_note.created
            )
            for db_note in db_notes
        ]
        
    async def search_by_vector(
        self, 
        embedding: List[float], 
        user_id: Optional[str] = None, 
        limit: int = 10
    ) -> List[Note]:
        """Search notes by vector similarity - Basic implementation without vector search"""
        # This is a placeholder implementation since this class doesn't support vector search
        # Just return recent notes instead
        if user_id:
            return await self.list_by_user(user_id, skip=0, limit=limit)
        else:
            # If no user_id provided, we can't search, so return empty list
            return []