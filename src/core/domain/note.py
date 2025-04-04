from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Note:
    """Note domain entity"""
    note_id: Optional[str] = None
    user_id: str = ""
    content: str = ""
    created: datetime = datetime.now()