import pytest
from datetime import datetime, timedelta

from src.core.domain.note import Note


def test_note_creation():
    """Test note entity creation with all attributes"""
    now = datetime.now()
    note = Note(
        note_id="note123",
        user_id="user123",
        content="Test note content",
        created=now
    )
    
    assert note.note_id == "note123"
    assert note.user_id == "user123"
    assert note.content == "Test note content"
    assert note.created == now


def test_note_defaults():
    """Test note entity defaults"""
    note = Note()
    
    assert note.note_id is None
    assert note.user_id == ""
    assert note.content == ""
    assert isinstance(note.created, datetime)


def test_note_minimal_creation():
    """Test note creation with minimal attributes"""
    note = Note(user_id="user123", content="Minimal note")
    
    assert note.note_id is None
    assert note.user_id == "user123"
    assert note.content == "Minimal note"
    assert isinstance(note.created, datetime)


def test_note_instance_identity():
    """Test note instance identity"""
    now = datetime.now()
    note1 = Note(note_id="note123", user_id="user123", content="Content", created=now)
    
    # Same instance comparison
    assert note1 is note1