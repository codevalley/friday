"""Enhanced SQLAlchemy models with vector support"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from src.config import get_settings

Base = declarative_base()

settings = get_settings()
VECTOR_DIMENSIONS = settings.vector_dimensions

# Try to import pgvector, but don't fail if not available
try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False
    Vector = None  # Type stub for static analysis

def generate_uuid():
    """Generate a UUID for a primary key"""
    return str(uuid.uuid4())


class UserModel(Base):
    """SQLAlchemy model for User entity"""
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(50), nullable=False, unique=True, index=True)
    user_secret = Column(String(255), nullable=False)  # Hashed password
    tier = Column(String(20), nullable=False, default="free")
    created_at = Column(DateTime, default=datetime.now)

    notes = relationship("NoteModel", back_populates="user", cascade="all, delete-orphan")


class NoteModel(Base):
    """SQLAlchemy model for Note entity with optional vector support"""
    __tablename__ = "notes"

    note_id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    content = Column(Text, nullable=False)
    created = Column(DateTime, default=datetime.now)

    # Conditionally add vector column if pgvector is available
    if HAS_PGVECTOR and settings.vector_search_enabled:
        embedding = Column(Vector(VECTOR_DIMENSIONS), nullable=True)

    user = relationship("UserModel", back_populates="notes")


# Define indexes for vector search if pgvector is available
if HAS_PGVECTOR and settings.vector_search_enabled:
    from sqlalchemy import Index
    from pgvector.sqlalchemy import IvfflatIndex
    
    # Create an IVF index on the embedding column for faster search
    # This will be created when tables are created
    vector_index = Index(
        'notes_embedding_idx', 
        NoteModel.embedding,
        postgresql_using='ivfflat',
        postgresql_with={'lists': 100}
    )