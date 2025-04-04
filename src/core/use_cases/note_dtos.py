from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NoteCreateDTO(BaseModel):
    """Data transfer object for creating a note"""
    content: str = Field(..., min_length=1, max_length=10000)
    user_id: Optional[str] = None  # This can be derived from the auth token


class NoteUpdateDTO(BaseModel):
    """Data transfer object for updating a note"""
    content: str = Field(..., min_length=1, max_length=10000)


class NoteReadDTO(BaseModel):
    """Data transfer object for reading a note"""
    note_id: str
    user_id: str
    content: str
    created: datetime

    model_config = {"from_attributes": True}