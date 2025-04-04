import uuid
from datetime import datetime
from typing import Dict, List, Optional

from src.core.domain.note import Note
from src.core.repositories.note_repo import NoteRepository


class InMemoryNoteRepository(NoteRepository):
    """In-memory implementation of NoteRepository for testing"""
    
    def __init__(self):
        self.notes: Dict[str, Note] = {}
        self.user_notes: Dict[str, List[str]] = {}  # Maps user_id -> list of note_ids
    
    async def create(self, note: Note) -> Note:
        """Create a new note"""
        # Generate ID if not provided
        if not note.note_id:
            note.note_id = str(uuid.uuid4())
        
        # Set creation time if not provided
        if not note.created:
            note.created = datetime.now()
        
        # Store note
        self.notes[note.note_id] = note
        
        # Update user-notes index
        if note.user_id not in self.user_notes:
            self.user_notes[note.user_id] = []
        
        self.user_notes[note.user_id].append(note.note_id)
        
        return note
    
    async def get_by_id(self, note_id: str) -> Optional[Note]:
        """Get a note by ID"""
        return self.notes.get(note_id)
    
    async def update(self, note: Note) -> Note:
        """Update a note"""
        if not note.note_id or note.note_id not in self.notes:
            raise ValueError(f"Note with ID {note.note_id} not found")
        
        # Get existing note
        existing_note = self.notes[note.note_id]
        
        # If user is changing, update user-notes index
        if note.user_id != existing_note.user_id:
            # Remove from old user's notes
            if existing_note.user_id in self.user_notes:
                self.user_notes[existing_note.user_id].remove(note.note_id)
            
            # Add to new user's notes
            if note.user_id not in self.user_notes:
                self.user_notes[note.user_id] = []
            
            self.user_notes[note.user_id].append(note.note_id)
        
        # Update note
        self.notes[note.note_id] = note
        
        return note
    
    async def delete(self, note_id: str) -> bool:
        """Delete a note"""
        if note_id not in self.notes:
            return False
        
        # Remove from user-notes index
        note = self.notes[note_id]
        if note.user_id in self.user_notes and note_id in self.user_notes[note.user_id]:
            self.user_notes[note.user_id].remove(note_id)
        
        # Remove note
        del self.notes[note_id]
        
        return True
    
    async def list_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Note]:
        """List notes for a specific user with pagination"""
        if user_id not in self.user_notes:
            return []
        
        # Get note IDs for user
        note_ids = self.user_notes[user_id]
        
        # Get notes
        notes = [self.notes[note_id] for note_id in note_ids if note_id in self.notes]
        
        # Sort by created time (descending)
        notes.sort(key=lambda note: note.created, reverse=True)
        
        # Apply pagination
        return notes[skip:skip + limit]