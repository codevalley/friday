import pytest
import uuid
from datetime import datetime, timedelta

from src.core.domain.note import Note
from src.infrastructure.persistence.memory.note_repo import InMemoryNoteRepository


@pytest.fixture
def note_repo():
    """Return a new in-memory note repository"""
    return InMemoryNoteRepository()


@pytest.fixture
def sample_note():
    """Return a sample note"""
    return Note(
        user_id="user123",
        content="This is a test note."
    )


@pytest.mark.asyncio
async def test_create_note(note_repo, sample_note):
    """Test creating a note"""
    created_note = await note_repo.create(sample_note)
    
    assert created_note.note_id is not None
    assert created_note.user_id == "user123"
    assert created_note.content == "This is a test note."
    assert isinstance(created_note.created, datetime)
    
    # Verify it's in the repository
    assert created_note.note_id in note_repo.notes
    assert created_note.note_id in note_repo.user_notes["user123"]


@pytest.mark.asyncio
async def test_create_note_with_existing_id(note_repo):
    """Test creating a note with a pre-defined ID"""
    note_id = str(uuid.uuid4())
    note = Note(
        note_id=note_id,
        user_id="user123",
        content="Note with pre-defined ID"
    )
    
    created_note = await note_repo.create(note)
    
    assert created_note.note_id == note_id
    assert created_note.content == "Note with pre-defined ID"
    assert note_id in note_repo.notes


@pytest.mark.asyncio
async def test_get_by_id(note_repo, sample_note):
    """Test getting a note by ID"""
    created_note = await note_repo.create(sample_note)
    
    # Get note by ID
    note = await note_repo.get_by_id(created_note.note_id)
    
    assert note is not None
    assert note.note_id == created_note.note_id
    assert note.user_id == "user123"
    assert note.content == "This is a test note."
    
    # Test non-existent note
    non_existent = await note_repo.get_by_id(str(uuid.uuid4()))
    assert non_existent is None


@pytest.mark.asyncio
async def test_update_note(note_repo, sample_note):
    """Test updating a note"""
    created_note = await note_repo.create(sample_note)
    
    # Update note
    created_note.content = "This note has been updated."
    
    updated_note = await note_repo.update(created_note)
    
    assert updated_note.content == "This note has been updated."
    
    # Verify it's updated in the repository
    stored_note = note_repo.notes[created_note.note_id]
    assert stored_note.content == "This note has been updated."


@pytest.mark.asyncio
async def test_update_note_with_different_user(note_repo):
    """Test updating a note with a different user ID"""
    # Create a note with a specific user_id
    note = Note(user_id="user123", content="Note for user123")
    created_note = await note_repo.create(note)
    
    # Create a copy with an updated user_id
    updated_note = Note(
        note_id=created_note.note_id,
        user_id="user456",  # Changed user_id
        content=created_note.content,
        created=created_note.created
    )
    
    # Update the note
    result = await note_repo.update(updated_note)
    
    # Verify the update
    assert result.user_id == "user456"
    assert note_repo.notes[created_note.note_id].user_id == "user456"
    
    # Verify only new user has the note ID in their collection
    assert created_note.note_id in note_repo.user_notes.get("user456", [])


@pytest.mark.asyncio
async def test_update_nonexistent_note(note_repo):
    """Test updating a non-existent note raises error"""
    note = Note(
        note_id=str(uuid.uuid4()),
        user_id="user123",
        content="Non-existent note"
    )
    
    with pytest.raises(ValueError, match="Note with ID .* not found"):
        await note_repo.update(note)


@pytest.mark.asyncio
async def test_delete_note(note_repo, sample_note):
    """Test deleting a note"""
    created_note = await note_repo.create(sample_note)
    
    # Delete note
    result = await note_repo.delete(created_note.note_id)
    
    assert result is True
    assert created_note.note_id not in note_repo.notes
    assert created_note.note_id not in note_repo.user_notes["user123"]
    
    # Test deleting non-existent note
    result = await note_repo.delete(str(uuid.uuid4()))
    assert result is False


@pytest.mark.asyncio
async def test_list_by_user(note_repo):
    """Test listing notes for a specific user with pagination"""
    # Create multiple notes for the same user
    user_id = "user123"
    for i in range(5):
        await note_repo.create(Note(
            user_id=user_id,
            content=f"Note {i} for user123"
        ))
    
    # Create a note for a different user
    await note_repo.create(Note(
        user_id="user456",
        content="Note for user456"
    ))
    
    # List all notes for user123
    notes = await note_repo.list_by_user(user_id)
    assert len(notes) == 5
    
    # Test pagination
    notes = await note_repo.list_by_user(user_id, skip=2, limit=2)
    assert len(notes) == 2
    
    # Test non-existent user
    notes = await note_repo.list_by_user("nonexistent")
    assert len(notes) == 0


@pytest.mark.asyncio
async def test_sorting_by_created_time(note_repo):
    """Test that notes are sorted by created time (newest first)"""
    user_id = "user123"
    
    # Create notes with different creation times
    now = datetime.now()
    
    note1 = Note(user_id=user_id, content="Oldest note", created=now - timedelta(days=2))
    note2 = Note(user_id=user_id, content="Middle note", created=now - timedelta(days=1))
    note3 = Note(user_id=user_id, content="Newest note", created=now)
    
    await note_repo.create(note1)
    await note_repo.create(note2)
    await note_repo.create(note3)
    
    # List notes
    notes = await note_repo.list_by_user(user_id)
    
    # Check they are in the right order (newest first)
    assert len(notes) == 3
    assert notes[0].content == "Newest note"
    assert notes[1].content == "Middle note"
    assert notes[2].content == "Oldest note"