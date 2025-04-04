import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


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
    """SQLAlchemy model for Note entity"""
    __tablename__ = "notes"

    note_id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    content = Column(Text, nullable=False)
    created = Column(DateTime, default=datetime.now)

    user = relationship("UserModel", back_populates="notes")