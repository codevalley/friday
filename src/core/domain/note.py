from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Note:
    """Note domain entity"""
    note_id: Optional[str] = None
    user_id: str = ""
    content: str = ""
    created: datetime = datetime.now()
    embedding: Optional[List[float]] = None  # Vector embedding for semantic search