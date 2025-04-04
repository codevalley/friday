from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.domain.note import Note
from src.core.repositories.note_repo import NoteRepository
from src.core.repositories.user_repo import UserRepository
from src.core.services.cache_service import CacheService
from src.core.use_cases.note_dtos import NoteCreateDTO, NoteReadDTO, NoteUpdateDTO


class NoteService:
    """Note use cases implementation"""
    
    def __init__(
        self, 
        note_repo: NoteRepository, 
        user_repo: UserRepository,
        cache_service: Optional[CacheService] = None
    ):
        self.note_repo = note_repo
        self.user_repo = user_repo
        self.cache_service = cache_service
    
    async def create_note(self, note_create: NoteCreateDTO, current_user_id: str) -> NoteReadDTO:
        """Create a new note for the current user"""
        # Verify user exists
        user = await self.user_repo.get_by_id(current_user_id)
        if not user:
            raise ValueError(f"User with ID {current_user_id} not found")
        
        # Create note domain entity
        note = Note(
            user_id=current_user_id,
            content=note_create.content
        )
        
        # Save to repository
        created_note = await self.note_repo.create(note)
        
        # Invalidate cache
        if self.cache_service:
            await self.cache_service.delete(f"user:{current_user_id}:notes")
        
        # Convert to DTO
        return NoteReadDTO(
            note_id=created_note.note_id,
            user_id=created_note.user_id,
            content=created_note.content,
            created=created_note.created
        )
    
    async def get_note_by_id(self, note_id: str, current_user_id: str) -> Optional[NoteReadDTO]:
        """Get a note by ID if it belongs to the current user"""
        note = await self.note_repo.get_by_id(note_id)
        
        if not note or note.user_id != current_user_id:
            return None
        
        return NoteReadDTO(
            note_id=note.note_id,
            user_id=note.user_id,
            content=note.content,
            created=note.created
        )
    
    async def update_note(
        self, note_id: str, note_update: NoteUpdateDTO, current_user_id: str
    ) -> Optional[NoteReadDTO]:
        """Update a note if it belongs to the current user"""
        # Get existing note
        note = await self.note_repo.get_by_id(note_id)
        if not note or note.user_id != current_user_id:
            return None
        
        # Update content
        note.content = note_update.content
        
        # Save changes
        updated_note = await self.note_repo.update(note)
        
        # Invalidate cache
        if self.cache_service:
            await self.cache_service.delete(f"user:{current_user_id}:notes")
        
        return NoteReadDTO(
            note_id=updated_note.note_id,
            user_id=updated_note.user_id,
            content=updated_note.content,
            created=updated_note.created
        )
    
    async def delete_note(self, note_id: str, current_user_id: str) -> bool:
        """Delete a note if it belongs to the current user"""
        # Get note to check ownership
        note = await self.note_repo.get_by_id(note_id)
        if not note or note.user_id != current_user_id:
            return False
        
        # Delete note
        result = await self.note_repo.delete(note_id)
        
        # Invalidate cache
        if result and self.cache_service:
            await self.cache_service.delete(f"user:{current_user_id}:notes")
        
        return result
    
    async def list_user_notes(
        self, current_user_id: str, skip: int = 0, limit: int = 100
    ) -> List[NoteReadDTO]:
        """List notes for the current user"""
        # Check cache first
        if self.cache_service and skip == 0 and limit == 100:
            cached_notes = await self.cache_service.get(f"user:{current_user_id}:notes")
            if cached_notes:
                return [NoteReadDTO(**note) for note in cached_notes]
        
        # Get notes from repository
        notes = await self.note_repo.list_by_user(
            user_id=current_user_id, 
            skip=skip, 
            limit=limit
        )
        
        # Convert to DTOs
        note_dtos = [
            NoteReadDTO(
                note_id=note.note_id,
                user_id=note.user_id,
                content=note.content,
                created=note.created
            )
            for note in notes
        ]
        
        # Cache results
        if self.cache_service and skip == 0 and limit == 100:
            await self.cache_service.set(
                f"user:{current_user_id}:notes",
                [note.dict() for note in note_dtos],
                expire=60 * 5  # Cache for 5 minutes
            )
        
        return note_dtos