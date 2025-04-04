from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreateDTO(BaseModel):
    """Data transfer object for creating a user"""
    name: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    tier: Optional[str] = Field("free", pattern="^(free|premium|enterprise)$")


class UserUpdateDTO(BaseModel):
    """Data transfer object for updating a user"""
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=8)
    tier: Optional[str] = Field(None, pattern="^(free|premium|enterprise)$")


class UserReadDTO(BaseModel):
    """Data transfer object for reading a user"""
    user_id: str
    name: str
    tier: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserLoginDTO(BaseModel):
    """Data transfer object for user login"""
    name: str
    password: str


class TokenResponseDTO(BaseModel):
    """Data transfer object for token response"""
    access_token: str
    token_type: str = "bearer"