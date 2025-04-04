from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User domain entity"""
    user_id: Optional[str] = None
    name: str = ""
    user_secret: str = ""  # Hashed password or API key
    tier: str = "free"  # Subscription tier
    created_at: datetime = datetime.now()  # Adding created_at field